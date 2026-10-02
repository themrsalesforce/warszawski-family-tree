# Warszawski Family Tree project instructions

The user requires this project to be a real public Git repository, with meaningful changes committed and kept synchronized with GitHub. This mirrors the Chaikin project's completed-work and Drive-monitoring workflow; the Warszawski remote is public by explicit user request.

- Work in this checkout unless the task requires isolation. Canonical remote: `https://github.com/themrsalesforce/warszawski-family-tree.git`.
- After each completed edit or research task, run appropriate checks, inspect the diff, make a descriptive commit for the actual changes, push ordinarily, and verify the remote branch hash. Do not leave completed work only locally or ask again for routine commits/pushes.
- Every commit must represent a real content, code, data or asset-manifest change. No empty commits, no timestamp-only monitoring updates, and no commits when nothing changed.
- Preserve concurrent or unfinished edits. Stage only completed task changes; do not silently include another active task's work. Never reset, force-push, rewrite published history, or discard work to fix a synchronization conflict.
- Follow [SYNC.md](SYNC.md) for stable outside edits, remote updates, approved inbound Drive refreshes and conflict preservation. Before publishing, exclude credentials, transient authenticated download references and temporary files.
- Original binary files remain local and in Drive and are ignored by Git. Their source metadata/checksums are tracked, including the ZIP disguised as a `.json` file. Do not claim GitHub stores their bytes.
- Drive synchronization is inbound only. Do not upload local edits to Drive without a separate instruction.
- Keep historical imports intact. Never blindly rerun `scripts/index_project.py` over edited expanded archives. Stage incoming versions temporarily and compare original/member hashes before applying changes.
- Preserve genealogical uncertainty and source attribution. Sync is not permission to merge candidate people or change historical facts.
- Shared cross-family material uses the same canonical Drive IDs as the Chaikin repository. Do not merge the two repositories' histories or replace one family's data with the other's snapshots.
