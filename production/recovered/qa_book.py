from pathlib import Path
import fitz,json,re,subprocess,hashlib
R=Path(__file__).parent;D=R/'draft';B=R/'baseline'
N=24
changed={2,3,4,180,26,27,58,63,64,66,95,110,111,112,141,142,143,155,*range(205,213)}
names=['The-Warszawskis-Coffee-Table-Edition-2026-10-01-Reading-Copy.pdf','The-Warszawskis-Coffee-Table-Edition-2026-10-01-Print-Interior.pdf']
reports=[]
for name in names:
 old=fitz.open(B/name);d=fitz.open(D/name)
 assert len(d)==212+N
 assert len(d)%2==0
 off=9 if 'Print' in name else 0
 texts=[p.get_text() for p in d];alltext='\n'.join(texts)
 assert not re.search('skydiv|whether he jumped|talked about jumping',alltext,re.I)
 assert not re.search(r'\b\d{3}-\d{2}-\d{4}\b',alltext)
 assert 'Solomon Garson' not in alltext and 'Rachael Garson' not in alltext
 assert 'Private family edition • 2 October 2026' in texts[3]
 assert 'gathered through 2 October 2026' in texts[3]
 assert 'The original 131-source catalogue' in texts[179]
 assert 'Escowitch' in texts[110] and 'strong combined maiden-name' in texts[110]
 assert '20 November 1924' in alltext and '26 November' in alltext
 assert 'Maimi is fifth; Dassi is youngest.' in alltext
 assert 'No spouse or children are recorded in the supplied family roster' in texts[103]
 assert 'he had a thing' not in texts[40]
 assert len(d[40].get_image_info())==3 and len(d[42].get_image_info())==1
 for i in range(1,d.xref_length()):
  if d.xref_is_stream(i):assert b'skydiv' not in d.xref_stream(i).lower(),(name,i)
 untouched=[]
 for oldn in range(1,213):
  ni=oldn-1+(N if oldn>=205 else 0)
  assert old[oldn-1].mediabox==d[ni].mediabox
  assert old[oldn-1].trimbox==d[ni].trimbox
  if oldn in changed:continue
  assert old[oldn-1].get_text()==d[ni].get_text(),(name,oldn,'changed text')
  a=old[oldn-1].get_pixmap(matrix=fitz.Matrix(.8,.8));b=d[ni].get_pixmap(matrix=fitz.Matrix(.8,.8))
  assert a.samples==b.samples,(name,oldn,'changed pixels')
  untouched.append(oldn)
 assert len(untouched)==186
 # Every numbered page carries its correct displayed footer, including the moved index.
 for i in range(1,len(d)):
  spans=[s for b in d[i].get_text('dict')['blocks'] if b['type']==0 for l in b['lines'] for s in l['spans']]
  footer=[s['text'] for s in spans if s['origin'][1]>740+off and s['text'].isdigit()]
  assert str(i+1) in footer,(name,i+1,footer)
  for s in spans:
   assert s['bbox'][0]>=-1 and s['bbox'][2]<=d[i].rect.width+1,(name,i+1,'horizontal overflow',s['text'])
   assert s['font'],(name,i+1,'unknown font')
 toc=d.get_toc()
 assert any(t=='New records and research' and p==205 for level,t,p in toc)
 assert any(t=='Name index' and p==229 for level,t,p in toc)
 assert all(1<=p<=len(d) for level,t,p in toc)
 toc_links=d[2].get_links()
 assert len(toc_links)==15
 assert [x['page']+1 for x in toc_links if x['kind']==1][-2:]==[205,229]
 assert len(d[227].get_links())==20
 for i,p in enumerate(d):
  for link in p.get_links():
   if link['kind']==fitz.LINK_GOTO:assert 0<=link['page']<len(d),(i,link)
 ff=subprocess.run(['pdffonts',str(D/name)],capture_output=True,text=True)
 assert ff.returncode==0 and not ff.stderr,ff.stderr
 for line in ff.stdout.splitlines()[2:]:
  assert re.search(r'\byes\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$',line),line
 report={'file':name,'pages':len(d),'unchanged_old_pages_pixel_verified':len(untouched),'new_pages':N,'changed_original_pages':sorted(changed),'photo_pages_unchanged':[41,43],'navigation_pass':True,'all_fonts_embedded':True,'font_warnings':0,'text_and_stream_removal_checks':True,'sha256':hashlib.sha256((D/name).read_bytes()).hexdigest()}
 reports.append(report)
print(json.dumps(reports,indent=2));(D/'qa-results.json').write_text(json.dumps(reports,indent=2))
