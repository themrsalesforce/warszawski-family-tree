# Current edition and preserved source entry points

The revised **200-page** edition is implemented and verified. Read [the production guide](production/README.md), [changes and closure](analysis/rebuild-2026-10-02/CHANGES-AND-CLOSURE.md) and [next handoff](analysis/rebuild-2026-10-02/HANDOFF.md) before editing. Current PDFs are `output/pdf/The-Warszawskis-Revised-2026-10-02-{Reading,Print,Compact}.pdf`; the complete private production ZIP is `output/Warszawski-Revised-Production-2026-10-02.zip`. Binary artifacts are local and in private Library, not in Git. The ignored `output/library-delivery.json` records exact saved Library identities/versions.

Current editable references are [production/data](production/data/). All 61 working graph people map to the retained 183 register entries and 57 households; candidates remain separate. The following are preserved historical entry points, rather than the current revised edition:

- [Preserved 236-page reading source](Warszawski/05-Print-editions/The-Warszawskis-Coffee-Table-Edition-2026-10-01-Reading-Copy.pdf).
- [Preserved 236-page print source](Warszawski/05-Print-editions/The-Warszawskis-Coffee-Table-Edition-2026-10-01-Print-Interior.pdf).
- [Older editable manuscript, 212-page edition](Warszawski/05-Print-editions/expanded/Family-Coffee-Table-Editions-Editable-Texts-and-Print-Checks-2026-10-01/The-Warszawskis-editable-manuscript.md).
- [Research reference edition](Warszawski/05-Print-editions/The-Warszawskis-Research-Reference-Edition-2026-10-01.pdf).
- [Most advanced tree snapshot found, internally v1.18](Warszawski/03-Archive-records/expanded/warszawski-family-tree-v1.17/warszawski-tree.json): 61 person entries and 89 source entries before duplicate-ID resolution.
- [Research notes](Warszawski/04-Research-notes/).
- [Archive records](Warszawski/03-Archive-records/).
- [Shared index](Family-History-Shared/00-Index/START-HERE.md).

The preserved source reading/print PDFs have **236 pages** and an internal “updated 2 October 2026” colophon, despite their October 1 filenames. Their extracted text matches page by page. The imported editable manuscript, technical checklist and image checklist describe an older **212-page** edition and omit the later research appendix. The [review evidence](analysis/review-2026-10-02/review-verification.json) records hashes, geometry and coverage; [page text](analysis/review-2026-10-02/page-text.json) represents the actual current PDF, not editable production layout.

Version numbers in filenames are unreliable: the archive named v1.17 contains internal format v1.18, while archive-records/v1.15 contains internal v1.17. The v1.18 metadata also retains older package notes and generation timestamps. These are preserved snapshots, not a claim that their content is fully current. The historical 61-person tree was not reconciled with that book register. The new versioned working representation and explicit graph/register map perform that reconciliation without altering this snapshot.

The initial inspected folders lacked the complete current production package. It was subsequently recovered from private Library and reproduced all 472 baseline reading/print pages pixel-for-pixel. Legacy layout remains PDF artwork; new reference sections are editable JSON and code. The new private package reproduces all 400 revised reading/print page renders from its own inputs. Native legacy design files and a physical printer proof remain outstanding.
