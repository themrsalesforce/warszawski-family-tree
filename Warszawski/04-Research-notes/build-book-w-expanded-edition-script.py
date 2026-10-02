#!/usr/bin/env python3
# The Warszawskis - expanded family edition. Published-biography voice.
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import os, sys

W, H = letter
IMG = "/tmp/book/img"
DL = "/downloads/"

INK = HexColor("#1a1a18")
PAPER = HexColor("#faf7f2")
CREAM = HexColor("#f3ede2")
SAGE = HexColor("#4a7a6a")
GOLD = HexColor("#9a7b3f")
GREY = HexColor("#6b6b66")
FAINT = HexColor("#e4dccb")

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/book/warsz-pass1.pdf"
c = canvas.Canvas(OUT, pagesize=letter)
c.setTitle("The Warszawskis - A Family History (September 2026)")

TOC = []          # (depth, title, page) collected during the build
RECORD = ("--toc--" not in sys.argv[1])

def bg(color=PAPER):
    c.setFillColor(color); c.rect(0, 0, W, H, stroke=0, fill=1); c.setFillColor(INK)

def footer(n):
    c.setFont("Times-Roman", 9); c.setFillColor(GREY)
    c.drawCentredString(W/2, 26, str(n))
    c.setFont("Helvetica", 6.5)
    c.drawCentredString(W/2, 15, "T H E   W A R S Z A W S K I S")
    c.setFillColor(INK)

def wrap(text, font, size, width):
    words = text.split(); lines = []; cur = ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if c.stringWidth(t, font, size) <= width: cur = t
        else:
            if cur: lines.append(cur)
            cur = w_
    if cur: lines.append(cur)
    return lines

def kicker(x, y, text, color=GOLD):
    c.setFont("Helvetica-Bold", 8.5); c.setFillColor(color)
    c.drawString(x, y, text.upper()); c.setFillColor(INK)

def title(x, y, text, size=26, font="Times-Bold", color=INK):
    c.setFont(font, size); c.setFillColor(color); c.drawString(x, y, text); c.setFillColor(INK)

def subtitle(x, y, text, size=12):
    c.setFont("Times-Italic", size); c.setFillColor(GREY); c.drawString(x, y, text); c.setFillColor(INK)

def body(x, y, text, width, size=10.5, leading=15.5, font="Times-Roman"):
    for para in text.strip().split("\n\n"):
        for line in wrap(para, font, size, width):
            c.setFont(font, size); c.setFillColor(INK)
            c.drawString(x, y, line); y -= leading
        y -= leading * 0.55
    return y

def quoteblock(x, y, text, width, size=11, leading=16):
    c.setStrokeColor(GOLD); c.setLineWidth(2)
    c.line(x, y+6, x, y - leading*len(wrap(text, "Times-Italic", size, width-18)) - 8)
    return body(x+16, y, text, width-18, size, leading, font="Times-Italic")

def pic(path, x, y, maxw, maxh, caption=None, capsize=8.5, center=True):
    im = Image.open(path); iw, ih = im.size
    scale = min(maxw/iw, maxh/ih); dw, dh = iw*scale, ih*scale
    dx = x + (maxw-dw)/2 if center else x
    c.drawImage(ImageReader(path), dx, y-dh, dw, dh, preserveAspectRatio=True)
    if caption:
        c.setFont("Times-Italic", capsize); c.setFillColor(GREY)
        cy = y-dh-13
        for line in wrap(caption, "Times-Italic", capsize, maxw):
            c.drawCentredString(x+maxw/2, cy, line) if center else c.drawString(x, cy, line)
            cy -= capsize+3
        c.setFillColor(INK)
        return cy-6
    return y-dh

def hrule(x, y, w_, color=HexColor("#d8d0c2")):
    c.setStrokeColor(color); c.setLineWidth(0.8); c.line(x, y, x+w_, y)

page = 0
def newpage(color=PAPER, folio=True, toc=None):
    global page
    if page: c.showPage()
    c.setPageSize(letter)   # size applies when THIS page is finalized
    page += 1; bg(color)
    if toc: TOC.append((toc[0], toc[1], page))
    if folio and page > 1: footer(page)
    return page

def divider(num, part, heading, lede):
    newpage(CREAM, folio=False)
    c.setFont("Times-Bold", 110); c.setFillColor(FAINT); c.drawString(50, H-170, num)
    c.setFillColor(INK)
    kicker(56, H-240, part)
    title(56, H-285, heading, size=34)
    body(56, H-330, lede, 420, 12, 18)

def chapter(kick, name, sub, text, toc_title=None):
    newpage(toc=(1, toc_title or name))
    kicker(56, H-70, kick)
    title(56, H-95, name)
    if sub: subtitle(56, H-113, sub)
    return body(56, H-145, text, 500)

# ================= 1. COVER =================
newpage(CREAM, folio=False)
c.setFont("Helvetica-Bold", 10); c.drawCentredString(W/2, H-70, "A  F A M I L Y   H I S T O R Y")
c.setStrokeColor(GOLD); c.setLineWidth(1.2); c.line(150, H-92, W-150, H-92)
c.setFont("Times-Bold", 46); c.drawCentredString(W/2, H-155, "The Warszawskis")
c.setFont("Times-Italic", 14.5); c.setFillColor(GREY)
c.drawCentredString(W/2, H-184, "Warsaw and Babruysk, Paris and Subcarpathia,")
c.drawCentredString(W/2, H-203, "and a household in Cleveland")
c.setFillColor(INK)
c.setFont("Times-Bold", 19); c.setFillColor(GOLD)
c.drawCentredString(W/2, H-330, "Warszawski  ·  Zelkind  ·  Kogen")
c.drawCentredString(W/2, H-362, "Hersh  ·  Garson")
c.setStrokeColor(GOLD); c.setLineWidth(0.8); c.line(216, H-388, W-216, H-388)
c.setFillColor(INK); c.setFont("Times-Roman", 12)
c.drawCentredString(W/2, 120, "Assembled for the family")
c.setFont("Times-Roman", 12); c.drawCentredString(W/2, 104, "September 2026")

# ================= 2. TITLE PAGE =================
newpage(folio=False)
c.setFont("Times-Bold", 30); c.drawCentredString(W/2, H-260, "The Warszawskis")
c.setFont("Times-Italic", 14); c.setFillColor(GREY)
c.drawCentredString(W/2, H-288, "A family history in stories and records")
c.setStrokeColor(GOLD); c.setLineWidth(0.8); c.line(236, H-306, W-236, H-306)
c.setFillColor(INK)
c.setFont("Times-Roman", 11.5)
c.drawCentredString(W/2, 130, "First family edition")

# ================= 3. EPIGRAPH =================
newpage(folio=False)
c.setFont("Times-Italic", 15); c.setFillColor(INK)
ep = ["\u201cborn in Cleveland, Ohio on Dec. 1, 1897.", "My race is Hebrew.\u201d"]
c.drawCentredString(W/2, H-330, ep[0]); c.drawCentredString(W/2, H-354, ep[1])
c.setFont("Times-Roman", 10.5); c.setFillColor(GREY)
c.drawCentredString(W/2, H-388, "Pearl Garson, in her sworn Petition for Naturalization, January 25, 1940")
c.setFillColor(INK)

