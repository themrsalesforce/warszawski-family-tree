"""Create a small chat copy while retaining text, page count and links."""
from pathlib import Path
from io import BytesIO
import hashlib,json
import pymupdf as fitz
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/pdf'
src=OUT/'The-Warszawskis-Revised-2026-10-02-Reading.pdf';dst=OUT/'The-Warszawskis-Revised-2026-10-02-Compact.pdf'
d=fitz.open(src);seen=set();changes=[]
for p in d:
    for img in p.get_images(full=True):
        x=img[0]
        if x in seen:continue
        seen.add(x)
        try:
            im=Image.open(BytesIO(d.extract_image(x)['image']));old=im.size
            if im.width<300 and im.height<300:continue
            im.thumbnail((1150,1150),Image.Resampling.LANCZOS)
            if im.mode not in ['RGB','L']:im=im.convert('RGB')
            b=BytesIO();im.save(b,format='JPEG',quality=68,optimize=True)
            p.replace_image(x,stream=b.getvalue());changes.append({'xref':x,'old_pixels':old,'new_pixels':im.size})
        except Exception as e:raise RuntimeError((x,str(e)))
d.save(dst,garbage=4,deflate=True);d.close();a=fitz.open(src);b=fitz.open(dst)
assert len(a)==len(b)
assert all(p.get_text()==b[i].get_text() for i,p in enumerate(a))
assert a.get_toc()==b.get_toc()
assert [len(p.get_links()) for p in a]==[len(p.get_links()) for p in b]
assert dst.stat().st_size<9_000_000,dst.stat().st_size
(ROOT/'analysis/rebuild-2026-10-02/compact-verification.json').write_text(json.dumps({'pages':len(b),'bytes':dst.stat().st_size,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'text_identical':True,'outline_identical':True,'link_counts_identical':True,'image_changes':changes,'purpose':'Compressed screen reading; full-resolution print retained separately'},indent=2)+'\n')
print(len(b),'pages',dst.stat().st_size,'bytes; text and navigation preserved')
