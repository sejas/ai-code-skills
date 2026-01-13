#!/bin/bash

# Hook: speak-commit.sh
# Type: PostToolUse (after git commit)
# Description: Speaks repository name and commit message after successful commits

# Read stdin (contains the tool output)
input=$(cat)

# Check if this was a git commit command
if ! echo "$input" | grep -q "git commit"; then
    echo "$input"
    exit 0
fi

# Get the repository name (basename of git root directory)
repo_name=$(git rev-parse --show-toplevel 2>/dev/null | xargs basename)

if [ -z "$repo_name" ]; then
    repo_name="unknown repository"
fi

# Get the last commit message (first line only for brevity)
commit_msg=$(git log -1 --pretty=format:"%s" 2>/dev/null)

if [ -z "$commit_msg" ]; then
    # If we can't get the commit message, just announce the repo
    say "Commit made to $repo_name" &
else
    # Extract the commit type and description for better speech
    # Handle conventional commit format: "type: description"
    if echo "$commit_msg" | grep -q ":"; then
        commit_type=$(echo "$commit_msg" | cut -d: -f1 | tr '[:upper:]' '[:lower:]')
        commit_desc=$(echo "$commit_msg" | cut -d: -f2- | sed 's/^[[:space:]]*//')

        # Make it sound more natural
        case "$commit_type" in
            feat)
                announcement="Feature added to $repo_name: $commit_desc"
                ;;
            fix)
                announcement="Bug fixed in $repo_name: $commit_desc"
                ;;
            docs)
                announcement="Documentation updated in $repo_name: $commit_desc"
                ;;
            chore)
                announcement="Chore completed in $repo_name: $commit_desc"
                ;;
            refactor)
                announcement="Code refactored in $repo_name: $commit_desc"
                ;;
            test)
                announcement="Tests added to $repo_name: $commit_desc"
                ;;
            style)
                announcement="Code styled in $repo_name: $commit_desc"
                ;;
            *)
                announcement="Committed to $repo_name: $commit_msg"
                ;;
        esac
    else
        announcement="Committed to $repo_name: $commit_msg"
    fi

    # Speak in background so it doesn't block
    # Use a pleasant voice (Samantha is default female voice on macOS)
    say -v Samantha "$announcement" &
fi

# Pass through the original output
echo "$input"
