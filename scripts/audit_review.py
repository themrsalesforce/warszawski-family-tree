"""Read-only audit of the actual 236-page PDFs, not the stale 212-page checklist.

Requires pymupdf. Saves page coverage, register/household entries, exact source links,
and edition comparison for a reproducible review. Does not authenticate sources.
"""
from pathlib import Path
import collections
import csv
import hashlib
import json
import re
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/review-2026-10-02'
OUT.mkdir(parents=True, exist_ok=True)
BASE = ROOT / 'Warszawski/05-Print-editions'
READING = BASE / 'The-Warszawskis-Coffee-Table-Edition-2026-10-01-Reading-Copy.pdf'
PRINT = BASE / 'The-Warszawskis-Coffee-Table-Edition-2026-10-01-Print-Interior.pdf'


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def entries(doc, first, last, font_size):
    records = []
    current = None
    for index in range(first - 1, last):
        for block in doc[index].get_text('dict', sort=True)['blocks']:
            if block['type'] != 0:
                continue
            for line in block['lines']:
                for span in line['spans']:
                    text = span['text'].strip()
                    if not text or text == 'THE WARSZAWSKIS' or text == str(index + 1):
                        continue
                    if abs(span['size'] - font_size) < 0.05:
                        if current and current.get('heading_open'):
                            current['name'] += ' ' + text
                        else:
                            current = {'page': index + 1, 'name': text, 'text': '', 'heading_open': True}
                            records.append(current)
                    elif current:
                        current['heading_open'] = False
                        current['text'] += text + '\n'
    for record in records:
        record.pop('heading_open', None)
        record['classification'] = record['text'].splitlines()[0] if record['text'] else ''
    return records


def main():
    reading, printing = pymupdf.open(READING), pymupdf.open(PRINT)
    page_records, source_links = [], []
    for index, page in enumerate(reading):
        text = page.get_text(sort=True)
        spans = [s for b in page.get_text('dict', sort=True)['blocks'] if b['type'] == 0
                 for line in b['lines'] for s in line['spans'] if s['text'].strip()]
        page_records.append({'page': index + 1, 'words': len(text.split()),
                             'heading': ' / '.join(s['text'] for s in spans if s['size'] >= 25),
                             'image_placements': len(page.get_image_info()),
                             'text': text})
        for link in page.get_links():
            if link.get('uri'):
                source_links.append({'page': index + 1, 'url': link['uri'], 'bbox': list(link['from'])})
    dump('page-text.json', page_records)
    dump('pdf-source-links.json', source_links)
    people = entries(reading, 100, 151, 18)
    households = entries(reading, 152, 164, 18)
    sources = entries(reading, 180, 204, 16.5)
    new_sources = entries(reading, 224, 227, 12.5)
    dump('register-coverage.json', people)
    dump('household-coverage.json', households)
    dump('source-catalogue-coverage.json', sources + new_sources)
    all_text = '\n'.join(p['text'] for p in page_records)
    used = set(re.findall(r'\bS\d{3}\b', all_text))
    defined = {s['name'].split()[0] for s in sources}
    result = {
        'review_date': '2026-10-02',
        'reading_sha256': hashlib.sha256(READING.read_bytes()).hexdigest(),
        'print_sha256': hashlib.sha256(PRINT.read_bytes()).hexdigest(),
        'reading_pages': len(reading), 'print_pages': len(printing),
        'differing_text_pages': [i + 1 for i in range(min(len(reading), len(printing)))
                                 if reading[i].get_text() != printing[i].get_text()],
        'reading_page_size': list(reading[0].rect), 'print_page_size': list(printing[0].rect),
        'print_trim_box': list(printing[0].trimbox),
        'words_including_headers_and_reference_material': sum(p['words'] for p in page_records),
        'person_entries': len(people), 'household_entries': len(households),
        'person_classifications': dict(collections.Counter(r['classification'].split(' · ')[0] for r in people)),
        'source_entries_S': len(sources), 'source_entries_W': len(new_sources),
        'undefined_S_identifiers': sorted(used - defined),
        'external_link_placements': len(source_links),
        'limitations': ['No independent authentication of every claim',
                       'Automated extraction may not read scanned handwriting',
                       'Source entries include search results and derivative records',
                       'No full current production-source package supplied'],
    }
    dump('review-verification.json', result)
    with (OUT / 'page-map.csv').open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['page', 'words', 'heading', 'image_placements'], lineterminator='\n')
        writer.writeheader()
        writer.writerows({k: p[k] for k in writer.fieldnames} for p in page_records)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