# ================= 4. A NOTE ON THE TEXT =================
newpage(toc=(0, "A note on the text"))
kicker(56, H-70, "Before the story")
title(56, H-95, "A note on the text")
body(56, H-135, """This book gathers everything the family knows about the Warszawski line - what the records show, what the stones say, and what the family remembers - told as one continuous story.

Names appear as the family uses them: Szyman is Shimon; Gabby is Ileen; Zeidy Larry is Aryeh Leib, and on his naturalization card, Arie Lawrence Hersh. Where a record and a memory differ, both are given in the telling. Where the search is still open, the chapter says so - the searching is part of this family's story too.

The photographs and documents come from the family's own archive: headstones at Zion Memorial Park in Bedford Heights, the cemetery's register, Cleveland's Jewish press, and the public naturalization files of Cuyahoga County. The original records stay in the family archive; what is printed here is for the family table.

This is a living book. Corrections, memories and photographs are always welcome - the next edition will be richer for them.""", 500, 11.5, 17)

# ================= 5. CONTENTS =================
newpage(folio=True)
kicker(56, H-70, "Contents")
title(56, H-95, "In this book")
import json as _json
try:
    toc_data = _json.load(open("/tmp/book/warsz-toc.json"))
except Exception:
    toc_data = []
part_marks = [(7, "Part one - The old generations"), (25, "Part two - Cleveland"), (33, "Part three - The next generation"), (42, "The centerfold"), (43, "Afterword and records")]
cols = [(56, 214), (326, 214)]
ci = 0
x0, colw = cols[0]
y = H-140
mi = 0
for depth, t_, p_ in toc_data:
    while mi < len(part_marks) and p_ >= part_marks[mi][0]:
        if y < 150 and ci == 0:
            ci = 1; x0, colw = cols[1]; y = H-140
        y -= 8
        c.setFont("Helvetica-Bold", 10.5); c.setFillColor(INK); c.drawString(x0, y, part_marks[mi][1]); y -= 20
        mi += 1
    if y < 120 and ci == 0:
        ci = 1; x0, colw = cols[1]; y = H-140
    c.setFont("Times-Roman", 10.5); c.drawString(x0+12, y, t_)
    c.setFillColor(GREY); c.drawRightString(x0+colw, y, str(p_)); c.setFillColor(INK)
    y -= 18.5

# ================= PART I =================
divider("I", "Part one", "The old generations",
 "Survivor families, the names Hersh, Warszawski, Zelkind and Garson, and the record of lives interrupted by war and remade in Cleveland. The documents are thin where the world was cruel; what survives is printed here whole.")

# --- Ch 1 Szyman ---
chapter("Chapter one", "The tailor of Cedar-Center", "Szyman Warszawski, 1918 - 1995", """Szyman Warszawski - Shimon to his family - was born in Poland on April 1, 1918; a Social Security index gives the city as Warsaw. He lived in Russia through the Second World War, and came home to a Poland that was no longer the world he had left. In 1962 he immigrated to Cleveland with his wife Berta, and there he built the life his grandchildren would remember: for twenty-five years he owned the Mayflower Tailoring Company at Cedar-Center, a member of Kol Israel, a working man of the old school. He retired around 1988, seven years before his death.

He and Berta were married forty years. Their son Joseph - Joe - was their only child, born after the war; five grandchildren followed. A brother, Benyamin, made his life in Israel.

The records disagree about one thing, and the disagreement is worth preserving. His headstone at Zion Memorial Park gives his Hebrew name as Shimon ben Zisl - his father named Zisl. A Social Security index entry names his parents as Joseph Warszavski and Rochel Goldberg. Both are printed here, unsettled, exactly as they stand; perhaps Zisl-Joseph was one man with two names, as families often carried. What is certain is the life: Warsaw, the war years in Russia, the return, and then thirty-three years in Cleveland.

Szyman died on July 18, 1995, and was buried the next day at Zion Memorial Park, plot 6-6-111 - directly beside Mordukh Zelkind, his father-in-law, at 6-6-110. The two families had come through the century together, and in the cemetery of a city an ocean from Warsaw, they lie side by side.""")

# --- CJN facsimile ---
newpage(toc=(1, "The obituary, 1995 - facsimile"))
kicker(56, H-70, "From the Cleveland Jewish News")
title(56, H-95, "The obituary, August 18, 1995")
subtitle(56, H-113, "Cleveland Jewish News, obituaries page")
y = pic(IMG+"/szyman-cjn-obit-1995-crop.png", 56, H-150, 500, 320,
    "Szyman Warszawski's obituary as it ran in the Cleveland Jewish News, August 18, 1995.")
y = body(56, y-16, """"Szyman Warszawski, who owned Mayflower Tailoring Co. at Cedar-Center for 25 years, died on July 18. He retired seven years ago. A member of Kol Israel, he was born in Poland and lived in Russia during World War II. He immigrated to Cleveland in 1962.

Surviving Mr. Warszawski are his wife of 40 years, Berta; son, Joseph; five grandchildren; and a brother, Benyamin, in Israel.\"""", 500, 11, 16)

# --- Szyman stone ---
newpage(folio=True)
y = pic(DL+"Szyman Warszawski headstone - Zion Memorial Park - FindAGrave 273716163.jpg", 56, H-120, 500, 470,
    "Szyman Warszawski, Zion Memorial Park, Bedford Heights. \"Beloved husband, father - grandfather.\" The Hebrew line names him Shimon ben Zisl, 1918 - 1995. Photograph from the public memorial record.")

# --- Ch 2 Berta ---
chapter("Chapter two", "Berta, called Grammy", "Bila bat Mordechai, 1935 - 2016", """Berta Zelkind was born on May 15, 1935, a daughter of Mordechai and Elka Zelkind, and grew up in a world that was coming apart. She spoke in later years of where she fled from - not of where she went, how she returned, or how she met Szyman. That part of her story the family still hopes to recover.

What survives is the warmth. To the next generation she was Grammy. Szyman called her Bella, and when Shimon and Mushky Warszawski named their daughter Nechama years later, Bella became her nickname too - the name traveling down the family, as names do. A friend named Frieda, meeting Berta's grandchildren long after, cried when she realized whose family they were. "Bertha was my friend," she said. It is a small scene, and it says more about her than a date can.

Her headstone reads: Bila bat Mordechai - her father Mordechai's name, carried in stone - May 15, 1935 to November 28, 2016, niftera 27 Cheshvan 5777, "Beloved Mother, Grandmother, Great Grandmother, Sister." She was interred the next day, November 29, in section Z6, row 1, grave 58. The family keeps her yahrtzeit on 26 Cheshvan; the stone's Hebrew date reads the 27th. Both are kept here, side by side, as the family keeps them.""")

