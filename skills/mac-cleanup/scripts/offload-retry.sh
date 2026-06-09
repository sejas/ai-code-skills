#!/bin/bash
# offload-retry.sh — rsync large/irreplaceable files to a remote (e.g. Hetzner
# Storage Box) with an auto-retry loop that survives SSH drops on long transfers.
#
# Tuned for macOS openrsync + bash 3.2. Removes each local source file ONLY
# after rsync confirms it transferred (frees disk as it goes). Set KEEP=1 to
# copy without deleting.
#
# Usage:
#   offload-retry.sh <dest>  <src> [<src> ...]
#   KEEP=1 offload-retry.sh <dest> <src> ...     # copy only, keep locals
#
# Examples:
#   offload-retry.sh storagebox:pictures/ ~/Documents/photos-disk
#   offload-retry.sh storagebox:studio-wordpress-backups/ "$(cat list.txt)"
#
# Notes:
#   - <dest> is an ssh-config alias + remote path. Create the remote dir first:
#       ssh <alias> "mkdir -p <path>"
#   - Multiple sources flatten into <dest> by basename (no path collisions).
#   - Directory sources leave empty shells after move — trash them after.
set -u

[ $# -lt 2 ] && { echo "usage: $0 <alias:dest/path> <src> [src...]" >&2; exit 2; }
DEST="$1"; shift
SRCS=("$@")

REMOVE="--remove-source-files"
[ "${KEEP:-0}" = "1" ] && REMOVE=""

echo ">>> ${#SRCS[@]} source(s) -> $DEST  (KEEP=${KEEP:-0})"
n=0
until rsync -avP $REMOVE --timeout=120 \
  -e "ssh -o ServerAliveInterval=20 -o ServerAliveCountMax=5" \
  "${SRCS[@]}" "$DEST" ; do
  n=$((n+1))
  echo ">>> rsync dropped (attempt $n) — retry in 10s..."
  [ "$n" -ge 80 ] && { echo ">>> GAVE UP after 80 retries"; exit 1; }
  sleep 10
done
echo ">>> OFFLOAD COMPLETE after $n retries"
