"""Rebuild the current edition from preserved PDF artwork and editable data.

No historical source is overwritten. Run prepare_revision.py first. The package
README describes required ignored artwork/fonts and private artifact delivery.
"""
from pathlib import Path
from io import BytesIO
from xml.sax.saxutils import escape
import argparse, collections, hashlib, json, re
import pymupdf as fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import EmbeddedType1Face, Font
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'production/data'; OUT=ROOT/'output/pdf'; OUT.mkdir(parents=True,exist_ok=True)
QA=ROOT/'analysis/rebuild-2026-10-02'; QA.mkdir(parents=True,exist_ok=True)
ap=argparse.ArgumentParser()
ap.add_argument('--assets',type=Path,default=ROOT/'.import-tmp/production-recovery/current/Rebuild')
ap.add_argument('--reading',type=Path,default=ROOT/'Warszawski/05-Print-editions/The-Warszawskis-Coffee-Table-Edition-2026-10-01-Reading-Copy.pdf')
ap.add_argument('--print-pdf',type=Path,default=ROOT/'Warszawski/05-Print-editions/The-Warszawskis-Coffee-Table-Edition-2026-10-01-Print-Interior.pdf')
args=ap.parse_args()
fonts=args.assets/'fonts'
for n,s in [('Charter','bchr8a'),('CharterBold','bchb8a'),('CharterItalic','bchri8a')]:
    f=EmbeddedType1Face(str(fonts/(s+'.afm')),str(fonts/(s+'.pfb')))
    pdfmetrics.registerTypeFace(f);pdfmetrics.registerFont(Font(n,f.name,'WinAnsiEncoding'))
for n,f in [('OpenSans','OpenSans-Regular.ttf'),('OpenSansLight','OpenSans-Light.ttf')]:pdfmetrics.registerFont(TTFont(n,str(fonts/f)))
pdfmetrics.registerFontFamily('Charter',normal='Charter',bold='CharterBold',italic='CharterItalic',boldItalic='CharterItalic')
CREAM='#FCFAF5';INK='#282A26';MUTED='#717466';RUST='#845B44'
cream=(252/255,250/255,245/255)
source=fitz.open(args.reading)
register=json.loads((DATA/'register.json').read_text());households=json.loads((DATA/'households.json').read_text())
notes=json.loads((DATA/'story-notes.json').read_text());sources=json.loads((DATA/'source-crosswalk.json').read_text())
PAGE_MAP={}

def norm(s):
    return s.replace('\u2011','-').replace('\u2013','-').replace('\u2014',' - ').replace('\u2010','-')
def style(size=11.3,leading=15.0,font='Charter',color=INK):
    return ParagraphStyle('book',fontName=font,fontSize=size,leading=leading,textColor=HexColor(color))
def paragraph(text,w=486,size=11.3,leading=15.0,font='Charter',color=INK):
    p=Paragraph(text,style(size,leading,font,color));p.wrap(w,10000);return p
def plain(text):return escape(norm(text))
def cleanup(text):
    lines=[x.strip() for x in text.splitlines() if x.strip()]
    lines=[x for x in lines if not re.fullmatch(r'[A-Z](?:\s+[A-Z]){5,}',x) and x!='THE WARSZAWSKIS']
    return lines
def record_paragraphs(r,kind):
    lines=[line for line in cleanup(r['text']) if not line.startswith('Sources:')]
    if kind=='register':
        # Repeated trailing source lists add no evidence; consolidate all IDs once.
        text=' '.join(lines)
        if PAGE_MAP and r['id'] in ['P034','P148']:
            for old in [207,220,215]:text=re.sub(r'\b'+str(old)+r'\b',str(PAGE_MAP[old]),text)
        text=re.sub(r'Sources:.*?(?=(?:Contemporary engagement notice:|Original birth notice:|La Paz, Argentina)|$)','',text)
        text=re.sub(r'\[(?:[SW]\d{2,3}[\s,;\-]*)+\]','',text)
        labels=['Parents','Partner or spouse','Children','Co-parent named in index']
        pattern=r'(?=(?:Parents(?: \([^:]+\))?|Partner or spouse|Children(?: \([^:]+\))?|Co-parent named in index \([^:]+\)):)'
        chunks=re.split(pattern,text)
        # A compact paragraph carries qualified fields, original prose and one citation set.
        body=' '.join(x.strip() for x in chunks if x.strip())
        body=re.sub(r'((?:Parents|Partner or spouse|Children|Co-parent named in index)(?: \([^:]+\))?):',r' · <b>\1:</b>',plain(body))
        ps=[paragraph(body)]
        ids=', '.join(r['source_ids'])
        if ids:ps.append(paragraph('Evidence: '+ids,size=9.0,leading=12,font='OpenSansLight',color=MUTED))
        return ps
    if kind=='households':
        text=' '.join(lines)
        text=re.sub(r'Sources:.*$', '',text)
        text=text.replace('Children recorded: none supplied for this group.', 'No children supplied; absence of information does not establish childlessness.')
        ids=', '.join(r['source_ids'])
        return [paragraph(plain(text)),paragraph('Evidence: '+ids,size=9,leading=12,font='OpenSansLight',color=MUTED)]
    if kind=='notes':
        return [paragraph(plain(' '.join(lines)),size=10.5,leading=14.5)]
    text=' '.join(lines)
    text=re.sub(r'Open source record\s*[·:]?','',text)
    text=re.sub(r'https?://\S+','',text)
    ps=[paragraph(plain(text),size=10.5,leading=14.5)]
    if r['id']=='W01':ps.append(paragraph('Also catalogued as S063: one underlying marriage record.',size=9,leading=12,font='OpenSansLight',color=MUTED))
    # Exact links remain clickable even when old print labels were abbreviated.
    for url in r['urls']:
        ps.append(paragraph('<link href="'+escape(url,{'"':'&quot;'})+'" color="#845B44">Open exact source record</link>',size=9,leading=12,font='OpenSansLight'))
    return ps

