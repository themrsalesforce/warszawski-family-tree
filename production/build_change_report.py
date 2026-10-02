"""Render the concise tracked change/closure report using embedded book fonts."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import EmbeddedType1Face,Font
ROOT=Path(__file__).resolve().parents[1]
assets=ROOT/'assets/fonts'
if not assets.exists():assets=ROOT/'.import-tmp/production-recovery/current/Rebuild/fonts'
for n,s in [('Charter','bchr8a'),('CharterBold','bchb8a')]:
 f=EmbeddedType1Face(str(assets/(s+'.afm')),str(assets/(s+'.pfb')));pdfmetrics.registerTypeFace(f);pdfmetrics.registerFont(Font(n,f.name,'WinAnsiEncoding'))
pdfmetrics.registerFontFamily('Charter',normal='Charter',bold='CharterBold',italic='Charter',boldItalic='CharterBold')
def reportcanvas(*args,**kw):
 kw.update(initialFontName='Charter',invariant=1)
 return canvas.Canvas(*args,**kw)
flow=[]
for block in (ROOT/'analysis/rebuild-2026-10-02/CHANGES-AND-CLOSURE.md').read_text().split('\n\n'):
 size=22 if block.startswith('# ') else 15 if block.startswith('## ') else 10.5
 text=block.replace('## ','').replace('# ','').replace('**','').replace('\n- ','<br/>• ').replace('\n',' ')
 flow.append(Paragraph(escape(text).replace('&lt;br/&gt;','<br/>'),ParagraphStyle('report',fontName='CharterBold' if size>11 else 'Charter',fontSize=size,leading=size+4,spaceAfter=9)))
SimpleDocTemplate(str(ROOT/'output/pdf/Warszawski-Changes-and-Closure-2026-10-02.pdf'),pagesize=(612,792),leftMargin=54,rightMargin=54,topMargin=54,bottomMargin=54,title='Warszawski revision changes and closure',author='Warszawski family editorial project').build(flow,canvasmaker=reportcanvas)
