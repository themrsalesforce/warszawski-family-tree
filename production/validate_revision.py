"""Coverage, geometry, navigation, renderer and asset checks for revised edition."""
from pathlib import Path
import collections, hashlib, json, re, subprocess
import pymupdf as fitz
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/pdf';QA=ROOT/'analysis/rebuild-2026-10-02'
CACHE=ROOT/'.analysis-cache/revision-proof';CACHE.mkdir(parents=True,exist_ok=True)
pageinfo=json.loads((QA/'pagination.json').read_text());positions=pageinfo['positions']
reg=json.loads((ROOT/'production/data/register.json').read_text());hh=json.loads((ROOT/'production/data/households.json').read_text())
sourcecross=json.loads((ROOT/'production/data/source-crosswalk.json').read_text())
tree=json.loads((ROOT/'production/data/working-tree-v1.19.json').read_text())
read=fitz.open(OUT/'The-Warszawskis-Revised-2026-10-02-Reading.pdf');printing=fitz.open(OUT/'The-Warszawskis-Revised-2026-10-02-Print.pdf')
assert len(read)==len(printing)==pageinfo['page_count']
expected_contents=[row[2]-1 for row in pageinfo['toc'] if row[0]==1]
assert [link['page'] for link in read[2].get_links()]==expected_contents, 'Contents contains stale or duplicate hotspots'
assert [link['page'] for link in printing[2].get_links()]==expected_contents
assert len(json.loads((ROOT/'production/data/graph-register-map.json').read_text()))==61
assert all(row['register_ids'] for row in json.loads((ROOT/'production/data/graph-register-map.json').read_text()))
normalize=lambda t:re.sub(r'\s+','',t).replace('\u2013','-').replace('\u2014','-')
coverage=[]
for r in reg+hh:
    n=positions[r['id']]['page'];t=read[n-1].get_text()
    found=normalize(r['name']) in normalize(t)
    coverage.append({'id':r['id'],'name':r['name'],'final_page':n,'baseline_page':r['baseline_page'],'heading_present':found})
assert all(x['heading_present'] for x in coverage)
duplicateids={}
for group in ['persons','open_questions','research_leads']:
    c=collections.Counter(x['id'] for x in tree[group]);duplicateids[group]=[k for k,v in c.items() if v>1]
assert not any(duplicateids.values())
idx=json.loads((QA/'name-index.json').read_text())
assert next(x for x in idx if x.get('register_id')=='P058')['pages'][0]==57
assert all(194 in next(x for x in idx if x.get('register_id')==pid)['pages'] for pid in ['P058','P059','P060'])
assert 53 not in next(x for x in idx if x.get('register_id')=='P027')['pages']
assert 34 not in next(x for x in idx if x.get('register_id')=='P058')['pages']
for pid,needed in {'P003':[15,16,24,57,194],'P027':[6,8,9,56],'P002':[6,10,55],'P035':[28,30,180]}.items():
    refs=next(x for x in idx if x.get('register_id')==pid)['pages'];assert set(needed).issubset(refs),(pid,refs)
badlinks=[];bounds=[];images=[];textdiff=[];overlaps=[]
for i,p in enumerate(read):
    if normalize(p.get_text())!=normalize(printing[i].get_text()):textdiff.append(i+1)
    for l in p.get_links():
        if l['kind']==fitz.LINK_GOTO and not 0<=l.get('page',-1)<len(read):badlinks.append({'page':i+1,'target':l.get('page')})
    spans=[s for b in p.get_text('dict')['blocks'] if b['type']==0 for line in b['lines'] for s in line['spans'] if s['text'].strip()]
    for s in spans:
        r=fitz.Rect(s['bbox'])
        if r.x0<0 or r.y0<0 or r.x1>p.rect.width+.1 or r.y1>p.rect.height+.1:bounds.append({'page':i+1,'text':s['text'],'bbox':list(r)})
    for j,a in enumerate(spans):
        for b in spans[j+1:]:
            ra,rb=fitz.Rect(a['bbox']),fitz.Rect(b['bbox']);x=ra&rb
            if x.width>8 and x.height>min(ra.height,rb.height)*.7:overlaps.append({'page':i+1,'a':a['text'],'b':b['text'],'bbox':list(x)})
    for k,img in enumerate(printing[i].get_image_info()):
        r=fitz.Rect(img['bbox']);dpi=min(img['width']/r.width*72,img['height']/r.height*72) if r.width and r.height else 0
        credit=next((x['text'] for x in json.loads((ROOT/'production/data/story-notes.json').read_text()) if re.search(r'Reading pages?\s+.*?\b'+str(i+1)+r'\b',x['text'])),None) if i<99 else 'Source facsimile retained from current 236-page edition; source catalogue and source package carry locators.'
        images.append({'page':i+1,'placement':k+1,'pixels':[img['width'],img['height']],'bbox':list(r),'effective_dpi':round(dpi,1),'credit_note':credit,'permission_status':'JEM license unresolved' if i+1 in [48,49] else 'Existing private-review reproduction; no new permission inferred','quality_status':'below 130 dpi at this placement' if dpi<130 and r.width>150 and r.height>150 else 'measured; physical proof remains outstanding'})
    pix=p.get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False);pix.save(CACHE/f'reading-{i+1:03}.png')
    pp=printing[i].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False);pp.save(CACHE/f'print-{i+1:03}.png')
assert not badlinks and not bounds,(badlinks,bounds)
# Fonts are checked by independent Poppler rather than inferred from one renderer.
fontresults={}
for kind in ['Reading','Print']:
    p=OUT/f'The-Warszawskis-Revised-2026-10-02-{kind}.pdf'
    r=subprocess.run(['pdffonts',str(p)],capture_output=True,text=True,check=True)
    missing=[line for line in r.stdout.splitlines()[2:] if re.search(r'\bno\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$',line)]
    assert not missing,(kind,missing)
    fontresults[kind]={'all_fonts_embedded':True,'font_rows':len(r.stdout.splitlines())-2,'poppler_output':r.stdout}
# Contact sheets contain every page; high resolution individual pages are retained.
for start in range(0,len(read),12):
    sheet=Image.new('RGB',(3*390,4*520),'#dadada');draw=ImageDraw.Draw(sheet)
    for j in range(min(12,len(read)-start)):
        p=start+j;im=Image.open(CACHE/f'reading-{p+1:03}.png');im.thumbnail((374,484));x=(j%3)*390+8;y=(j//3)*520+28;sheet.paste(im,(x,y));draw.text((x,y-20),f'Revised page {p+1}',fill='black')
    sheet.save(CACHE/f'contact-{start+1:03}-{min(start+12,len(read)):03}.jpg',quality=92)
report={'page_count':len(read),'baseline_pages':236,'reduction':236-len(read),'register_entries':len(reg),'household_entries':len(hh),'graph_nodes':len(tree['persons']),'coverage_pass':True,'contents_targets':expected_contents,'contents_hotspots_exact':True,'duplicate_ids':duplicateids,'bad_links':badlinks,'out_of_page_text':bounds,'reading_print_text_difference_pages':textdiff,'overlap_candidates':overlaps,'fonts':fontresults,'rendered_reading_pages':len(read),'rendered_print_pages':len(printing),'physical_printer_proof':'Not performed','source_permissions':'Unresolved where indicated; this is a private family review edition','precise_Ilana_birth_field':'Deliberately blank pending owner review'}
(QA/'coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n');(QA/'asset-credit-permission-checklist.json').write_text(json.dumps(images,ensure_ascii=False,indent=2)+'\n');(QA/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['fonts','overlap_candidates']}));print('Overlap candidates',len(overlaps))
