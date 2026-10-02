"""Track ignored asset hashes; preserve bytes outside Git and avoid no-change churn."""
import hashlib
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXTENSIONS = {'.pdf', '.zip', '.doc', '.docx', '.xlsx', '.pptx', '.jpg', '.jpeg',
              '.png', '.gif', '.tif', '.tiff', '.webp', '.mp3', '.mp4', '.mov',
              '.woff', '.woff2', '.ttf', '.otf'}
DISGUISED_ARCHIVES = {'Warszawski/03-Archive-records/warszawski-family-tree-v1.17.json'}


def main():
    target = ROOT / 'inventory/local-binary-state.json'
    previous = json.loads(target.read_text()) if target.exists() else []
    names = subprocess.check_output(['git', 'ls-files', '--others', '--ignored',
                                     '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')
    records = []
    for name in sorted(filter(None, names)):
        relative = pathlib.PurePosixPath(name)
        if any(part.startswith('.') or part in {'__pycache__', 'node_modules', '__MACOSX'}
               for part in relative.parts):
            continue
        path = ROOT / name
        if (path.suffix.lower() not in EXTENSIONS and name not in DISGUISED_ARCHIVES) or not path.is_file() or path.is_symlink():
            continue
        before = path.stat()
        with path.open('rb') as source:
            sha = hashlib.file_digest(source, 'sha256').hexdigest()
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise SystemExit(f'Asset is being edited; retry later: {name}')
        records.append({'path': name, 'bytes': after.st_size, 'sha256': sha})
    if records != previous:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
    old, new = {x['path']: x for x in previous}, {x['path']: x for x in records}
    changes = sum(old.get(name) != new.get(name) for name in old.keys() | new.keys())
    print(json.dumps({'binary_assets': len(records), 'changed_asset_records': changes,
                      'manifest_updated': records != previous}))


if __name__ == '__main__':
    main()
