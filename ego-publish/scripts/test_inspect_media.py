import tempfile
import unittest
from pathlib import Path

from inspect_media import inspect


class MediaInventoryTest(unittest.TestCase):
    def test_recommendations_and_read_only_scope(self):
        cases = {
            'photo': (['实拍.JPG', '封面_3x4.png', '小红书定时发布记录.png'], 'image'),
            'video': (['成片.MOV', '封面_16x9.png', '字幕.srt'], 'video'),
            'mixed': (['成片.mp4', '整车.jpg'], 'mixed'),
            'multiple': (['成片.mp4', '另一个.webm'], 'choose_video'),
            'covers': (['封面_1x1.png'], 'cover_only'),
            'empty': (['模型信息.md'], 'no_media'),
            'artifacts': (['发布预览_小红书.png', '小红书定时草稿预览.png'], 'no_media'),
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, (names, expected) in cases.items():
                folder = root / name
                folder.mkdir()
                for filename in names:
                    (folder / filename).write_bytes(b'fixture: filename inventory, not a media decoder')
                before = {p.name: p.read_bytes() for p in folder.iterdir()}
                result = inspect(folder)
                with self.subTest(name=name):
                    self.assertEqual(result['recommendation'], expected)
                    self.assertEqual(before, {p.name: p.read_bytes() for p in folder.iterdir()})
            photo = root / 'photo'
            (photo / '.hidden.mp4').write_bytes(b'')
            (photo / 'external.mov').symlink_to(root / 'video' / '成片.MOV')
            self.assertEqual(inspect(photo)['recommendation'], 'image')
            groups = inspect(photo)['files']
            self.assertEqual([Path(p['path']).name for p in groups['images']], ['实拍.JPG'])
            self.assertEqual(len(groups['covers']), 1)
            self.assertEqual(len(groups['excluded_images']), 1)
            self.assertEqual(inspect(root)['recommendation'], 'choose_folder')
            self.assertFalse(inspect(root)['files']['images'])
            hidden = root / '.cover-work'
            hidden.mkdir()
            (hidden / 'draft.mp4').write_bytes(b'')
            self.assertNotIn(str(hidden), [p['path'] for p in inspect(root)['subfolders']])
            with self.assertRaises(FileNotFoundError):
                inspect(root / 'missing')
            with self.assertRaises(ValueError):
                inspect(photo / '实拍.JPG')


if __name__ == '__main__':
    unittest.main()