class Section:
    def __init__(self,name,first,title,intro):
        self.path=OUT/(name+'.pdf');self.c=canvas.Canvas(str(self.path),pagesize=(612,792),pageCompression=1,initialFontName='Charter',invariant=1)
        self.first=first;self.n=first-1;self.title=title;self.positions={};self.pages=0
        self.newpage();self.drawtitle(title,29)
        if intro:self.drawpara(paragraph(plain(intro)));self.y+=17
    def newpage(self):
        if self.pages:self.c.showPage()
        self.pages+=1;self.n+=1;self.left=72 if self.n%2 else 54;self.y=85
        self.c.setFillColor(HexColor(CREAM));self.c.rect(0,0,612,792,fill=1,stroke=0)
        self.c.setFillColor(HexColor(MUTED));self.c.setFont('OpenSansLight',7.5);self.c.drawString(self.left,740,self.title.upper())
        self.c.drawString(self.left,39,'THE WARSZAWSKIS');self.c.setFont('OpenSansLight',9);self.c.drawRightString(self.left+486,39,str(self.n))
    def drawtitle(self,text,size):
        p=paragraph(plain(text),size=size,leading=size+4);self.drawpara(p);self.y+=12
    def drawpara(self,p):
        w,h=p.wrap(486,10000);p.drawOn(self.c,self.left,792-self.y-h);self.y+=h+4
    def record(self,r,kind):
        ps=record_paragraphs(r,kind)
        size=15.2 if kind=='register' else 13.5 if kind=='households' else 12.5
        head=paragraph(plain(r['name']),size=size,leading=size+3)
        height=sum(p.wrap(486,10000)[1]+4 for p in [head]+ps)+12
        if height>628:raise ValueError(('record exceeds full page',r['id'],height))
        if self.y+height>714:self.newpage()
        self.positions[r['id']]={'page':self.n,'y':self.y,'name':r['name']}
        self.drawpara(head);self.y+=3
        for p in ps:self.drawpara(p)
        self.y+=8 if kind=='register' else 5
    def finish(self):self.c.save();return self.pages

sections=[];positions={};nextpage=100
for name,title,intro,records,kind in [
    ('register','The family register','Every one of the 183 baseline entries is retained, including candidates and unresolved identities. Indexed or inferred relationship fields are qualified beside the names. The historical 61-node graph is a separate representation, reconciled by explicit identity mapping.',register,'register'),
    ('households','The recorded households','All 57 recorded groups are retained. Co-parent groups are not automatically documented marriages. No children supplied means no information was supplied, not childlessness. Household roster names remain attributed to their source.',households,'households'),
    ('story-notes','Notes to the stories','Story and image notes follow the preserved narrative pages. Full S/W locators appear once in the canonical source catalogue. Original pixels and watermarks are retained; permission and physical proof remain outstanding where stated.',notes,'notes'),
    ('sources','Source catalogue','The S and W series resolve here. S063 and W01 are two IDs for the same underlying marriage; they do not count as independent witnesses. An index, transcription, finding aid, public tree, or negative search retains its limited scope. Exact recovered links are clickable; unresolved locators are not invented.',[r for r in sources if r['id']!='S063'],'sources')]:
    section=Section(name,nextpage,title,intro)
    for r in records:section.record(r,kind)
    count=section.finish();sections.append({'name':name,'title':title,'first':nextpage,'pages':count,'path':section.path})
    positions.update(section.positions);nextpage+=count
