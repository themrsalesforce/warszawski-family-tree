from pathlib import Path
from io import BytesIO
from xml.sax.saxutils import escape
import json, re, hashlib
import fitz
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import EmbeddedType1Face, Font
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).parent
SRC=ROOT.parent/'Source-images'; OUT=ROOT/'draft'; OUT.mkdir(exist_ok=True)
FIG=ROOT/'figures'; FIG.mkdir(exist_ok=True)
BASE=ROOT/'baseline'
READ=BASE/'The-Warszawskis-Coffee-Table-Edition-2026-10-01-Reading-Copy.pdf'
PRINT=BASE/'The-Warszawskis-Coffee-Table-Edition-2026-10-01-Print-Interior.pdf'
CREAM='#FCFAF5'; INK='#282A26'; RUST='#845B44'; GREEN='#283E40'; MUTED='#717466'; PALE='#DFDAD0'
for name,stem in [('Charter','bchr8a'),('CharterItalic','bchri8a'),('CharterBold','bchb8a')]:
    d=ROOT/'fonts'
    face=EmbeddedType1Face(str(d/(stem+'.afm')),str(d/(stem+'.pfb')))
    pdfmetrics.registerTypeFace(face); pdfmetrics.registerFont(Font(name,face.name,'WinAnsiEncoding'))
