"""Read-only geometry and image-resolution triage of the actual print interior."""
from pathlib import Path
import json
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'Warszawski/05-Print-editions/The-Warszawskis-Coffee-Table-Edition-2026-10-01-Print-Interior.pdf'
OUTPUT = ROOT / 'analysis/review-2026-10-02/print-layout-verification.json'


def main():
    document = pymupdf.open(SOURCE)
    result = {
        'source': str(SOURCE.relative_to(ROOT)), 'page_count': len(document),
        'large_image_placements_below_130dpi': [],
        'large_image_placements_below_200dpi': [],
        'text_outside_page': [], 'bad_internal_links': [],
    }
    for number, page in enumerate(document, 1):
        for placement in page.get_image_info():
            rect = pymupdf.Rect(placement['bbox'])
            if rect.width <= 150 or rect.height <= 150:
                continue
            dpi = min(placement['width'] / rect.width * 72,
                      placement['height'] / rect.height * 72)
            info = {'page': number, 'dpi': round(dpi, 1),
                    'pixels': [placement['width'], placement['height']]}
            if dpi < 130:
                result['large_image_placements_below_130dpi'].append(info)
            if dpi < 200:
                result['large_image_placements_below_200dpi'].append(info)
        for block in page.get_text('dict')['blocks']:
            if block['type'] != 0:
                continue
            for line in block['lines']:
                for span in line['spans']:
                    if span['text'].strip() and not page.rect.contains(pymupdf.Rect(span['bbox'])):
                        result['text_outside_page'].append({
                            'page': number, 'text': span['text'], 'bbox': span['bbox']})
        for link in page.get_links():
            if link.get('kind') == pymupdf.LINK_GOTO and not 0 <= link.get('page', -1) < len(document):
                result['bad_internal_links'].append({'page': number, 'target': link.get('page')})
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: len(value) for key, value in result.items() if isinstance(value, list)}))


if __name__ == '__main__':
    main()