positions['S063']=positions['W01']
appendixfirst=nextpage
mapold={n:n for n in range(1,100)}
for j,n in enumerate(range(205,224)):mapold[n]=appendixfirst+j
# Source catalogue/old indices are replaced; their references resolve to new sections.
for r in register:mapold.setdefault(r['baseline_page'],positions[r['id']]['page'])
for r in households:mapold.setdefault(r['baseline_page'],positions[r['id']]['page'])
for r in sources:
    if r['baseline_page'] is not None:mapold.setdefault(r['baseline_page'],positions[r['id']]['page'])
for r in notes:mapold.setdefault(r['baseline_page'],positions[r['id']]['page'])
PAGE_MAP=mapold
# A second reference pass uses final pagination; numbers retain the same layout
# footprint, and a section-count assertion catches any reflow.
for s,records,kind in [(sections[0],register,'register')]:
    section=Section(s['name'],s['first'],s['title'],'Every one of the 183 baseline entries is retained, including candidates and unresolved identities. Indexed or inferred relationship fields are qualified beside the names. The historical 61-node graph is a separate representation, reconciled by explicit identity mapping.')
    for r in records:section.record(r,kind)
    count=section.finish();assert count==s['pages'],('reference pass changed pagination',count,s['pages'])

# Patch only text areas on preserved narrative/record artwork. Reflow full paragraphs
# with the recovered embedded Charter face; never paint over a source image.
patchbuf=BytesIO();pc=canvas.Canvas(patchbuf,pagesize=(612,792),pageCompression=1,initialFontName='Charter',invariant=1);patches=[]
def patch(n,rect,text,size=12.1,leading=18,font='Charter'):
    if patches:pc.showPage()
    patches.append((n,fitz.Rect(rect)))
    p=paragraph(text,rect[2]-rect[0],size,leading,font)
    h=p.wrap(rect[2]-rect[0],10000)[1]
    if h>rect[3]-rect[1]:raise ValueError(('patch overflow',n,h,rect))
    p.drawOn(pc,rect[0],792-rect[1]-h)
def blockpatch(n,starts,transform,size=None):
    blocks=source[n-1].get_text('dict')['blocks']
    matches=[]
    for b in blocks:
        if b['type']!=0:continue
        s=[s for l in b['lines'] for s in l['spans']]
        text=' '.join(s1['text'] for s1 in s)
        if text.startswith(starts):matches.append((b,s,text))
    if len(matches)!=1:raise ValueError(('patch not unique',n,starts,len(matches)))
    b,s,text=matches[0];box=b['bbox'];patch(n,[box[0],box[1]-1,box[2]+2,box[3]+12],plain(transform(text)),size or s[0]['size'],18 if (size or s[0]['size'])>=12 else 14.2)

