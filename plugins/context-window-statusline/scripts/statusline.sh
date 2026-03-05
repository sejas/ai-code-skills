#!/usr/bin/env bash
# Claude Code Status Line — Context Window Visualizer
# Reads JSON session data from stdin and displays a context window progress bar
#
# Install: Copy to ~/.claude/statusline.sh
# Configure in ~/.claude/settings.json:
#   "statusLine": { "type": "command", "command": "~/.claude/statusline.sh", "padding": 1 }

DATA=$(cat)

# Extract fields with jq
MODEL=$(echo "$DATA" | jq -r '.model.display_name // "..."')
USED_PCT=$(echo "$DATA" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
REMAINING_PCT=$(echo "$DATA" | jq -r '.context_window.remaining_percentage // 100' | cut -d. -f1)
INPUT_TOKENS=$(echo "$DATA" | jq -r '.context_window.current_usage.input_tokens // 0')
OUTPUT_TOKENS=$(echo "$DATA" | jq -r '.context_window.current_usage.output_tokens // 0')
CACHE_READ=$(echo "$DATA" | jq -r '.context_window.current_usage.cache_read_input_tokens // 0')
CACHE_WRITE=$(echo "$DATA" | jq -r '.context_window.current_usage.cache_creation_input_tokens // 0')
WINDOW_SIZE=$(echo "$DATA" | jq -r '.context_window.context_window_size // 200000')
TOTAL_COST=$(echo "$DATA" | jq -r '.cost.total_cost_usd // 0')
TOTAL_DURATION=$(echo "$DATA" | jq -r '.cost.total_duration_ms // 0')
API_DURATION=$(echo "$DATA" | jq -r '.cost.total_api_duration_ms // 0')
LINES_ADDED=$(echo "$DATA" | jq -r '.cost.total_lines_added // 0')
LINES_REMOVED=$(echo "$DATA" | jq -r '.cost.total_lines_removed // 0')

# ANSI Colors
RESET="\033[0m"
BOLD="\033[1m"
DIM="\033[2m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
CYAN="\033[36m"
MAGENTA="\033[35m"
WHITE="\033[37m"

# Color based on context usage
if [ "$USED_PCT" -ge 90 ]; then
    BAR_COLOR="$RED"
    PCT_LABEL="${RED}${BOLD}${USED_PCT}%${RESET}"
elif [ "$USED_PCT" -ge 70 ]; then
    BAR_COLOR="$YELLOW"
    PCT_LABEL="${YELLOW}${BOLD}${USED_PCT}%${RESET}"
elif [ "$USED_PCT" -ge 40 ]; then
    BAR_COLOR="$CYAN"
    PCT_LABEL="${CYAN}${USED_PCT}%${RESET}"
else
    BAR_COLOR="$GREEN"
    PCT_LABEL="${GREEN}${USED_PCT}%${RESET}"
fi

# Build progress bar (20 chars wide)
BAR_WIDTH=20
FILLED=$((USED_PCT * BAR_WIDTH / 100))
EMPTY=$((BAR_WIDTH - FILLED))
BAR="${BAR_COLOR}"
for ((i = 0; i < FILLED; i++)); do BAR+="█"; done
BAR+="${DIM}"
for ((i = 0; i < EMPTY; i++)); do BAR+="░"; done
BAR+="${RESET}"

# Format token counts
format_tokens() {
    local t=$1
    if [ "$t" -ge 1000000 ]; then
        printf "%.1fM" "$(echo "scale=1; $t/1000000" | bc)"
    elif [ "$t" -ge 1000 ]; then
        printf "%.1fk" "$(echo "scale=1; $t/1000" | bc)"
    else
        echo "$t"
    fi
}

INPUT_FMT=$(format_tokens "$INPUT_TOKENS")
OUTPUT_FMT=$(format_tokens "$OUTPUT_TOKENS")
CACHE_READ_FMT=$(format_tokens "$CACHE_READ")
WINDOW_FMT=$(format_tokens "$WINDOW_SIZE")

# Format duration
format_duration() {
    local ms=$1
    local secs=$((ms / 1000))
    local mins=$((secs / 60))
    local hrs=$((mins / 60))
    if [ "$hrs" -gt 0 ]; then
        printf "%dh%02dm" "$hrs" "$((mins % 60))"
    elif [ "$mins" -gt 0 ]; then
        printf "%dm%02ds" "$mins" "$((secs % 60))"
    else
        printf "%ds" "$secs"
    fi
}

DURATION_FMT=$(format_duration "$TOTAL_DURATION")
API_DURATION_FMT=$(format_duration "$API_DURATION")

# Format cost
if [ "$(echo "$TOTAL_COST > 0" | bc -l 2>/dev/null)" = "1" ]; then
    COST_FMT=$(printf "$%.4f" "$TOTAL_COST")
else
    COST_FMT="\$0.00"
fi

# Line 1: Model + Context bar + Tokens
printf '%b' "${BOLD}${MAGENTA}${MODEL}${RESET} ${DIM}│${RESET} ${BAR} ${PCT_LABEL} ${DIM}(${INPUT_FMT}in ${OUTPUT_FMT}out ${DIM}cached:${RESET}${DIM}${CACHE_READ_FMT})${RESET} ${DIM}of ${WINDOW_FMT}${RESET}"
echo

# Line 2: Cost + Duration + Lines changed
printf '%b' "${DIM}${WHITE}💰${RESET} ${CYAN}${COST_FMT}${RESET} ${DIM}│${RESET} ${DIM}⏱${RESET}  ${WHITE}${DURATION_FMT}${RESET} ${DIM}(api: ${API_DURATION_FMT})${RESET} ${DIM}│${RESET} ${GREEN}+${LINES_ADDED}${RESET} ${RED}-${LINES_REMOVED}${RESET}"
echo
