#!/usr/bin/env python3
"""backup-dedup.py — group WordPress/Studio/Jetpack backups by site, keep the
latest of each, and emit a MOVE list (latest per site) + DELETE list (older or
redundant same-site copies).

Backups are identified by name patterns (studio-backup-*, jetpack-backup-*,
*.wpress, aiowpm*, *wpcomstaging*). The trailing -YYYY-MM-DD-HH-MM-SS timestamp
is stripped to derive site identity; the newest timestamp per site is kept.

Usage:
    backup-dedup.py <root> [<root> ...]

Writes:
    /tmp/backup_move.txt    (newline-separated full paths — feed to offload-retry.sh)
    /tmp/backup_delete.txt  (older/redundant — trash after move verifies)

Then:
    while IFS= read -r p || [ -n "$p" ]; do SRCS+=("$p"); done < /tmp/backup_move.txt
    ssh <alias> "mkdir -p studio-wordpress-backups"
    offload-retry.sh <alias>:studio-wordpress-backups/ "${SRCS[@]}"
"""
import os, re, subprocess, sys
from collections import defaultdict

INCLUDE = re.compile(r"(studio-backup|jetpack-backup|\.wpress$|aiowpm|aiowpmigration|wpcomstaging)", re.I)
EXCLUDE = re.compile(r"(claude-backup|Uptime_Kuma|backupurl\.diff|jetpack-beta|^jetpack\.zip$|"
                     r"backups-content-model|backup-files|import log|\.png$|\.rtf$|\.pdf$|_files$)", re.I)
TS = re.compile(r"-(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})")

def du(path):
    try:
        return int(subprocess.check_output(["du","-sk",path], stderr=subprocess.DEVNULL).split()[0]) * 1024
    except Exception:
        return 0

def human(n):
    for u in "BKMGT":
        if n < 1024: return f"{n:.0f}{u}"
        n /= 1024
    return f"{n:.0f}P"

def collect(roots):
    items = []
    for root in roots:
        for dp, dirs, files in os.walk(root):
            if dp[len(root):].count(os.sep) >= 2:
                dirs[:] = []
            for name in list(files) + list(dirs):
                if EXCLUDE.search(name) or not INCLUDE.search(name):
                    continue
                items.append(os.path.join(dp, name))
    items = sorted(set(items))
    # drop nested entries whose ancestor is itself a matched backup
    return [p for p in items if not any(p != q and p.startswith(q + os.sep) for q in items)]

def site_key(path):
    base = re.sub(r"\.(sql|zip|tar\.gz|tgz|wpress)$", "", os.path.basename(path), flags=re.I)
    m = TS.search(base)
    return TS.sub("", base), (m.group(1) if m else "0000-00-00-00-00-00")

def main(roots):
    groups = defaultdict(list)
    for p in collect(roots):
        k, ts = site_key(p)
        groups[k].append((ts, p))

    move, delete = [], []
    for lst in groups.values():
        lst.sort()
        latest = lst[-1][0]
        keepers = [p for ts, p in lst if ts == latest]
        delete += [p for ts, p in lst if ts != latest]
        if len(keepers) > 1:                       # same ts, multiple formats -> keep largest
            keepers.sort(key=du)
            move.append(keepers[-1]); delete += keepers[:-1]
        else:
            move.append(keepers[0])

    msz, dsz = sum(map(du, move)), sum(map(du, delete))
    print(f"=== SITES {len(groups)} | MOVE {len(move)} ({human(msz)}) | DELETE {len(delete)} ({human(dsz)}) ===\n")
    print("--- MOVE (latest per site) ---")
    for p in sorted(move): print(f"  {human(du(p)):>6}  {p}")
    print("\n--- DELETE (older/redundant) ---")
    for p in sorted(delete): print(f"  {human(du(p)):>6}  {p}")
    open("/tmp/backup_move.txt","w").write("\n".join(move))
    open("/tmp/backup_delete.txt","w").write("\n".join(delete))
    print(f"\nWrote /tmp/backup_move.txt ({len(move)}) and /tmp/backup_delete.txt ({len(delete)}).")
    print(f"Potential reclaim if both actioned: {human(msz+dsz)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: backup-dedup.py <root> [<root> ...]")
    main([os.path.expanduser(r) for r in sys.argv[1:]])