# --- Berta stone ---
newpage(folio=True)
y = pic(DL+"Berta Warszawski headstone - Zion Memorial Park - FindAGrave 273776627.jpg", 56, H-120, 500, 470,
    "Berta Warszawski, Zion Memorial Park. \"Beloved Mother, Grandmother, Great Grandmother, Sister.\" Photograph from the public memorial record.")

# --- Ch 3 Zelkinds ---
chapter("Chapter three", "The Zelkinds of Babruysk", "Mordechai and Elka, and four daughters", """Mordechai Zelkind - Mordukh - was born in 1912; Elka Kogen, his wife, was born November 12, 1913, in Babruysk, on the Berezina in what is now Belarus. A Social Security index names her parents as Isac Kaga and Tsilya Gershon. How Mordukh and Elka survived the war, and when they came to America, the record has not yet told us.

What it tells us in full is the family they raised. Mordukh's death notice in the Plain Dealer of September 25, 1996 reads: "MORDUKH ZELKIND, beloved husband of Elka (nee Kogen), devoted father of Bertha Warshawsky, Gail Zelkind, Maria Komisarchik (Isaak) and Celya Elin (Matvey), loving grandfather of Joseph Warshawsky, Dimitry and Kira Komisarchik, Inna and Boris Elin, great grandfather of seven... Interment Zion Memorial Park."

Every name in that notice is a thread. Bertha Warshawsky is Berta - Grammy - Joe's mother; the Warshawsky spelling is how the paper heard the name. Gail, Maria and Celya are Berta's sisters. And "grandson Joseph Warshawsky" is Joe himself, named in his grandfather's notice twenty-one years before his own stone would stand in the same cemetery.

Mordukh was interred on September 25, 1996, in section Z6, row 6, grave 110 - beside Szyman, his son-in-law, at 6-6-111. Elka followed him on March 14, 2005, and was interred March 16, in Z6, row 4. Her stone reads 1914 - 2005; the Social Security index gives her birth as November 12, 1913. The year stands as the stone has it, with the index noted alongside - a single year's disagreement in a life of ninety-one.

Gail Zelkind, Berta's sister, was born July 25, 1942 and died February 28, 2013. Her stone carries her portrait, a young woman smiling out of black granite - the only face of her the record holds.""", toc_title="The Zelkinds of Babruysk")

# --- Zelkind portraits ---
newpage(folio=True, toc=(1, "The portraits on the stones"))
kicker(56, H-70, "Zion Memorial Park")
title(56, H-95, "The portraits on the stones")
subtitle(56, H-113, "Ceramic portraits, as the stones carry them")
y1 = pic(IMG+"/mordukh-stone-portrait.png", 56, H-160, 240, 330, "Mordukh Zelkind, 1912 - 1996.")
y2 = pic(IMG+"/elka-stone-portrait.png", 316, H-160, 240, 330, "Elka Zelkind, 1914 - 2005.")
y = min(y1, y2)
y = body(56, y-16, """The stones at Zion Memorial Park carry ceramic portraits, the old-country custom the family brought to Cleveland: Mordukh in his jacket and tie, Elka in her dark dress and earrings. Beneath Elka's portrait the stone reads, in part, "Beloved Wife, Mother, Grandmother and Great Grandmother.\"""", 500, 10.5, 15)

# --- Gail stone ---
newpage(folio=True)
y = pic(IMG+"/gail-stone.png", 56, H-150, 500, 300,
    "Gail Zelkind, July 25, 1942 - February 28, 2013. Berta's sister, Mordukh and Elka's daughter.")
y = body(56, y-16, """Gail outlived her father by seventeen years and lies in the same cemetery. Her stone gives her simply - her name, her dates, her portrait - a daughter of the Babruysk Zelkinds who made her whole life in America.""", 500, 10.5, 15)

# --- Ch 4 Larry ---
chapter("Chapter four", "Zeidy Larry", "Arie Lawrence Hersh, 1925 - 2012", """Larry Hersh was born Aryeh Leib on June 1, 1925, in Czechoslovakia - in the family's memory, the Khust region of Subcarpathia, where the Hershkovitz families had lived for generations under names the border kept changing. He survived Auschwitz. Of seven siblings, he and his sister Judy came through; the others did not. Judy - Judith Dratler, nee Herskowitz - lived to ninety-six and died in Cleveland in 2025.

After the war his road ran through Israel: when he took his American citizenship he was recorded as a subject of Israel, and the index trail suggests he reached the United States around 1954. What Israel held for him - where he lived, whom he knew - the record has not yet yielded.

On August 11, 1961, in the U.S. District Court at Cleveland, he became an American, and the court's card settled the family name in his own hand: "Name changed as part of nat. from: ARIE - LARRY - HERSH KOVITZ" - signed Arie Lawrence Hersh. Hershkovitz, the name of the old country, became Hersh on the card that made him a citizen.

He did not spend his American years quietly. In October 1972, Cleveland's Jewish press named him a leader of the city's Jewish Survival Legion and a national board member - formerly the local coordinator of the Jewish Defense League: a survivor of Auschwitz, twenty-seven years on, standing publicly for Jewish defense in his new city. The family remembers the same man at the kitchen table - Zeidy Larry, Aryeh Leib. Both portraits are true.

His own account of the war years exists. On August 13, 1984 he sat for a Holocaust oral history - three videocassettes, now in the United States Holocaust Memorial Museum's collection, waiting to be requested. When the family brings it home, his voice will tell this chapter himself.

Larry died on January 3, 2012 and was interred the same day at Zion Memorial Park, plot Z3-1-35 - directly beside Ileen, at Z3-1-34, as they had lain side by side for three years already, and now for good.""", toc_title="Zeidy Larry")

# --- Larry card facsimile ---
newpage(toc=(1, "The naturalization card, 1961"))
kicker(56, H-70, "From the public record")
title(56, H-95, "The card that made him an American, 1961")
subtitle(56, H-113, "Naturalization card, U.S. District Court, Cleveland - certificate no. 8195469")
y = pic(IMG+"/facsimile-larry-1961-naturalization-card.png", 56, H-160, 500, 340,
    "Naturalized August 11, 1961; subject of Israel; recorded August 23, 1961. Cuyahoga County naturalization card file, form no. 600.")
y = body(56, y-16, """One card carries the whole chapter: the country he came from, the date he became an American, the name he left behind, and his own signature - Arie Lawrence Hersh.""", 500, 11, 16)

# --- name change detail ---
newpage(folio=True, toc=(1, "The name, in his own hand"))
kicker(56, H-70, "In his own hand")
title(56, H-95, "The name, settled in ink")
y = pic(DL+"hersh-card-detail-203dd1b3.png", 56, H-170, 500, 130,
    "Magnified from the card: \"Name changed as part of nat. from: ARIE - LARRY - HERSH KOVITZ\" - and below, the signature, Arie Lawrence Hersh.")
