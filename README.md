# Warszawski Family Tree

Research repository imported from Google Drive on 2026-10-02, following the Chaikin project's organization and synchronization approach. The [GitHub repository](https://github.com/themrsalesforce/warszawski-family-tree) is public by the user's request.

## Start here

- [October 2 research and editorial review](analysis/review-2026-10-02/REVIEW.md): proposed 194-page budget, accuracy corrections and prioritized closure criteria.
- [Current sources](CURRENT-SOURCES.md): edition selection and tree-version caveats.
- [Import report](analysis/IMPORT-REPORT.md): completeness, checksums, archive expansion and extraction limits.
- [Tree baseline](analysis/TREE-STRUCTURE.md): duplicate IDs, missing references and relationship-cycle checks.
- [Drive snapshot](inventory/drive-snapshot.json): original names, metadata, paths and source URLs.
- [Original-file manifest](inventory/import-manifest.json): verified byte counts and SHA-256 checksums.

## Contents and preservation

`Warszawski/` preserves the complete Family History/Warszawski branch, including the Chaikin manuscripts misfiled there. `05-Print-editions/` contains the separately stored Warszawski editions and shared editorial bundles. `Family-History-Shared/` preserves the shared index, original images, earlier proof and unlinked leads. Inclusion is not evidence of a relationship.

Originals remain unchanged. Archives are expanded beside their originals; the archive manifest identifies their members. One Drive file named `warszawski-family-tree-v1.17.json` is actually a ZIP containing internally versioned v1.18 JSON. The importer detects archives by content, not filename alone.

## Git

Git tracks Markdown, extracted text, genealogy data, source code and inventories. PDFs, images, ZIPs, Office files and fonts stay on disk, with checksums, and are ignored as in the Chaikin repository. The disguised ZIP is also ignored; its expanded JSON is tracked. A Git clone alone cannot restore the ignored originals: retain Drive and a local backup.

Completed changes are committed and pushed to [themrsalesforce/warszawski-family-tree](https://github.com/themrsalesforce/warszawski-family-tree). A 15-minute recurring monitor checks stable outside edits and approved inbound Drive changes; see [SYNC.md](SYNC.md) and [AGENTS.md](AGENTS.md). Every commit represents an actual change; an unchanged monitor run creates no commit. Shared materials use the same Drive source IDs as the Chaikin project, while each repository keeps its own family data and history.

## Reproduce the import checks

```sh
python3 scripts/index_project.py
python3 scripts/check_tree.py
```

Python 3.11+, Poppler `pdftotext`, and macOS `textutil` are needed. Re-indexing regenerates preserved archive expansions, so make substantive changes in a separate working copy. Imported historical build scripts are preserved as source, not automatically executed. Scans marked for OCR or review are not fully represented by extracted text.

Exact duplicates and repeated claims across revisions are not independent evidence. Relationships, dates, source quality and unresolved identifications must be reviewed separately from file integrity and graph structure.

## Reproduce the current-edition review

The review covers the actual 236-page PDFs. Its extracted text and evidence tables are tracked; rendered inspection images remain under ignored `.analysis-cache/`. The older editable/checklist bundle describes 212 pages and is not a complete current production package.

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements-review.txt
.venv/bin/python scripts/audit_review.py
.venv/bin/python scripts/audit_print_layout.py
.venv/bin/python scripts/review_manuscript_layout.py
python3 scripts/check_review.py
```

External checks can be repeated into a new snapshot directory with `scripts/verify_review_sources.py --output .analysis-cache/source-recheck`. Original imported genealogy snapshots remain unchanged; proposed corrections are in the review and closure ledger.
