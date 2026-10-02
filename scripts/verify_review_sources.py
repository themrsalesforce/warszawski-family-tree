"""Recheck public review URLs into a new snapshot; never download interview video.

Usage: python3 scripts/verify_review_sources.py --output .analysis-cache/source-recheck
The historical review log is not overwritten. No credentials are used.
"""
from pathlib import Path
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / 'analysis/review-2026-10-02/source-verification/verification-log.json'
MAX_BYTES = 5 * 1024 * 1024


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    log_path = output / 'verification-log.json'
    if log_path.exists():
        parser.error('Use a new snapshot directory; an existing verification log is preserved.')
    originals = json.loads(SEED.read_text())
    unique = {}
    for entry in originals:
        unique.setdefault((entry['url'], entry.get('method', 'GET')), entry)
    checked_at = datetime.now(timezone.utc).isoformat()

    def retrieve(entry):
        url, method = entry['url'], entry.get('method', 'GET')
        if not url.startswith('https://'):
            raise ValueError('Only recorded HTTPS public URLs are supported.')
        if url.lower().endswith('.mp4') and method != 'HEAD':
            raise ValueError('Video must use HEAD metadata checks, not GET.')
        result = {'id': entry['id'], 'url': url, 'method': method, 'checked_at': checked_at}
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}, method=method)
            with urllib.request.urlopen(request, timeout=25) as response:
                mime = response.headers.get_content_type()
                result.update(http_status=response.status, mime_type=mime)
                if method == 'HEAD':
                    result.update(status='head-available', content_length=response.headers.get('Content-Length'))
                else:
                    data = response.read(MAX_BYTES + 1)
                    if len(data) > MAX_BYTES:
                        raise ValueError('Response exceeds snapshot size limit.')
                    extension = '.pdf' if data.startswith(b'%PDF') else '.jpg' if data.startswith(b'\xff\xd8') else '.vtt' if url.endswith('.vtt') else '.html'
                    (output / (entry['id'] + extension)).write_bytes(data)
                    result.update(status='retrieved', bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        except Exception as error:
            result.update(status='unavailable', error=str(error))
        return result

    with ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(retrieve, unique.values()))
    log_path.write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps({'checked': len(results), 'available': sum(r['status'] != 'unavailable' for r in results), 'log': str(log_path)}))


if __name__ == '__main__':
    main()
