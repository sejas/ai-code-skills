# macOS cleanup quirks (hard-won)

Gotchas that silently break cleanup scripts on stock macOS.

## Shell & tools

- **Default shell is bash 3.2** — no `mapfile`/`readarray`. Read file lists with:
  ```bash
  SRCS=(); while IFS= read -r p || [ -n "$p" ]; do [ -n "$p" ] && SRCS+=("$p"); done < list.txt
  ```
  The `|| [ -n "$p" ]` captures the last line when the file has no trailing newline.

- **macOS ships openrsync**, not GNU rsync. It **rejects `--append-verify`** (prints a usage dump, exits non-zero). Stick to `-avP --remove-source-files --timeout=120`. Verify with `rsync --version` (shows `openrsync`).

- **`grep` may be aliased to `ugrep`** in some setups — `\|` alternation breaks. Avoid piping rsync through grep filters; log to a file and read the tail instead.

## Deletion & Trash

- **`rm` / `rmdir` are often blocked** by the agent permission policy. The **`trash` CLI is allowed** (`brew install trash`). Prefer it — it's also recoverable.
- **Trash does not reclaim space** until emptied; it lives on the same APFS volume.
- **`~/.Trash` is not shell-readable** without Full Disk Access (`Operation not permitted`). Empty via Finder, or:
  ```bash
  osascript -e 'tell application "Finder" to empty trash'
  ```
  This empties **everything** in Trash — warn the user first (irreversible, includes pre-existing items).
- `--remove-source-files` deletes transferred **files** but leaves **empty directory shells**. After a directory move, verify `find <dir> -type f | wc -l` is 0, then `trash` the shell.

## SSH / Storage Box (Hetzner)

- Long transfers drop with `io_read_blocking` / exit 255 — wrap rsync in an `until ... done` retry loop with `ServerAliveInterval=20`.
- **Sub-accounts support SSH keys.** Install with `ssh-copy-id -s -i <key>.pub <alias>` — the **`-s` (SFTP mode) is required**; plain mode fails on Storage Box.
- Ports: 22/23 SSH/SFTP, 445 SMB. Config alias example:
  ```
  Host storagebox
      HostName uXXXXXX-subN.your-storagebox.de
      User uXXXXXX-subN
      Port 23
      IdentityFile ~/.ssh/id_hetzner
      IdentitiesOnly yes
      ServerAliveInterval 30
  ```
- The "not using a post-quantum key exchange" warning is noise — filter it from logs.

## Docker

- `docker system df` shows reclaimable; `docker system prune -a --volumes -f` clears it. Daemon must be running (`open -a Docker`, then poll `docker info`).
- `Docker.raw` is a sparse image; after prune it auto-trims on APFS (e.g. 20G → ~400M) without manual compaction.

## Background long transfers

- Offloading 100G+ can run for hours/overnight. Launch with `run_in_background`, use the retry loop, and report on completion rather than blocking.
- Don't let the source disk fill during a copy-then-delete; `--remove-source-files` is safer than plain copy when free space is tight (frees as it goes).
