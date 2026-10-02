from pathlib import Path
import json,re,hashlib,datetime
import fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import EmbeddedType1Face,Font
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.colors import HexColor

R=Path(__file__).parent; D=R/'draft'; D.mkdir(exist_ok=True)
B=R/'baseline'
RN='The-Warszawskis-Coffee-Table-Edition-2026-10-01-Reading-Copy.pdf'
PN='The-Warszawskis-Coffee-Table-Edition-2026-10-01-Print-Interior.pdf'
CREAM=(252/255,250/255,245/255);INK='#282A26';MUTED='#717466';RUST='#845B44'
for n,s in [('Charter','bchr8a'),('CharterItalic','bchri8a'),('CharterBold','bchb8a')]:
 p=R/'fonts';f=EmbeddedType1Face(str(p/(s+'.afm')),str(p/(s+'.pfb')))
 pdfmetrics.registerTypeFace(f);pdfmetrics.registerFont(Font(n,f.name,'WinAnsiEncoding'))
for n,f in [('OpenSans','OpenSans-Regular.ttf'),('OpenSansLight','OpenSans-Light.ttf')]:pdfmetrics.registerFont(TTFont(n,str(R/'fonts'/f)))
pdfmetrics.registerFontFamily('Charter',normal='Charter',bold='CharterBold',italic='CharterItalic',boldItalic='CharterItalic')
original=fitz.open(B/RN); supp=fitz.open(D/'research-supplement.pdf');N=len(supp)
assert N%2==0
patches=[]; c=canvas.Canvas(str(D/'main-text-patches.pdf'),pagesize=(612,792),pageCompression=1,initialFontName='Charter')
def txt(t,x,y,size=12.1,font='Charter',color=INK):
 c.setFillColor(HexColor(color));c.setFont(font,size);c.drawString(x,792-y,t)
def para(t,x,y,w=486,size=12.1,leading=18,font='Charter',color=INK):
 p=Paragraph(t,ParagraphStyle('p',fontName=font,fontSize=size,leading=leading,textColor=HexColor(color)))
 ww,hh=p.wrap(w,1000);p.drawOn(c,x,792-y-hh)
 if y+hh>727:raise ValueError((patches[-1],y+hh,t))
 return y+hh
def new_patch(pageno,rect):
 if patches:c.showPage()
 patches.append({'page':pageno,'rect':rect})

# Keep the current edition date, research cut-off and catalogue scope consistent.
new_patch(4,[50,120,310,137])
txt('Private family edition • 2 October 2026',54,131.58,12.1,'CharterItalic',RUST)
new_patch(4,[50,509,545,525])
txt('adds the substantive records gathered through 2 October 2026. Earlier editions and',54,519.58,12.1)
new_patch(180,[50,126,320,143])
txt('The original 131-source catalogue',54,137.38,12.1,'CharterItalic',RUST)

# Contents: retain the known chapter sequence and insert one new chapter.
new_patch(3,[65,80,565,724]);txt('Contents',72,159,36)
contents=[(x[1],x[2]) for x in original.get_toc() if x[0]==1]
contents=[(t,p+N if p>=205 else p) for t,p in contents]
contents.insert(-1,('New records and research',205))
for j,(t,p) in enumerate(contents):
 y=192+j*34;txt(t,72,y,14);c.setFillColor(HexColor(MUTED));c.setFont('OpenSansLight',10);c.drawRightString(558,792-y,str(p))

new_patch(27,[65,80,565,725])
paragraphs=[
'''He grew up in Cleveland, became a bookkeeper, and on September 12, 1916 married Pearl Adelstein in Cuyahoga County. Three years later, on September 18, 1919, he stood in the U.S. District Court for the Northern District of Ohio and swore his Declaration of Intention - the first formal step toward citizenship. The clerk recorded Paris, May 30, 1895; occupation bookkeeper; last foreign residence “Pairs, France,” the clerk’s misspelling; and departure from Havre. He was twenty-four, three years married, a father of four-month-old Rochelle.''',
'''The full 1924 packet now completes that paper trail. Filed as Victor Gershanovitz, petition 19277 records a formal change to Victor Garson when the court admitted him on November 20, 1924. Certificate 2116415 was issued on November 26. Pearl’s later petition gives the same naturalization date and certificate number. The recovered pages appear in the new-records section beginning on page 205.''',
'''Ohio’s government-derived death index records his death at East Cleveland on August 13, 1978, five years after Pearl. The original death certificate has not been inspected. His newspaper notice announces the Monday, August 14 funeral at the Berkowitz-Kumin Memorial Chapel; the cemetery register gives that same date for interment at Zion Memorial Park. The family sat shiva at the Sanford Simons’. The notice’s feminine forms “grandmother” and “great grandmother” are preserved as printed.''',
'''An early transcription of the declaration gave his last foreign residence as Metz, in Alsace-Lorraine, and for a while the search ran to Metz. A magnified reading of the original settled it: the word is “Pairs,” Paris. The new surname evidence opens a better search, while the proposed Paris birth act and passenger identification remain unproved.''']
y=85
for t in paragraphs:y=para(t,72,y)+15

