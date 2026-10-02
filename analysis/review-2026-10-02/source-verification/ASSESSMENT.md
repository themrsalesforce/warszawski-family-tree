# External-source verification assessment

Checked 2 October 2026. [Retrieval log](verification-log.json) records exact URLs, methods, status and checksums. A downloaded page or HTTP success is not by itself a validated genealogy claim.

| Source | Result | What was checked | Limitation |
| --- | --- | --- | --- |
| CPL Rosamond, record 614868 | HTML retrieved and content inspected | 25 January 1983 Plain Dealer, p. 2E; spouse Sanford; original-scan request route | Original obituary not obtained |
| CPL Rose Karr, record 569015 | HTML retrieved and content inspected | Alliance/Karr wording, publication citation and family summary | Library transcription; not a newspaper facsimile |
| CPL city-directory coverage guide | PDF retrieved | Coverage guide available for the Janowitz search | A guide does not identify the uncle |
| USHMM irn505021 | HTML retrieved and metadata/player inspected | Correct interview record, three video endpoints | No listening verification |
| USHMM part-3 transcript | PDF retrieved and text inspected | Arrival/uncle/camp passages | Automated transcript, not the recording |
| USHMM captions, parts 1–3 | All retrieved; part 1 succeeded on retry | Passage locators for counts, uncle and arrival | Derivative captions may mishear names |
| USHMM video, parts 1–3 | HTTP HEAD 200, video/mp4 | Endpoints exist and supply plausible file lengths | Videos not downloaded or listened to; full playback not tested |
| Archives de Paris act 2087 | JPEG retrieved and cropped for visual reading | Date, child and parent-name comparison | Reading qualification remains; identity with Cleveland Victor unresolved |
| AJA MS-361 Series D | Finding aid retrieved and entry inspected | D56/5 Polish refugee lists in Sweden, 1945–1946 | Individual lists not inspected |
| Arolsen Mordka search | HTML retrieved | Search route exists | Application shell did not expose the individual nine-document case; not counted as case verification |
| Bergen-Belsen list | HTTP 405 denied | Access failure recorded | No live rereading of entry |
| Northern Mariner 34(1), pp.129–138 | PDF retrieved | Published historical context source available | Does not authenticate Larry's individual actions |
| Judith Dratler CJN obituary | HTTP 429 | Failure recorded | Imported references remain; no successful fresh page verification |
| NARA women/naturalization history | HTML retrieved and content checked | Historical context for separate citizenship | Does not adjudicate Pearl's individual status |
| La Paz municipality | Official content found through web search | La Paz is a municipality in Entre Ríos, Argentina | Direct Python fetch failed TLS validation; search-backed finding retained in report; Yitzchak's exact residence unresolved |

The imported book already contained most of these research locators. This review distinguishes what could be reread directly from what remains a citation or inaccessible lead. No external request, email or record order was submitted.

Rechecks should go to a new snapshot directory. `scripts/verify_review_sources.py` uses the recorded public URLs and methods, never authenticated Drive transfer references. Binary downloads remain ignored by Git, consistent with the imported originals. Keep local/Drive backups to preserve them.
