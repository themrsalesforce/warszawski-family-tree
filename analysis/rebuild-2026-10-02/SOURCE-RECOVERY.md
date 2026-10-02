# Current production recovered

The private Library source package `Warszawski-Research-Update-Sources-2026-10-02.zip` was recovered into the canonical Mac project. Its 67,986,129 bytes and SHA-256 `7a4d2e7b3c76c79a40ec07820965e01c749911716f1a4993488fb52e454c7f85` match the supplied provenance. The historical import was preserved.

Running the recovered supplement and integration builders reproduced all 236 reading pages and all 236 print pages pixel-for-pixel at 72 dpi against the imported current edition. The imported reading and print hashes match the handoff. See `source-recovery-verification.json` and `recovered-package-manifest.json`.

The package recovers the actual current layout: a preserved 212-page PDF-artwork baseline plus the 24-page October 2 supplement and targeted corrections. Most legacy pages remain PDF artwork, rather than a fully editable original design file. The revised reference sections will therefore be recreated as editable structured data and flowing text; photographs, source facsimiles and family narrative artwork will be retained. This distinction remains part of the production handoff.

Recovered builders are tracked in `production/recovered/`; binary layout inputs, original images and fonts remain local and in the private production package. A Git clone does not contain their bytes. No Drive writeback or recurring monitor was created.