new_patch(110,[49,425,548,725])
txt('Core family · Birth: 1895-05-30 · Paris, France; Death: 1978-08-13 · East Cleveland, Ohio',54,439.7,8.6,'OpenSansLight',MUTED)
y=451
for t in ['<b>Parents:</b> Solomon and Rachael; surnames not established','<b>Partner or spouse:</b> Pearl (Adelstein) Garson','<b>Children:</b> Rosamond (Garson) Simon; Ileen (Ilene, Gabby) Hersh; Rochelle (Garson) Horwich']:
 y=para(t,54,y,size=10.2,leading=14.5)+4.7
t='His 1919 declaration and 1924 petition record Paris birth on 30 May 1895. Petition 19277 was filed as Victor Gershanovitz; the court admitted him and changed his name to Victor Garson on 20 November 1924, with certificate 2116415 issued 26 November. His marriage names Solomon and Rachael; her maiden surname remains unknown. The 1920 census places Harry and Louis Allen in his household as brothers-in-law. Ohio’s death index records 13 August 1978 at East Cleveland; the cemetery gives interment on 14 August. See the new records on pages 207-220. [S101, S102, S066, S070, S067, S062, S063, S064; W01-W07, W23]'
y=para(t,54,y,size=10.3,leading=14.5)+17
txt('Sources: existing register citations above; new records W01-W07 and W23',54,y,8.4,'OpenSansLight',MUTED)

new_patch(111,[65,79,565,725])
def register(title,tag,lines,body,refs,y):
 txt(title,72,y,18);txt(tag,72,y+29.9,9,'OpenSansLight',MUTED);y+=41
 for t in lines:y=para(t,72,y,size=10.2,leading=14.5)+4.7
 y=para(body,72,y,size=10.3,leading=14.5)+17
 txt(refs,72,y,8.4,'OpenSansLight',MUTED)
 return y+47.6
y=register('Pearl (Adelstein) Garson','Core family · Birth: 1897-12-01 · Cleveland, Ohio; Death: 1973-03 · Cleveland, Ohio',[
 '<b>Parents:</b> Sam Adelstein; Rebecca (Escowitch) Adelstein',
 '<b>Partner or spouse:</b> Victor Garson',
 '<b>Children:</b> Rosamond (Garson) Simon; Ileen (Ilene, Gabby) Hersh; Rochelle (Garson) Horwich'],
 'Her 1916 marriage and delayed birth certificate name Sam and Rebecca. The certificate, filed 25 January 1940, confirms Cleveland birth on 1 December 1897; its supporting affidavit explicitly identifies Rose Alliance as her sister. Her sworn citizenship petition gives the births of Rochelle, Rosamond and Ileen. The original 1973 notice announces a 4 March funeral without stating her death day. Rose’s 1906 marriage reads Rebecca Escowitch; together with the sister affidavit, this is strong combined maiden-name evidence. Other fields use Adelstein; Escovitch is an alternate transcription. Earlier family origins remain unresolved. [S102, S066, S030, S070, S062, S063, S064; W01, W04-W06, W26, W28]',
 'Sources: existing register citations above; W01, W04-W06, W26, W28',102)
y=register('Solomon (Victor’s father)','Core family · Surname not established',[
 '<b>Other named parent:</b> Rachael (Victor’s mother)','<b>Children:</b> Victor Garson'],
 'Named as Victor’s father in the original 1916 marriage record. Neither Garson nor Gershanovitz is independently established as his surname. The conflicting Paris candidate does not identify him. [S063; W01, W08]',
 'Sources: S063; W01, W08',y)
y=register('Rachael (Victor’s mother)','Core family · Surname not established',[
 '<b>Other named parent:</b> Solomon (Victor’s father)','<b>Children:</b> Victor Garson'],
 'The original marriage gives Rachael followed by “l-n-u,” apparently last name unknown. Her own surname and earlier life remain unproved. [S063; W01]',
 'Sources: S063; W01',y)

