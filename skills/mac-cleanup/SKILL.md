---
name: mac-cleanup
description: This skill should be used when the user asks to "clean up my Mac", "free disk space", "my disk is full", "what's taking up space", "reclaim storage", "offload files", or wants to dedupe/archive backups and media to remote storage. Provides a scan → categorize → offload/clean → reclaim workflow with tested scripts and macOS-specific gotchas.
version: 0.1.0
---

# Mac Cleanup

Free disk space on macOS safely: find the real space hogs, sort them into
risk buckets, offload irreplaceable data to remote storage, delete only what
regenerates, and actually reclaim the space. Built for stock macOS (bash 3.2,
openrsync, permission-restricted `rm`, `trash` CLI) and Hetzner Storage Box
offload.

## Iron rules

1. **Scan before deleting.** Never guess what's big — measure.
2. **Categorize before touching.** Every hog is regenerable cache, app data,
   personal media, or a backup. Handling differs (see
   `references/cleanup-playbook.md`).
3. **Offload, don't delete, irreplaceable media.** Copy to remote, verify on the
   remote, *then* remove local.
4. **Confirm anything personal or >10G.** VMs, photo archives, large app data.
5. **Reclaim is not done until Trash is emptied.** `trash` frees nothing on its own.

## Workflow

### 1. Scan

Run the read-only scanner:

```bash
bash ~/.claude/skills/mac-cleanup/scripts/scan-disk.sh
```

It reports free space and ranked consumers across `$HOME`, `Library/Group
Containers` (Parallels VMs hide here), `Application Support`, `Caches`, package
caches, Docker, `node_modules`, `Downloads`, and Trash.

### 2. Categorize

Sort each hog using `references/cleanup-playbook.md`:

- **Regenerable caches** (npm, .cache, playwright, electron, typescript, Docker
  images) → clean immediately, just announce it.
- **App data / models** (Claude vm_bundles, Whisper models, browser caches) →
  low risk, confirm; keep state DBs.
- **Personal media** (photos, video, wedding/travel archives) → offload only.
- **Backups** (studio/jetpack/.wpress) → keep one latest per site, offload it.

### 3. Offload personal media + backups

Set up the remote once (Hetzner Storage Box — see `references/macos-quirks.md`
for `ssh-copy-id -s`). Create the remote dir, then use the retry-loop offloader
(survives SSH drops, removes local only after each file verifies):

```bash
ssh <alias> "mkdir -p pictures"
bash ~/.claude/skills/mac-cleanup/scripts/offload-retry.sh <alias>:pictures/ ~/Documents/photos-disk
```

For backups, dedupe first — keep latest per site:

```bash
python3 ~/.claude/skills/mac-cleanup/scripts/backup-dedup.py ~/Downloads
# writes /tmp/backup_move.txt (latest per site) + /tmp/backup_delete.txt (older)
ssh <alias> "mkdir -p studio-wordpress-backups"
SRCS=(); while IFS= read -r p || [ -n "$p" ]; do [ -n "$p" ] && SRCS+=("$p"); done < /tmp/backup_move.txt
bash ~/.claude/skills/mac-cleanup/scripts/offload-retry.sh <alias>:studio-wordpress-backups/ "${SRCS[@]}"
```

Run long transfers in the background and report on completion.

### 4. Clean regenerable caches

```bash
npm cache clean --force
docker system prune -a --volumes -f      # daemon must be running
```

For cache directories, use `trash` (not `rm` — usually blocked):

```bash
trash ~/.cache ~/Library/Caches/{ms-playwright,electron,typescript,Cypress,Yarn,node-gyp,pip}
```

### 5. Verify + reclaim

- After any directory move, confirm sources emptied: `find <dir> -type f | wc -l` → 0,
  then `trash` the empty shells.
- Verify offloaded data landed: `ssh <alias> "du -sh <remote>/*"`.
- Trash holds the freed space until emptied. Offer to empty (irreversible, clears
  ALL trash):
  ```bash
  osascript -e 'tell application "Finder" to empty trash'
  ```
- Re-run `scan-disk.sh`; report before/after free space.

## Critical macOS gotchas

Read `references/macos-quirks.md` before scripting. Highlights:

- **bash 3.2**: no `mapfile`; read lists with `while IFS= read -r p || [ -n "$p" ]`.
- **openrsync**: rejects `--append-verify`; use `-avP --remove-source-files --timeout=120`.
- **`rm`/`rmdir` blocked**, `trash` allowed; `~/.Trash` not shell-readable.
- **SSH drops** on long transfers → retry loop (built into `offload-retry.sh`).
- **`Docker.raw`** auto-shrinks on APFS after prune.

## Resources

- `scripts/scan-disk.sh` — read-only hog scanner.
- `scripts/offload-retry.sh` — rsync-to-remote with SSH-drop retry + verified local removal.
- `scripts/backup-dedup.py` — group WP/Studio backups by site, emit move/delete lists.
- `references/cleanup-playbook.md` — the four buckets + decision flow + never-delete list.
- `references/macos-quirks.md` — bash/openrsync/trash/SSH/Docker specifics.