blockpatch(16,'Larry Hersh’s 1984',lambda t:'His 1961 naturalization card records his birth date as 1 June 1925 [S039]. His 1984 account places his birth in Khust; civil birth verification remains separate. In the family he was Aryeh Leib, Zeidy Larry. The card preserves Arie-Larry-Hersh Kovitz and his chosen American signature, Arie Lawrence Hersh.')
blockpatch(16,'He and his sister Judith',lambda t:'He and his sister Judith survived the Holocaust. His testimony reports four sisters, five children in all. Family accounts preserve a differing total with inconsistent children/siblings wording that needs checking. Judith’s 2025 obituary remembers her parents and siblings who perished, without naming them all.')
patch(17,[72,85,558,141],plain('The Jewish Veterans Network tribute identifies the young man as Larry Hersh. His 1961 card records his birth date as 1 June 1925; the tribute’s exact death day is a compiled claim. Its wartime chronology needs comparison with his own account. The photograph retains its attributed private-review provenance.'),size=9.8,leading=14)
blockpatch(24,'Naturalized 11 August',lambda t:t+' The original card’s birth field reads 6/1/25: 1 June 1925 [S039].',size=10.4)
blockpatch(40,'He grew up on the east side.',lambda t:t.replace('stepping up to the Torah the week he turned thirteen.','with the ceremony announced for 14 October, five days before his Gregorian thirteenth birthday [S035].'))
blockpatch(44,'Ilana, the eldest',lambda t:'Ilana and Shmaya Marinovsky’s wedding date, 28 February 2012, is family-reported [S030, S001]; no original announcement is identified. Their Houston household is associated with Chabad and Torah Day School. The family names their children Molly, Rocky, Isaac and Bella.')
# Established delayed-birth and sister evidence enters the main story, not only its appendix.
patch(30,[54,164,540,727],'<br/><br/>'.join([
    'Pearl Adelstein’s own 1940 petition reports Cleveland birth on 1 December 1897. Her delayed birth certificate, filed 25 January 1940, names Sam and Rebecca Adelstein. The day is the claimed birth date; 1940 is the registration year [S070; W04].',
    'Rose Alliance’s supporting affidavit, dated 24 January 1940, explicitly calls her Pearl’s sister. Rose’s 1906 marriage names Rebecca Escowitch as her mother. Together these documents support the sibling link and the maternal surname reading; Escovitch remains an alternate transcription [W05, W26].',
    'Pearl married Victor on 12 September 1916. Her later citizenship petition belongs in the changing legal context for American women marrying foreign nationals. The petition records her own account; historical citizenship law is context rather than a separate determination of her status [W01, W04, S070].',
    'The petition records Cleveland births for Rochelle (9 May 1919), Rosamond (6 January 1926) and Ileen (30 July 1933). Ileen is Gabby. These are the petition’s reported dates, not three newly inspected civil birth certificates [S070].',
    'Pearl’s original notice announces a 4 March 1973 funeral and names her daughters and siblings. The compiled 3 March death day is kept distinct from the service date. The later source section follows the Allen siblings individually: Edward’s veterans’ card links Isidor Adelstein and Edward Allen; the affidavit notary Harry Allen is not identified as her brother merely by his name [S064; W27-W29].'
]),size=12.1,leading=18)
patch(57,[72,366,195,410],'<b>Jacob</b><br/>Judith’s 1949 abstract<br/>sibling evidence [S132/S103]',size=9.4,leading=11.5)
patch(57,[72,439,194,483],'<b>Leah / Lee Yanowitz</b><br/>Judith’s 1949 abstract<br/>sibling evidence [S132/S103]',size=9.0,leading=11.5)
patch(57,[72,657,558,733],plain('Judith’s 1949 marriage abstract names her father Jacob and mother’s maiden name Lee Yanowitz. Her 2025 obituary names Lawrence Hersh as her brother; this combined evidence supports Larry’s parental names. Judith was 21 in 1949; the differing oral-history age remains attributed. The uncle, lost sisters and separate Janowitz families remain unidentified/unlinked [S132, S103, S089].'),size=10.2,leading=14)
# Visible flags immediately beside indexed/inferred edges on the relevant diagrams.
patch(55,[420,516,558,533],'Inferred allocation',size=8.6,leading=11,font='OpenSansLight')
patch(55,[420,650,558,667],'Inferred allocation',size=8.6,leading=11,font='OpenSansLight')
patch(56,[274,271,410,288],'Indexed parents: provisional',size=8.1,leading=10.5,font='OpenSansLight')
patch(56,[274,505,410,522],'Indexed parents: provisional',size=8.1,leading=10.5,font='OpenSansLight')
patch(95,[72,164,558,705],'<br/><br/>'.join([
    '<b>Warszawski:</b> resolve Szyman’s indexed Joseph/Rochel parentage against the Zisl patronymic with original SS-5, birth or marriage records. Joe’s precise Polish birthplace remains unknown.',
    '<b>Zelkind:</b> Elka’s indexed Isac Kaga/Tsilya Gershon parentage, 1913 date and 1914 stone year remain in conflict. The separate Kogen families remain unlinked.',
    '<b>Hersh:</b> Judith’s 1949 original gives father Jacob and mother Lee Yanowitz; her obituary links her to Larry. The Cleveland uncle and lost sisters still need identifying records. The 1984 recording has an online route; crucial spoken names still need timestamped listening. Its four sisters/five children differs from inconsistent family children/siblings wording.',
    '<b>Garson:</b> the candidate Paris act 2087 is now examined, but its Israel/Rosa parents conflict with Victor’s American Solomon/Rachael account. Resolve his original-surname chain before another Garson sweep. Aline’s actual 1920 marriage is act 3605; the earlier 5559 locator is superseded.',
    '<b>Cleveland:</b> obtain the precise Rosamond and Rose Karr newspaper originals, and certificates where exact death days remain inferred from services/interment. Household and wedding confirmations remain source-specific.',
    '<b>Production:</b> current source package is recovered; better originals and reproduction permissions remain outstanding for some images. A rendered digital proof is separate from a physical printer proof.'
]),size=11.5,leading=16)

# Repoint explicit current-book page references in preserved text to the new layout.
def remap_phrase(t):
    def replace(m):
        nums=[int(x) for x in re.findall(r'\d+',m.group())]
        result=m.group()
        for old in sorted(set(nums),reverse=True):
            if old in mapold:result=re.sub(r'\b'+str(old)+r'\b',str(mapold[old]),result)
        return result
    return re.sub(r'\bpages?\s+\d{2,3}(?:\s*[-–,]\s*\d{2,3})*',replace,t)
