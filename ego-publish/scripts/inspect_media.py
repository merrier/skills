#!/usr/bin/env python3
"""Read-only filename inventory; inspect actual media before selecting uploads."""

import argparse
import json
from pathlib import Path


IMAGES = {'.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.avif', '.tif', '.tiff', '.bmp', '.gif'}
VIDEOS = {'.mp4', '.mov', '.m4v', '.webm', '.mkv', '.avi', '.mts', '.m2ts', '.wmv'}
SUBTITLES = {'.srt', '.vtt', '.ass', '.ssa'}
COVER_PREFIXES = ('封面', 'cover', 'thumbnail', 'thumb_', '海报')
ARTIFACT_PREFIXES = (
    '发布记录', '发布截图', '发布预览', '草稿预览', '联系表', 'contact-sheet',
    '小红书发布记录', '小红书定时发布记录', '小红书定时草稿预览', '小红书定时草稿核验',
)
SKIP_DIRS = {'node_modules', '__pycache__', '备份', '水印原图备份', '原图备份', '旧封面', 'backup', 'backups'}


def file_kind(path):
    name, ext = path.name.casefold(), path.suffix.casefold()
    if ext in IMAGES:
        if name.startswith(ARTIFACT_PREFIXES):
            return 'excluded_images'
        return 'covers' if name.startswith(COVER_PREFIXES) else 'images'
    if ext in VIDEOS:
        return 'videos'
    if ext in SUBTITLES:
        return 'subtitles'
    if ext in {'.md', '.txt', '.json'}:
        return 'documents'
    return None


def files_in(folder):
    groups = {name: [] for name in ('images', 'videos', 'covers', 'subtitles', 'documents', 'excluded_images')}
    for path in sorted(folder.iterdir(), key=lambda p: p.name.casefold()):
        if path.name.startswith('.') or path.is_symlink() or not path.is_file():
            continue
        kind = file_kind(path)
        if kind:
            groups[kind].append({'path': str(path), 'bytes': path.stat().st_size})
    return groups


def inspect(folder):
    folder = Path(folder).expanduser().resolve(strict=True)
    if not folder.is_dir():
        raise ValueError('Expected a material directory')
    groups = files_in(folder)
    children = []
    for child in sorted(folder.iterdir(), key=lambda p: p.name.casefold()):
        if child.name.startswith('.') or child.name.casefold() in SKIP_DIRS or child.is_symlink() or not child.is_dir():
            continue
        counts = {key: len(value) for key, value in files_in(child).items() if key in ('images', 'videos', 'covers')}
        children.append({'path': str(child), 'direct_counts': counts})

    images, videos = len(groups['images']), len(groups['videos'])
    if videos > 1:
        recommendation = 'choose_video'
    elif videos and images:
        recommendation = 'mixed'
    elif videos:
        recommendation = 'video'
    elif images:
        recommendation = 'image'
    elif any(any(child['direct_counts'].values()) for child in children):
        recommendation = 'choose_folder'
    elif groups['covers']:
        recommendation = 'cover_only'
    else:
        recommendation = 'no_media'
    return {'folder': str(folder), 'recommendation': recommendation,
            'scope': 'direct_files_only', 'files': groups, 'subfolders': children}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', help='One selected material directory; children are listed, not merged')
    args = parser.parse_args()
    try:
        result = inspect(args.folder)
    except (OSError, ValueError) as error:
        parser.exit(2, f'{error}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
