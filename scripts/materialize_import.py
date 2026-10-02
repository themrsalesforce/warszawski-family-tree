"""Materialize authenticated Drive file references supplied on stdin.

Transfer URLs are transient and are never saved in the repository.
"""
import concurrent.futures
import hashlib
import json
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]


def download(item):
    target = ROOT / item['local_path']
    target.resolve().relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_name(target.name + '.download-part')
    try:
        request = urllib.request.Request(item['download_url'], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(request, timeout=180) as response:
            with partial.open('wb') as output:
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
        size = partial.stat().st_size
        expected = item.get('size')
        if expected is not None and size != int(expected):
            raise ValueError(f'size mismatch: {size} != {expected}')
        partial.replace(target)
        with target.open('rb') as source:
            digest = hashlib.file_digest(source, 'sha256').hexdigest()
        return {'id': item['id'], 'local_path': item['local_path'],
                'status': 'downloaded', 'bytes': size, 'sha256': digest}
    except Exception as exc:
        partial.unlink(missing_ok=True)
        return {'id': item['id'], 'local_path': item['local_path'],
                'status': 'failed', 'error': str(exc)}


if __name__ == '__main__':
    items = json.load(sys.stdin)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(download, items))
    log = ROOT / 'inventory' / 'download-log.jsonl'
    with log.open('a') as output:
        for result in results:
            output.write(json.dumps(result, ensure_ascii=False) + '\n')
    print(json.dumps({'completed': sum(x['status'] == 'downloaded' for x in results),
                      'failed': [x for x in results if x['status'] != 'downloaded']}))