y = body(56, y-22, """The family had remembered the name as Hirsch; his sister Judy's obituary printed Herskowitz. The card ends the discussion. Whatever the border called the family - Hershkovitz in Subcarpathia, Hersh Kovitz on the clerk's card - Larry chose Hersh, signed it himself, and Hersh it has been ever since.""", 500, 11, 16)

# --- Ch 5 Ileen ---
chapter("Chapter five", "Ileen, called Gabby", "Shaina Yuda, 1933 - 2009", """Ileen Garson was born in Cleveland on July 30, 1933, the youngest of Victor and Pearl Garson's three daughters, and grew up on the east side in the years when the streetcars still ran. Her Hebrew name was Shaina Yuda; to her grandchildren she was Gabby. She married Larry Hersh - Zeidy Larry - and together they raised their family in Cleveland.

Her obituary in the Plain Dealer of May 23, 2009 keeps the whole constellation in one paragraph: "beloved wife of Lawrence; devoted mother of Suzanne Greenberg, Seth, Laurel Warszawski, Joseph and Marci Hersh; cherished grandmother of Ilana, Aliya, Shoshana, Yechiel, Moriah, Shymon, Chaya, Simcha and Hadassah Warszawski, Koby and Dylan Greenberg; dear sister of the following deceased: Rochelle Horwich and Rosamond Simon."

Laurel Warszawski is Lori - Joe's wife. The nine Warszawski grandchildren named in that notice are Joe and Lori's children, Gabby's grandchildren, each one counted. Her sisters, Rochelle and Rosamond, had gone before her.

Gabby died on May 22, 2009 - 28 Iyar 5769, the date the family keeps as her yahrtzeit - and was interred on May 24 at Zion Memorial Park, plot Z3-1-34. When Larry followed in 2012, the cemetery's register placed him in the next grave over. The two plots, Z3-1-34 and Z3-1-35, are the whole story of a marriage, told in the cemetery's own shorthand.""", toc_title="Ileen, called Gabby")

# --- Ch 6 Victor ---
chapter("Chapter six", "The Garsons of Paris", "Victor Garson, 1895 - 1978", """Victor Garson was born in Paris on May 30, 1895, the son of Solomon and Rachael Garson. In 1902 - so his wife would swear decades later - he entered the United States at New York, a boy of seven; the family had sailed from Le Havre, and almost certainly Solomon and Rachael brought him over themselves.

He grew up in Cleveland, became a bookkeeper, and on September 12, 1916 married Pearl Adelstein in Cuyahoga County. Three years later, on September 18, 1919, he stood in the U.S. District Court for the Northern District of Ohio and swore his Declaration of Intention - the first formal step toward citizenship. The clerk wrote him down: born Paris, May 30, 1895; occupation bookkeeper; last foreign residence "Pairs, France," the clerk's own misspelling of Paris; emigrated from Le Havre, the vessel unnamed. He renounced his allegiance to the French Republic. He was twenty-four, three years married, a father of four-month-old Rochelle.

The certificate itself took fifteen more years: Victor Garson was naturalized on November 20, 1934. He lived the rest of his life in Cleveland, and died in East Cleveland on August 13, 1978, five years after Pearl. They lie at Zion Memorial Park.

One page of his story was nearly misread. An early transcription of the declaration gave his last foreign residence as Metz, in Alsace-Lorraine - and for a while the search ran to Metz. A magnified reading of the original settled it: the word is "Pairs," Paris, where he was born. The correction is printed here as it belongs in a family record - plainly, and in the same ink as the mistake.""", toc_title="The Garsons of Paris")

# --- Victor facsimile ---
newpage(toc=(1, "The Declaration of Intention, 1919"))
kicker(56, H-70, "From the public record")
title(56, H-95, "The Declaration of Intention, 1919")
subtitle(56, H-113, "Declaration no. 28845, U.S. District Court, Northern District of Ohio - September 18, 1919")
y = pic(IMG+"/facsimile-victor-1919-pairs-detail.png", 56, H-160, 500, 85,
    "Magnified: emigrated from \"Havre, France\"; last foreign residence \"Pairs, France\" - the clerk's misspelling of Paris.")
y1 = pic(IMG+"/facsimile-victor-1919-declaration.png", 56, y-18, 240, 320,
    "The full declaration: born Paris, May 30, 1895; bookkeeper; renounces the French Republic.")
y2 = body(330, y-18, """He signed it seven months before his second daughter was born. The certificate would come in 1934; the intention was sworn in 1919, in a careful hand, by a young father from Paris who had already been in America seventeen years.""", 226, 10.5, 15)

# --- Ch 7 Pearl ---
chapter("Chapter seven", "An American twice over", "Pearl Adelstein Garson, 1897 - 1973", """Pearl Adelstein was born in Cleveland on December 1, 1897 - American from her first breath, in the city where she would live her whole life. Family memory had placed her birth in France, or in Latvia; her own hand settles it. On January 25, 1940, swearing her Petition for Naturalization, she wrote: "born in Cleveland, Ohio on Dec. 1, 1897. My race is Hebrew."

That an American-born woman should have to petition for citizenship at all is the story. When Pearl married Victor Garson on September 12, 1916, he was a French national - and under the Expatriation Act of 1907, an American woman's citizenship followed her husband's. By saying yes to Victor, Pearl lost the country of her birth. The Cable Act of 1922 opened the way back, and in 1940 she took it, swearing "I have not acquired any other nationality by affirmative act." Her petition was granted; certificate 73676. Cleveland-born, made foreign by marriage, American again by her own signature.

The petition is a family document in the fullest sense. It lists her three daughters with their exact dates, all born in Cleveland: Rochelle, May 9, 1919; Rosamond, January 6, 1926; Ileen, July 30, 1933. Ileen is Gabby. On one sworn page, Pearl gives us her birth, her marriage, her husband's crossing and naturalization, and the birthdays of all three girls.

Pearl died in Cleveland Heights on March 3, 1973. Her obituary names her daughters - Rosamond Simon, Ileen Hersh and Rochelle Horwich - and through Ileen the line runs on: to Lori, to Joe's house in Cleveland, and to the nine grandchildren named in Gabby's own notice thirty-six years later.""", toc_title="An American twice over")

# --- Pearl facsimile ---
newpage(toc=(1, "Pearl's petition, 1940"))
kicker(56, H-70, "From the public record")
title(56, H-95, "Pearl's petition, 1940")
subtitle(56, H-113, "Petition for Naturalization, U.S. District Court, Northern District of Ohio - certificate 73676")
y = pic(IMG+"/facsimile-pearl-1940-petition.png", 56, H-160, 500, 290,
    "In her own hand: born Cleveland, December 1, 1897; married Victor September 12, 1916; three daughters with their dates. Petition under the Cable Act, January 25, 1940.")
y = body(56, y-16, """An American-born woman petitioning to become an American - because the law of 1907 had made her French by marriage. The Cable Act gave her the path back, and she took it.""", 500, 11, 16)