new_patch(112,[49,121,548,140])
txt('Core family · Birth: 1926-01-06 · Cleveland, Ohio; Death: 1983-01 (index)',54,131.88,9,'OpenSansLight',MUTED)
new_patch(112,[49,180,548,266])
y=para('Pearl’s petition records Cleveland birth on 6 January 1926. Her Social Security index gives death in January 1983 and parents Victor Garson and Pearl Adelstein. Rochelle’s notice names her as the late Rosamond Simon, wife of Sanford. The original notice behind CPL’s 25 January 1983 finding is still uncollected. [S070, S064, S110, S131; W21]',54,181,size=10.3,leading=14.5)
txt('Sources: S070, S064, S110, S131; W21',54,y+16,8.4,'OpenSansLight',MUTED)

# Remove the inherited projection of Victor's American surname onto his parents.
new_patch(26,[49,587,547,715])
para('Victor reported birth in Paris on May 30, 1895. His 1916 marriage names his parents as Solomon and Rachael, without establishing either parent’s surname. According to his naturalization record, he entered the United States at New York in 1902, a boy of seven. His travelling companions have not been proved by a passenger manifest.',54,590)
new_patch(58,[70,302,168,322])
txt('Solomon',72,316,13);txt('Victor’s father',72,330,8.5,'OpenSansLight',MUTED);txt('Surname not established',72,342,8.1,'OpenSansLight',MUTED)
new_patch(58,[70,366,164,386])
txt('Rachael',72,380,13);txt('Victor’s mother',72,394,8.5,'OpenSansLight',MUTED);txt('Surname not established',72,406,8.1,'OpenSansLight',MUTED)
new_patch(58,[70,681,558,729])
para('Pearl’s parents are named as Sam and Rebecca; the strongest combined maiden-name reading is Escowitch. Her siblings are followed through the new records on pages 211-217. The separate French Garson trees remain unlinked to Victor.',72,684,size=9.8,leading=13.5,font='OpenSansLight',color=MUTED)
new_patch(63,[68,159,562,251])
para('Victor’s marriage names his parents as Solomon and Rachael. Their surnames are not established; his American name Garson is not projected backward onto them. His own 1924 packet names Gershanovitz but does not name his parents. The French households that follow remain separate research families, with no proved bridge to Victor.',72,162)
new_patch(64,[49,129,546,326])
y=para('A record naming a Solomon as a son of Aron and Caroline would be a lead to test, not a completed link to Victor. Neither Garson nor Gershanovitz is established as the surname used by Victor’s father. A “Guerchen, Abraham Gershon” who died at Hellimer in 1855 remains another unlinked historical person.',54,133)
para('A verified passenger identification for Victor’s reported 1902 arrival remains important. Neither the fact that he was seven nor the later petition establishes which relatives travelled with him. The candidate comparisons and their conflicting details appear on pages 218-220.',54,y+15)
new_patch(66,[51,490,538,508])
txt('Solomon, Victor’s father, is unproved. The children must not be called Victor’s',54,502.58,12.1)
new_patch(155,[68,319,558,378])
txt('Solomon and Rachael',72,337.76,18)
txt('Victor’s parents · Their surnames are not established',72,367.64,9,'OpenSansLight',MUTED)
new_patch(210,[51,260,290,276])
txt('Rachael (Victor’s mother)',54,271.1,11.1)
new_patch(211,[69,106,312,122])
txt('Solomon (Victor’s father)',72,117.1,11.1)

# Supersede the old blanket parent/surname negatives in the sibling register.
# Locate only Harry's source paragraph; other entries on that page are untouched.
for block in original[140].get_text('dict')['blocks']:
 if block['type']!=0:continue
 st=' '.join(sp['text'] for line in block['lines'] for sp in line['spans'])
 if st.startswith('Brother of Pearl named'):
  bb=block['bbox']; new_patch(141,[bb[0]-3,bb[1]-2,544,bb[3]+35])
  y=para('Brother of Pearl named in her 1973 notice. The 1920 census records Harry and Louis Allen in Victor’s household as his brothers-in-law. A separate parentage record for Harry has not been inspected. [S064; W06]',54,bb[1],size=10.3,leading=14.5)
  txt('Sources: S064; W06',54,y+15,8.4,'OpenSansLight',MUTED)
