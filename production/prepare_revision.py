"""Create a versioned editorial working set without modifying historical imports."""
from pathlib import Path
import collections, csv, json, re, unicodedata
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'analysis/review-2026-10-02'
OUT = ROOT / 'production/data'
OUT.mkdir(parents=True, exist_ok=True)
BASE = ROOT / 'Warszawski/05-Print-editions/The-Warszawskis-Coffee-Table-Edition-2026-10-01-Reading-Copy.pdf'
TREE = ROOT / 'Warszawski/03-Archive-records/expanded/warszawski-family-tree-v1.17/warszawski-tree.json'

def dump(name, data):
    (OUT/name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')

def clean(text):
    text = re.sub(r'(?m)^\s*[A-Z](?:\s+[A-Z]){5,}\s*$', '', text)
    text = re.sub(r'(?m)^THE WARSZAWSKIS\s*$', '', text)
    text = text.replace('Leah Hersh nee Janowitz (Larry\'s mother)', "Leah Hersh (Larry's mother; maternal surname unconfirmed)")
    return text.strip()

register = json.loads((REVIEW/'register-coverage.json').read_text())
households = json.loads((REVIEW/'household-coverage.json').read_text())
for collection, prefix in [(register,'P'), (households,'H')]:
    for i, record in enumerate(collection,1):
        record['id'] = f'{prefix}{i:03}'
        record['baseline_name'] = record['name']
        record['baseline_page'] = record.pop('page')
        record['name'] = clean(record['name'])
        record['text'] = clean(record['text'])
        record['source_ids'] = sorted(set(re.findall(r'\b[SW]\d{2,3}\b', record['text'])))

for r in register:
    n, t = r['name'], r['text']
    if n == 'Lawrence (Larry) Hersh':
        t=t.replace('Birth: 1925-06-01; Death: 2012-01-03','Birth: 1925-06-01 (1961 card; civil birth record unexamined); Death: 2012-01-03 (compiled claim; interment recorded that day)')
        t=t.replace('earlier family account gives seven siblings','family accounts preserve a differing total with inconsistent children/siblings wording; original wording needs confirmation')
        t=t.replace('his naturalization card gives 1 June','his original 1961 naturalization card gives 1 June [S039]')
    if n == 'Lori (Leah) Warszawski':
        t += '\nContemporary engagement notice: Laurel Ruth Hersh [S032]. Hirsch is retained as a reported family variant, not a separately verified legal maiden surname [S030].'
    if n == 'Ilana Marinovsky':
        t=t.replace('Married Shmaya Marinovsky on 28 February 2012.', 'Family-reported wedding to Shmaya Marinovsky on 28 February 2012 [S030, S001]; no original wedding announcement identified.')
        t += '\nOriginal birth notice: Ilana Chava, daughter of Joseph and Laurel; June 4, in the 26 August 1988 issue, printed p. 40 [S033]. The year is issue context, not a separately inspected birth certificate.'
    if n == 'Szyman (Shimon) Warszawski':
        t=t.replace('Birth: 1918-04-01', 'Birth: 1918-04-01 (index)')
        t=t.replace('Parents:', 'Parents (indexed; provisional, Zisl/Joseph conflict unresolved):',1)
    if n == 'Elka Zelkind':
        t=t.replace('Birth: 1913-11-12; Death: 2005-03-14','Birth: 1913-11-12 (index; stone 1914); Death: 2005-03-14 (index)')
        t=t.replace('Parents:', 'Parents (indexed; original record unexamined):',1)
    if n in ['Joseph Warszavski','Rochel Goldberg','Isac Kaga','Tsilya Gershon']:
        t=t.replace('Children:', 'Children (indexed parentage; provisional):',1)
        t=t.replace('Partner or spouse:', 'Co-parent named in index (marriage unconfirmed):',1)
    if n in ['Maria Komisarchik','Celya Elin','Isaak Komisarchik','Matvey Elin','Susanne Greenberg','Seth Greenberg']:
        t=t.replace('Children:', 'Children (allocation inferred from grouped notice surnames):',1)
    if n in ['Dimitry Komisarchik','Kira Komisarchik','Inna Elin','Boris Elin','Koby Greenberg','Dylan Greenberg']:
        t=t.replace('Parents:', 'Parents (allocation inferred from grouped notice surnames):',1)
    if n == 'Julia Maria Garson':t=t.replace('Birth: 1877', 'Birth: approximately 1877 (age-derived)')
    if n == 'Marius Gabriel Garson':t=t.replace('Birth: 1864', 'Birth: approximately 1864 (age-derived; not identified with Auguste)')
    if n == 'Ileen (Ilene, Gabby) Hersh':t=t.replace('Death: 2009-05-22','Death: 2009-05-22 (obituary claim; certificate unexamined)')
    if n == 'Yitzchak Reiter':
        t += '\nLa Paz, Argentina is the printed place. La Paz exists in Entre Rios; this does not independently establish his residence [S109].'
    t=t.replace('in the family edition, page','in the historical September family edition, page')
    t=t.replace('an family accounts','family accounts')
    r['text']=t
    r['source_ids']=sorted(set(re.findall(r'\b[SW]\d{2,3}\b',t)))

for r in households:
    if r['name']=='Chaya Brocha Katz and Dovi Katz':
        r['text']=r['text'].replace('Sources: S019','Sources: S024 (unnamed announcement); S030, S105 (Nesya, family roster).')
        r['text']=r['text'].replace('Baby girl announcement December 3, 2025 (very likely this couple; please confirm).','Baby girl announcement, 3 December 2025 [S024]; identification with this household and Nesya remains unconfirmed. The unnamed notice is not an additional child.')
    if r['name']=='Hadassa Miriam Hirsch and Doni Hirsch':
        r['text']=r['text'].replace("Lori's maiden name is also Hirsch.", 'Lori is Laurel Ruth Hersh in the contemporary notice; Hirsch is a reported family variant.')
        r['text']=r['text'].replace('Sources: S015','Sources: S015; S030, S105 (children); S032 (Lori name).')
    if r['name']=='Ilana Marinovsky and Shmaya Marinovsky':
        r['text'] += '\nWedding on 28 February 2012 is family-reported [S030, S001]; an original announcement remains unidentified.'
    if r['name']=='Victor Garson and Pearl (Adelstein) Garson':
        r['text']=r['text'].replace('Sources: S063','Sources: S070 (daughters and reported births); S064, S102 (later married-name notices); S063/W01 (marriage only)')
    r['source_ids']=sorted(set(re.findall(r'\b[SW]\d{2,3}\b',r['text'])))


# Newly inspected 1949 original, joined through the independently verified S103
# sibling/spouse obituary. Exact original spellings stay separate from normalization.
father="Jacob (Judith's 1949 abstract; Larry's father by sibling evidence)"
mother="Leah / Lee Yanowitz (Judith's 1949 abstract; combined sibling evidence)"
oldfather="Mr. Hersh(kovitz) of Khust (Larry's father)"
oldmother="Leah Hersh (Larry's mother; maternal surname unconfirmed)"
parent_claim="Judith's 1949 marriage abstract names her father Jacob and gives her mother's maiden name as Lee Yanowitz. Her 2025 obituary explicitly names Lawrence Hersh as her brother; together these support Larry's parental names, with Lee/Leah and Yanowitz/Janowitz variants retained. The uncle and lost sisters remain unidentified [S132, S103, S089]."
for r in register+households:
    has_parent=oldfather in r['name']+r['text'] or oldmother in r['name']+r['text']
    if has_parent:r['source_ids']=sorted(set(r['source_ids'])|{'S132','S103'})
    r['name']=r['name'].replace(oldfather,father).replace(oldmother,mother)
    r['text']=r['text'].replace(oldfather,father).replace(oldmother,mother)
    if r['id'] in ['P058','P059']:
        r['text'] += '\n'+parent_claim
    if r['id']=='P059':
        r['text']=r['text'].replace('not independently confirmed by Leah’s civil record','now supported as a maternal surname variant by Judith’s original marriage abstract, but the uncle’s identity remains unconfirmed')
    if r['id']=='P060':r['text'] += "\nOriginal 1949 abstract: bride Judith Herskovitz, age 21, born Czecho-Slovakia; father Jacob, mother's maiden name Lee Yanowitz. Wedding 20 November 1949; license 14 November; certification 22 November is not the wedding date [S132]."
    if r['id'] in ['P127','H042']:r['text'] += "\nPhilip Dratler and Judith Herskovitz in original 1949 abstract; wedding 20 November 1949, certification 22 November [S132]. Phillip/Herskowitz are later obituary spellings [S103]."
    if r['id']=='H020':r['text'] += '\n'+parent_claim
    r['source_ids']=sorted(set(r['source_ids'])|set(re.findall(r'\b[SW]\d{2,3}\b',r['text'])))

# The historical 61-node graph remains a separate representation, reconciled by
# exact identity/explicit aliases only. Extra register entries are not asserted kin.
tree=json.loads(TREE.read_text())
tree['meta']['format_version']='1.19.0-editorial'
tree['meta']['package_note']='Editorial working copy: current 183-entry register reconciled separately; historical snapshots preserved. No candidate family merged.'
tree['meta']['reviewed_at']='2026-10-02'
tree['meta']['draft_note']='See production/data/register.json, graph-register-map.json and closure-ledger.json for current coverage and unresolved identities.'
seen=set();questions=[];closed=[]
dispositions={r['original_id']:r for r in csv.DictReader((REVIEW/'question-disposition.csv').open())}
for q in tree['open_questions']:
    if q['id'] in seen:continue
    seen.add(q['id']);d=dispositions.get(q['id'],{})
    q['historical_question']=q['question'];q['review_disposition']=d.get('disposition','open')
    q['editorial_note']=d.get('reason','')
    q['question']=d.get('reason',q['question'])
    if d.get('disposition','').startswith('resolved') or d.get('disposition')=='superseded-by-new-roster':closed.append(q)
    else:questions.append(q)
tree['open_questions']=questions;tree['closed_findings']=closed
counts=collections.Counter()
for lead in tree['research_leads']:
    counts[lead['id']]+=1
    if counts[lead['id']]==2 and lead['id'] in ['lead_34','lead_35','lead_36','lead_37']:
        lead['historical_id']=lead['id'];lead['id']='lead_'+str(int(lead['id'].split('_')[1])+6)
    if lead['id']=='lead_34':lead['text']='Candidate Paris birth act 2087 is inspected; Victor Jerchonossitch born 30 May 1895, parents Israel and Rosa. Identity with Cleveland Victor remains unproved; resolve original surname and both parental conflicts [W01-W03, W08-W10, W22].'
    if lead['id']=='lead_36':lead['text']='Aline Garson and Edouard Adolphe Godenne marriage: original Paris 17e act 3605, 16 October 1920, already presented. Older 5559 locator is superseded [S083, S104].'
    if lead['id']=='lead_41':lead['text']='Three USHMM recording parts have an online access route [S089; R32]. Load-bearing names still require timestamped listening verification; captions are derivative, not a second witness.'

for p in tree['persons']:
    if p['id']=='per_solomon_garson':
        p['names']['display']='Solomon (Victor’s father)';p['names']['surname_birth']=None
        p.setdefault('notes',[]).append('The 1916 marriage names Solomon. Victor adopted Garson in 1924; neither Garson nor Gershanovitz is independently established as his father’s surname [W01-W03].')
    if p['id']=='per_rachael_garson':
        p['names']['display']='Rachael (Victor’s mother)';p['names']['surname_birth']=None
        p.setdefault('notes',[]).append('The 1916 marriage names Rachael with last name unknown; no surname projected backward from Victor [W01].')
    if p['id'] in ['per_joe','per_lori']:
        p['relationships']['child_ids']=['per_ilana','per_aliya','per_shoshy','per_yechiel','per_maimi','per_shimon','per_chaya_brocha','per_simcha','per_hadassa']
        p.setdefault('notes',[]).append('Order confirmed by family 1 October 2026 [S001]; not inferred from obituary list.')
    if p['id']=='per_lori':
        p['names']['surname_birth']='Hersh'
        p.setdefault('notes',[]).append('Contemporary notice spells Laurel Ruth Hersh; Hirsch is a reported family variant, requiring clarification [S032, S030].')
    if p['id']=='per_ilana':
        p['life_events']['birth']['date'].update({'value':None,'precision':None,'source_ids':['s_cjn_1988_ilana'],'note':'Original June 4 notice inspected in CJN issue 26 August 1988, printed p. 40. Precise living-person birth field deliberately remains blank pending owner review.'})
        p['notes']=['Ilana Chava in the original 1988 birth notice; June 4, with issue year context. Wedding is family-reported. Current children preserved in the register; no dates inferred for them.']
    if p['id']=='per_victor_garson':
        p['names']['surname_birth']=None
        p['names']['documented_name_history']=[{'name':'Victor Gershanovitz','scope':'1924 petition, not original birth proof','sources':['W02']},{'name':'Victor Garson','scope':'Documented adoption at 1924 admission; earlier usage also recorded','sources':['W02','W03','S062']}]
        for fact in p.get('facts',[]):
            if fact.get('field')=='marriage':fact['value']='Married Pearl Adelstein on 12 September 1916. Original marriage names Solomon and Rachael, surnames unestablished [S063/W01].'
        p.setdefault('notes',[]).append('Current original packet supersedes the stale 1934 attribution: admitted and named Victor Garson on 20 November 1924; certificate issued 26 November [W02-W03].')
        for fact in p.get('facts',[]):
            if '1934' in str(fact) and 'naturali' in str(fact).lower():
                fact['historical_value']=fact.get('value');fact['value']='Admission and name change 20 November 1924; certificate 2116415 issued 26 November 1924 [W02-W03].';fact['editorial_status']='corrected-from-original-packet'
    if 'leah' in p['names']['display'].lower() and 'janowitz' in p['names']['display'].lower():
        p['names']['display']="Leah Hersh (Larry's mother; maternal surname unconfirmed)"
        p['names']['surname_birth']=None
    if p['names']['display'] in ['Joseph Warszavski','Rochel Goldberg','Isac Kaga','Tsilya Gershon'] or p['id'] in ['per_shimon_elder','per_elka_zelkind']:
        p.setdefault('relationships',{})['qualification']='Indexed parentage provisional; original SS-5/birth unexamined. Szyman Zisl/Joseph conflict remains unresolved.'
    if p['id']=='per_leah_hersh':
        for fact in p.get('facts',[]):
            if fact.get('field')=='identity':fact['value']='Larry’s mother Leah is identified in the interview message to her brother. Janowitz/Janovitz/Yanowicz are uncle-associated research variants; Leah’s maiden surname is unconfirmed pending an identifying original-record chain.'
    if p['id']=='per_bertha':
        for fact in p.get('facts',[]):
            if fact.get('field')=='birthday':fact['value']='15 May 1935 recorded on her stone [S043/S058]; civil birth certificate unexamined.'
    if p['id']=='per_aline_garson':
        for fact in p.get('facts',[]):
            if fact.get('field')=='margin_marriage':fact['value']='Married Edouard Adolphe Godenne 16 October 1920, Paris 17e act 3605, register 17M399, viewer 21 [S104].';fact['note']='Original marriage already presented; old 5559 locator superseded. Does not name Marius’s parents.'
# Correct stale active claims throughout the working representation, including
# events/source descriptions. Original snapshots remain the audit trail.
def repair_active(value):
    if isinstance(value,dict):
        for k,v in list(value.items()):
            if k.startswith('historical_'):continue
            if isinstance(v,str):
                if 'naturali' in v.lower() and '1934' in v and ('Victor' in v or 'certificate 2116415' in v or 'cert 2116415' in v):
                    value[k]=v.replace('November 20, 1934','November 20, 1924').replace('fifteen years later','five years later')+' [Corrected against W02-W03: admission 20 November 1924; certificate issued 26 November.]'
                elif '5559' in v and ('Godenne' in v or '1920' in v):value[k]=v.replace('5559','3605')+' [Correct original act locator; older locator superseded.]'
                elif 'seven siblings' in v:
                    value[k]=v.replace('one of seven siblings','part of a differing family total (original children/siblings wording needs checking)').replace('seven siblings','a differing family total (wording unverified)')
                elif v=="Lori's maiden name is also Hirsch. No family link between the two Hirsch families is assumed.":value[k]='Contemporary notice names Laurel Ruth Hersh; Hirsch remains a reported family variant [S032, S030]. No kinship inferred from that spelling.'
            else:repair_active(v)
    elif isinstance(value,list):
        for i,v in enumerate(value):
            if isinstance(v,str):
                value[i]=v.replace('one of seven siblings','a differing family total whose children/siblings wording needs checking')
            else:repair_active(v)
repair_active(tree)
for ev in tree.get('events',[]):
    if '1934-11-20' in str(ev) and 'Victor' in str(ev):
        if isinstance(ev.get('date'),dict):ev['date']['value']='1924-11-20';ev['date']['note']='Admission/name change W02-W03; certificate issued 26 November.'
    if ev.get('id')=='evt_victor_naturalization':ev['place']='Cuyahoga County Court of Common Pleas';ev['editorial_source_ids']=['W02','W03'];ev['date_types']={'admission_and_name_change':'1924-11-20','certificate_issuance':'1924-11-26'}
for s in tree['sources']:
    if s['id']=='s_ohio_marriage_victor_pearl':s['description']='Marriage application 111752, page 188, DGS 004030138 image 1100. License 11 September 1916; return 12 September. Groom’s parents Solomon and Rachael (last name unknown), surnames unestablished [S063/W01].'
for u in tree.get('unions',[]):
    if u['id']=='uni_bertha':u['notes']=['Joe’s parents Szyman and Berta; Berta’s maiden surname Zelkind is source-attributed in family notices [S050/S034]. Stone gives 1935-2016; civil records remain open.']
    if u['id']=='uni_joe_lori':u['child_ids']=['per_ilana','per_aliya','per_shoshy','per_yechiel','per_maimi','per_shimon','per_chaya_brocha','per_simcha','per_hadassa']
for p in tree['persons']:
    if p['id']=='per_leah_hersh':
        p['names']['display']=mother;p['names']['surname_birth']='Yanowitz'
        p['names']['surname_basis']='Judith original abstract + S103 sibling link; Lee/Leah normalization qualified'
        p.setdefault('notes',[]).append(parent_claim)
        for f in p.get('facts',[]):
            if f.get('field')=='identity':f['value']=parent_claim;f['source_ids']=['s_judith_marriage_1949','s_judith_obituary_2025','s_ushmm_hersh_oral_1984'];f['qualification']='combined sibling evidence; exact Lee/Leah variant retained'
    if p['names']['display']==oldfather:
        p['names']['display']=father;p['names']['given']='Jacob';p['names']['given_basis']='Judith 1949 abstract + S103 sibling link';p['names']['surname_birth']=None
        for f in p.get('facts',[]):
            if f.get('field')=='identity':f['value']=parent_claim;f['source_ids']=['s_judith_marriage_1949','s_judith_obituary_2025','s_ushmm_hersh_oral_1984'];f['qualification']='combined sibling evidence; original father field has no surname'
        p.setdefault('notes',[]).append(parent_claim)
    if p['id']=='per_judy_hersh':p.setdefault('notes',[]).append("1949 original calls her Judith Herskovitz, age 21, father Jacob, mother Lee Yanowitz; wedding 20 November 1949 [S132].")
for q in tree['open_questions']:
    if any(x in q['question'].lower() for x in ['leah','uncle','father']):q['new_evidence_note']=parent_claim+' Narrowed, not fully closed.'
for lead in tree['research_leads']:
    if any(x in lead.get('text','').lower() for x in ['leah','janowitz','hershkovitz']):lead['new_evidence_note']=parent_claim+' No candidate memorial household merged.'
tree['sources'].append({'id':'s_judith_obituary_2025','title':'Judith Dratler née Herskowitz obituary','editorial_id':'S103','description':'Cleveland Jewish News, posted 9 June 2025, updated 12 June; explicitly identifies Lawrence Hersh as her brother and Phillip Dratler as husband. Independently reread by ancestry reviewer.'})
tree['sources'].append({'id':'s_judith_marriage_1949','title':'Judith Herskovitz and Philip Dratler original certified marriage abstract','editorial_id':'S132','description':'Ohio state file 09457, A 201127; DGS 005261981 image 12. License 14 November, wedding 20 November, certified 22 November 1949. Father Jacob; maiden name of mother Lee Yanowitz. Original displayed scan inspected.'})
tree['statistics']['editorial_register_entries']=len(register)
tree['statistics']['editorial_household_entries']=len(households)
dump('working-tree-v1.19.json',tree)

def normalized(s):return re.sub(r'[^a-z0-9]+','',unicodedata.normalize('NFKD',s).lower())
mapping=[]
aliases={'Leah Hersh nee Janowitz (Larry\'s mother)':"Leah Hersh (Larry's mother; maternal surname unconfirmed)"}
for p in tree['persons']:
    matches=[r['id'] for r in register if normalized(r['name'])==normalized(p['names']['display']) or normalized(r['baseline_name'])==normalized(p['names']['display'])]
    if p['id']=='per_judy_hersh':
        matches=[r['id'] for r in register if r['name']=="Judith Dratler (nee Herskowitz) - 'Judy'"]
    assert len(matches)<=1,(p['id'],matches)
    mapping.append({'graph_id':p['id'],'graph_display':p['names']['display'],'register_ids':matches,'status':'exact-display-match' if matches else 'requires-explicit-identity-review'})
dump('graph-register-map.json',mapping)
dump('register.json',register);dump('households.json',households)

doc=fitz.open(BASE)
def entries(first,last,size):
    result=[];current=None
    for idx in range(first-1,last):
        for b in doc[idx].get_text('dict',sort=True)['blocks']:
            if b['type']!=0:continue
            for l in b['lines']:
                for s in l['spans']:
                    txt=s['text'].strip()
                    if not txt or txt=='THE WARSZAWSKIS' or txt==str(idx+1):continue
                    if abs(s['size']-size)<.06:
                        if current and current.get('heading_open'):current['name']+=' '+txt
                        else:
                            current={'name':txt,'text':'','baseline_page':idx+1,'heading_open':True};result.append(current)
                    elif current:
                        current['heading_open']=False;current['text']+=txt+'\n'
    for r in result:r.pop('heading_open',None);r['text']=clean(r['text'])
    return result
notes=entries(165,179,17)
for i,r in enumerate(notes,1):
    r['id']=f'N{i:03}'
    if r['name']=='Ilana and Shmaya Marinovsky':r['text']=r['text'].replace('wedding announcement, 28 February 2012','family-reported wedding, 28 February 2012 [S030, S001]; no original announcement identified')
    if r['name']=='The family at 770':r['name']='JEM preview provenance (individual portraits)';r['text']+='\nLegacy group-photo title retired: the current pages show individual Sunday-dollars previews. Permission remains outstanding.'
    if r['name']=='Where the proven Garson line stops':r['text']+='\nVictor marriage [S063/W01] names Solomon and Rachael; W02-W03 establish his earlier surname and adopted Garson name. Candidate Paris parentage W08 remains unlinked.'
dump('story-notes.json',notes)

sources=json.loads((REVIEW/'source-catalogue-coverage.json').read_text())
for r in sources:
    r['id']=r['name'].split()[0];r['baseline_page']=r.pop('page');r['text']=clean(r['text'])
    if r['id']=='S109':r['text']=r['text'].replace('The printed overseas place La Paz, Argentina is geographically inconsistent.','The printed place is La Paz, Argentina. A municipality of that name exists in Entre Rios; Yitzchak Reiter\'s actual residence remains unverified.')
    r['canonical_id']='W01' if r['id']=='S063' else r['id']
    r['citation_usage']=[{'register_id':p['id'],'name':p['name']} for p in register if r['id'] in p['source_ids']]
    r['supported_claims']=[{'catalogued_scope':r['text'],'limitation':'Citation usage is not a claim that this source establishes every field in the referenced entry.'}]
    # Each source gets the exact embedded URI under its own entry, not a generic homepage guessed from prose.
    srcsize=16.5 if r['id'].startswith('S') else 12.5
    pag=doc[r['baseline_page']-1]
    headings=[s for b in pag.get_text('dict')['blocks'] if b['type']==0 for l in b['lines'] for s in l['spans'] if abs(s['size']-srcsize)<.06]
    start=next((s['bbox'][1] for s in headings if s['text'].startswith(r['id']+' ')),0)
    stop=min([s['bbox'][1] for s in headings if s['bbox'][1]>start+3 and re.match(r'^[SW]\d{2,3} ',s['text'])]+[740])
    r['urls']=list(dict.fromkeys(l['uri'] for l in pag.get_links() if l.get('uri') and start<=l['from'].y0<stop))
    r['original_locator']=r['text']
    r['local_originals']=[]
    for url in r['urls']:
        m=re.search(r'drive.google.com/file/d/([^/]+)',url)
        if m:
            manifest=json.loads((ROOT/'inventory/import-manifest.json').read_text())
            records=manifest if isinstance(manifest,list) else manifest.get('files',[])
            r['local_originals'] += [x.get('local_path',x.get('path')) for x in records if x.get('id',x.get('drive_id'))==m.group(1)]
    r['local_original_metadata']=[{'path':p,'sha256':next((x['sha256'] for x in json.loads((ROOT/'inventory/import-manifest.json').read_text()) if x.get('local_path')==p),None)} for p in r['local_originals']]
    if r['id']=='S062':r['document_components']=['declaration_victor_28845_1919'];r['text']+='\nSame declaration component as W02; the 1924 petition within W02 is a distinct document.'
    if r['id']=='W02':r['document_components']=['declaration_victor_28845_1919','petition_victor_19277_1924']
    if r['id']=='W03':r['document_components']=['order_victor_19277_1924']
    if r['id']=='S070':r['document_components']=['petition_pearl_1940'];r['text']+='\nPearl’s separate 1940 case, not a duplicate of Victor’s W02/W03 packet.'
    r['locator_status']='Original locator retained; generic-only locators remain unresolved, never invented.'
sources.append({'id':'S132','name':'S132 Judith Herskovitz and Philip Dratler — original 1949 certified marriage abstract','baseline_page':None,'canonical_id':'S132','text':'Ohio Department of Health, Cuyahoga County Probate Court. State file 09457, A 201127; DGS 005261981, microfilm 2251661, image 12. Bride Judith Herskovitz, 21, Czecho-Slovakia; father Jacob (no surname in that field); maiden name of mother Lee Yanowitz. License 14 November 1949; wedding 20 November; abstract certified 22 November. Original displayed scan inspected; S103 obituary supplies the sibling identity bridge, not this abstract alone. Does not identify uncle or lost sisters.','urls':['https://www.familysearch.org/ark:/61903/3:1:33SQ-G16K-9P69'],'document_components':['judith_marriage_1949'],'supported_claims':['Literal Judith parent fields','Judith/Philip wedding and distinct license/certification dates'],'citation_usage':[r['id'] for r in register+households if 'S132' in r['source_ids']],'locator_status':'Original displayed scan inspected; maximum-resolution master unavailable','local_original':{'path':'assets/new-evidence/Judith-Herskovits-Philip-Dratler-1949-certified-abstract.png','sha256':'b31d6dedc80422aff0e44b4e26ecc2041eea045a7fe9a408e84853bb325c76ad'}})
dump('source-crosswalk.json',sources)

ledger=json.loads(json.dumps(list(csv.DictReader((REVIEW/'open-items.csv').open()))))
updates={'R01':('partly-closed-production-recovered','All 472 baseline pages reproduced; legacy layout is PDF artwork. Revised flowing reference sections recreated; no original native layout recovered.'),'R02':('implemented','One working q_14; four distinct leads renumbered per preservation map; every original person and lead retained.'),'R03':('partly-implemented','All S/W IDs mapped, S063/W01 canonicalized, source URLs and claim usage retained; source-specific unresolved locators remain explicit.'),'R34':('partly-implemented-owner-review-pending','Original 1988 issue inspected; June 4 notice claim and issue context retained. Precise living-person birth field deliberately blank pending owner review; certificate unexamined.'),'R35':('implemented','Indexed parentage and grouped-surname allocations qualified beside relationship fields; no inference promoted to proof.'),'R26':('digital-proof-completed-physical-proof-open','All revised pages rendered by PyMuPDF, Poppler and Apple CoreGraphics; coverage and navigation validated. Physical printer proof outstanding.')}
updates.update({'R07':('narrowed-by-original','Judith 1949 abstract gives mother maiden name Lee Yanowitz; S103 obituary explicitly links Judith and Larry. Combined evidence supports maternal name variants; Cleveland uncle remains unidentified.'),'R39':('narrowed-by-original','Judith 1949 abstract names father Jacob; S103 sibling link supplies combined Larry parent attribution. Original father field gives no surname. Lost sisters and compatible memorial household remain unlinked.'),'R05':('open-route-verified','Live NUMIDENT confirms indexed parentage without an image. Official 1918 Warsaw inventory returns only marriage annexes; original SS-5 route verified, not requested. Joseph/Zisl conflict unresolved.'),'R06':('open-index-rechecked','Live NUMIDENT rechecked, no image. Original SS-5/civil record remains unexamined; dates and Kaga/Kagan/Kogen variants unresolved.')})
for r in ledger:
    if r['id'] in updates:r['revision_status'],r['revision_result']=updates[r['id']]
    else:r['revision_status']=r['status'];r['revision_result']='Historical review disposition retained; no new identity proof obtained in this rebuild.'
dump('closure-ledger.json',ledger)
print(json.dumps({'register':len(register),'households':len(households),'sources':len(sources),'notes':len(notes),'graph_nodes':len(tree['persons']),'mapped_nodes':sum(bool(x['register_ids']) for x in mapping),'working_questions':len(questions),'research_leads':len(tree['research_leads'])}))