# --- Ch 8 Garson question ---
chapter("Chapter eight", "The Garson question", "A marriage in Metz, 1865, and the missing link", """Where did the Garsons come from before Paris? The family's oldest documentable footprint is Victor's - Paris, 1895. Behind that, the trail thins to a surname and a region.

In Metz, in Alsace-Lorraine, the civil register records a marriage on September 1, 1865: Aron Garson to Caroline Levy. In the Metz-Chambiere cemetery the same couple lies under a second spelling - "Gerson Aron, 1841-1924" and "Levy Caroline Gerson, c.1845-1909." A rare surname, one region, two spellings - and in Cleveland, Victor's marriage record names his father as Solomon.

If a Solomon Garson - or Gerson - was born to Aron and Caroline in Metz in the years after 1865, the line from Metz to Paris to Cleveland would close into a single thread. That record has not yet been found; the French civil registers and the Moselle archives hold the answer, and the search is mapped and waiting. A "Guerchen, Abraham Gershon" who died at Hellimer in 1855 may belong to an earlier generation still.

And there is one more archive to exhaust: a hundred and thirty-three manifests in the Ellis Island records carry the name Garson between 1892 and 1924. Somewhere in that stack should be the Le Havre sailing of 1902 - Solomon, Rachael, and a seven-year-old boy named Victor.""", toc_title="The Garson question")


# --- Paris interlude: Julia's children ---
chapter("From the Archives de Paris", "Julia's children", "Two more Garsons of the 18th arrondissement, 1895 - 1898", """The registers of the 18th arrondissement hold two more Garsons, and they hold them close. On November 4, 1895 - five months after Victor's birth across the same city - a young domestic named Julia Maria Garson, eighteen years old, bore a son, Marcel Eugene Jules, at a midwife's home in the 18th. No father is named on the act; the boy carried his mother's name. Two and a half years later, in March 1898, the registers record Charlotte, born to Julia Garson, now twenty-two, at another midwife's rooms in the same arrondissement. Again, no father is named.

The ages agree with each other. The arrondissement is the same, the surname is rare, and both children came into the world at midwives' homes. The acts are printed here as one woman's story - Julia Maria Garson, born about 1877 - and the family may yet prove that she belongs to Solomon's generation of Garsons. If she was his sister, then Marcel and Charlotte were Victor's first cousins, growing up in Paris while he crossed the ocean.

Marcel's act carries one more line, written long after. In the margin, a later hand recorded his death on February 21, 1963 - a Paris life of sixty-seven years, ending a few streets from where it began. What became of Charlotte, the registers have not yet said.""", toc_title="Julia's children")

# --- Marcel act facsimile ---
newpage(toc=(1, "Marcel's birth act - facsimile"))
kicker(56, H-70, "From the Archives de Paris")
title(56, H-95, "Marcel's birth act, 1895")
subtitle(56, H-113, "Acte de naissance N\u00b0 5097, Paris 18e - Archives de Paris, V4E 10322")
y = pic(DL+"garson-act5097-18e-1895-64915984.jpg", 56, H-140, 500, 430,
    "Act N\u00b0 5097, November 4, 1895: 'Fils de Julia Maria Garson, agee de dix-huit ans... et de pere non denomme.' The margin carries his death notation of February 21, 1963.")
y = body(56, y-16, """Born at nine in the morning at the home of the declarant, the midwife Desiree Dreux, who had assisted at the birth; the witnesses a glove-cutter and a wine merchant of the neighboring streets. A working quarter of Paris, at a working hour.""", 500, 11, 16)

# --- Charlotte act facsimile ---
newpage(toc=(1, "Charlotte's birth act - facsimile"))
kicker(56, H-70, "From the Archives de Paris")
title(56, H-95, "Charlotte's birth act, 1898")
subtitle(56, H-113, "Acte de naissance N\u00b0 1182, Paris 18e - Archives de Paris, V4E 10385, feuillet 66")
y = pic(DL+"garson-act1182-18e-1898-aa375edb.jpg", 56, H-140, 500, 430,
    "Act N\u00b0 1182: born March 4, 1898, at five in the morning; declared on the seventh, the date under which the decennial table indexes her. Mother Julia Garson, twenty-two; father not named.")
y = body(56, y-16, """The midwife this time is Virginie Brice; the witnesses a housekeeper and a concierge of the quarter. Two women of the neighborhood, signing beside a mother who signed alone.""", 500, 11, 16)

# ================= PART II =================
divider("II", "Part two", "Cleveland",
 "Joe Warszawski was born in postwar Poland and raised in Cleveland, and the family's American life is his life: school, work, marriage, nine children, and a house that remembered him in gestures before it remembered him in dates.")

# --- Ch 9 Zion ---
chapter("Chapter nine", "Zion Memorial Park", "The cemetery that holds them all", """One cemetery in Bedford Heights holds the whole Cleveland story of this family. At Zion Memorial Park lie Szyman and Berta; Mordukh and Elka and their daughter Gail; Larry and Ileen; Victor and Pearl; and Joe himself. The cemetery's own register keeps the interments in its plain clerk's hand - BERTHA Warszawski, November 29, 2016, Z6 row 1 grave 58; MORDUKH Zelkind, September 25, 1996, Z6 row 6 grave 110; ELKA Zelkind, March 16, 2005; LAWRENCE Hersh, January 3, 2012, Z3 row 1 grave 35; ILEEN Hersh, May 24, 2009, Z3 row 1 grave 34.

Read closely, the register tells its own small truths. Larry and Ileen lie in adjacent graves, the marriage continuing in the plot numbers. Mordukh lies beside Szyman - father-in-law and son-in-law, the Zelkinds and the Warszawskis together in death as they had been in life.

And the register has one eloquent silence. Joe's stone stands photographed at Zion - yet the cemetery's online register carries no entry for him at all. A gap in the database, not a doubt about the ground: a reminder, worth keeping, that absence from a list is not absence from the world.""", toc_title="Zion Memorial Park")

# --- register facsimile ---
newpage(toc=(1, "The cemetery register - facsimile"))
kicker(56, H-70, "From the public record")
title(56, H-95, "The cemetery's own register")
subtitle(56, H-113, "Zion Memorial Park, interment listings")
y = pic(IMG+"/zion-hersh-register.png", 56, H-160, 500, 250,
    "The Hersh listings: ILEEN, interred May 24, 2009, Z3-1-34; LAWRENCE, January 3, 2012, Z3-1-35 - adjacent graves. The second Lawrence line is the cemetery's own reservation marker, not a second burial.")
y = pic(IMG+"/zion-warszawski-register.png", 56, y-24, 500, 40,
    "The Warszawski listing: BERTHA, interred November 29, 2016, Z6-1-58. Joe's name does not appear - a register gap, noted by the cemetery's own records, beside his photographed stone.")

