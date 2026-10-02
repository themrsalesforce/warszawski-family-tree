# Warszawski Family Tree project instructions

The user requires this project to be a real public Git repository, with meaningful changes committed and kept synchronized with GitHub. This mirrors the Chaikin project's completed-work and on-demand update workflow; the Warszawski remote is public by explicit user request.

- Work in this checkout unless the task requires isolation. Canonical remote: `https://github.com/themrsalesforce/warszawski-family-tree.git`.
- After each completed edit or research task, run appropriate checks, inspect the diff, make a descriptive commit for the actual changes, push ordinarily, and verify the remote branch hash. Do not leave completed work only locally or ask again for routine commits/pushes.
- Every commit must represent a real content, code, data or asset-manifest change. No empty commits, no timestamp-only sync updates, and no commits when nothing changed.
- Preserve concurrent or unfinished edits. Stage only completed task changes; do not silently include another active task's work. Never reset, force-push, rewrite published history, or discard work to fix a synchronization conflict.
- Read these instructions, [SYNC.md](SYNC.md) and the current handoff when starting work or taking over from another chat. Before editing, inspect Git status and recent commits, fetch the expected remote, and fast-forward only when clean and compatible. Preserve unfinished work and resolve conflicts without discarding either version.
- Synchronization is on demand. When the user flags incoming updates or asks to sync, reconcile stable outside edits and approved inbound Drive changes using SYNC.md. The recurring monitor has been removed; do not recreate background polling unless explicitly requested.
- Finish a handoff by recording the source edition, changes made, checks, open items, output locations and pushed commit in the project folder. The next chat must read that record before reprocessing. Before publishing, exclude credentials, transient authenticated download references and temporary files.
- Original binary files remain local and in Drive and are ignored by Git. Their source metadata/checksums are tracked, including the ZIP disguised as a `.json` file. Do not claim GitHub stores their bytes.
- Drive synchronization is inbound only. Do not upload local edits to Drive without a separate instruction.
- Keep historical imports intact. Never blindly rerun `scripts/index_project.py` over edited expanded archives. Stage incoming versions temporarily and compare original/member hashes before applying changes.
- Preserve genealogical uncertainty and source attribution. Sync is not permission to merge candidate people or change historical facts.
- Shared cross-family material uses the same canonical Drive IDs as the Chaikin repository. Do not merge the two repositories' histories or replace one family's data with the other's snapshots.
