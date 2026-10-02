"""Read-only structural checks for the imported v1.18 family-tree JSON."""
import collections
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
TREE = ROOT / 'Warszawski/03-Archive-records/expanded/warszawski-family-tree-v1.17/warszawski-tree.json'


def main():
    tree = json.loads(TREE.read_text())
    groups = {key: value for key, value in tree.items()
              if isinstance(value, list) and value and isinstance(value[0], dict)}
    issues = []
    for group, records in groups.items():
        counts = collections.Counter(record.get('id') for record in records if record.get('id'))
        for key, count in counts.items():
            if count > 1:
                issues.append({'type': 'duplicate-id', 'group': group, 'id': key, 'count': count})
    indexes = {key: {record['id'] for record in records if record.get('id')}
               for key, records in groups.items()}
    reference_keys = {
        'source_id': 'sources', 'source_ids': 'sources',
        'person_id': 'persons', 'person_ids': 'persons', 'focus_person_id': 'persons',
        'named_after_person_id': 'persons', 'parent_id': 'persons', 'parent_ids': 'persons',
        'child_id': 'persons', 'child_ids': 'persons', 'spouse_ids': 'persons',
        'sibling_ids': 'persons', 'partner_ids': 'persons', 'member_ids': 'persons',
        'union_id': 'unions', 'union_ids': 'unions', 'parent_union_ids': 'unions',
        'branch_id': 'branches',
    }

    def walk(value, location):
        if isinstance(value, dict):
            for key, content in value.items():
                path = f'{location}.{key}'
                if key in reference_keys and content is not None:
                    values = content if isinstance(content, list) else [content]
                    for identifier in values:
                        if isinstance(identifier, str) and identifier not in indexes.get(reference_keys[key], set()):
                            issues.append({'type': 'missing-reference', 'path': path,
                                           'id': identifier, 'target_group': reference_keys[key]})
                walk(content, path)
        elif isinstance(value, list):
            for i, content in enumerate(value):
                walk(content, f'{location}[{i}]')

    walk(tree, '$')
    edges = collections.defaultdict(set)
    for person in tree.get('persons', []):
        rel = person.get('relationships', {})
        for parent in rel.get('parent_ids', []):
            edges[parent].add(person['id'])
        for child in rel.get('child_ids', []):
            edges[person['id']].add(child)
    for union in tree.get('unions', []):
        for parent in union.get('partner_ids', []):
            for child in union.get('child_ids', []):
                edges[parent].add(child)
    visited, active = set(), []

    def visit(person):
        if person in active:
            issues.append({'type': 'parent-child-cycle', 'cycle': active[active.index(person):] + [person]})
            return
        if person in visited:
            return
        active.append(person)
        for child in sorted(edges[person]):
            visit(child)
        active.pop()
        visited.add(person)

    for person in sorted(indexes.get('persons', set())):
        visit(person)
    result = {'source': str(TREE.relative_to(ROOT)), 'counts': {k: len(v) for k, v in groups.items()},
              'checks': ['duplicate IDs', 'recognized person/union/branch/source references',
                         'cycles in person and union parent-child references'], 'issues': issues}
    target = ROOT / 'analysis/tree-structure.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    report = ['# Tree structural baseline', '', f'Source: `{result["source"]}`.', '',
              '| Record type | Count |', '| --- | ---: |',
              *[f'| {key} | {count} |' for key, count in result['counts'].items()], '',
              f'Issues found by these checks: {len(issues)}.', '',
              *[f'- {item["type"]}: `{item.get("id", "")}` in '
                f'`{item.get("group", item.get("path", "parent_child_links"))}`.' for item in issues], '',
              'Checks cover duplicate IDs, recognized relationship/source references, and parent-child '
              'cycles in person and union relationship data. Detailed findings are in `tree-structure.json`. '
              'This is not a factual genealogy audit, full schema validation, or a reconciliation with the manuscript.', '']
    (ROOT / 'analysis/TREE-STRUCTURE.md').write_text('\n'.join(report))
    print(json.dumps({'counts': result['counts'], 'issues': len(issues),
                      'issue_types': dict(collections.Counter(x['type'] for x in issues))}))


if __name__ == '__main__':
    main()
