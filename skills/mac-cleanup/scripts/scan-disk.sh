#!/bin/bash
# scan-disk.sh — read-only disk-hog scan for Mac cleanup.
# Prints free space + ranked space consumers across common locations.
# Safe: never deletes or moves anything.
#
# Usage: scan-disk.sh [home_dir]   (defaults to $HOME)
set -u
H="${1:-$HOME}"

hr() { printf '%s\n' "------------------------------------------------------------"; }
top() { du -sh "$@"/* 2>/dev/null | sort -rh | head -"${TOPN:-12}"; }

echo "=== DISK ==="
df -h "$H" | tail -1

hr; echo "=== TOP-LEVEL \$HOME (top 15) ==="
du -sh "$H"/* 2>/dev/null | sort -rh | head -15

hr; echo "=== Library hogs ==="
du -sh "$H/Library/Group Containers" "$H/Library/Application Support" \
       "$H/Library/Caches" "$H/Library/Containers" "$H/Library/Mobile Documents" 2>/dev/null | sort -rh

hr; echo "=== Group Containers detail (Parallels/VMs often hide here) ==="
du -sh "$H/Library/Group Containers"/* 2>/dev/null | sort -rh | head -8

hr; echo "=== Application Support detail ==="
du -sh "$H/Library/Application Support"/* 2>/dev/null | sort -rh | head -12

hr; echo "=== Caches detail (mostly regenerable) ==="
du -sh "$H/Library/Caches"/* 2>/dev/null | sort -rh | head -12

hr; echo "=== Package-manager caches (regenerable) ==="
du -sh "$H/.npm" "$H/.cache" "$H/.bun" "$H/.gradle" "$H/.cocoapods" \
       "$H/Library/pnpm" "$H/Library/Caches/pnpm" 2>/dev/null | sort -rh

hr; echo "=== Docker (Docker.raw allocated vs real du) ==="
DRAW="$H/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw"
[ -f "$DRAW" ] && { ls -lh "$DRAW" | awk '{print "allocated:", $5}'; du -sh "$DRAW" 2>/dev/null | awk '{print "real:", $1}'; } || echo "  no Docker.raw"

hr; echo "=== node_modules total (Documents + worktrees) ==="
find "$H/Documents" "$H/worktrees.nosync" -type d -name node_modules -prune 2>/dev/null \
  -exec du -sk {} + 2>/dev/null | awk '{s+=$1} END {printf "  %.1f GB (regenerable)\n", s/1048576}'

hr; echo "=== Downloads detail ==="
du -sh "$H/Downloads"/* 2>/dev/null | sort -rh | head -12

hr; echo "=== Trash (reclaims only after emptying) ==="
du -sh "$H/.Trash" 2>/dev/null || echo "  ~/.Trash not readable (no Full Disk Access) — empty via Finder"

hr; echo "Done. Categorize before deleting — see references/cleanup-playbook.md"
