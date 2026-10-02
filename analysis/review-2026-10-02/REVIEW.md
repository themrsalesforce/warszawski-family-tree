# Warszawski family history — research and editorial review

Review date: 2 October 2026. All page references below are to the **actual 236-page reading PDF**, whose filename still says 2026-10-01.

## Recommendation

Keep the family narrative, photographs and readable family charts. Aim for **about 194 pages, with a practical planning range of 190–205**, by reducing repetition in the register, households, source notes and research appendix. This is an estimated 13–20% reduction from 236 pages, not a rendered new edition. Do the accuracy and source reconciliation first; cutting the qualifications would make the book shorter but less trustworthy.

The most useful next research is the identity bridge from **Victor Gershanovitz/Garson to the candidate Paris birth act**, and the original records resolving **Szyman's Zisl/Joseph patronymic**. Broad searches for unrelated Garson families now have lower value. Pearl's Cleveland birth, her Adelstein parents and Rose's identity already have substantial documentary support in the current book; their old questions should not keep driving research as though nothing had been found.

The Git repository follows the Chaikin project's preservation approach. The verified import was committed as `be3484f`. Text, data, scripts and manifests are tracked; originals and expanded binary evidence remain on disk and in Drive with checksums. The subsequent setup adds the [public GitHub remote](https://github.com/themrsalesforce/warszawski-family-tree) and [on-demand synchronization and handoff rules](../../SYNC.md). A clone alone does not restore the ignored originals.

## Deliverables

- [Condensation plan](CONDENSATION-PLAN.md): section budgets, precise cuts and a sample of the proposed editorial treatment.
- [Developer reprocessing handoff](DEV-HANDOFF.md): implementation order, validation and delivery requirements.
- [Accuracy and source findings](ACCURACY-AND-SOURCES.md): corrections, unsupported certainty and new source checks.
- [Open items and closure criteria](OPEN-ITEMS.md): a prioritized research agenda, including questions already answered or superseded.
- [Machine-readable closure ledger](open-items.csv), [old-question dispositions](question-disposition.csv) and [duplicate-ID resolution map](tree-id-resolution.csv).
- [Page map](page-map.csv), [183 register entries](register-coverage.json), [57 household entries](household-coverage.json), [source catalogue coverage](source-catalogue-coverage.json) and [exact external PDF links](pdf-source-links.json).
- [Edition verification](review-verification.json), [print layout checks](print-layout-verification.json), [reading layout checks](reading-layout-verification.json) and [live source-check assessment](source-verification/ASSESSMENT.md).

## What was actually reviewed

The review covered text extraction from all 236 pages, a rendered contact-sheet overview of every page, full-page inspection of selected documents and dense pages, the register and household sections, the S001–S131 and W01–W30 catalogues, the internally v1.18 tree, older editable material, research notes and the Chaikin repository's corresponding import/review structure. Selected primary-source images were read visually. External checks retrieved the candidate French birth act, USHMM catalogue and transcript/captions, CPL finding records, archive finding aids and historical context. The retrieval log distinguishes successful downloads, HTTP metadata checks and failures.

This is a comprehensive editorial and evidence-consistency review, **not independent authentication of every person, date or original record**. No family member or archive was contacted. No original manuscript, imported JSON or PDF was changed. No new family relationship was asserted from a matching surname. There is no revised, shortened PDF yet.

## The baseline matters

| Artifact | Finding | Consequence |
| --- | --- | --- |
| Current reading and print PDFs | Both 236 pages; extracted text matches page by page; colophon says updated 2 October | Use these for the review, not the dates in their filenames |
| Editable manuscript, technical checklist and image checklist | Describe the older 212-page edition and omit the later appendix | They cannot yet rebuild or certify the current book |
| Most advanced imported tree | Filename v1.17 is a ZIP; extracted data is internally v1.18, with 61 people and 89 sources | Preserve the original; reconcile data rather than selecting the highest filename |
| Current PDF register | 183 entries: 91 labelled core family, 92 labelled unlinked research person | “Core” is a category, not a proof rating; it includes provisional indexed ancestors and unresolved identities |
| Structured open questions | 20 rows, including an identical repeated q_14 | Several questions are obsolete or partly answered |
| Research leads | Four IDs reused for different leads | Do not silently discard one record when making a dictionary keyed by ID |