new_patch(142,[49,140,548,606])
# Retain the four established profiles, but distinguish each person's evidence.
records=[('Sydney Allen',102,'Brother of Pearl named in her 1973 notice. His individual parentage and surname-change records remain unverified. [S064]','Sources: S064'),('Edward Allen',234.38,'Brother of Pearl named in her 1973 notice. An original veterans’ card links Isidor Adelstein with Edward Allen; Edward B Allen’s 1952 marriage names Samuel and Rebecca Adelstein. See the source distinctions on page 215. [S064; W27-W28]','Sources: S064; W27-W28'),('Louis Allen',366.76,'Brother of Pearl named in her 1973 notice. The original 1920 census places him, aged eighteen, in Victor’s household as a brother-in-law. His individual birth record remains to be verified. [S064; W06]','Sources: S064; W06'),('Howard Allen',499.14,'Brother of Pearl named in her 1973 notice. His individual parentage and surname-change records remain unverified. [S064]','Sources: S064')]
# Sydney's existing title and tag remain above the redaction; redraw later profiles.
for title,yy,body,ref in records:
 if title!='Sydney Allen':txt(title,54,yy,18);txt('Core family',54,yy+29.88,9,'OpenSansLight',MUTED)
 y=para(body,54,yy+42.73,size=10.3,leading=14.5)
 txt(ref,54,y+15,8.4,'OpenSansLight',MUTED)
new_patch(143,[68,84,558,201])
txt('Rose (Adelstein) Alliance Karr',72,102,18);txt('Core family',72,131.88,9,'OpenSansLight',MUTED)
y=para('Rose Adelstein married Sam Alliance in 1906. The 1940 affidavit names Rose Alliance as Pearl’s sister. CPL’s 1970 transcription calls Rose Karr formerly Rose Alliance; Pearl’s 1973 notice calls her deceased. [S064; W05, W26, W29]',72,144,size=10.3,leading=14.5)
txt('Sources: S064; W05, W26, W29',72,y+11,8.4,'OpenSansLight',MUTED)

# Restore the original breathing room after Rose's expanded profile.
new_patch(143,[68,201,562,704])
fontmap={'CharterBT-Roman':'Charter','CharterBT-Bold':'CharterBold','CharterBT-Italic':'CharterItalic','OpenSans-Light':'OpenSansLight','OpenSans':'OpenSans'}
for block in original[142].get_text('dict')['blocks']:
 if block['type']!=0:continue
 for line in block['lines']:
  for sp in line['spans']:
   if 200<sp['origin'][1]<720:
    color='#'+format(sp['color'],'06x')
    txt(sp['text'],sp['origin'][0],sp['origin'][1]+25,sp['size'],fontmap[sp['font']],color)
# Keep the Garson diagram consistent with Rosamond's newly inspected death index.
for block in original[57].get_text('dict')['blocks']:
 if block['type']!=0:continue
 for line in block['lines']:
  for sp in line['spans']:
   if sp['text']=='born 1926':
    bb=sp['bbox'];new_patch(58,[bb[0]-2,bb[1]-2,bb[2]+3,bb[3]+2])
    txt('1926–1983',sp['origin'][0],sp['origin'][1],sp['size'],'OpenSansLight',MUTED)

new_patch(2,[50,123,560,146])
txt('Private family edition · Updated 2 October 2026',54,136.2,12.1,'CharterItalic',RUST)
new_patch(95,[65,604,565,678])
para('Newly recovered Garson and Adelstein records, candidate comparisons and the next precise research questions appear on pages 205-228.',72,616,size=11.5,leading=15.5,font='CharterItalic',color=RUST)
new_patch(212,[50,684,555,705])
txt('Private family edition · Updated 2 October 2026',54,696,9,'OpenSansLight',MUTED)
c.save(); patches_doc=fitz.open(D/'main-text-patches.pdf')
book=fitz.open(B/RN)
for j,item in enumerate(patches):
 p=book[item['page']-1];p.add_redact_annot(fitz.Rect(item['rect']),fill=CREAM);p.apply_redactions(images=0,graphics=0)
 p.show_pdf_page(p.rect,patches_doc,j)

# Add the new-records supplement immediately before the original name index.
book.insert_pdf(supp,start_at=204,links=True,annots=True)

