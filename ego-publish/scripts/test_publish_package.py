import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from publish_package import compare, config, snapshot


class PublishPackageTest(unittest.TestCase):
    def test_gallery_resume_changes_and_video(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            photos = [folder / name for name in ('front.jpg', 'rear.jpg')]
            cover = folder / 'cover.png'
            for path in photos + [cover]:
                path.write_bytes(b'original')
            package = {
                'schemaVersion': 1, 'taskId': str(uuid4()), 'kind': 'image',
                'platformOrder': ['xiaohongshu', 'bilibili'],
                'shared': {'title': '小车身，大尾翼', 'body': '实物观察第一段。\n\n产品信息第二段。',
                           'topics': ['汽车模型'], 'media': [str(p) for p in photos], 'covers': {'main': str(cover)},
                           'schedule': {'mode': 'scheduled', 'at': '2099-09-11T20:18:00+08:00'},
                           'location': None, 'music': None, 'visibility': 'public', 'action': 'submit'},
                'platforms': {'xiaohongshu': {'account': 'test', 'settings': {}, 'overrides': {}},
                              'bilibili': {'account': 'test', 'settings': {}, 'overrides': {
                                  'title': {'from': '小车身，大尾翼', 'value': '小车身，大尾翼 | 1:43 Ford Escort'}}}},
            }
            frozen = snapshot(package)
            self.assertEqual(frozen['platforms']['bilibili']['effective']['body'], package['shared']['body'])
            self.assertEqual(compare(frozen)['platforms']['bilibili']['next'], 'needs_confirmation')
            self.assertEqual(compare(frozen, frozen)['platforms']['xiaohongshu']['next'], 'resume_and_verify')
            changed = copy.deepcopy(package)
            changed['shared']['title'] = '新的文案'
            with self.assertRaisesRegex(ValueError, 'stale override'):
                snapshot(changed)
            changed = copy.deepcopy(package)
            changed['shared']['media'].reverse()
            report = compare(snapshot(changed), frozen)['platforms']
            self.assertEqual(report['xiaohongshu']['changed'], ['media'])
            photos[0].write_bytes(b'replaced')  # Same path and length; stat-only identity would miss it.
            self.assertEqual(compare(snapshot(package), frozen)['platforms']['xiaohongshu']['changed'], ['media'])
            photos[0].write_bytes(b'original')
            cover.write_bytes(b'newcover')
            self.assertEqual(compare(snapshot(package), frozen)['platforms']['bilibili']['changed'], ['covers'])
            cover.write_bytes(b'original')
            changed = copy.deepcopy(package)
            changed['platforms']['bilibili']['settings']['collection'] = 'new'
            report = compare(snapshot(changed), frozen)['platforms']
            self.assertEqual(report['xiaohongshu']['changed'], [])
            self.assertEqual(report['bilibili']['changed'], ['content'])
            receipts = {'schemaVersion': 1, 'taskId': package['taskId'], 'platforms': {}}
            for status in ('submit_started', 'submitted', 'unknown'):
                receipts['platforms']['bilibili'] = {'status': status}
                self.assertEqual(compare(snapshot(changed), frozen, receipts)['platforms']['bilibili']['next'],
                                 'verify_result_only')
            receipts['taskId'] = str(uuid4())
            with self.assertRaisesRegex(ValueError, 'another task'):
                compare(frozen, frozen, receipts)
            expired = compare(frozen, frozen, now=datetime(2100, 1, 1, tzinfo=timezone.utc))
            self.assertEqual(expired['platforms']['bilibili']['next'], 'needs_new_time')
            changed = copy.deepcopy(package)
            changed['shared']['schedule']['at'] = '2099-09-11T20:18:00'
            with self.assertRaisesRegex(ValueError, 'timezone'):
                snapshot(changed)
            changed = copy.deepcopy(package)
            changed['shared']['media'].append(str(photos[0]))
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                snapshot(changed)
            changed = copy.deepcopy(package)
            changed['kind'] = 'video'
            video = folder / 'finished.mp4'
            video.write_bytes(b'video bytes; not a decoder test')
            changed['shared']['media'] = [str(video)]
            self.assertEqual(len(snapshot(changed)['platforms']['bilibili']['mediaFiles']), 1)
            with self.assertRaisesRegex(ValueError, 'Content type changed'):
                compare(snapshot(changed), frozen)
            changed['shared']['media'].append(str(video))
            with self.assertRaisesRegex(ValueError, 'exactly one'):
                snapshot(changed)
            package_file, frozen_file = folder / 'package.json', folder / 'confirmed.json'
            package_file.write_text(json.dumps(package), encoding='utf-8')
            command = [sys.executable, '-B', str(Path(__file__).with_name('publish_package.py')),
                       'snapshot', str(package_file), '--output', str(frozen_file)]
            subprocess.run(command, capture_output=True, check=True)
            before = frozen_file.read_bytes()
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(frozen_file.read_bytes(), before)
            photos[0].unlink()
            with self.assertRaises(FileNotFoundError):
                snapshot(package)

    def test_private_preferences_are_read_only_and_do_not_grant_authorization(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ, {'XDG_CONFIG_HOME': temporary}):
            with patch.dict(os.environ):
                os.environ.pop('EGO_PUBLISH_CONFIG', None)
                result = config()
                self.assertFalse(result['exists'])
                self.assertTrue(result['preferences']['keepResultTabs'])
                path = Path(result['path'])
                self.assertFalse(path.exists())
            explicit = Path(temporary) / 'explicit.json'
            explicit.write_text(json.dumps({'schemaVersion': 1, 'keepResultTabs': False,
                                           'defaultPlatforms': ['bilibili']}))
            with patch.dict(os.environ, {'EGO_PUBLISH_CONFIG': str(explicit)}):
                self.assertFalse(config()['preferences']['keepResultTabs'])
                self.assertEqual(config()['preferences']['defaultPlatforms'], ['bilibili'])
                explicit.write_text(json.dumps({'authorization': 'auto publish everything'}))
                with self.assertRaisesRegex(ValueError, 'Unknown private preference'):
                    config()


if __name__ == '__main__':
    unittest.main()
