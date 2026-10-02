"""Verify preservation, local report links, coverage and non-overlapping page budget."""
from pathlib import Path
import csv
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/review-2026-10-02'


def main():
    manifest = json.loads((ROOT / 'inventory/import-manifest.json').read_text())
    failures = [record['local_path'] for record in manifest
                if not (ROOT / record['local_path']).exists()
                or hashlib.sha256((ROOT / record['local_path']).read_bytes()).hexdigest() != record['sha256']]
    source_folder = OUT / 'source-verification'
    source_log = json.loads((source_folder / 'verification-log.json').read_text())
    source_failures = []
    checked_source_paths = set()
    for record in source_log:
        if record['status'] != 'retrieved':
            continue
        name = record['id'].removesuffix('-retry')
        candidates = [path for path in source_folder.glob(name + '.*') if path.suffix in {'.html', '.pdf', '.jpg', '.vtt'}]
        if len(candidates) != 1 or hashlib.sha256(candidates[0].read_bytes()).hexdigest() != record['sha256']:
            source_failures.append(name)
        else:
            checked_source_paths.add(candidates[0])
    missing_links = []
    reports = [ROOT / 'README.md', ROOT / 'CURRENT-SOURCES.md',
               *OUT.glob('*.md'), OUT / 'source-verification/ASSESSMENT.md']
    for path in reports:
        for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if '://' in link or link.startswith('#'):
                continue
            target = link.split('#')[0]
            if target and not (path.parent / target).exists():
                missing_links.append({'file': str(path.relative_to(ROOT)), 'link': link})
    people = json.loads((OUT / 'register-coverage.json').read_text())
    households = json.loads((OUT / 'household-coverage.json').read_text())
    with (OUT / 'open-items.csv').open() as file:
        ledger = list(csv.DictReader(file))
    with (OUT / 'question-disposition.csv').open() as file:
        questions = list(csv.DictReader(file))
    budget = []
    for line in (OUT / 'CONDENSATION-PLAN.md').read_text().splitlines():
        if not line.startswith('| ') or '**Total**' in line:
            continue
        cells = [value.strip() for value in line.strip('|').split('|')]
        if len(cells) == 6 and cells[2].isdigit():
            budget.append((int(cells[2]), int(cells[3]), int(cells[4])))
    result = {
        'original_files_verified_unchanged': len(manifest) - len(failures),
        'original_hash_failures': failures,
        'external_snapshots_verified': len(checked_source_paths),
        'external_snapshot_hash_failures': source_failures,
        'broken_local_report_links': missing_links,
        'register_entries': len(people), 'household_entries': len(households),
        'review_items': len(ledger),
        'unique_review_item_ids': len({row['id'] for row in ledger}),
        'question_rows_mapped': len(questions),
        'budget_current_pages': sum(row[0] for row in budget),
        'budget_proposed_pages': sum(row[1] for row in budget),
        'budget_savings': sum(row[2] for row in budget),
    }
    assert not failures and not source_failures and not missing_links, result
    assert result['budget_current_pages'] == 236 and result['budget_proposed_pages'] == 194, result
    assert all(current - proposed == saved for current, proposed, saved in budget), budget
    assert len(people) == 183 and len(households) == 57, result
    assert len(ledger) == result['unique_review_item_ids'] == 39 and len(questions) == 20, result
    (OUT / 'completion-checks.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
