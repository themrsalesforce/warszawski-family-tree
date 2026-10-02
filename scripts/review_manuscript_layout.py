"""Read-only PDF audit and contact sheets for the 2026-10-02 review."""
from pathlib import Path
import json, re, hashlib
import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'Warszawski/05-Print-editions/The-Warszawskis-Coffee-Table-Edition-2026-10-01-Reading-Copy.pdf'
OUT = ROOT / '.analysis-cache/review-layout'
OUT.mkdir(parents=True, exist_ok=True)
doc = fitz.open(SOURCE)
summary = {'source': str(SOURCE.relative_to(ROOT)), 'sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(), 'page_count': len(doc), 'pages': [], 'bad_links': [], 'overlaps': [], 'small_text': [], 'image_resolution': []}
images = []
for i, page in enumerate(doc):
    spans = []
    for block in page.get_text('dict')['blocks']:
        if block['type'] != 0:
            continue
        for line in block['lines']:
            for span in line['spans']:
                if span['text'].strip():
                    spans.append(span)
    text = page.get_text()
    summary['pages'].append({'page': i+1, 'rect': list(page.rect), 'words': len(text.split()), 'minimum_font_size': min((s['size'] for s in spans), default=0), 'replacement_chars': text.count('\ufffd')})
    for link in page.get_links():
        if link.get('kind') == fitz.LINK_GOTO and not 0 <= link.get('page', -1) < len(doc):
            summary['bad_links'].append({'page': i+1, 'link': link})
    tiny = [s for s in spans if s['size'] < 7.5 and len(s['text'].strip()) > 10]
    if tiny:
        summary['small_text'].append({'page': i+1, 'examples': [{'text': s['text'], 'size': s['size']} for s in tiny[:4]]})
    for n, a in enumerate(spans):
        ar = fitz.Rect(a['bbox'])
        for b in spans[n+1:]:
            br = fitz.Rect(b['bbox'])
            inter = ar & br
            if inter.width > 5 and inter.height > min(ar.height,br.height)*0.65:
                summary['overlaps'].append({'page': i+1, 'a': a['text'], 'b': b['text'], 'bbox': list(inter)})
    for info in page.get_image_info():
        rect = fitz.Rect(info['bbox'])
        dpi = min(info['width']/rect.width*72, info['height']/rect.height*72) if rect.width and rect.height else 0
        if rect.width > 150 and rect.height > 150 and dpi < 130:
            summary['image_resolution'].append({'page': i+1, 'pixels': [info['width'],info['height']], 'dpi': round(dpi,1), 'bbox': list(rect)})
    pix = page.get_pixmap(matrix=fitz.Matrix(0.6,0.6), alpha=False)
    images.append(Image.frombytes('RGB', [pix.width,pix.height],pix.samples))
    if len(images) == 12 or i == len(doc)-1:
        start = i+2-len(images)
        sheet = Image.new('RGB',(3*385,4*510),'#dadada')
        draw=ImageDraw.Draw(sheet)
        for j, im in enumerate(images):
            x=(j%3)*385+8;y=(j//3)*510+25
            sheet.paste(im,(x,y))
            draw.text((x,y-19),f'PDF page {start+j}',fill='black')
        sheet.save(OUT / f'contact-{start:03d}-{i+1:03d}.jpg',quality=92)
        images=[]
(OUT/'layout-audit.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
(ROOT/'analysis/review-2026-10-02/reading-layout-verification.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:len(summary[k]) for k in ['pages','bad_links','overlaps','small_text','image_resolution']}))
