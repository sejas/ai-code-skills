# Mac Cleanup Playbook — categories & decision rules

Categorize every hog before touching it. Four buckets, different handling.

## 1. Regenerable caches — delete freely, zero risk

Tools re-fetch on next use. No confirmation needed beyond a heads-up.

| Path | Notes |
|---|---|
| `~/.npm` | `npm cache clean --force` (frees in place, no trash) |
| `~/.cache` | build caches |
| `~/Library/Caches/ms-playwright` | re-downloads browsers |
| `~/Library/Caches/{electron,typescript,Cypress,Yarn,node-gyp,pip}` | all regenerable |
| `~/Library/Caches/<browser>` | browser disk cache (not profile) |
| `node_modules` (×N) | `npm/yarn/pnpm install` rebuilds — but ASK; can be 30G+ and slow to reinstall |
| Docker | `docker system prune -a --volumes` (daemon must be running). `Docker.raw` auto-shrinks on APFS after prune |

## 2. App data / models — low risk, confirm

Re-downloads or regenerates, but may carry user state.

| Path | Keep vs clean |
|---|---|
| `~/Library/Application Support/<app>/Cache` | safe |
| Claude Desktop `vm_bundles` | sandbox VM images, re-download |
| MacWhisper `models` | re-downloadable. **Keep `Database`** (transcript history) |
| Browser `Application Support/<browser>` | profile = history/passwords. Only clear the Cache subdir |

## 3. Personal / irreplaceable media — OFFLOAD, never delete

Photos, videos, wedding/travel archives. Move to remote storage, verify, then remove local.

- Use `scripts/offload-retry.sh <alias>:pictures/ <src>` (removes local only after verified transfer).
- For 360 footage: `.insv`/`.insp`/`.dng` are originals — keep; `.lrv` are low-res proxies — safe to drop (editor regenerates).
- Always verify on remote (file count + `du -sh`) before trusting the local deletion.

## 4. Backups — keep one latest per site, offload it

WordPress/Studio/Jetpack site backups accumulate many timestamped copies.

- Run `scripts/backup-dedup.py <roots...>` → groups by site, picks latest, writes move/delete lists.
- Offload the move list to `<alias>:studio-wordpress-backups/`.
- Trash the delete list (older/redundant) after the move verifies.

## Decision flow

1. `scan-disk.sh` → ranked hogs.
2. Tag each hog into bucket 1–4.
3. Bucket 1: clean immediately (mention it). Bucket 2–4: confirm with user, especially anything >10G or personal.
4. Offload buckets 3–4 with retry script; clean buckets 1–2.
5. Trash, then prompt to empty Trash (space isn't reclaimed until emptied).
6. Re-run `scan-disk.sh`; report before/after free space.

## What to NEVER auto-delete

- Anything in bucket 3 (personal media) without an offload+verify first.
- Parallels/VMware VM images (`Group Containers/*parallels*`, `*.pvm`) — large but often in active use. Always ask.
- `~/Library/Mobile Documents` (iCloud Drive local mirror) — deleting affects synced data.
- A whole app's `Application Support` dir — strip only caches/models, not state DBs.