retained=list(range(1,100))+list(range(205,224))
already={n for n,rect in patches}
for n in [27,58,64]:
    if n in already:continue
    for b in source[n-1].get_text('dict')['blocks']:
        if b['type']!=0:continue
        s=[s for l in b['lines'] for s in l['spans']];t=' '.join(x['text'] for x in s)
        revised=remap_phrase(t)
        if revised!=t:
            box=b['bbox'];patch(n,[box[0],box[1]-1,box[2]+2,box[3]+8],plain(revised),s[0]['size'],18 if s[0]['size']>=12 else 14)
pc.save();patchdoc=fitz.open(stream=patchbuf.getvalue(),filetype='pdf')
for i,(n,rect) in enumerate(patches):
    p=source[n-1];p.add_redact_annot(rect,fill=cream);p.apply_redactions(images=0,graphics=0);p.show_pdf_page(p.rect,patchdoc,i)

book=fitz.open()
for n in range(1,100):book.insert_pdf(source,from_page=n-1,to_page=n-1,links=False)
for s in sections:
    d=fitz.open(s['path']);book.insert_pdf(d,links=True)
for n in range(205,224):book.insert_pdf(source,from_page=n-1,to_page=n-1,links=False)
assert len(book)==appendixfirst+18

# New original preserved as a legible displayed-scan facsimile.
newbuf=BytesIO();nc=canvas.Canvas(newbuf,pagesize=(612,792),initialFontName='Charter',invariant=1,pageCompression=1)
nc.setFillColor(HexColor(CREAM));nc.rect(0,0,612,792,fill=1,stroke=0)
nc.setFillColor(HexColor(INK));nc.setFont('Charter',27);nc.drawString(54,694,'Judith’s parents on record')
nc.drawImage(str(args.assets/'new-evidence/Judith-Herskovits-Philip-Dratler-1949-certified-abstract.png'),54,257,width=504,height=410,preserveAspectRatio=True)
for text,y in [("Judith Herskovitz and Philip Dratler, Cuyahoga County. State file 09457; A 201127; DGS 005261981, image 12. Wedding 20 November 1949; 22 November is certification [S132].",215),("The explicit fields name father Jacob and mother's maiden name Lee Yanowitz. Judith’s S103 obituary identifies Lawrence Hersh as her brother. Together these support the parental names in Larry’s line; they do not identify the Cleveland uncle or lost sisters. Lee/Leah and Herskovitz/Herskowitz remain attributed variants.",155)]:
    q=paragraph(plain(text),size=10.5,leading=14);h=q.wrap(504,10000)[1];q.drawOn(nc,54,y-h)
nc.setFillColor(HexColor(MUTED));nc.setFont('OpenSansLight',8);nc.drawString(54,45,'Displayed archival scan; maximum-resolution master and physical proof outstanding.')
nc.drawRightString(558,30,str(len(book)+1));nc.save();nd=fitz.open(stream=newbuf.getvalue(),filetype='pdf');book.insert_pdf(nd)

