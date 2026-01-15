# Claude with tmux
c() {
  local session="${PWD##*/}"
  [[ $# -gt 0 && ! "$1" =~ ^- ]] && { session="$1"; shift; }

  tmux has-session -t "$session" 2>/dev/null ||
    tmux new-session -d -s "$session" "claude $*"

  tmux attach-session -t "$session"
}

# Run tmux ls if IPHONE environment variable is set to true
if [[ "$IPHONE" == "true" ]]; then
  tmux new-session \; choose-session
fi