# Renumber existing final pages, preserving every index entry and its register references.
for oldnum in range(205,213):
 idx=oldnum-1+N;p=book[idx]
 spans=[s for b in p.get_text('dict')['blocks'] if b['type']==0 for l in b['lines'] for s in l['spans'] if s['text']==str(oldnum) and s['origin'][1]>740]
 assert len(spans)==1,(oldnum,spans)
 s=spans[0];right=s['bbox'][2];y=s['origin'][1]
 p.add_redact_annot(fitz.Rect(s['bbox'])+(-2,-2,2,2),fill=CREAM);p.apply_redactions(images=0,graphics=0)
 p.insert_font(fontname='RevisionSans',fontfile=str(R/'fonts'/'OpenSans-Light.ttf'))
 text=str(oldnum+N);f=fitz.Font(fontfile=str(R/'fonts'/'OpenSans-Light.ttf'))
 p.insert_text((right-f.text_length(text,fontsize=9),y),text,fontname='RevisionSans',fontsize=9,color=(113/255,116/255,102/255))

# Rebuild TOC navigation and preserve the original outline entries.
toc=[[1,t,p] for t,p in contents]
outline=json.loads((D/'supplement-outline.json').read_text())
at=next(i for i,x in enumerate(toc) if x[1]=='New records and research')
toc[at+1:at+1]=[[2,x['title'],x['page']] for x in outline[1:]]
book.set_toc(toc)
p=book[2]
for l in p.get_links():p.delete_link(l)
for j,(t,n) in enumerate(contents):p.insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(72,174+j*34,558,197+j*34),'page':n-1,'to':fitz.Point(0,0)})
# Make new-evidence index entries navigable to their first referenced page.
p=book[204+N-1]
for b in p.get_text('dict')['blocks']:
 if b['type']!=0:continue
 for l in b['lines']:
  for s in l['spans']:
   if re.fullmatch(r'\d{3}(?:\s*[-,]\s*\d{3})*',s['text']) and 160<s['origin'][1]<670:
    n=int(s['text'][:3]);p.insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(54,s['bbox'][1]-2,540,s['bbox'][3]+2),'page':n-1,'to':fitz.Point(0,0)})
meta=book.metadata.copy();meta['modDate']=datetime.datetime.now(datetime.timezone.utc).strftime('D:%Y%m%d%H%M%SZ');book.set_metadata(meta)
readout=D/RN;book.save(readout,garbage=4,deflate=True)
book.close();book=fitz.open(readout)

# Full-resolution print: keep untouched original print pages; replace changed trim
# pages with the valid embedded-font reading page, and add supplement at bleed size.
pr=fitz.open(B/PN)
changed=[1,2,3,25,26,57,62,63,65,94,109,110,111,140,141,142,154,179] # zero-based original pages changed before insertion
def place_trim(p,readidx):
 bg=(40/255,62/255,64/255) if readidx==204 else CREAM
 p.add_redact_annot(p.rect,fill=bg);p.apply_redactions(images=1,graphics=2)
 p.show_pdf_page(fitz.Rect(9,9,621,801),book,readidx,keep_proportion=False)
 # Copy hyperlinks from corresponding trim page with the bleed translation.
 for l in p.get_links():p.delete_link(l)
 for l in book[readidx].get_links():
  v={k:val for k,val in l.items() if k not in ['xref','id']};v['from']=l['from']+(9,9,9,9)
  if 'to' in v and v.get('kind')==fitz.LINK_GOTO:v['to']=v['to']+fitz.Point(9,9)
  # Deferred until the final page count exists.
  pending_links.append((p.number,v))
pending_links=[]
for i in changed:place_trim(pr[i],i)
for j in range(N):
 p=pr.new_page(pno=204+j,width=630,height=810);p.set_trimbox(fitz.Rect(9,9,621,801));p.set_bleedbox(p.rect)
 place_trim(p,204+j)
for oldnum in range(205,213):place_trim(pr[oldnum-1+N],oldnum-1+N)
for pidx,l in pending_links:pr[pidx].insert_link(l)
pr.set_toc(toc);pr.set_metadata(meta)
printout=D/PN;pr.save(printout,garbage=4,deflate=True)
pr.close()

newchanged=sorted(set([x+1 for x in changed]+list(range(205,213+N))+[2]))
for n in newchanged:
 book[n-1].get_pixmap(matrix=fitz.Matrix(1.35,1.35)).save(D/f'reading-{n:03}.png')
(D/'updated-manuscript.txt').write_text('\n\n'.join(f'PAGE {i+1}\n'+p.get_text() for i,p in enumerate(book)))
manifest=[]
for p in [readout,printout]:manifest.append({'path':str(p),'bytes':p.stat().st_size,'pages':len(fitz.open(p)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(D/'outputs.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
