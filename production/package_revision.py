"""Assemble private binary production package; no ignored originals go to Git."""
from pathlib import Path
import argparse,hashlib,json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1];ap=argparse.ArgumentParser();ap.add_argument('--zip',action='store_true');args=ap.parse_args()
PKG=ROOT/'.import-tmp/revised-package';PKG.mkdir(exist_ok=True)
def copy(src,dst):
    target=PKG/dst;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/src,target)
for n in ['Reading-Copy','Print-Interior']:
    copy('Warszawski/05-Print-editions/The-Warszawskis-Coffee-Table-Edition-2026-10-01-'+n+'.pdf','inputs/Source-236-'+('Reading' if n=='Reading-Copy' else 'Print')+'.pdf')
for p in (ROOT/'.import-tmp/production-recovery/current/Rebuild/fonts').iterdir():copy(p.relative_to(ROOT),Path('assets/fonts')/p.name)
for p in (ROOT/'.import-tmp/production-recovery/current/Rebuild/new-evidence').iterdir():copy(p.relative_to(ROOT),Path('assets/new-evidence')/p.name)
for p in (ROOT/'production').rglob('*'):
    if p.is_file() and '__pycache__' not in str(p):copy(p.relative_to(ROOT),p.relative_to(ROOT))
for name in ['HANDOFF.md','library-roundtrip-verification.json']:
    stale=PKG/'analysis/rebuild-2026-10-02'/name
    if stale.exists():stale.unlink()  # Delivery state is maintained in the repository.
for p in (ROOT/'analysis/rebuild-2026-10-02').glob('*'):
    if p.is_file() and p.name not in ['HANDOFF.md','library-roundtrip-verification.json']:copy(p.relative_to(ROOT),p.relative_to(ROOT))
for n in ['ANCESTRY-REPORT-2026-10-02.md','NEW-JUDITH-ORIGINAL.md','judith-tile-manifest.json','reassemble_judith.py']:
    copy('.import-tmp/ancestry-review/current/'+n,'assets/new-evidence/'+n)
for p in (ROOT/'.import-tmp/ancestry-review/current/judith-original-tiles').iterdir():copy(p.relative_to(ROOT),Path('assets/new-evidence/judith-original-tiles')/p.name)
copy('production/README.md','README.md')
copy('output/pdf/The-Warszawskis-Revised-2026-10-02-Editable.txt','editable/Full-Reading-Text.txt')
copy('output/pdf/Warszawski-Changes-and-Closure-2026-10-02.pdf','documentation/Changes-and-Closure.pdf')
(PKG/'verify_package.py').write_text('''from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent
m=json.loads((root/'package-manifest.json').read_text())
for f in m['files']:
 p=root/f['path'];assert p.stat().st_size==f['bytes'],p
 assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'],p
print('All',len(m['files']),'package files verified')
''')
files=[]
for p in sorted(PKG.rglob('*')):
    if p.is_file() and p.name!='package-manifest.json' and not any(x in p.parts for x in ['output','.analysis-cache','__pycache__']):files.append({'path':str(p.relative_to(PKG)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(PKG/'package-manifest.json').write_text(json.dumps({'revision_pages':json.loads((ROOT/'analysis/rebuild-2026-10-02/build-manifest.json').read_text())['page_count'],'input_pages':236,'recovered_native_layout':False,'files':files},indent=2)+'\n')
if args.zip:
 out=ROOT/'output/Warszawski-Revised-Production-2026-10-02.zip'
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(PKG.rglob('*')):
   if p.is_file() and not any(x in p.parts for x in ['output','.analysis-cache','__pycache__']):z.write(p,p.relative_to(PKG))
 print(out,out.stat().st_size,hashlib.sha256(out.read_bytes()).hexdigest())
else:print(PKG)