# Combined name/alias index generated from final pagination, including narrative
# and research references. Unresolved entries retain their register labels.
indexrows=[]
identity_terms={
 'P002':['Berta Warszawski','Bertha Warszawski','Berta Zelkind','Bertha Zelkind'],
 'P003':['Larry Hersh','Lawrence Hersh','Arie Lawrence Hersh'],
 'P004':['Ileen Hersh','Ilene Hersh','Ileen Garson','Ilene Garson'],
 'P027':['Szyman Warszawski','Szymon Warszawski'],
 'P035':['Pearl Adelstein','Pearl Garson'],
 'P039':['Rochelle Horwich','Rochelle Garson'],
}
chapter_refs={
 'P002':[6,7,10,11,12,13,14,50,55,56],
 'P003':list(range(15,25))+[57,95,194],
 'P004':[25,26,27,30,34,57],
 'P027':[6,7,8,9,10,12,14,50,55,56,95],
 'P035':[25,26,27,28,30,31,32,33,34]+[mapold[n] for n in [207,210,211,212,213,214,215,216]],
}
# Named chapter/portrait references independently checked against the final
# narrative artwork. Merge with full-name matches; never match a given name alone.
checked_refs={
 'P003':[4,5]+list(range(15,25))+[26,38,39,50,57,58,59]+list(range(93,98))+[101,194],
 'P004':[25,26,31,34,38,39,44,50,57,58,59,101,186],
 'P002':[5,6,7,10,11,12,14,38,44,50,55,56,100],
 'P027':[6,7,8,9,10,38,39,50,55,56,106],
 'P035':[5,26,27,30,31,32,34,38,50,58,59,108,176,177]+list(range(181,188))+[191,193],
 'P034':[5,26,27,28,29,31,33,38,50,58,59,61,64,107]+list(range(176,181))+list(range(187,191))+[193],
 'P001':[4,5,26,36,40,41,42,44,47,48]+list(range(50,57))+[100],
 'P005':[4,5,26,36,40,44,47,48]+list(range(50,55))+[57,101,186],
 'P028':[6,7,12,13,14,38,39,44,50,55,56,89,106],
 'P039':[26,31,34,35,47,58,59,109],
 'P038':[26,31,34,47,58,108],
}
for pid,pages in checked_refs.items():chapter_refs[pid]=sorted(set(chapter_refs.get(pid,[])+pages))
aliases={
 'Abba':'Joe Warszawski','Grammy':'Berta (Bertha) Warszawski','Bella (Berta)':'Berta (Bertha) Warszawski',
 'Gabby':'Ileen (Ilene, Gabby) Hersh','Zaida Larry':'Lawrence (Larry) Hersh','Zeidy Larry':'Lawrence (Larry) Hersh',
 'Chiel':'Yechiel Warszawski','Shim':'Shimon Warszawski','Dassi':'Hadassa Miriam Hirsch',
 'Laurel Ruth Hersh':'Lori (Leah) Warszawski','Arie Lawrence Hersh':'Lawrence (Larry) Hersh',
 'Victor Gershanovitz':'Victor Garson','Isidor Adelstein':'Edward Allen','Rose Alliance':'Rose (Adelstein) Alliance Karr',
 'Janowitz (Leah research variant)':"Leah / Lee Yanowitz (Judith's 1949 abstract; combined sibling evidence)",
 'Lee Yanowitz':"Leah / Lee Yanowitz (Judith's 1949 abstract; combined sibling evidence)",
 'Judith Herskovitz':"Judith Dratler (nee Herskowitz) - 'Judy'"}
pagewords=[re.sub(r'\s+',' ',p.get_text()) for p in book]
for r in register:
    terms=[r['name']]
    if '(' in r['name']:
        base=r['name'].split(' (')[0]
        if len(base.split())>=2:terms.append(base)  # Single given names conflate unrelated people.
    joined=re.sub(r'\([^)]*\)','',r['name']).strip()
    joined=re.sub(r'\s+',' ',joined)
    if len(joined.split())>=2:terms.append(joined)
    terms+=identity_terms.get(r['id'],[])
    refs=sorted(set([positions[r['id']]['page']]+chapter_refs.get(r['id'],[])+[i+1 for i,t in enumerate(pagewords) if any(x and x in t for x in terms) and (i<99 or i>=appendixfirst-1)]))
    if r['id']=='P027':refs=[n for n in refs if n!=53]  # Younger Shimon's household chart.
    if r['id'] in ['P058','P059','P060']:
        refs=sorted(set([positions[r['id']]['page'],57,95,positions['S132']['page'],194]+([16,positions['S103']['page']] if r['id']=='P060' else [])))
    if r['name'].startswith("Jacob (Rochelle") or r['name'].startswith("Ian (Rochelle"):
        refs=sorted(set([34,positions[r['id']]['page']]))
    indexrows.append({'name':r['name'],'pages':refs,'register_id':r['id']})
for alias,target in aliases.items():
    targetrow=next(r for r in indexrows if r['name']==target)
    indexrows.append({'name':alias+' - see '+target,'pages':targetrow['pages'],'register_id':targetrow['register_id']})
for name in ['Sam Adelstein','Rebecca Escowitch','Rosa Pilensky','Israel Jerchonossitch']:
    refs=[i+1 for i,t in enumerate(pagewords) if name in t]
    if refs:indexrows.append({'name':name,'pages':refs,'register_id':None})
indexrows.sort(key=lambda r:re.sub(r'[^a-z0-9]','',r['name'].lower()))
indexfirst=len(book)+1
indexbuf=BytesIO();ic=canvas.Canvas(indexbuf,pagesize=(612,792),initialFontName='Charter',invariant=1,pageCompression=1)
idxpage=indexfirst;col=0;y=143;left=54
def indexframe():
    ic.setFillColor(HexColor(CREAM));ic.rect(0,0,612,792,fill=1,stroke=0)
    ic.setFillColor(HexColor(MUTED));ic.setFont('OpenSansLight',7.5);ic.drawString(54,740,'NAME AND ALIAS INDEX');ic.drawString(54,39,'THE WARSZAWSKIS');ic.setFont('OpenSansLight',9);ic.drawRightString(558,39,str(idxpage))
    ic.setFillColor(HexColor(INK));ic.setFont('Charter',28);ic.drawString(54,690,'Name and alias index')