# --- Ch 10 Joe childhood ---
chapter("Chapter ten", "A postwar childhood", "Joe Warszawski, born October 19, 1959", """Joe Warszawski - Joseph Sam, Yosef Yitzchak ben Shimon - was born on October 19, 1959, in Poland, into the after-silence of the war. The family remembers the country but not the city; the record has not yet supplied it. His father had been born in Warsaw and lived through the war in Russia; his mother had fled from somewhere she would only ever describe as the place she fled from. Three years after Joe was born, the family carried him to Cleveland, and Poland became the old country.

He grew up on the east side. A notice in the Cleveland Jewish News of October 13, 1972 announced his bar mitzvah for the next morning at Sinai Synagogue - a boy of the Heights, stepping up to the Torah the week he turned thirteen. He went on to Cleveland Heights High School, class of 1978, where the school's memorial page today keeps his name and his dates.

Of those years the family keeps the texture rather than the chronology: a household with one child at its center, Szyman at the tailoring shop at Cedar-Center, Berta - Bella - at the heart of the home.""", toc_title="A postwar childhood")

# --- Ch 11 Joe & Lori ---
chapter("Chapter eleven", "Joe and Lori", "Cleveland, 1986", """The Cleveland Jewish News of 1986 carried the announcement: the engagement of Laurel Ruth Hersh to Joseph Warszawski.

Laurel Ruth - Lori, Leah Rochel - was Gabby and Larry's daughter, an Ursuline College graduate working as a registered nurse at Rainbow Babies and Children's Hospital. Joe was attending Cleveland State University and working as a technical adviser at ProSearch of Medina. The notice joined two Cleveland survivor families - Hersh of Subcarpathia by way of Auschwitz and Israel, Warszawski of Warsaw by way of Russia - into one household.

They married and built the house the family remembers: Cleveland, nine children, and the ordinary heroics of a big Jewish family. Lori's work among Cleveland's children and Joe's long days framed the household; the chapters the children remember best are the small ones, and the family remembers them in the next pages.""", toc_title="Joe and Lori")

# --- Ch 12 memories ---
chapter("Chapter twelve", "What a household remembers", "The early market, Purim, and a thing for skydiving", """A daughter remembers that Joe woke very early to go to the market. It is one line, and it holds a whole life: the father up before the house, out the door in the dark, doing the day's work before the day began. Which market, and what he brought home, the interview has yet to be done - the family will tell it, and this book will grow by a page.

Another memory has music in it. On Purim, people from Telshe yeshiva would come to dance with Abba. The year is not fixed and the room is not named, but the scene is unmistakable - the students spilling in, the dancing, the house loud with it. It is the kind of detail a pedigree never holds, and a family never loses.

And one remark stands waiting for its explanation: he had a thing for skydiving. Whether he jumped, watched, or only talked about jumping, the children will know. The line is printed as it was given - a father's small daring, preserved by the people who loved him.""", toc_title="What a household remembers")

# --- Ch 13 Feb 2017 ---
chapter("Chapter thirteen", "February 2017", "The drive to Cleveland", """Joe Warszawski died on February 18, 2017 - 22 Shevat 5777. He was fifty-seven.

The family came to Cleveland for the levaya. A daughter remembers the drive - and remembers that her husband had just turned twenty-five, old enough to rent a car, the practical fact by which grief arranged its logistics. It is often that way in families: the journey to the funeral is itself a memory, kept with the funeral it served.

His stone at Zion Memorial Park names him in two languages: Joseph Warszawski - Yosef Yitzchak ben Shimon - October 19, 1959 to February 18, 2017, niftar 22 Shevat 5777, "Beloved Husband, Father, Grandfather." The Hebrew line settles one last fact the records had left open: his father, named in stone, is Shimon - Szyman, the tailor of Cedar-Center.

The family keeps his yahrtzeit each 22 Shevat. The grandchildren named for him carry the rest.""", toc_title="February 2017")

# --- Joe stone ---
newpage(folio=True)
y = pic(DL+"Joseph Warszawski headstone - Zion Memorial Park - FindAGrave 273775046.jpg", 56, H-120, 500, 470,
    "Joe's stone at Zion Memorial Park. Two small stones rest on the ledger, left by visitors - the old custom, still kept. Photograph from the public memorial record.")

# ================= PART III =================
divider("III", "Part three", "The next generation",
 "Joe and Lori raised nine children, and the story is still being lived. Engagements in Crown Heights, weddings at Oholei Torah, babies announced to the world - the notices pile up like a second archive, and every one of them says 'of Cleveland.'")

# --- Ch 14 roster ---
chapter("Chapter fourteen", "The nine children", "The household Joe and Lori built", """Nine children grew up in Joe and Lori's house: Ilana, Aliya, Shoshana - Shoshy, Yechiel, Shimon, Chaya Brocha, Hadassa, Simcha and Maimi. Gabby's 2009 obituary names them in a row, the whole flock, with her daughter Laurel's family around them. They grew up, as the engagement notices all say, "of Cleveland" - and then the weddings scattered them in the familiar way, to Crown Heights, to Houston, to London, and back.

The pages that follow give each of them their due - what the family reports and what the public notices recorded. Birth order the family will supply; the roster here is the family's own.""", toc_title="The nine children")

# --- Households ---
chapter("The children", "Ilana and Shmaya Marinovsky", "Married February 28, 2012", """Ilana, the eldest of the nine to marry, wed Shmaya Marinovsky on February 28, 2012. The couple made their home in Houston, where Shmaya serves as a Chabad shliach associated with Torah Day School - the family's reach now running from Cleveland to Texas.""", toc_title="Ilana and Shmaya Marinovsky")

chapter("The children", "Aliya and Shmuly Andrusier", "L'Chaim, October 2013", """Aliya's L'Chaim with Shmuly Andrusier was celebrated in October 2013 at Beis Levi Yitzchak shul in Crown Heights - the notice read "Shmuly Andrusier and Aliyah Warszaski," the paper's spelling doing its usual work on the name. Crown Heights would keep turning up in this family's notices: the neighborhood where so many of the celebrations gathered.""", toc_title="Aliya and Shmuly Andrusier")

chapter("The children", "Shoshy and Shmuel", "Engaged August 22, 2014 - married December 8, 2014", """Shoshana - Shoshy - was announced engaged to Shmuel Chaikin of Johannesburg on August 22, 2014, and they were married on December 8, 2014. Their family grew quickly: Ella, Abie and Mika.

Shoshy is the daughter through whom this book's research runs - it was her asking after the Warszawski line that set the archive digging. The family she married into carries its own long story, told in its own volume; here she stands in her parents' house, one of the nine.""", toc_title="Shoshy and Shmuel")

chapter("The children", "Shimon and Mushky Warszawski", "Engaged January 12, 2019 - married March 4, 2019", """Shimon's engagement to Mushky Chayempour of Toronto was announced on January 12, 2019, the L'Chaim held at the Lubavitch Yeshiva hall in Crown Heights, and they married on March 4, 2019. A daughter was born to them in January 2020, announced from Crown Heights - and when they named her Nechama, she became Bella, carrying Grammy Berta's name into the fourth generation.

Shimon graduated law school in May 2024 and passed the bar that October, bringing the family's Cleveland story a profession it had not held before.""", toc_title="Shimon and Mushky Warszawski")

