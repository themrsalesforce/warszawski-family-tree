# Warszawski Family Tree

Local research repository imported from Google Drive on 2026-10-02, following the Chaikin project's organization and version-control approach.

## Start here

- [Current sources](CURRENT-SOURCES.md): edition selection and tree-version caveats.
- [Import report](analysis/IMPORT-REPORT.md): completeness, checksums, archive expansion and extraction limits.
- [Tree baseline](analysis/TREE-STRUCTURE.md): duplicate IDs, missing references and relationship-cycle checks.
- [Drive snapshot](inventory/drive-snapshot.json): original names, metadata, paths and source URLs.
- [Original-file manifest](inventory/import-manifest.json): verified byte counts and SHA-256 checksums.

## Contents and preservation

`Warszawski/` preserves the complete Family History/Warszawski branch, including the Chaikin manuscripts misfiled there. `05-Print-editions/` contains the separately stored Warszawski editions and shared editorial bundles. `Family-History-Shared/` preserves the shared index, original images, earlier proof and unlinked leads. Inclusion is not evidence of a relationship.

Originals remain unchanged. Archives are expanded beside their originals; the archive manifest identifies their members. One Drive file named `warszawski-family-tree-v1.17.json` is actually a ZIP containing internally versioned v1.18 JSON. The importer detects archives by content, not filename alone.

## Git

Git tracks Markdown, extracted text, genealogy data, source code and inventories. PDFs, images, ZIPs, Office files and fonts stay on disk, with checksums, and are ignored as in the Chaikin repository. The disguised ZIP is also ignored; its expanded JSON is tracked. A Git clone alone cannot restore the ignored originals: retain Drive and a local backup. This is a local Git repository with no remote configured and no automatic Drive synchronization.

## Reproduce the import checks

```sh
python3 scripts/index_project.py
python3 scripts/check_tree.py
```

Python 3.11+, Poppler `pdftotext`, and macOS `textutil` are needed. Re-indexing regenerates preserved archive expansions, so make substantive changes in a separate working copy. Imported historical build scripts are preserved as source, not automatically executed. Scans marked for OCR or review are not fully represented by extracted text.

Exact duplicates and repeated claims across revisions are not independent evidence. Relationships, dates, source quality and unresolved identifications must be reviewed separately from file integrity and graph structure.
