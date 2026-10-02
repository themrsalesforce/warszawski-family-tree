# GitHub and Google Drive synchronization

Canonical public remote: [themrsalesforce/warszawski-family-tree](https://github.com/themrsalesforce/warszawski-family-tree). Completed changes are committed and pushed. A recurring monitor checks stable outside edits and inbound Drive changes every 15 minutes when the local host and Codex are available.

This follows the latest Chaikin setup inspected at commit `16f6648`, with the explicit difference that this repository is public. Each family retains its own history, research and production data. Shared materials converge through their canonical Drive source IDs, not by copying all files or merging branches between repositories.

## Authorized scope

- Google Drive → local project: new/changed files in the approved folders below.
- Local tracked files → public GitHub: completed edits, additions, deliberate deletions and meaningful binary-manifest changes, including stable outside edits.
- GitHub → local project: fast-forward updates when the checkout is clean and histories are compatible.
- Every commit records an actual change. No empty commits or no-change timestamp churn.
- No automatic Drive deletion/writeback, destructive overwrite, history rewrite or force push.

Large PDFs, images, ZIPs, Office files, recordings and fonts remain ignored. `python3 scripts/snapshot_binary_state.py` records their hashes in `inventory/local-binary-state.json`. This also includes the known ZIP named `warszawski-family-tree-v1.17.json`. GitHub stores the manifest, not those binary bytes. Keep local/Drive backups for recovery.

## Approved Drive sources

1. Full recursive Warszawski branch: `15qlGHoNux8jiYxc8EFCHLjEQafVKiUHO` → `Warszawski/`.
2. Full recursive shared index: `1sLbYft-9SEBSELzE-FABoqJSXA8j7sT3` → `Family-History-Shared/00-Index/`.
3. Full recursive shared cross-family branch: `1nb1iwqDk3o-3gNyHw9K9QNZqEFJuaCm8` → `Family-History-Shared/03-Cross-family/`.
4. Print editions: `1NpZ0pfau-LTl-HDMQDKzmlLyb7xOm7Zw` → `Warszawski/05-Print-editions/`. Include Warszawski-named editions/production sources and shared editorial bundles/print notes. **Exclude standalone Chaikin editions and production sources**, including its research-reference edition even though that title contains “reference-edition.”

Use connected Google Drive tools and fresh authenticated download references. Never extract connector credentials or save transient transfer URLs. Preserve source IDs, modification times, sizes, local paths and hashes. `inventory/drive-snapshot.json` and `inventory/import-manifest.json` are the initial import baselines. Refresh affected records after verified changes; do not pretend an unresolved conflict has been imported.

## Each monitor run

1. Verify the checkout and exact expected remote. Check active editing tasks, timestamps and file stability. Do not stage work still being written by another task. Inspect stable changes before publishing them to this public repository.
2. Snapshot stable ignored assets. Commit completed local content changes and meaningful checksum changes with a descriptive message. Push pending local commits ordinarily. Fetch the remote and fast-forward only when compatible and safe. Preserve/report divergence instead of resetting or force-pushing.
3. Enumerate approved folders recursively, including new subfolders. Treat failed/truncated listings as incomplete. Compare IDs, modification times, sizes and paths with the baseline. Download only new/changed files. Record missing IDs for review without deleting local copies.
4. Stage incoming downloads under ignored `.import-tmp/`; verify full byte counts and SHA-256. Immediately before replacement, compare the local original with its previous imported checksum. If local and Drive both changed, or a file is active, preserve both versions and report the conflict. A Drive rename/move cannot erase a locally edited file.
5. For changed archives, safely expand to a temporary directory and compare each existing member against the prior member manifest before applying changes. Detect archives by content, including the disguised JSON ZIP. Preserve edited members. Generate affected text/inventory records separately; do not blindly re-index every historical archive or alter research claims as part of sync.
6. Commit the genuine completed changes, push, and verify local/remote hashes agree. No changes means no commit. Keep unchanged inventory data byte-stable. Record real failures/conflicts in `analysis/sync/` without repeated timestamp-only entries.

Stay quiet while nothing has meaningfully changed. Notify for an imported update, completed outside-edit sync, failure, or conflict needing attention. Continue monitoring after success until the user pauses or removes it.

## Setup verification

The initial setup on October 2, 2026 created public GitHub repository `themrsalesforce/warszawski-family-tree` and active thread monitor `sync-warszawski-family-tree`. A fresh recursive Drive enumeration matched all 229 imported files: no new, changed or missing files, with no listing errors. The binary manifest covers 298 local assets; an immediate repeat produced zero changed records and did not rewrite the manifest. The review check verified all 229 original hashes, 13 external snapshots, 39 unique review items and all local report links. These checks verify setup and preservation, not an implemented new edition.

## Manual verification

```sh
git status --short --branch
git remote -v
git fetch origin
git rev-parse HEAD origin/main
python3 scripts/snapshot_binary_state.py
```

Use `python3 scripts/check_review.py` for the October 2 review's preserved originals, coverage and page budget. That check is intentionally tied to the historical baseline, not a claim that a later regenerated edition still has 236 pages.

The monitor is periodic, not instantaneous, and requires the computer on with Codex running. [Official scheduled-task requirements](https://learn.chatgpt.com/docs/automations).