indexframe();indexpositions=[]
for r in indexrows:
    label=plain(r['name'])+' <font color="#717466">'+', '.join(map(str,r['pages']))+'</font>'
    p=paragraph(label,w=235,size=10.1,leading=13.4);h=p.wrap(235,10000)[1]
    if y+h>713:
        if col==0:col=1;y=143
        else:ic.showPage();idxpage+=1;col=0;y=143;indexframe()
    x=54+col*260;p.drawOn(ic,x,792-y-h)
    indexpositions.append({'page':idxpage,'rect':[x,y,x+235,y+h],'target':r['pages'][0] if r['pages'] else None})
    y+=h+7.4
ic.save();idxdoc=fitz.open(stream=indexbuf.getvalue(),filetype='pdf');book.insert_pdf(idxdoc,links=True)
book.insert_pdf(source,from_page=235,to_page=235,links=False);mapold[236]=len(book)

# Rebuild contents after all flowing sections and the index have final positions.
toc=[x for x in source.get_toc() if x[0]==1 and x[2]<100]
toc += [[1,s['title'],s['first']] for s in sections]
toc += [[1,'New records and research',appendixfirst]]
toc += [[2,title,mapold[p]] for level,title,p in source.get_toc() if level==2 and 206<=p<=223]
toc += [[2,'Judith’s parents on record',appendixfirst+19]]
toc += [[1,'Name and alias index',indexfirst]]
buf=BytesIO();tc=canvas.Canvas(buf,pagesize=(612,792),initialFontName='Charter',invariant=1,pageCompression=1)
tc.setFillColor(HexColor(CREAM));tc.rect(0,0,612,792,fill=1,stroke=0)
tc.setFillColor(HexColor(INK));tc.setFont('Charter',36);tc.drawString(72,650,'Contents')
top=[x for x in toc if x[0]==1]
for i,(_,title,n) in enumerate(top):
    yy=193+i*30;tc.setFont('Charter',14);tc.drawString(72,792-yy,norm(title));tc.setFont('OpenSansLight',10);tc.drawRightString(558,792-yy,str(n))
tc.save();td=fitz.open(stream=buf.getvalue(),filetype='pdf');p=book[2];p.add_redact_annot(fitz.Rect(65,80,565,725),fill=cream);p.apply_redactions(images=0,graphics=0);p.show_pdf_page(p.rect,td,0)
for i,(_,title,n) in enumerate(top):p.insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(72,176+i*30,558,199+i*30),'page':n-1})
book.set_toc(toc)

# Restore preserved external links and translate any existing internal navigation.
for old in retained:
    if old==3:continue  # Old contents hotspots were replaced by final rows.
    p=book[mapold[old]-1]
    for l in source[old-1].get_links():
        if l.get('kind')==fitz.LINK_URI:p.insert_link({'kind':fitz.LINK_URI,'from':l['from'],'uri':l['uri']})
        elif l.get('kind')==fitz.LINK_GOTO and l.get('page',-1)+1 in mapold:p.insert_link({'kind':fitz.LINK_GOTO,'from':l['from'],'page':mapold[l['page']+1]-1})
for ip in indexpositions:
    if ip['target']:book[ip['page']-1].insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(ip['rect']),'page':ip['target']-1})

# Remove duplicate inherited chart footers, renumber retained artwork, and make
# all visible S/W citations navigate to their actual canonical source entry.
fontfile=str(fonts/'OpenSans-Light.ttf');ff=fitz.Font(fontfile=fontfile)
def footer_background(old):
    pix=source[old-1].get_pixmap(clip=fitz.Rect(20,740,21,741),alpha=False)
    return tuple(c/255 for c in pix.pixel(0,0))
for old,new in mapold.items():
    if old not in retained and old!=236:continue
    bg=footer_background(old);fc=(.79,.82,.78) if sum(bg)<1.5 else (.443,.455,.400)
    p=book[new-1];p.add_redact_annot(fitz.Rect(45,735,569,771),fill=bg);p.apply_redactions(images=0,graphics=0)
    p.insert_font(fontname='RevisionSans',fontfile=fontfile)
    p.insert_text((72 if new%2 else 54,753),'THE WARSZAWSKIS',fontname='RevisionSans',fontsize=7.6,color=fc)
    p.insert_text((558-ff.text_length(str(new),fontsize=9),753),str(new),fontname='RevisionSans',fontsize=9,color=fc)
