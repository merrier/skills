#!/usr/bin/env python3
"""Local publish manifest, fingerprints and resume checks; never operates a browser."""

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID
from zoneinfo import ZoneInfo

from inspect_media import IMAGES, VIDEOS


PLATFORMS = {'xiaohongshu', 'bilibili', 'douyin', 'wechat-channels'}
FIELDS = {'title', 'body', 'topics', 'media', 'covers', 'schedule', 'location', 'music', 'visibility', 'action'}
RESULT_STATES = {'submit_started', 'submitted', 'unknown'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    with Path(path).open(encoding='utf-8') as stream:
        value = json.load(stream)
    require(isinstance(value, dict), f'{path}: expected JSON object')
    return value


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def config():
    path = Path(os.environ.get('EGO_PUBLISH_CONFIG') or
                Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config') / 'ego-publish/config.json').expanduser()
    value = read_json(path) if path.exists() else {}
    allowed = {'schemaVersion', 'timezone', 'defaultPlatforms', 'keepResultTabs', 'bodyStyle', 'platforms'}
    require(not value.keys() - allowed, 'Unknown private preference; do not store credentials or publish authorization')
    result = {'schemaVersion': 1, 'timezone': 'Asia/Shanghai', 'defaultPlatforms': ['xiaohongshu'],
              'keepResultTabs': True, 'bodyStyle': '模型基础信息置顶，每项用 emoji 字段：值 单独一行，缺项省略；后接实物观察、细节介绍和互动问题', 'platforms': {}}
    result.update(value)
    require(result['schemaVersion'] == 1, 'Unsupported config schemaVersion')
    ZoneInfo(result['timezone'])
    require(isinstance(result['keepResultTabs'], bool), 'keepResultTabs must be boolean')
    require(isinstance(result['bodyStyle'], str), 'bodyStyle must be text')
    targets = result['defaultPlatforms']
    require(isinstance(targets, list) and targets and all(p in PLATFORMS for p in targets)
            and len(set(targets)) == len(targets), 'Invalid defaultPlatforms')
    require(isinstance(result['platforms'], dict), 'platforms must be an object')
    for platform, preferences in result['platforms'].items():
        require(platform in PLATFORMS and isinstance(preferences, dict), 'Invalid platform preferences')
        require(not preferences.keys() - {'titleFormat', 'collectionRule', 'collections'}, 'Unknown platform preference')
        require(isinstance(preferences.get('titleFormat', ''), str), 'titleFormat must be text')
        require(preferences.get('collectionRule', 'per_post') in {'per_post', 'model_scale'}, 'Invalid collectionRule')
        collections = preferences.get('collections', {})
        require(isinstance(collections, dict) and all(isinstance(k, str) and isinstance(v, str)
                and v.strip() for k, v in collections.items()), 'collections must map scale to name')
    return {'path': str(path), 'exists': path.exists(), 'preferences': result}


def file_identity(filename, extensions, cache):
    require(isinstance(filename, str) and Path(filename).is_absolute(), 'Media paths must be absolute')
    path = Path(filename).resolve(strict=True)
    require(path.is_file() and path.suffix.casefold() in extensions, f'Invalid media: {filename}')
    if str(path) not in cache:
        before = path.stat()
        hasher = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                hasher.update(chunk)
        after = path.stat()
        require((before.st_size, before.st_mtime_ns, before.st_ino) ==
                (after.st_size, after.st_mtime_ns, after.st_ino), f'File changed while hashing: {path}')
        require(after.st_size > 0, f'Empty media: {path}')
        cache[str(path)] = {'path': str(path), 'bytes': after.st_size, 'sha256': hasher.hexdigest()}
    return cache[str(path)]


def schedule_time(schedule):
    require(isinstance(schedule, dict), 'schedule must be an object')
    require(schedule.get('mode') in {'immediate', 'scheduled'}, 'Invalid schedule mode')
    if schedule['mode'] == 'immediate':
        require(set(schedule) == {'mode'}, 'Immediate schedule must not contain an old date')
        return None
    require(set(schedule) == {'mode', 'at'}, 'Scheduled date required')
    result = datetime.fromisoformat(schedule['at'])
    require(result.utcoffset() is not None, 'Scheduled date must include timezone offset')
    return result


def snapshot(package):
    require(package.get('schemaVersion') == 1, 'Unsupported package schemaVersion')
    UUID(package['taskId'])
    require(package.get('kind') in {'image', 'video'}, 'kind must be image or video')
    order, platforms, shared = package['platformOrder'], package['platforms'], package['shared']
    require(isinstance(order, list) and order and all(p in PLATFORMS for p in order)
            and len(set(order)) == len(order), 'Invalid platformOrder')
    require(isinstance(platforms, dict) and set(order) == set(platforms), 'platformOrder must list every platform once')
    require(isinstance(shared, dict) and set(shared) == FIELDS, f'shared requires fields: {sorted(FIELDS)}')
    cache, resolved = {}, {}
    for platform in order:
        target = platforms[platform]
        require(isinstance(target, dict) and set(target) <= {'account', 'settings', 'overrides'}, 'Invalid platform fields')
        require(isinstance(target.get('account'), str) and target['account'].strip(), f'{platform}: account required')
        require(isinstance(target.get('settings'), dict), f'{platform}: settings required')
        effective = dict(shared)
        overrides = target.get('overrides', {})
        require(isinstance(overrides, dict) and set(overrides) <= FIELDS, f'{platform}: invalid override')
        for field, override in overrides.items():
            require(isinstance(override, dict) and set(override) == {'from', 'value'}, f'{platform}.{field}: use from/value')
            require(override['from'] == shared[field], f'{platform}.{field}: stale override; review against changed shared value')
            effective[field] = override['value']
        for field in ('title', 'body', 'visibility'):
            require(isinstance(effective[field], str) and effective[field].strip(), f'{platform}: {field} required')
        require(effective['action'] in {'draft', 'submit'}, f'{platform}: action must be draft or submit')
        require(isinstance(effective['topics'], list) and all(isinstance(t, str) and t.strip()
                for t in effective['topics']), f'{platform}: invalid topics')
        require(effective['location'] is None or isinstance(effective['location'], str), 'location must be text or null')
        require(effective['music'] is None or isinstance(effective['music'], dict), 'music must be an object or null')
        schedule_time(effective['schedule'])
        media, covers = effective['media'], effective['covers']
        require(isinstance(media, list) and media, f'{platform}: ordered media required')
        require(package['kind'] == 'image' or len(media) == 1, 'Choose exactly one finished video')
        identities = [file_identity(p, IMAGES if package['kind'] == 'image' else VIDEOS, cache) for p in media]
        require(len({p['path'] for p in identities}) == len(media), f'{platform}: duplicate media')
        require(isinstance(covers, dict) and all(isinstance(k, str) and k for k in covers), 'covers must map slot to file')
        cover_files = {slot: file_identity(path, IMAGES, cache) for slot, path in covers.items()}
        effective.update(account=target['account'], settings=target['settings'])
        fingerprints = {
            'content': digest({k: v for k, v in effective.items() if k not in {'media', 'covers'}}),
            'media': digest(identities), 'covers': digest(cover_files),
        }
        resolved[platform] = {'effective': effective, 'mediaFiles': identities, 'coverFiles': cover_files,
                              'fingerprints': fingerprints, 'fingerprint': digest(fingerprints)}
    return {'schemaVersion': 1, 'taskId': package['taskId'], 'kind': package['kind'],
            'platformOrder': order, 'platforms': resolved}


def compare(current, confirmed=None, receipts=None, now=None):
    now = now or datetime.now(timezone.utc)
    for record in (confirmed, receipts):
        if record is not None:
            require(record.get('schemaVersion') == 1 and record.get('taskId') == current['taskId'],
                    'Record belongs to another task or legacy schema; inspect before migrating')
    if confirmed:
        require(confirmed.get('kind') == current['kind'], 'Content type changed; create a new task')
    results = {}
    for platform, item in current['platforms'].items():
        old = (confirmed or {}).get('platforms', {}).get(platform)
        receipt = (receipts or {}).get('platforms', {}).get(platform)
        status = receipt.get('status') if receipt else None
        require(status in {None, 'draft', 'failed'} | RESULT_STATES, f'{platform}: invalid receipt status')
        changed = [field for field, value in item['fingerprints'].items()
                   if not old or old['fingerprints'].get(field) != value]
        if status in RESULT_STATES:
            action = 'verify_result_only'
        elif changed:
            action = 'needs_confirmation'
        elif (at := schedule_time(item['effective']['schedule'])) and at <= now:
            action = 'needs_new_time'
        else:
            action = 'resume_and_verify'
        results[platform] = {'next': action, 'changed': changed, 'recordedStatus': status,
                             'fingerprint': item['fingerprint'], 'plannedAction': item['effective']['action']}
    removed = set((confirmed or {}).get('platforms', {})) - set(current['platforms'])
    return {'taskId': current['taskId'], 'platforms': results, 'removedPlatforms': sorted(removed),
            'note': 'Local comparison only. Check live page and actual user authorization before any submission.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('config', help='Read private preferences; does not apply them to a confirmed plan')
    inspect_command = commands.add_parser('check', help='Validate, resolve platform values and compare a prior snapshot')
    inspect_command.add_argument('package')
    inspect_command.add_argument('--against')
    inspect_command.add_argument('--receipts')
    save = commands.add_parser('snapshot', help='Save local fingerprints; this command does not grant publish authorization')
    save.add_argument('package')
    save.add_argument('--output', required=True, help='New filename; existing snapshots are never overwritten')
    args = parser.parse_args()
    try:
        if args.command == 'config':
            result = config()
        else:
            current = snapshot(read_json(args.package))
            if args.command == 'snapshot':
                with Path(args.output).open('x', encoding='utf-8') as stream:
                    json.dump(current, stream, ensure_ascii=False, indent=2)
                    stream.write('\n')
                result = {'snapshotPath': str(Path(args.output).resolve()), 'taskId': current['taskId']}
            else:
                result = {'snapshot': current, 'comparison': compare(current,
                          read_json(args.against) if args.against else None,
                          read_json(args.receipts) if args.receipts else None)}
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f'{error}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
