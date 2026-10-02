"""Verify originals, expand ZIPs, extract document text, and inventory the project.

Run from any directory: python3 scripts/index_project.py
Requires Poppler's pdftotext and macOS textutil for document extraction.
Imported source scripts are not executed.
"""
import collections
import concurrent.futures
import csv
import hashlib
import json
import pathlib
import stat
import subprocess
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {'.md', '.txt', '.csv', '.tsv', '.json', '.jsonl', '.yaml', '.yml',
                   '.py', '.js', '.ts', '.html', '.css', '.xml', '.xsd', '.ged', '.svg',
                   '.tex', '.mmd', '.kml', '.vtt'}


def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def expand(archive):
    destination = archive.parent / 'expanded' / archive.stem
    members = []
    with zipfile.ZipFile(archive) as source:
        for info in source.infolist():
            relative = pathlib.PurePosixPath(info.filename)
            if relative.is_absolute() or '..' in relative.parts or '\\' in info.filename:
                raise ValueError(f'Unsafe archive path: {info.filename}')
            if any(x in {'.git', '__MACOSX'} for x in relative.parts):
                continue
            if stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError(f'Archive symlink: {info.filename}')
            target = destination.joinpath(*relative.parts)
            target.resolve().relative_to(ROOT)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            # Reading complete members checks ZIP CRCs; preserve original bytes.
            content = source.read(info)
            target.write_bytes(content)
            members.append({'path': str(target.relative_to(ROOT)), 'bytes': len(content),
                            'sha256': hashlib.sha256(content).hexdigest()})
    return {'archive': str(archive.relative_to(ROOT)), 'members': members}


def extract_text(path):
    relative = path.relative_to(ROOT)
    target = ROOT / 'analysis' / 'document-text' / relative.with_suffix(relative.suffix + '.txt')
    target.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == '.pdf':
        command = ['pdftotext', '-layout', str(path), str(target)]
    else:
        command = ['textutil', '-convert', 'txt', '-output', str(target), str(path)]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        if result.returncode:
            raise ValueError(result.stderr[:500])
        content = target.read_text(errors='replace')
        return {'source': str(relative), 'text': str(target.relative_to(ROOT)),
                'status': 'extracted' if len(content.strip()) >= 50 else 'needs-ocr-or-review',
                'characters': len(content)}
    except Exception as exc:
        return {'source': str(relative), 'status': 'failed', 'error': str(exc)}


def main():
    snapshot = json.loads((ROOT / 'inventory' / 'drive-snapshot.json').read_text())
    originals = []
    for item in snapshot['files']:
        path = ROOT / item['local_path']
        record = {k: item.get(k) for k in ('id', 'title', 'url', 'local_path', 'mime_type',
                                          'size', 'modified_time', 'parent_id')}
        if not path.exists():
            record['status'] = 'missing'
        else:
            record.update(bytes=path.stat().st_size, sha256=digest(path), status='verified')
            if item.get('size') is not None and path.stat().st_size != int(item['size']):
                record['status'] = 'size-mismatch'
        originals.append(record)
    write_json(ROOT / 'inventory' / 'import-manifest.json', originals)
    missing = [x for x in originals if x['status'] != 'verified']
    if missing:
        raise SystemExit(f'Incomplete import: {len(missing)} originals missing or wrong size')
    archives = []
    queue = [ROOT / x['local_path'] for x in originals if zipfile.is_zipfile(ROOT / x['local_path'])]
    while queue:
        archive = queue.pop(0)
        result = expand(archive)
        archives.append(result)
        queue.extend(ROOT / x['path'] for x in result['members'] if zipfile.is_zipfile(ROOT / x['path']))
    write_json(ROOT / 'inventory' / 'archive-members.json', archives)
    files = [p for folder in ('Warszawski', 'Family-History-Shared')
             for p in (ROOT / folder).rglob('*') if p.is_file()]
    documents = [p for p in files if p.suffix.lower() in {'.pdf', '.doc', '.docx'}]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        extraction = list(pool.map(extract_text, documents))
    write_json(ROOT / 'inventory' / 'text-extraction.json', extraction)
    records = []
    groups = collections.defaultdict(list)
    for p in files:
        sha = digest(p)
        relative = str(p.relative_to(ROOT))
        records.append({'path': relative, 'bytes': p.stat().st_size,
                        'extension': p.suffix.lower(), 'sha256': sha,
                        'text_source': p.suffix.lower() in TEXT_EXTENSIONS})
        groups[sha].append(relative)
    write_json(ROOT / 'inventory' / 'project-files.json', records)
    duplicates = [{'sha256': key, 'paths': paths} for key, paths in groups.items() if len(paths) > 1]
    write_json(ROOT / 'inventory' / 'duplicate-groups.json', duplicates)
    with (ROOT / 'inventory' / 'project-files.csv').open('w', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    extensions = collections.Counter(x['extension'] for x in records)
    report = [
        '# Warszawski project import and baseline inventory', '',
        'Import date: 2026-10-02. This report checks file completeness and accessibility; '
        'it does not establish the accuracy of genealogical claims.', '',
        f'- Drive originals verified: {len(originals)} / {len(originals)}.',
        f'- Original bytes downloaded: {sum(x["bytes"] for x in originals):,}.',
        f'- ZIP archives expanded with CRC checks: {len(archives)}.',
        f'- Files in the imported and expanded corpus: {len(records):,}.',
        f'- Text/source files: {sum(x["text_source"] for x in records):,}.',
        f'- Exact duplicate groups: {len(duplicates):,} (preserved).',
        f'- Documents with text extracted: {sum(x["status"] == "extracted" for x in extraction):,}.',
        f'- Documents needing OCR or review: {sum(x["status"] == "needs-ocr-or-review" for x in extraction):,}.',
        f'- Document extraction failures: {sum(x["status"] == "failed" for x in extraction):,}.', '',
        '## File types', '', '| Extension | Files |', '| --- | ---: |',
        *[f'| {ext or "(none)"} | {count:,} |' for ext, count in sorted(extensions.items())], '',
        '## Scope and provenance', '',
        'The complete Family History/Warszawski folder is preserved, including misfiled Chaikin manuscripts. Shared index and cross-family files and separately stored Warszawski print editions are also included.', '',
        'Original Drive metadata and source URLs are in inventory/drive-snapshot.json. '
        'inventory/import-manifest.json records SHA-256 checksums and byte counts. '
        'inventory/archive-members.json maps expanded files to their original ZIPs. '
        'inventory/duplicate-groups.json identifies identical files across versions.', '',
        '## Analysis limits', '',
        'Text extraction preserves readable content but cannot establish document layout, '
        'read handwriting, or interpret images. OCR has not been run. Extraction status for '
        'every PDF/Word document is recorded in inventory/text-extraction.json. Historical '
        'snapshots contain repeated people, claims, and sources; do not sum them as separate '
        'evidence. Imported build scripts have not been executed.', '',
        '## Next substantive checks', '',
        '1. Compare the latest tree-data snapshot with the current editable production manuscript.',
        '2. Audit people, relationship links, conflicting dates, source references, and unresolved claims.',
        '3. Review scans requiring OCR and build a source-to-claim evidence index.', ''
    ]
    target = ROOT / 'analysis' / 'IMPORT-REPORT.md'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('\n'.join(report))
    print('\n'.join(report[:14]))


if __name__ == '__main__':
    main()