for p in book:
    used=set(re.findall(r'\b[SW]\d{2,3}\b',p.get_text()))
    for sid in used:
        if sid in positions:
            for rect in p.search_for(sid):p.insert_link({'kind':fitz.LINK_GOTO,'from':rect,'page':positions[sid]['page']-1,'to':fitz.Point(0,positions[sid]['y'])})

book.set_metadata({'title':'The Warszawskis - revised family edition - 2 October 2026','author':'Warszawski family editorial project','subject':'Revised private reading edition; uncertainty and source attribution retained','creator':'Reproducible Warszawski revision builder'})
reading=OUT/'The-Warszawskis-Revised-2026-10-02-Reading.pdf'
book.save(reading,garbage=4,deflate=True);book.close();book=fitz.open(reading)

# Print retains original full-resolution artwork wherever it was not patched.
# Recreated/changed pages are drawn as vector PDF content at 9-point bleed inset.
originalprint=fitz.open(args.print_pdf);printing=fitz.open();inverse={new:old for old,new in mapold.items() if old in retained or old==236}
patched={n for n,_ in patches}|{3}
for i,p in enumerate(book):
    old=inverse.get(i+1)
    if old and old!=3:
        printing.insert_pdf(originalprint,from_page=old-1,to_page=old-1,links=False)
        bg=footer_background(old);fc=(.79,.82,.78) if sum(bg)<1.5 else (.443,.455,.400)
        pp=printing[-1]
        changed=[(j,rect) for j,(n,rect) in enumerate(patches) if n==old]
        for j,rect in changed:pp.add_redact_annot(rect+(9,9,9,9),fill=cream)
        if changed:
            pp.apply_redactions(images=0,graphics=0)
            for j,rect in changed:pp.show_pdf_page(fitz.Rect(9,9,621,801),patchdoc,j,keep_proportion=False)
        pp.add_redact_annot(fitz.Rect(45,744,578,780),fill=bg);pp.apply_redactions(images=0,graphics=0)
        pp.insert_font(fontname='RevisionSans',fontfile=fontfile);pp.insert_text((81 if (i+1)%2 else 63,762),'THE WARSZAWSKIS',fontname='RevisionSans',fontsize=7.6,color=fc);pp.insert_text((567-ff.text_length(str(i+1),fontsize=9),762),str(i+1),fontname='RevisionSans',fontsize=9,color=fc)
    else:
        pp=printing.new_page(width=630,height=810);pp.draw_rect(pp.rect,color=None,fill=cream);pp.show_pdf_page(fitz.Rect(9,9,621,801),book,i,keep_proportion=False)
    pp.set_trimbox(fitz.Rect(9,9,621,801));pp.set_bleedbox(pp.rect)
for i,p in enumerate(book):
    for l in p.get_links():
        v={k:val for k,val in l.items() if k not in ['xref','id']};v['from']=l['from']+(9,9,9,9)
        if 'to' in v and v.get('kind')==fitz.LINK_GOTO:v['to']=v['to']+fitz.Point(9,9)
        printing[i].insert_link(v)
printing.set_toc(toc);printing.set_metadata(book.metadata)
printout=OUT/'The-Warszawskis-Revised-2026-10-02-Print.pdf';printing.save(printout,garbage=4,deflate=True);printing.close()

(QA/'pagination.json').write_text(json.dumps({'page_count':len(book),'sections':[{k:v for k,v in s.items() if k!='path'} for s in sections],'appendix_first':appendixfirst,'index_first':indexfirst,'positions':positions,'baseline_to_final':mapold,'toc':toc,'patches':[{'baseline_page':n,'rect':list(r)} for n,r in patches]},ensure_ascii=False,indent=2)+'\n')
(QA/'name-index.json').write_text(json.dumps(indexrows,ensure_ascii=False,indent=2)+'\n')
(OUT/'The-Warszawskis-Revised-2026-10-02-Editable.txt').write_text('\n\n'.join(f'PAGE {i+1}\n'+p.get_text(sort=True) for i,p in enumerate(book)))
(QA/'build-manifest.json').write_text(json.dumps({'page_count':len(book),'register_entries':len(register),'households':len(households),'S_sources':len([r for r in sources if r['id'].startswith('S')]),'W_sources':30,'outputs':[{'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [reading,printout]],'legacy_layout':'Preserved PDF artwork; editable reference sections recreated; no native legacy design file recovered.'},indent=2)+'\n')
print(json.dumps({'pages':len(book),'sections':[{k:v for k,v in s.items() if k!='path'} for s in sections],'appendix':appendixfirst,'index':indexfirst,'patches':len(patches)}))