chapter("The children", "Chaya Brocha and Dovi Katz", "Engaged January 10, 2023 - married March 12, 2023", """Chaya Brocha's engagement to Dovi Katz of Crown Heights was announced on January 10, 2023, the L'Chaim that same night at the Lubavitch Yeshiva; the wedding followed on March 12, 2023, at Oholei Torah. A daughter was announced to the couple in December 2025 - the newest name on the tree, and very nearly the newest page of this book.""", toc_title="Chaya Brocha and Dovi Katz")

chapter("The children", "Hadassa and Doni Hirsch", "Engaged November 6, 2022 - married February 2, 2023", """Hadassa Miriam - Dassi to the notices - was announced engaged to Daniel Hirsch of Coral Springs, Florida on November 6, 2022, the L'Chaim that night at Ulam Chana hall at Machon Chana. The wedding was celebrated on February 2, 2023 in the Oholei Torah ballroom - two of Joe and Lori's daughters married at Oholei Torah within six weeks of one another, a season of celebration the family still talks about.""", toc_title="Hadassa and Doni Hirsch")

chapter("The children", "Yechiel, Simcha, and Maimi", "The household continues", """Yechiel - Yechiel Yaakov - spent the years 2019 to 2023 working at the American Dream mall in New Jersey, the family's one outpost in retail's great cathedral, and is single.

Simcha - Simcha Sora Chia - went into nursing, graduating from nursing school around the end of 2023, carrying forward the work Lori did at Rainbow Babies a generation before.

Maimi, the youngest, was announced engaged to Dovid Inglis of London, England on December 28, 2018 - the family's reach extending across the Atlantic, the notices now reading "of Crown Heights" and "of London" where they once read "of Cleveland.\"""", toc_title="Yechiel, Simcha, and Maimi")

# --- wider family ---
chapter("The family around them", "The wider family", "Aunts, uncles, and the Garson sisters", """Lori's sisters and brothers are part of the household's story. Suzanne married Seth Greenberg; the family made its way from Cleveland to Alabama. Marcy never married. Ileen's obituary keeps them all in one line - Suzanne Greenberg, Seth, Laurel Warszawski, Joseph and Marci Hersh - a sentence of siblings.

On the Garson side, Gabby's two sisters were the last of their generation: Rochelle, born May 9, 1919, who married a Horwich, and Rosamond, born January 6, 1926, who married a Simon. Both had died before Gabby's own notice was written in 2009 - "dear sister of the following deceased" - the three Cleveland daughters of Victor and Pearl, born 1919, 1926 and 1933, each named on their mother's sworn petition.""", toc_title="The wider family")

# ================= CENTERFOLD =================
LW, LH = landscape(letter)
c.showPage(); page += 1
c.setPageSize((LW, LH))   # applies when the centerfold page is finalized
c.setFillColor(CREAM); c.rect(0, 0, LW, LH, stroke=0, fill=1); c.setFillColor(INK)
c.setFont("Helvetica-Bold", 8.5); c.setFillColor(GOLD)
c.drawCentredString(LW/2, LH-42, "T H E   F A M I L Y   T R E E")
c.setFont("Times-Bold", 22); c.setFillColor(INK)
c.drawCentredString(LW/2, LH-70, "Six generations, grandmother to granddaughter")
c.setFont("Times-Italic", 10.5); c.setFillColor(GREY)
c.drawCentredString(LW/2, LH-88, "Zelkind and Kogen of Babruysk, Warszawski of Warsaw, Garson of Paris, Hersh of Subcarpathia - meeting at Joe and Lori")
c.setFillColor(INK)

def box(x, y, w_, h_, name, sub, fill=HexColor("#ffffff"), edge=SAGE, namefont=("Helvetica-Bold", 8.5), subfont=("Helvetica", 6.8)):
    c.setFillColor(fill); c.setStrokeColor(edge); c.setLineWidth(1.1)
    c.roundRect(x, y, w_, h_, 5, stroke=1, fill=1)
    c.setFillColor(INK); c.setFont(*namefont)
    c.drawCentredString(x+w_/2, y+h_-14, name)
    c.setFont(*subfont); c.setFillColor(GREY)
    c.drawCentredString(x+w_/2, y+5, sub)
    c.setFillColor(INK)

def vline(x, y1, y2):
    c.setStrokeColor(GREY); c.setLineWidth(0.9); c.line(x, y1, x, y2)
def hline(x1, x2, y):
    c.setStrokeColor(GREY); c.setLineWidth(0.9); c.line(x1, y, x2, y)
def join(x1, x2, ytop, ybot):
    vline(x1, ytop, ytop-11); vline(x2, ytop, ytop-11)
    hline(x1, x2, ytop-11)
    vline((x1+x2)/2, ytop-11, ybot)

BW_, BH_, GY = 108, 34, 44
top = LH-128
# great-great-grandparents
box(140, top, BW_, BH_, "Solomon Garson", "")
box(254, top, BW_, BH_, "Rachael Garson", "")
box(430, top, BW_, BH_, "Joseph Warszavski", "per SS index")
box(544, top, BW_, BH_, "Rochel Goldberg", "per SS index")
# great-grandparents
g1 = top - GY - BH_
box(46, g1, 118, BH_, "Victor Garson", "Paris 1895 - 1978")
box(174, g1, 118, BH_, "Pearl Adelstein", "Cleveland 1897 - 1973")
box(352, g1, 118, BH_, "Mordukh Zelkind", "1912 - 1996")
box(480, g1, 118, BH_, "Elka Kogen", "Babruysk 1913 - 2005")
join(194, 308, top, g1+BH_)     # Solomon+Rachael -> Victor
join(484, 598, top, g1+BH_)     # Joseph+Rochel -> Szyman's row below (to grandparents row)
# grandparents
g2 = g1 - GY - BH_
box(46, g2, 118, BH_, "Larry Hersh", "1925 - 2012")
box(174, g2, 118, BH_, "Ileen (Gabby)", "1933 - 2009")
box(352, g2, 130, BH_, "Szyman Warszawski", "Warsaw 1918 - 1995")
box(492, g2, 118, BH_, "Berta Zelkind", "1935 - 2016")
join(105, 233, g1, g2+BH_)      # Victor+Pearl -> Ileen
join(416, 540, g1, g2+BH_)      # Mordukh+Elka -> Berta
# parents
g3 = g2 - GY - BH_
box(240, g3, 128, BH_+6, "Joe Warszawski", "1959 - 2017")
box(424, g3, 128, BH_+6, "Lori (Leah Rochel)", "nee Hersh")
join(105, 233, g2, g3+BH_+6)    # Larry+Ileen -> Lori
join(417, 551, g2, g3+BH_+6)    # Szyman+Berta -> Joe
# children row
g4 = g3 - GY - BH_
kids = ["Ilana", "Aliya", "Shoshy", "Yechiel", "Shimon", "Chaya Brocha", "Hadassa", "Simcha", "Maimi"]
kw = 64; gap = 6; total = len(kids)*kw + (len(kids)-1)*gap
startx = (LW-total)/2
centers = []
for i, nm in enumerate(kids):
    x = startx + i*(kw+gap)
    fill = INK if nm == "Shoshy" else HexColor("#ffffff")
    edge = INK if nm == "Shoshy" else SAGE
    box(x, g4, kw, 30, nm, "", fill=fill, edge=edge, namefont=("Helvetica-Bold", 7.5))
    if nm == "Shoshy":
        c.setFillColor(HexColor("#ffffff")); c.setFont("Helvetica-Bold", 7.5)
        c.drawCentredString(x+kw/2, g4+16, nm); c.setFillColor(INK)
    centers.append(x+kw/2)
