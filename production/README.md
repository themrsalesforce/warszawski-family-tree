# Revised Warszawski edition

The 2 October 2026 revision has 200 pages. It retains all 183 register entries, all 57 households, all 61 graph people and all 39 distinct research leads. The source edition has 236 pages. Its 212-page legacy design survives as PDF artwork; the actual 24-page later supplement was recovered and retained. Native editable legacy design files were not recovered. The new register, households, story notes, canonical catalogue and index are generated from editable JSON and Python; targeted prose/chart corrections are applied to preserved artwork.

The private Library production ZIP supplies **all binary inputs required to rebuild the revision**, fonts with notices, literal source facsimile, pinned requirements, code, editable data and validation reports. A Git clone alone does not contain the ignored PDFs/images/fonts. Original files and imports remain untouched. Drive is inbound only; there is no background monitor.

## Build from the private package

Use Python 3.14 and create a virtual environment. Install `production/requirements.txt`; install Poppler for `pdffonts` and `pdftoppm`. Then run:

```sh
python verify_package.py
python production/build_revision.py --assets assets --reading inputs/Source-236-Reading.pdf --print-pdf inputs/Source-236-Print.pdf
python production/compact_reading.py
python production/validate_revision.py
```

On macOS with the listed Quartz dependency, run `python production/render_independent.py` to render every reading and print page independently through Poppler and Apple CoreGraphics and check embedded CID-to-glyph maps. No Apple renderer is claimed on other platforms. Generated PDFs go to `output/pdf/`. JSON validation goes to `analysis/rebuild-2026-10-02/`.

`production/prepare_revision.py` is the editorial recovery transformation in the canonical checkout. Its historical review files and tree are required to regenerate the working JSON. The delivery package includes the final prepared JSON; the normal rebuild deliberately uses that reviewed state, rather than rerunning extraction over historical sources.

## Editing and evidence

Keep `baseline_name`, `baseline_page` and historical IDs as provenance. Do not merge research candidates into the confirmed genealogy. `canonical-documents.json` records supported claims and limits for individually reviewed originals; `source-crosswalk.json` resolves every S/W ID and explicitly preserves unresolved generic locators. Citation usage is a mapping of manuscript claims to catalogue entries, not certification of every underlying original. S063/W01 are one marriage; S062 is the declaration component within W02, which also holds the later petition. S070 is Pearl's separate case.

S132 is Judith's 1949 original abstract, with literal father Jacob and mother's maiden name Lee Yanowitz. Attribution to Larry's parents uses S103's explicit sibling link; exact Lee/Leah and surname spelling variants remain visible. The uncle, lost sisters and compatible memorial household are still unlinked. Ilana's precise living-person birth field remains deliberately blank pending owner review.

The compact PDF preserves text and navigation while compressing images for screen reading. Use the separate full-resolution print interior for printer review. Some original images remain below the checklist's quality threshold, JEM permissions remain unresolved, and **no physical printer proof has been inspected**. The print file has 9-point bleed and an 8.5 × 11-inch trim; confirm the chosen printer's requirements before manufacture.
