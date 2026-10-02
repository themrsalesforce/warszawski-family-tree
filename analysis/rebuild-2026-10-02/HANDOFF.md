# Revised Warszawski edition handoff — 2 October 2026

Read root AGENTS.md, SYNC.md, CURRENT-SOURCES.md, production/README.md and this handoff at takeover. Work in the Warszawski checkout; preserve histories, ignored originals and other tasks' edits. Synchronization is on demand; no recurring monitor or Drive upload was created.

## Completed production

The final revised reading, print and compact interiors have **200 pages**, reduced from 236 while retaining **183 register entries, 57 households, 61 graph people and all 39 distinct research leads**. The name/alias index has 203 rows. Duplicate q_14 and reused leads are reconciled in a versioned working copy, preserving old identifiers and historical snapshots. All source S/W identifiers resolve; S063/W01 is one marriage, S062 is the W02 declaration component, S070 is Pearl's separate petition. Precise original claims/limits are separate from catalogue usage and unresolved generic locators.

Current 236-page sources were recovered from the actual private Library package, not the stale 212-page editable bundle. All 472 baseline reading/print renders matched. Recovery commit: `bf6358576be941d9940c3a4b43dffdc3a9bf59ea`, pushed and remote verified. Imported source hashes remain reading `0f6e26c0adc86bb826dd2daf3b6e9f01fc99c7bcbeb4bad99e7a9d0772e28a38` and print `c2ff33df3b0bf61eef56e2578021cbaedbafa871407786b48156794ececbb3a0`.

Legacy layout remains preserved PDF artwork, not an original native design file. Reference sections, index, revised field data and targeted corrections are editable/reproducible code and JSON. The new private ZIP contains its own source PDFs, fonts/notices, actual new original, final editable data, builders, pinned requirements, full extracted reading text and validation manifests. Its 67 package files pass the included checksum verifier. An isolated rebuild matches **all 400 revised page renders**; PDF-container bytes need not be identical.

## Evidence and corrections

Read CHANGES-AND-CLOSURE.md and production/data/closure-ledger.json for all 39 dispositions. Implemented Larry's **S039 1961 card** attribution, children/siblings conflict wording, La Paz correction, S019/S024 baby citation, Lori Hersh/Hirsch distinction, Joe bar-mitzvah wording, Ilana wedding-source qualification, Aline act3605, Victor's 1924 court/date correction and immediate indexed/inferred relationship flags.

New S132 original: Judith Herskovitz–Philip Dratler 1949 Ohio marriage abstract, state09457/A201127/DGS005261981 image12. Literal father Jacob; explicit mother's maiden name Lee Yanowitz. Wedding20November, license14November, certification22November. Independently inspected original pixels and verified S103 obituary sibling bridge support Larry's parental names as **combined evidence**. Exact variants and qualification appear in graph/register/household/chart/index. R07/R39 are narrowed, not fully closed. No compatible memorial family or candidate pedigree was merged.

Ilana's precise living-person birth field remains deliberately blank pending owner review. Original 1988 notice claim and issue context are separately retained.

## Output locations and delivery

Paths below are relative to the canonical Mac project folder:

| Deliverable | Local path | Local bytes |
| --- | --- | ---: |
| Compact reading, 200pp | `output/pdf/The-Warszawskis-Revised-2026-10-02-Compact.pdf` | 8,008,359 |
| Full reading, 200pp | `output/pdf/The-Warszawskis-Revised-2026-10-02-Reading.pdf` | 23,760,063 |
| Full-resolution print, 200pp | `output/pdf/The-Warszawskis-Revised-2026-10-02-Print.pdf` | 45,980,689 |
| Changes/closure, 2pp | `output/pdf/Warszawski-Changes-and-Closure-2026-10-02.pdf` | 77,960 |
| Reproducible package | `output/Warszawski-Revised-Production-2026-10-02.zip` | 57,880,109 |
| Extracted editable reading text | `output/pdf/The-Warszawskis-Revised-2026-10-02-Editable.txt` | See local file |

All five primary artifacts are confirmed in **private Library**. Exact IDs and versions are in ignored `output/library-delivery.json`; final compact is **version4**, full reading/print/package version1, report version0. Root chat can attach the compact/report within its10MB cap; larger files remain convenient Mac files and private Library artifacts. Do not imply a Git clone contains binaries. No new Drive destination/upload was authorized.

Actual saved artifacts were materialized back into this Mac under `.import-tmp/final-library-roundtrip/`. Full reading, print and ZIP are byte-identical to local outputs. Library compact/report bytes differ, but all 200/2 page renders, text, outlines and navigation exactly match; both hash sets are recorded in library-roundtrip-verification.json. Delivered compact is8,033,364bytes, SHA256 `d919f756c7646aa1374d54be017c16d3b4010ade2555e483b11180db0130187f`. ZIP SHA256 `061d6db3101d4893c6666d3cc3557c3aac56d0737002954260ec54942e2613aa`.

## Verification and limitations

Every reading/print page rendered through PyMuPDF, Poppler and Apple CoreGraphics. Embedded fonts and CID-to-glyph maps pass. All183/57 coverage, unique IDs, geometry, overlap candidates, reading/print text parity and link destinations pass. Contents contains exactly15 current row hotspots. Major-figure narrative/evidence index references use checked multiword/identity-specific sets; single given names cannot conflate unrelated Jacobs. Independent reviewer findings on chart connectors, grammar, stale contents links and index regressions were fixed and guarded.

Print caption corrections preserve the print source's full-resolution images. Asset-level DPI/credits/permissions are measured in asset-credit-permission-checklist.json. Some poor originals and JEM permissions remain open. **No physical printer proof was inspected.** Native legacy design recovery remains incomplete but does not block this reproducible edition.

Open genealogy: Victor Paris/American parent identity; Szyman Zisl/Joseph; original Elka records; timestamped interview listening; uncle/lost sisters; precise civil dates, family confirmations, unresolved aliases/candidates and some original newspaper locators. New NUMIDENT/inventory findings establish bounded routes, not inspected SS-5 originals. Do not infer a negative search from stalled access. Some CJN archive retrievals returned403; no newly examined original is claimed from that attempt.

The final revision and handoff are scoped public text/code/data/manifests. Binary assets and delivery records stay ignored. The exact completed revision push/hash is recorded below after publication verification.

## Closure accounting

The39 review items comprise2 fully implemented structural/qualification items,5 established resolved manuscript/documentary claims,4 partly closed production/source/owner-review items,2 narrowed by the new original,25 still open (including rechecked index/original-record routes), and1 established interview access route. The working tree has16 open broad questions and3 closed broad findings; no new uncle/lost-sister or candidate-family identity is declared closed. Final independent review passed the200-page proof; its last elder-Szyman p53 crosshit was removed and guarded.

## Verified publication

Completed revision commit **`1bb9b71f705118cec63a3b6dd6d87059bab699d9`** was ordinarily pushed to `origin/main`; `git ls-remote origin refs/heads/main` matched that exact local hash. The preceding recovered-source commit is `bf6358576be941d9940c3a4b43dffdc3a9bf59ea`. This final publication record is a separate handoff commit; inspect `git log -1` for its hash. No published history was rewritten. All primary artifacts were saved and round-trip verified before the revision commit.