join(304, 488, g3, g4+30)
vline(centers[2], g4, g4-8); 
# grandchildren under Shoshy
g5 = g4 - 34
for i, nm in enumerate(["Ella", "Abie", "Mika"]):
    box(centers[2] + (i-1)*66 - 28, g5, 56, 24, nm, "", namefont=("Helvetica-Bold", 7.5))
vline(centers[2], g4, g5+24)
c.setFont("Times-Italic", 9); c.setFillColor(GREY)
c.drawCentredString(LW/2, 40, "Positions are schematic, not birth order. The grandchildren's row grows with the family.")
c.setFont("Times-Roman", 9); c.drawCentredString(LW/2, 26, str(page))
c.setFillColor(INK)
TOC.append((0, "The family tree (centerfold)", page))

# ================= THE SEARCH CONTINUES =================
chapter("Afterword", "The search continues", "Where the record still runs ahead of the book", """A family book is never finished; this one pauses here, mid-search, on purpose.

Three threads are closest to hand. In the archive of the United States Holocaust Memorial Museum wait three videocassettes: Larry Hersh's own testimony, recorded on August 13, 1984. His war years, the loss of his siblings, the road through Israel - all of it is on that tape, in his own voice, and the family has only to request it.

In the Ellis Island records, a hundred and thirty-three manifests carry the name Garson between 1892 and 1924; among them should be the 1902 Le Havre crossing of Solomon, Rachael and seven-year-old Victor. And in the civil registers of Metz and the archives of the Moselle, a Solomon Garson born after 1865 would tie Victor's Paris to Aron Garson and Caroline Levy, married there in 1865 - the oldest link this family has yet found in Europe.

Closest to hand is Julia. Her own birth act, somewhere in the Paris registers around 1877, would name her parents - and tell the family whether Marcel and Charlotte were Victor's cousins. The sweep for Victor's own act continues across the remaining arrondissements.

Farther back still, the Kogen line of Babruysk and the Hershkovitz households of Subcarpathia - the 1828 census already holds an "Aria Herskovitz" at Felsofalu - wait for their hours in the archives. Each answer will find its page in the next edition.""", toc_title="The search continues")

# ================= RECORDS CONSULTED =================
newpage(toc=(0, "Records consulted"))
kicker(56, H-70, "Records consulted")
title(56, H-95, "Records consulted")
y = H-140
groups = [
 ("Vital and court records", """Cuyahoga County marriage record of Victor Garson and Pearl Adelstein, September 12, 1916. Declaration of Intention no. 28845, U.S. District Court, Northern District of Ohio, September 18, 1919 (Victor Garson). Petition for Naturalization, certificate 73676, January 25, 1940 (Pearl Garson, under the Cable Act). Naturalization of Victor Garson, certificate 2116415, November 20, 1934. Naturalization card, certificate 8195469, office no. 201619, August 11, 1961 (Arie Lawrence Hersh). U.S. Social Security NUMIDENT index entries for Szymon Warszawski and Elka Kagan Zelkind. Archives de Paris, etat civil: acte de naissance N\u00b0 5097, Marcel Eugene Jules Garson, Paris 18e, November 4, 1895 (V4E 10322, with margin notations of 1921 and 1963); acte de naissance N\u00b0 1182, Charlotte Garson, Paris 18e, born March 4, 1898, declared March 7, 1898 (V4E 10385, feuillet 66); table decennale, Paris 18e (D1M9 220)."""),
 ("Newspapers and notices", """Cleveland Jewish News: obituary of Szyman Warszawski, August 18, 1995; bar mitzvah notice of Joseph Warszawski, October 13, 1972; report on the Jewish Survival Legion, October 1972; engagement notice of Laurel Ruth Hersh and Joseph Warszawski, 1986; obituary of Judith Dratler, June 9, 2025. Plain Dealer: death notice of Mordukh Zelkind, September 25, 1996; obituary of Ileen G. Hersh, May 23, 2009; obituary of Pearl Garson, March 1973. Engagement, wedding and birth notices on COLlive, ChabadInfo and Anash, 2013-2025. Heights High School class of 1978 memorial page."""),
 ("Cemetery records", """Zion Memorial Park, Bedford Heights: online interment register and photographed headstones of Joseph, Szyman and Berta Warszawski (FindAGrave memorials 273775046, 273716163, 273776627); BillionGraves photographs of the Mordukh, Elka and Gail Zelkind stones; JewishGen Online Worldwide Burial Registry entries for Zion Memorial Park. Metz civil marriage register, September 1, 1865 (Aron Garson and Caroline Levy); Metz-Chambiere cemetery burials via JOWBR."""),
 ("Archives", """United States Holocaust Memorial Museum: Fortunoff collection oral history of Larry Hersh, recorded August 13, 1984 (RG-50.091.0080, three videocassettes). JewishGen Subcarpathia vital records and the 1828 property tax census. Babruysk and Bobruisk records via JewishGen."""),
 ("Family testimony", """The recollections of the family, given 2021-2026 and preserved in the family archive - the naming of Grammy Bella, the market mornings, the Purim dancing, the drive to Cleveland in February 2017, and the roster of the nine children, exactly as the family gave it."""),
]
for head, txt in groups:
    c.setFont("Times-Bold", 13); c.setFillColor(INK); c.drawString(56, y, head); y -= 20
    y = body(56, y, txt, 500, 10, 14) - 12

# ================= COLOPHON =================
newpage(folio=False)
kicker(56, H-70, "Colophon")
title(56, H-95, "About this book")
y = body(56, H-135, """The Warszawskis was assembled for the family from the records above and the family's own archive, in September 2026.

The research tree behind it - forty-two people, seventy-eight sources, every fact tied to its evidence - lives in the family archive, and the public tree site carries the same pedigree online. The original documents and photographs are preserved in the archive; the pages of this book are their telling.

Corrections, memories, photographs and documents are always welcome. This is the first family edition; the next will be richer.""", 500, 11, 16)
y -= 16
hrule(56, y, 500)
c.setFont("Helvetica", 8); c.setFillColor(GREY)
c.drawString(56, y-18, "42 people  ·  78 sources  ·  6 generations")
c.drawString(56, y-30, "Assembled September 2026.")
c.setFillColor(INK)

c.save()

import json
with open("/tmp/book/warsz-toc.json", "w") as f:
    json.dump(TOC, f)
print("written", OUT, os.path.getsize(OUT), "bytes,", page, "pages")