for name,file in [('OpenSans','OpenSans-Regular.ttf'),('OpenSansLight','OpenSans-Light.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(ROOT/'fonts'/file)))
pdfmetrics.registerFontFamily('Charter',normal='Charter',bold='CharterBold',italic='CharterItalic',boldItalic='CharterItalic')

def crop(name,source,box):
    f=FIG/(name+'.jpg')
    im=Image.open(source).convert('RGB').crop(box)
    im.save(f,quality=96,subsampling=0)
    return f

# These are documentary crops only: original pixels and relative positions are retained.
marriage=crop('marriage-111752',SRC/'Victor_Garson_Pearl_Adelstein_1916_image1100_original.jpg',(30,2700,2400,3560))
petition=crop('victor-petition-19277',SRC/'Victor_Garson_1924_petition_declaration_PGTZ_original.jpg',(2690,170,4910,3650))
petition_detail=crop('victor-petition-names-and-crossing',SRC/'Victor_Garson_1924_petition_declaration_PGTZ_original.jpg',(2720,760,4840,1610))
order=crop('victor-court-order',SRC/'Victor_Garson_1924_naturalization_PGGF_original.jpg',(380,200,2630,3700))
order_detail=crop('victor-name-change-detail',SRC/'Victor_Garson_1924_naturalization_PGGF_original.jpg',(480,1200,2550,1770))
birth=crop('pearl-birth-certificate',SRC/'Pearl-Adelstein-birth-certificate-1940-displayed-scan.png',(62,58,1185,985))
affidavit=crop('rose-sister-affidavit',SRC/'Pearl-Adelstein-Rose-Alliance-affidavit-1940-displayed-scan.png',(65,52,1190,980))
affidavit_detail=crop('rose-alliance-sister-detail',SRC/'Pearl-Adelstein-Rose-Alliance-affidavit-1940-displayed-scan.png',(82,710,1180,952))
census_src=SRC/'1920-census-visible-source.jpg'
census_names=crop('1920-garson-allen-household',census_src,(168,552,665,645))
census_origins=crop('1920-garson-origins',census_src,(655,552,1407,645))
census_head=crop('1920-census-heading',census_src,(30,28,1440,158))
manifest=SRC/'Victor_Gerschenowitz_Ryndam_candidate_1902_G636_original.jpg'
ryndam_names=crop('ryndam-rachel-victor-names',manifest,(225,1080,1630,1520))
ryndam_heading=crop('ryndam-ship-heading',manifest,(850,385,3930,650))
marcus=SRC/'marcus-1958-federal-card-reverse.jpg'
grenberg=SRC/'1910-Grenberg-candidate-crop.jpg'

class BookCanvas:
    def __init__(self,path):
        self.c=canvas.Canvas(str(path),pagesize=(612,792),pageCompression=1,initialFontName='Charter')
        self.c.setTitle('The Warszawskis - New records and research - 2 October 2026')
        self.pages=[]; self.number=None
    def text(self,text,x,y,size=12.1,font='Charter',color=INK):
        self.c.setFillColor(HexColor(color));self.c.setFont(font,size);self.c.drawString(x,792-y,text)
    def para(self,text,y,x=None,w=486,size=12.1,leading=18,font='Charter',color=INK):
        x=self.left if x is None else x
        st=ParagraphStyle('p',fontName=font,fontSize=size,leading=leading,textColor=HexColor(color),spaceAfter=0)
        p=Paragraph(text,st); ww,hh=p.wrap(w,1000);p.drawOn(self.c,x,792-y-hh)
        if y+hh>728:print(f'OVERFLOW Page {self.number}: {y+hh} {text[:70]}')
        return y+hh
    def photo(self,file,x,y,w=None,h=None):
        im=Image.open(file);iw,ih=im.size
        if w is None:w=h*iw/ih
        if h is None:h=w*ih/iw
        self.c.drawImage(str(file),x,792-y-h,width=w,height=h,preserveAspectRatio=True,mask='auto')
        return y+h
    def begin(self,n,title,section='NEW RECORDS AND RESEARCH',dark=False):
        if self.number is not None:self.c.showPage()
        self.number=n;self.left=72 if n%2 else 54
        self.dark=dark;self.pages.append({'page':n,'title':title})
        self.c.setFillColor(HexColor(GREEN if dark else CREAM));self.c.rect(0,0,612,792,fill=1,stroke=0)
        self.text(' '.join(section),self.left,52,7.3,'OpenSans', '#CAD0C8' if dark else MUTED)
        self.text('THE WARSZAWSKIS',self.left,753,7.6,'OpenSansLight','#CAD0C8' if dark else MUTED)
        self.c.setFillColor(HexColor('#CAD0C8' if dark else MUTED));self.c.setFont('OpenSansLight',9)
        self.c.drawRightString(self.left+486,39,str(n))
        if not dark:self.text(title,self.left,110,28)
    def sub(self,text,y=137):self.text(text,self.left,y,12.1,'CharterItalic',RUST)
    def cap(self,text,y):return self.para(text,y,size=10.1,leading=14.2,color=MUTED)
    def finish(self):self.c.save()

B=BookCanvas(OUT/'research-supplement.pdf')
B.begin(205,'New records',dark=True)
B.photo(order_detail,72,129,w=486)
B.text('New records',72,601,36,color=CREAM)
B.text('Names, signatures and the next questions',72,638,13.2,'CharterItalic','#DDD8CF')
B.text('Research update · 2 October 2026',72,714,9,'OpenSansLight','#CAD0C8')

B.begin(206,'What the new pages add')
B.sub('A guide to the discoveries in this edition')
y=B.para('The documents gathered here add names and relationships to the Cleveland story. They also show where an attractive lead still falls short of a family connection. The original pages are reproduced beside their readings so that the evidence can be revisited.',166)
y+=29; B.text('Victor’s earlier surname',B.left,y,20);y+=15
y=B.para('His 1924 petition was filed as Victor Gershanovitz. The court admitted him and formally changed his name to Victor Garson on 20 November 1924; the certificate was issued six days later. The earlier 1919 declaration and the final naturalization are now joined by the complete packet.',y+6)
y+=28;B.text('Pearl’s parents and sister',B.left,y,20);y+=15
y=B.para('The marriage application and delayed birth certificate name Sam and Rebecca Adelstein. On the supporting affidavit, Rose Alliance identifies herself plainly as Pearl’s sister. Rose’s 1906 marriage names their mother as Rebecca Escowitch. Together, the records provide strong evidence for that maiden-name reading, while other forms continue to use Adelstein.',y+6)
y+=28;B.text('The Allen brothers in the house',B.left,y,20);y+=15
y=B.para('The original 1920 census places Harry and Louis Allen with Victor, Pearl and baby Rachelle, each recorded as Victor’s brother-in-law. This is a contemporary household link behind the Allen names in Pearl’s later notice.',y+6)
y+=28;B.text('Where the questions remain',B.left,y,20);y+=15
y=B.para('The Paris birth act, the Ryndam passengers and a New York census lead remain candidates. The historical Edelstein records establish a separate research trail, with no shared ancestor yet proved. None of those proposed connections has been added to the confirmed family tree.',y+6)

B.begin(207,'Victor and Pearl marry')
B.sub('Cuyahoga County, 12 September 1916')
end=B.photo(marriage,B.left,169,w=486)
y=B.cap('Application 111752, the bottom entry on page 188. The license was issued on 11 September; the return records the marriage on 12 September 1916. The three unrelated applications above it are omitted here.',end+13)
y=B.para('The original gives Victor’s father as Solomon and his mother as Rachael, followed by “l-n-u,” apparently last name unknown. It is an explicit limit in the record: her maiden surname has not been recovered.',y+26)
y=B.para('Pearl’s father is written as Sam. Her mother’s entry reads Rebecca Adelstein, even though the printed line asks for the mother’s maiden name. Rose’s 1906 marriage provides the stronger maiden-name reading Escowitch; the sister affidavit supplies the link to Pearl. The differing field entries remain visible in this edition.',y+14)
y=B.para('Pearl is recorded as nineteen. The birth date she later swore to, 1 December 1897, would make her eighteen at this September 1916 marriage. Both readings are retained rather than silently adjusted.',y+14)
B.cap('Source: Cuyahoga County marriage record, FamilySearch DGS 004030138, image 1100. Source W01.',y+24)

B.begin(208,'From Gershanovitz to Garson')
B.sub('The petition and the court’s own order')
y=B.para('Victor already used Garson when he signed his 1919 declaration. In 1924 the full petition was entered as Victor Gershanovitz. The court order joins the two names in one proceeding, giving the family a documentary bridge rather than a resemblance between surnames.',168)
end=B.photo(petition_detail,B.left,y+22,w=486)
y=B.cap('The petition’s heading and family particulars. The name Gershanovitz is typed at the head of petition 19277. It records Paris and 30 May 1895, as well as wife Pearl and daughter Rochelle.',end+12)
end=B.photo(order_detail,B.left,y+20,w=486)
y=B.cap('The order admits Victor on 20 November 1924 and changes his name to Victor Garson. Certificate 2116415 was issued on 26 November. These are two different steps in the same case.',end+12)
B.cap('The complete relevant petition and order pages follow. Sources W02-W03.',y+17)

B.begin(209,'Victor’s petition')
B.sub('Petition 19277, filed in 1924')
# Complete relevant right-hand petition, without the neighboring case.
B.photo(petition,122,164,h=508)
B.cap('The complete petition page, including Victor’s signature and witness affidavits. Its self-reported voyage was Lorraine, from Havre on 22 November 1902 to New York on 2 December. The passenger candidate reproduced later differs in ship, port and dates. Source W02.',685)

B.begin(210,'The court changes his name')
B.sub('Admission 20 November 1924; certificate issued 26 November')
B.photo(order,113,157,h=515)
B.cap('Victor’s oath, admission and name-change order. The neighboring applicant’s page is excluded. No parents’ names appear in this packet, so the discovery resolves the surname history without settling the earlier generation. Source W03.',684)

B.begin(211,'Pearl’s birth put on record')
B.sub('Cleveland, 1 December 1897')
end=B.photo(birth,B.left,165,w=486)
y=B.cap('A delayed certificate filed on 25 January 1940, more than forty years after the birth it records. It names Pearl Adelstein, her parents Sam and Rebecca, and Russia as each parent’s birthplace. Source W04.',end+13)
y=B.para('This original agrees with Pearl’s sworn citizenship petition about her Cleveland birth. Its parent fields give the next generation a firmer starting point. Read alongside Rose’s marriage and sister affidavit, the strongest combined maiden-name evidence is Escowitch, also transcribed Escovitch. Both parents’ precise towns remain unresolved.',y+22)
B.cap('Parental ages are recorded as forty-two and forty-four; exact birth years are not inferred.',y+11)

B.begin(212,'Rose writes “Sister”')
B.sub('The supporting affidavit, 24 January 1940')
end=B.photo(affidavit,B.left,165,w=486)
y=B.cap('The reverse of Pearl’s delayed birth certificate. “Mrs Rose Alliance - Sister” is written on the relationship line. The affidavit is dated the day before the certificate was filed. Source W05.',end+13)
y=B.para('The single word supplies a direct family relationship. Rose Alliance was not inferred to be a relative from a shared surname; she identified herself as Pearl’s sister in the document supporting Pearl’s birth record.',y+22)
B.cap('Harry Allen signs and stamps the affidavit as notary. His name alone does not establish that this notary was the brother Harry Allen named in the census and Pearl’s death notice.',y+13)

B.begin(213,'Rebecca’s maiden name')
B.sub('Rose’s original marriage supplies the missing field')
rose_marriage=crop('rose-1906-marriage-entry',SRC/'Rose-Adelstein-Sam-Alliance-1906-original-detail.png',(125,180,1170,686))
end=B.photo(rose_marriage,B.left,166,w=486)
y=B.cap('Rose Adelstein and Sam Alliance, 16 January 1906. Application 45321, page 331. The bride’s father is Sam Adelstein; the mother’s explicitly designated maiden name reads Rebecca Escowitch. Source W26.',end+12)
y=B.para('This record directly concerns Rose. The bridge to Pearl is the original 1940 affidavit in which Mrs Rose Alliance identifies herself as Pearl’s sister. With Sam and Rebecca named across the records, the combined evidence strongly supports Escowitch as Pearl’s mother’s maiden name.',y+24)
y=B.para('Escovitch is an alternate transcription. Pearl’s 1916 marriage and 1940 birth certificate instead write Rebecca Adelstein; Edward’s 1952 marriage repeats that form. Those entries have not been erased or silently made to agree. Escowitch is the strongest available reading, not a settled spelling for every earlier generation.',y+15)
B.cap('The original gives Rose as twenty, born in Russia and working as a clerk. The document names her mother; it does not identify Rebecca’s parents or a precise birth town.',y+18)

B.begin(214,'Rose across three records')
B.sub('Adelstein, Alliance and Karr')
end=B.photo(affidavit_detail,B.left,166,w=486)
y=B.cap('The identifying line in Pearl’s 1940 supporting affidavit: Rose Alliance calls herself Sister. Source W05.',end+12)
y=B.para('The 1906 marriage records Rose Adelstein marrying Sam Alliance. More than three decades later, the sister affidavit puts Rose Alliance directly beside Pearl’s own birth evidence. A later newspaper record supplies the final surname bridge.',y+26)
y=B.para('Cleveland Public Library’s necrology transcription of the Plain Dealer notice dated 26 March 1970 identifies Mrs Rose Karr as “the former Rose Alliance.” It calls her Mrs Max Karr, gives her age as eighty-four, and names daughter Mrs Ruth Davidson, one sister and five brothers.',y+15)
y=B.para('That explicit former-name wording connects the Rose Karr named in Pearl’s 1973 notice to the Rose Alliance who supported her birth record. It does not give the date of Rose’s later marriage, and none is inferred here.',y+15)
B.cap('The accessible source is the library’s transcription, not a reproduced newspaper clipping. The original newspaper scan has not been obtained. Source W29.',y+19)

B.begin(215,'Isidor and Edward')
B.sub('An Adelstein to Allen name change in the records')
B.photo(SRC/'Isidor-Adelstein-Edward-Allen-VA-name-detail.png',B.left,167,w=215)
B.photo(SRC/'Isidor-Adelstein-Edward-Allen-VA-dates-detail.png',B.left,260,w=215)
y=B.para('The original veterans’ index card types ADELSTEIN ISIDOR and then ALLEN, EDWARD. It records birth on 9 June 1895, enlistment on 28 April 1918 and discharge on 18 October 1919. This directly documents both names for the same man.',165,x=B.left+246,w=240,size=11.4,leading=16.5)
B.cap('Relevant name and date bands from the original card. Source W27.',330)
edward_detail=crop('edward-1952-groom-fields',SRC/'Edward-Allen-Annette-Harris-1952-original-detail.png',(175,5,856,635))
B.photo(edward_detail,B.left,402,w=220)
y=B.para('Edward B Allen’s 1952 marriage abstract gives his age as fifty-seven, his father as Samuel and the mother’s maiden-name field as Rebecca Adelstein. The surname Allen in an index must not be added to the original father field, which contains only Samuel.',402,x=B.left+246,w=240,size=11.4,leading=16.5)
y=B.para('The ceremony was 28 August 1952. The license was issued on 14 August; 3 September is the abstract’s certification date, not the wedding date.',y+14,x=B.left+246,w=240,size=11.4,leading=16.5)
B.cap('The marriage’s Adelstein field is retained beside Rose’s Escowitch evidence. It does not settle a standardized maternal surname. Source W28. The 1920 census and Pearl’s later notice independently establish the broader Allen family context.',668)

B.begin(216,'Pearl’s side of the family')
B.sub('The newly documented parents in the known descent')
def box(x,y,w,h,name,detail=''):
    B.c.setStrokeColor(HexColor(PALE));B.c.setLineWidth(.8);B.c.roundRect(x,792-y-h,w,h,5,fill=0,stroke=1)
    B.text(name,x+12,y+25,15)
    if detail:B.para(detail,y+35,x=x+12,w=w-24,size=9.2,leading=12.6,color=MUTED)
def line(x1,y1,x2,y2):
    B.c.setStrokeColor(HexColor('#BCAF9B'));B.c.setLineWidth(.8);B.c.line(x1,792-y1,x2,792-y2)
box(72,180,216,77,'Sam Adelstein','Father named in the 1916 marriage<br/>and Pearl’s 1940 birth certificate')
box(324,180,234,77,'Rebecca Escowitch','Strong combined maiden-name reading;<br/>other records use Adelstein')
line(288,219,324,219);line(306,219,306,293)
box(185,293,242,72,'Pearl Adelstein Garson','1 December 1897 · Cleveland')
line(306,365,306,392)
box(185,392,242,72,'Ileen Garson Hersh','Gabby · Pearl and Victor’s daughter')
line(306,464,306,491)
box(185,491,242,72,'Lori Hersh Warszawski','Joe’s wife; mother of the nine children')
y=B.para('Alongside this direct descent, the records now identify Rose Alliance as Pearl’s sister and place Harry and Louis Allen in her married household as Victor’s brothers-in-law. Pearl’s 1973 notice supplies the wider sibling list: Harry, Sydney, Edward, Louis and Howard Allen, and the late Rose Karr.',596,size=11.5,leading=16.5)
B.cap('CPL’s 1970 necrology transcription calls Rose Karr the former Rose Alliance. Rebecca’s Escowitch reading combines Rose’s original marriage with Pearl’s sister affidavit; conflicting Adelstein fields remain recorded. Sources W01, W04-W06, W26, W28-W29.',y+18)

B.begin(217,'The Allen brothers at home')
B.sub('Cleveland’s 1920 census joins the names')
end=B.photo(census_head,B.left,165,w=486)
B.cap('Cleveland Ward 17, enumeration district 343, sheet 5A; enumerated 5 January 1920.',end+10)
end=B.photo(census_names,B.left,250,w=486)
B.cap('Household 79, lines 21-25: Victor, Pearl, baby Rachelle, Harry Allen and Louis Allen. Both Allen men are explicitly recorded as Victor’s brothers-in-law.',end+11)
end=B.photo(census_origins,B.left,410,w=486)
y=B.cap('The corresponding birthplace, language and occupation columns, enlarged separately. The row order is the same as in the household detail above. Source W06.',end+10)
y=B.para('Victor is twenty-four; Pearl twenty-three; Rachelle eight months; Harry twenty-six; and Louis eighteen. The record gives Victor’s birthplace and language as France and French, and both parents as Russia and Russian. Their names are not supplied.',y+23)
B.para('The immigration year reads 1900. That conflicts with the 1902 year in the naturalization evidence. The household relationship is useful even while the arrival-year discrepancy remains unresolved.',y+15)

B.begin(218,'A Victor born in Paris')
B.sub('A strong candidate, still outside the confirmed tree')
end=B.photo(SRC/'act2087-full-crop.jpg',B.left,166,w=486)
y=B.cap('Paris 20e, birth act 2087, registered 1 June 1895. The child is Victor, born 30 May 1895. The matching name, day and city make this an important candidate. Source W08.',end+12)
y=B.para('The surname in the act is approximately Jerchonossitch; an index renders it Gerchinovitch. The preferred reading of the father is Israël, forty-four, a tinsmith. The mother is read as Rosa Pilensky, with age thirty-three the preferred reading; the paleography remains qualified.',y+25)
y=B.para('Those parent names conflict with Solomon and Rachael in Victor Garson’s American marriage record. The surname’s similarity to Gershanovitz strengthens the reason to investigate, but it does not remove that conflict.',y+15)
B.para('An independent record naming the same mother or linking this Paris household to the Cleveland man is still needed. No French parent or maternal maiden surname has been inserted into the confirmed family tree.',y+15)

B.begin(219,'Rachel and Victor on the Ryndam')
B.sub('A passenger candidate with important differences')
end=B.photo(ryndam_heading,B.left,165,w=486)
B.cap('The manifest names the Ryndam and a departure from Boulogne in November 1902.',end+9)
end=B.photo(ryndam_names,B.left,262,w=486)
y=B.cap('Rachel Gerschenowitz, thirty-four and widowed, followed by Victor, seven. Paris is entered as their last residence. It is not a birthplace field. Source W09.',end+12)
y=B.para('The Ryndam arrived at New York on 1 December 1902. Victor’s naturalization petition instead recalls the Lorraine, leaving Havre on 22 November and arriving on 2 December. The names, age and Paris residence explain the lead; the conflicting voyage details prevent a confident identification.',y+24)
y=B.para('The Paris birth candidate’s mother is preferably read as thirty-three in 1895, which also conflicts with Rachel’s age thirty-four in 1902. The adjacent Grinberg infant is eight months old; the grouping alone does not establish a relationship to Rachel or Victor.',y+15)
B.cap('The complete manifest and reverse are retained with the source images. No travelling companion or new child has been added to Victor’s confirmed family.',y+18)

B.begin(220,'A New York lead to test')
B.sub('The 1910 Grenberg and Pelesky household is unlinked')
end=B.photo(grenberg,B.left,165,w=486)
y=B.cap('Manhattan, 1910: a France-born Victor, fifteen, in the household of Max and Mary Pelesky. This is an unresolved candidate, not a record assigned to Victor Garson. Source W10.',end+12)
y=B.para('The surname is read provisionally as Grenberg. His parents are entered as born in Russia, with Yiddish as their language. The indexed relationship says cousin, but the original entry is overwritten and begins with “Brother”; the continuation has not been securely read.',y+25)
y=B.para('The preferred arrival-year reading is 1904, another difference from Victor Garson’s 1902 statement. There is no named-parent link and no Cleveland connection. The resemblance between Pelesky and the passenger candidate’s contact name is a research clue only.',y+15)
B.para('The next useful step is to identify this household independently in another census or a vital record. Until that evidence exists, the image belongs among open questions and not among the family’s ancestors.',y+15)

B.begin(221,'Mordka becomes Marcus')
B.sub('A separate Edelstein record trail')
end=B.photo(marcus,B.left,166,w=486)
y=B.cap('The reverse of Marcus Edelstein’s federal naturalization index card explicitly types the former name Mordka Ejdelsztejn and the date 27 June 1958. Source W11.',end+12)
y=B.para('The front identifies Marcus as born on 2 February 1916 in Poland, with petition 131148 in the U.S. District Court at Cleveland. The typed reverse makes the old surname secure. The card does not give his parents, a Polish town or arrival particulars.',y+25)
y=B.para('A published 1945 Bergen-Belsen survivor list records “Edelsztajn, Mordka,” born 2 February 1916, with birthplace Kurow. The matching name and exact birthday strongly support the Kurów origin. Inclusion in that list does not, by itself, establish his wartime camp itinerary.',y+15)
B.cap('The list’s foreword is dated 7 September 1945. Its original entry was inspected on printed page 9. This evidence does not establish kinship to Pearl Adelstein. Sources W11 and W24.',y+18)

B.begin(222,'Adelstein and Edelstein')
B.sub('The connection question remains open')
y=B.para('The family’s question about Shoshy’s school friend Shifra led to a historical Edelstein household in Cleveland. Identification of the school friend remains tentative. A public 2012 family announcement is used here only as a dated source for names; it does not establish anyone’s present relationship status.',170)
y+=27;B.text('The historical household',B.left,y,20);y+=16
y=B.para('That announcement names Joseph and Rochelle Edelstein and the late Kayla and Marcus Edelstein. Marcus’s obituary index names Joseph among his children and Karola as his wife. The Kayla/Karola identification is strongly supported by the surrounding record trail, but it should remain qualified until an explicit original naming bridge is obtained.',y+4)
y=B.para('Karola Faige Edelstein’s Social Security index gives the alias Faigenbaum, birth on 6 April 1921 in Kurow, Poland, and parents Josef Faigenbaum and Shifra Friedman. Ohio’s death index instead gives 4 June 1921, a month-and-day disagreement retained here. Phillip Edelstein’s index names Marcus and Karola as parents and a 1947 birth at “Helsenberg,” Sweden, the index’s own spelling.',y+15)
y+=27;B.text('What would establish a connection',B.left,y,20);y+=16
y=B.para('Pearl’s records place Sam and Rebecca’s daughter in Cleveland by 1897. The Edelstein sources point toward Poland and postwar Sweden. Neither spelling nor broad geography supplies a common ancestor. Marcus’s parents and Sam and Rebecca’s precise origins are the missing connecting evidence.',y+4)
B.cap('Sources W11-W16. Survivor-list and published-testimony leads remain separately identified in the source notes; their full originals have not all been examined.',y+20)

B.begin(223,'The questions worth carrying forward')
B.sub('What would make the next connection reliable')
items=[
('Victor’s parents','The marriage names Solomon and Rachael; the Paris candidate names Israël and Rosa. A reliable maternal maiden name, an original Social Security application or another direct household record could resolve or disprove the proposed identity. A bounded NUMIDENT search found no defensible match to Victor’s own application.'),
('Pearl’s earlier family','The birth certificate and sister affidavit now anchor Sam, Rebecca and Rose. Rose’s original marriage makes Escowitch the strongest combined maiden-name reading for Rebecca, with Escovitch as a transcription variant. Sam and Rebecca’s precise birthplaces and parents remain open; the other online-tree variants are unproved.'),
('The Allen names','The 1920 household documents Harry and Louis; Pearl’s later notice names the wider set of brothers. An original veterans’ card directly links Isidor Adelstein with Edward Allen. CPL’s transcription joins Rose Alliance with Rose Karr. Further records are needed to explain the wider family’s changes of surname and resolve remaining identities.'),
('The Edelstein comparison','The full 1958 federal petition has been requested but not yet inspected. Arolsen’s catalogue identifies tracing case 331.509 for Mordka Ejdelsztejn, born 2 February 1916, with nine documents; their contents remain unexamined. Kurów marriage indexes for 1934-1939 yielded no target couple, and the official birth-register inventory omits 1916.'),
('A stronger end-of-life record','The Ohio government-derived index now supports Victor’s death on 13 August 1978 at East Cleveland. It is not the original certificate and gives no parents. The cemetery’s 14 August date is his interment, a different event.')]
y=170
for h,p in items:
    B.text(h,B.left,y,18);y=B.para(p,y+15,size=11.5,leading=16.4)+25
B.cap('Research status as of 2 October 2026. Unsuccessful searches are bounded by the records and indexes actually examined; they do not prove that an event or relationship never existed.',y-3)

sources=[
('W01','Victor Garson and Pearl Adelstein marriage record','Cuyahoga County, application 111752, page 188, license 11 September and return 12 September 1916. Original image inspected; only the relevant entry reproduced.','https://www.familysearch.org/ark:/61903/3:1:939K-BJ3N-RG'),
('W02','Victor Gershanovitz petition and attached declaration','Petition 19277 (1924), Cuyahoga County Common Pleas Court; attached federal declaration 28845, 18 September 1919. Original image inspected.','https://www.familysearch.org/ark:/61903/3:1:3QS7-8996-PGTZ'),
('W03','Victor’s admission and name-change order','Original order dated 20 November 1924; certificate 2116415 issued 26 November. The adjacent applicant’s case is excluded from the reproduction.','https://www.familysearch.org/ark:/61903/3:1:3QS7-8996-PGGF'),
('W04','Pearl Adelstein delayed birth certificate','DGS 004339078, image 383; filed 25 January 1940 for birth 1 December 1897. Original inspected and displayed scan preserved.','https://www.familysearch.org/ark:/61903/3:1:939N-GFS1-X2?lang=en&i=382'),
('W05','Rose Alliance’s supporting affidavit','DGS 004339078, image 384, dated 24 January 1940; relationship explicitly Sister. Original inspected and displayed scan preserved.','https://www.familysearch.org/ark:/61903/3:1:939N-GFS1-FN?lang=en&i=383'),
('W06','Victor and Pearl’s 1920 census household','Cleveland Ward 17, ED 343, sheet 5A, household 79, lines 21-25. Original inspected. Harry and Louis Allen each recorded as brother-in-law to Victor.','https://www.familysearch.org/ark:/61903/3:1:33S7-9RX2-3ZD'),
('W07','Victor Garson Ohio death index','Ohio Department of Health-derived index: 13 August 1978, East Cleveland; certificate 063533, volume 23386. Index inspected; original certificate not obtained.','https://www.familysearch.org/ark:/61903/1:1:VKLR-HTD?lang=en'),
('W08','Paris birth act 2087','Paris 20e, registered 1 June 1895, Victor born 30 May. Original inspected. Surname and parental readings remain qualified; identity with Victor Garson is unproved.','https://archives.paris.fr/_recherche-images/show/410797/image/287918/24/full/full/0/default.jpg'),
('W09','Ryndam passenger candidate','New York passenger manifest, Ryndam, arrival 1 December 1902, list E, Rachel and Victor Gerschenowitz. Original front and reverse inspected and preserved: DGS 007675229, item 2, images 4-5. Identity unproved.','https://www.familysearch.org/ark:/61903/3:1:3Q9M-C9T4-G636'),
('W10','Manhattan Grenberg and Pelesky candidate','1910 Manhattan Ward 12, ED 446, sheet 15B, line 98. Original inspected; overwritten relationship unresolved. Not assigned to Victor Garson.','https://www.familysearch.org/ark:/61903/3:1:33S7-9RVN-FHN'),
('W11','Marcus Edelstein federal naturalization cards','Front: born 2 February 1916, Poland, petition 131148, admitted 27 June 1958. Reverse types former name Mordka Ejdelsztejn. Both original sides inspected; reverse reproduced.','https://www.familysearch.org/ark:/61903/3:1:3QS7-L9HV-KQ2'),
('W12','Marcus Edelstein obituary index','GenealogyBank-derived FamilySearch index names wife Karola and children including Joseph. Original newspaper clipping not obtained; duplicate indexes are not independent testimony.','https://www.familysearch.org/ark:/61903/1:1:4CQL-P9MM?lang=en'),
('W13','The 2012 Edelstein family announcement','Cleveland Jewish News, Edelstein-Senders, posted 8 November 2012. Directly read family names. Used as historical evidence only; schoolfriend identification and present relationships are not established.','https://www.clevelandjewishnews.com/community/lifecycles/engagements/edelstein-senders/article_ea383076-29f1-11e2-b699-001a4bcf887a.html'),
('W14','Karola Faige Edelstein Social Security index','NUMIDENT entry: Faigenbaum alias; 6 April 1921, Kurow; parents Josef Faigenbaum and Shifra Friedman. Indexed data inspected, no original application. No Social Security number is reproduced.','https://www.familysearch.org/ark:/61903/1:1:6K3Q-K9NP?lang=en'),
('W15','Karola Edelstein Ohio death index','The inspected index gives birth 4 June 1921 and death 1 March 2000, disagreeing with NUMIDENT on the birth month and day. The conflict is preserved.','https://www.familysearch.org/ark:/61903/1:1:VKJP-PTT?lang=en'),
('W16','Phillip Edelstein Social Security index','Index gives birth 18 July 1947 at Helsenberg, Sweden, and parents Marcus Edelstein and Karola Faigenbaum. The place spelling is retained as indexed.','https://www.familysearch.org/ark:/61903/1:1:6K3G-9NWV?lang=en'),
('W17','The pending Marcus naturalization file','National Archives, RG 21, series 1127790; petition 131148, Cleveland, 1958. Original file requested but not inspected. Online partner petition coverage ending in 1946 does not establish absence of the later file.','https://catalog.archives.gov/id/1127790'),
('W18','Kurów Jewish civil-register inventory','Polish State Archives collection 35/1751/0. Official detailed inventory omits 1916. Original annual marriage indexes 1934-1939 examined without a target match; this is a bounded index result.','https://www.szukajwarchiwach.gov.pl/zespol/-/zespol/4488'),
('W19','Survivor-list leads for the Edelstein comparison','CRARG search-index transcriptions suggest Kajla and Mordka name/date links. Referenced originals were not all inspected. Greetings and matching dates do not establish parents or a common ancestor.','https://www.crarg.org/holocaust-records/edelsztajn-opoczno-radomsko'),
('W20','Polish refugees in Sweden finding aid','American Jewish Archives MS-361, D56/5: undated Polish-refugee lists, 1945-1946. Official finding aid inspected; the cited manuscript rows remain unviewed.','https://collections.americanjewisharchives.org/ms/ms0361/ms0361d.html'),
('W21','Rosamond Selma Garson Social Security index','Index records Garson and Simon names, birth 6 January 1926 in Cleveland, death January 1983, and parents Victor Garson and Pearl Adelstein. Indexed evidence; no original application.','https://www.familysearch.org/ark:/61903/1:1:6KSR-H9KL?lang=en'),
('W22','Victor’s 1917 draft registration','Original inspected: 5 June 1917, Paris birth 30 May 1895, a wife as dependent. No parent names or earlier surname. Corroborative, without a new ancestral link.','https://www.familysearch.org/ark:/61903/3:1:33SQ-G1DH-Q4M'),
('W24','Mordka in the 1945 survivor list','Sharit Ha P’Latah, Bergen-Belsen, volume I, 1945, printed page 9 (PDF page 19). Original inspected: Edelsztajn, Mordka; 2.2.16; Kurow. Foreword dated 7 September 1945; inclusion does not supply a camp itinerary.','https://www.infocenters.co.il/massuah/multimedia/Docs/pdf/disk20070109/26956.pdf'),
('W25','Mordka Ejdelsztejn Arolsen catalogue case','Catalogue metadata identifies tracing and documentation case 331.509, born 02.02.1916, subcollection 6.3.3.2, nine documents. The case documents were not inspected; no parents or additional biography can be inferred.','https://collections.arolsen-archives.org/en/search/?s=Mordka+Ejdelsztejn'),
('W23','Zion Memorial Park burial register','Victor Garson interred 14 August 1978, section Z4, row 1, grave 97. Register inspected; no parents or birth/death dates supplied. Interment is not the death date.','https://cemeteryregister.com/searchJF.asp?id=OH_JCLEVELAND')]

sources.extend([
('W26','Rose Adelstein and Sam Alliance marriage','Original marriage, 16 January 1906, application 45321, page 331, DGS 004016962 image 212. Rose’s father Sam Adelstein; mother’s explicitly designated maiden name Rebecca Escowitch.','https://www.familysearch.org/ark:/61903/3:1:939K-BPTV-G'),
('W27','Isidor Adelstein and Edward Allen alias card','Original VA Master Index card, image 2752 of 8000. Types Adelstein Isidor and Allen Edward; birth 9 June 1895, enlistment 28 April 1918, discharge 18 October 1919. Only relevant name/date bands reproduced.','https://www.familysearch.org/ark:/61903/3:1:3Q9M-CS1C-HWK7-W'),
('W28','Edward B Allen and Annette B Harris marriage','Original certified abstract, state 33137, application A236615, image 1892. Ceremony 28 August 1952; license 14 August; certification 3 September. Father literal Samuel; mother literal Rebecca Adelstein.','https://www.familysearch.org/ark:/61903/3:1:33S7-9162-BH1'),
('W29','Rose Karr formerly Rose Alliance','Cleveland Public Library necrology transcription, record 569015; Plain Dealer, 26 March 1970, reel 122. Explicit former name Rose Alliance; daughter Ruth Davidson, one sister and five brothers. Newspaper facsimile not obtained.','https://cpl.org/newsindex/showrecord/?record=569015&type=necrology')])
sources.append(('W30','Victor Social Security application search','Authenticated FamilySearch NUMIDENT queries for Victor Garson, Gershanovitz and Gerschenowitz produced no defensible match to his own application. This bounded search does not establish absence. Daughter records remain indexed corroboration only.','https://www.familysearch.org/en/search/collection/5000016'))
sources.sort(key=lambda x:int(x[0][1:]))
for pi,group in enumerate([sources[:8],sources[8:16],sources[16:24],sources[24:]]):
    B.begin(224+pi,'Sources for the new records',section='SOURCE NOTES')
    B.sub('Originals, indexes and leads kept distinct')
    y=157
    for code,title,desc,url in group:
        y=B.para(code+'  '+escape(title),y,size=12.5,leading=15,font='CharterBold')+4
        y=B.para(escape(desc),y,size=9.5,leading=12.7)+3
        if url:
            display=('FamilySearch · '+url.split('/ark:/61903/')[-1].split('?')[0]) if 'familysearch' in url else ('Open original source · '+re.sub(r'^https?://','',url).split('/')[0])
            y=B.para('<link href="'+escape(url,{'"':'&quot;'})+'" color="#845B44">'+escape(display)+'</link>',y,size=8.4,leading=10.5,font='OpenSansLight')+6
        else:y+=12

B.begin(228,'Index to the new evidence',section='NEW RECORDS')
B.sub('Page references for this research update')
new_index=[
('Adelstein, Pearl','207, 211-217'),('Adelstein, Sam','207, 211, 213, 216'),('Allen, Edward / Isidor Adelstein','215'),('Allen, Harry','212, 216-217'),('Allen, Louis','216-217'),('Alliance, Rose / Rose Karr','212-214, 216'),('Edelstein, Karola Faige','222'),('Edelstein, Marcus','221-223'),('Ejdelsztejn, Mordka','221-223'),('Escowitch, Rebecca','211, 213, 215-216'),('Faigenbaum, Josef','222'),('Friedman, Shifra','222'),('Garson, Victor','207-210, 217-220, 223'),('Gershanovitz, Victor','208-210'),('Gerschenowitz passengers','219'),('Grenberg census candidate','220'),('Paris birth candidate','218'),('Pelesky household','220'),('Rachael, Victor’s mother','207'),('Solomon, Victor’s father','207')]

y=172
for name,refs in new_index:
    B.text(name,B.left,y,12)
    B.c.setFillColor(HexColor(MUTED));B.c.setFont('OpenSansLight',10)
    B.c.drawRightString(B.left+486,792-y,refs);y+=24
B.cap('The main name index follows. Its references continue to point to the complete family register. Candidate entries above identify research pages, not additions to the confirmed genealogy.',y+8)
B.finish()
(OUT/'supplement-outline.json').write_text(json.dumps(B.pages,indent=2))
(ROOT/'sources-catalogue.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2))
print('SUPPLEMENT',len(B.pages),'pages')

# Export plain text of the new work for a reviewable, current source package.
sd=fitz.open(OUT/'research-supplement.pdf')
(OUT/'new-records-manuscript.txt').write_text('\n\n'.join(f'PAGE {205+i}\n'+p.get_text() for i,p in enumerate(sd)))
for i,p in enumerate(sd):p.get_pixmap(matrix=fitz.Matrix(1.35,1.35)).save(OUT/f'new-{205+i:03}.png')
print('Draft supplement rendered')
