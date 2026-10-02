"""Render every final page with Poppler and macOS CoreGraphics, and check CID maps."""
from pathlib import Path
import concurrent.futures, hashlib, json, re, struct, subprocess
import pymupdf as fitz
import Quartz as Q
from Foundation import NSURL

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/pdf';CACHE=ROOT/'.analysis-cache/independent-renderers';CACHE.mkdir(parents=True,exist_ok=True)
result={}
for kind in ['Reading','Print']:
    path=OUT/f'The-Warszawskis-Revised-2026-10-02-{kind}.pdf';d=fitz.open(path)
    target=CACHE/kind.lower();target.mkdir(exist_ok=True)
    for stale in target.glob('poppler-*.png'):stale.unlink()
    pp=subprocess.run(['pdftoppm','-r','72','-png',str(path),str(target/'poppler')],capture_output=True,text=True,check=True)
    assert not pp.stderr.strip(),pp.stderr
    pdf=Q.CGPDFDocumentCreateWithURL(NSURL.fileURLWithPath_(str(path)));assert pdf
    assert Q.CGPDFDocumentGetNumberOfPages(pdf)==len(d)
    apple=[]
    for n in range(1,len(d)+1):
        page=Q.CGPDFDocumentGetPage(pdf,n);r=Q.CGPDFPageGetBoxRect(page,Q.kCGPDFMediaBox);w,h=int(r.size.width),int(r.size.height)
        ctx=Q.CGBitmapContextCreate(None,w,h,8,w*4,Q.CGColorSpaceCreateDeviceRGB(),Q.kCGImageAlphaPremultipliedLast)
        assert ctx
        Q.CGContextSetRGBFillColor(ctx,1,1,1,1);Q.CGContextFillRect(ctx,Q.CGRectMake(0,0,w,h))
        transform=Q.CGPDFPageGetDrawingTransform(page,Q.kCGPDFMediaBox,Q.CGRectMake(0,0,w,h),0,True)
        Q.CGContextConcatCTM(ctx,transform);Q.CGContextDrawPDFPage(ctx,page)
        im=Q.CGBitmapContextCreateImage(ctx);p=target/f'apple-{n:03}.png'
        dest=Q.CGImageDestinationCreateWithURL(NSURL.fileURLWithPath_(str(p)),'public.png',1,None)
        Q.CGImageDestinationAddImage(dest,im,None);assert Q.CGImageDestinationFinalize(dest)
        apple.append({'page':n,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    maps=[]
    def ref(x,k):
        typ,val=d.xref_get_key(x,k);return int(val.split()[0]) if typ=='xref' else None
    for x in range(1,d.xref_length()):
        if '/CIDFontType2' not in d.xref_object(x):continue
        fd=ref(x,'FontDescriptor');ff=ref(fd,'FontFile2') if fd else None
        if not ff:continue
        font=d.xref_stream(ff);tables=struct.unpack('>H',font[4:6])[0];glyphs=None
        for j in range(tables):
            tag,checksum,offset,length=struct.unpack('>4sIII',font[12+j*16:28+j*16])
            if tag==b'maxp':glyphs=struct.unpack('>H',font[offset+4:offset+6])[0]
        cmap=ref(x,'CIDToGIDMap')
        if cmap:
            b=d.xref_stream(cmap);gids=struct.unpack('>'+str(len(b)//2)+'H',b)
            bad=[v for v in gids if v>=glyphs]
            assert not bad,(kind,x,glyphs,max(gids))
            maps.append({'font_xref':x,'glyph_count':glyphs,'mapped_cids':len(gids),'invalid_glyph_indices':len(bad)})
    result[kind]={'pages':len(d),'poppler_pngs':len(list(target.glob('poppler-*.png'))),'poppler_stderr':pp.stderr,'apple_pngs':len(apple),'apple_page_checksums':apple,'CID_maps':maps}
    assert result[kind]['poppler_pngs']==len(d)
    print(kind,len(d),'pages rendered by Poppler and Apple CoreGraphics; CID maps valid',flush=True)
(ROOT/'analysis/rebuild-2026-10-02/independent-renderers.json').write_text(json.dumps(result,indent=2)+'\n')