The reading and print editions have different page geometry, as expected for bleed: reading 8.5 × 11 inches; print 8.75 × 11.25 inches with an 8.5 × 11 trim box. The earlier checklist is not evidence that the current 236-page print interior passed a printer's preflight.

## Findings that should affect the next edition

1. **Larry's exact birth day has a stronger source than the narrative admits.** Page 24's 1961 naturalization card gives 6/1/25; page 101 correctly uses that record, but pages 16–17 characterize exact dates as resting on a compiled tribute. Say that he reported 1 June 1925 in the 1961 card. A civil birth record is still a separate open item.
2. **Some flat relationship fields lose the prose's qualifications.** Leah is headed “nee Janowitz” although the interview names her brother, not an original record of her maiden name. Szyman's indexed parents and inferred Zelkind/Greenberg grandchild allocations need visible qualifiers in the parent/child fields themselves.
3. **Several old questions are already answered in the book.** The nine children's order was confirmed on 1 October; Berta's Zelkind surname is documented; Lori appears as Laurel Ruth Hersh in the engagement notice; Pearl's birth is documented as Cleveland. Keep narrower residual questions where needed, rather than keeping the entire old question open.
4. **A real geographical correction is required.** S109 on page 199 calls La Paz, Argentina inconsistent. The original notice on page 90 prints that place for Yitzchak Reiter, and an official municipality exists in Entre Ríos. Preserve the printed place; exact identification remains open. [Municipality's description](https://lapaz.gob.ar/?q=node%2F69).
5. **The interview-access question can advance substantially.** The USHMM record exposes three video files; all responded to HTTP HEAD checks, and all three caption files were retrieved. This establishes a remote access route. Listening to the crucial passages remains open. [USHMM catalogue](https://collections.ushmm.org/search/catalog/irn505021).
6. **Victor's surname discovery changes the search strategy.** The current appendix already documents the 1924 Gershanovitz-to-Garson change. Search the original surname variants first. The candidate 1895 French act was retrieved and inspected again, but its parents conflict with the American record; do not merge it yet.
7. **Source references exist, but some do not support the attached claim.** Page 154 cites S019, a wedding report, for a December 2025 baby announcement; that announcement is S024. Repeating large source lists twice in each register entry both wastes space and hides these distinctions.
8. **The print interior retains genuinely small originals.** Eleven distinct pages contain large image placements below 130 effective dpi. Obtain better originals or reduce their reproduction size where possible. Do not invent image detail or shrink the whole book's typography to save pages.

## Condensation in numbers

Pages 100–204 occupy **105 pages, 44.5% of the book**, largely for registers, households, notes and the original source catalogue. The register and household list alone use 65 pages. The unlinked French research occupies another 26 narrative/document pages, in addition to its register entries and household repetitions. These are the primary places to save space.

The modest plan retains all 183 register entries in the book, with shorter factual entries and compact unlinked household tables. It does not require abandoning the research or reducing chart legibility. A more substantial 150–175-page family edition is plausible only if the full unlinked research apparatus moves into a separate companion; that is a different editorial decision and is not the recommended first step.

## Suggested order of work

1. Recover or reconstruct a complete current production package: editable text, actual chart/person data, original image assets, builder, requirements and manifests for the 236-page edition.
2. Apply the corrections and status changes in the accuracy report to a new working copy; preserve this import as the historical baseline.
3. Resolve the few high-value identity questions, with explicit evidence criteria. Keep the remaining candidates separate.
4. Implement the 194-page budget and regenerate every page reference and index from the revised source.
5. Review all rendered pages, verify links and claim-level citations, and order a physical proof before calling the result print-ready.

The smaller edition should explain each family's story once, preserve the evidence needed to trust it, and make uncertainty visible exactly where the uncertain fact appears.
