# Warszawski project import and baseline inventory

Import date: 2026-10-02. This report checks file completeness and accessibility; it does not establish the accuracy of genealogical claims.

- Drive originals verified: 229 / 229.
- Original bytes downloaded: 313,223,787.
- ZIP archives expanded with CRC checks: 25.
- Files in the imported and expanded corpus: 418.
- Text/source files: 125.
- Exact duplicate groups: 10 (preserved).
- Documents with text extracted: 30.
- Documents needing OCR or review: 9.
- Document extraction failures: 0.

## File types

| Extension | Files |
| --- | ---: |
| .csv | 18 |
| .ged | 2 |
| .html | 1 |
| .jpg | 168 |
| .json | 23 |
| .md | 48 |
| .mmd | 2 |
| .mp3 | 2 |
| .pdf | 39 |
| .png | 60 |
| .py | 1 |
| .ts | 2 |
| .txt | 24 |
| .xml | 2 |
| .xsd | 2 |
| .zip | 24 |

## Scope and provenance

The complete Family History/Warszawski folder is preserved, including misfiled Chaikin manuscripts. Shared index and cross-family files and separately stored Warszawski print editions are also included.

Original Drive metadata and source URLs are in inventory/drive-snapshot.json. inventory/import-manifest.json records SHA-256 checksums and byte counts. inventory/archive-members.json maps expanded files to their original ZIPs. inventory/duplicate-groups.json identifies identical files across versions.

## Analysis limits

Text extraction preserves readable content but cannot establish document layout, read handwriting, or interpret images. OCR has not been run. Extraction status for every PDF/Word document is recorded in inventory/text-extraction.json. Historical snapshots contain repeated people, claims, and sources; do not sum them as separate evidence. Imported build scripts have not been executed.

## Next substantive checks

1. Compare the latest tree-data snapshot with the current editable production manuscript.
2. Audit people, relationship links, conflicting dates, source references, and unresolved claims.
3. Review scans requiring OCR and build a source-to-claim evidence index.
