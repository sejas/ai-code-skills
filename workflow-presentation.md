---
marp: true
theme: default
_class: lead
paginate: true
backgroundColor: #fff
backgroundImage: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080"><defs><linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#667eea;stop-opacity:0.05" /><stop offset="100%" style="stop-color:#764ba2;stop-opacity:0.05" /></linearGradient></defs><rect width="1920" height="1080" fill="url(%23grad1)"/></svg>')
---

# Dev Workflow Plugin for Claude Code

## A Complete Development Automation System

---

# What's Included? 📦

## 9 Intelligent Hooks + 5 Powerful Skills

```
Hooks: Automated actions that run silently in background
Skills: User-invoked workflows with guided steps
```

---

# The Problem We're Solving

- ❌ Manual code formatting after every edit
- ❌ Inconsistent commit message formats
- ❌ Forgetting context between sessions
- ❌ Missing notifications when Claude needs input
- ❌ No structured development planning
- ❌ Manual PR description writing

---

# The Solution: Dev Workflow Plugin

✅ **Automation** - Hooks handle repetitive tasks
✅ **Best Practices** - Enforces standards automatically
✅ **Awareness** - Notifications keep you informed
✅ **Organization** - Intent-based development structure
✅ **Documentation** - Auto-generated PR descriptions
✅ **Productivity** - More time coding, less time managing

---

# Hook Lifecycle: The 5 Stages

```
┌─────────────────────────────────────────┐
│ 1️⃣  SESSION START → Git context injected     │
├─────────────────────────────────────────┤
│ 2️⃣  BEFORE TOOL → Commits validated         │
├─────────────────────────────────────────┤
│ 3️⃣  AFTER TOOL → Code formatted + announced │
├─────────────────────────────────────────┤
│ 4️⃣  NOTIFICATIONS → Desktop & phone alerts   │
├─────────────────────────────────────────┤
│ 5️⃣  SESSION END → Activity summarized        │
└─────────────────────────────────────────┘
```

---

# PreToolUse: commit-validator.sh

## Validates Before Execution

```bash
# ✅ Passes validation
feat: Add dark mode toggle to settings

# ❌ Fails - no prefix
Add dark mode toggle

# ❌ Fails - too long
fix: This is an extremely long commit message that goes way beyond the recommended length limit
```

**Enforces:**
- Conventional commit format (feat, fix, docs, etc.)
- Maximum 75 characters
- Blocks dangerous force commits (-f)

---

# PostToolUse (Part 1): auto-format.sh

## Automatic Code Formatting

```javascript
// ❌ Before (unformatted)
const x={a:1,b:2}; function foo(    ){return x}

// ✅ After (auto-formatted by Prettier)
const x = { a: 1, b: 2 };
function foo() {
  return x;
}
```

**Supports:**
- TypeScript/JavaScript (Prettier)
- PHP (PHPCBF with WordPress standards)

---

# PostToolUse (Part 2): speak-commit.sh

## Audio Feedback for Commits

```
🎤 "Feature commit to ai-code-skills.
   Added presentation skill to improve
   documentation workflow. Great work!"
```

**Benefits:**
- Audible confirmation of actions
- Different announcements per commit type
- Runs non-blocking in background

---

# SessionStart: session-context.sh

## Automatic Git Context Injection

```
📍 Current Branch: main
📝 Recent Commits:
  • feat: simplify plugin installation
  • feat: add presentation skill
  • docs: update with github.com/sejas/ai-code-skills
🚫 Uncommitted Changes:
  M .claude-plugin/plugin.json
  M README.md
```

---

# SessionEnd: Session Logging

## Two Options Available

### Option 1: Basic Logging
```
Simple activity log → ~/.claude/session-log.txt
Fast and lightweight
```

### Option 2: AI-Powered (save-summary.py)
```
Intelligent summarization → ~/.claude/session-logs/
Requires: Python 3 + claude-agent-sdk
```

---

# Notifications: notify.sh

## macOS Desktop Notifications

```
When Claude needs your attention:
• Permission requests
• Idle prompts (60+ seconds)
• Authentication events
```

**Trigger:** Automatically when action needed
**Tool:** terminal-notifier

---

# Notifications: remote-notify.sh

## Get Alerts on Your Phone

```
📱 Telegram
  CLAUDE_TELEGRAM_TOKEN
  CLAUDE_TELEGRAM_CHAT_ID

📱 ntfy.sh
  CLAUDE_NTFY_TOPIC
  (Mobile app or web)
```

**Configuration:** Via `.env` file (gitignored)

---

# Skill 1: /commit

## Intelligent Commit Message Generation

```
Usage: /commit

Action:
1. Analyzes staged changes
2. Determines commit type (feat, fix, docs, etc.)
3. Generates following conventions
4. Creates commit automatically
```

---

# Skill 2: /intent-start

## Begin Spec-Driven Development

```
Usage: /intent-start

Creates:
1. Problem statement
2. Solution approach
3. Requirements list
4. Success criteria

Output: Tracked in intent system
```

---

# Skill 3: /intent-finish

## Complete & Document Work

```
Usage: /intent-finish

Actions:
1. Marks intent as complete
2. Generates PR description
3. Includes context & requirements
4. Archives for reference
```

---

# Skill 4: /intent-list

## Track All Open Work

```
Usage: /intent-list

Shows:
✓ All active intents
✓ Progress status
✓ Current assignments
✓ Quick reference dashboard
```

---

# Skill 5: /presentation

## Generate Professional Slides

```
Usage: /presentation

Creates:
1. Marp presentation from intent spec
2. Professional formatting
3. Automatic slide generation
4. Ready to present or share
```

---

# Your Personal Configuration

### From ~/.claude/CLAUDE.md

```
✓ No online comments on GitHub
✓ Never commit/stage without approval
✓ Always provide diffs with suggestions
```

**Purpose:** Safety & professional standards

---

# Complete Workflow Example

```
1. Start session
   → Git context auto-injected

2. Plan work
   → /intent-start documents goal

3. Make changes
   → auto-format.sh formats code

4. Create commit
   → commit-validator.sh checks format
   → speak-commit.sh announces action

5. Get notified
   → notify.sh alerts when input needed

6. Finish intent
   → /intent-finish generates PR

7. Create demo
   → /presentation makes slides

8. End session
   → Session summary saved
```

---

# Installation

## One Command Setup

```bash
claude plugin install sejas/ai-code-skills
```

**What happens:**
- ✅ All 9 hooks configured
- ✅ All 5 skills registered
- ✅ MCP servers setup
- ✅ Permissions configured
- ✅ No manual steps needed!

---

# Requirements & Optional Tools

```
Essential:
• macOS
• Git
• Claude Code CLI

Optional (add features):
• Node.js/npm (formatting, presentations)
• PHP/Composer (PHP support)
• Python 3 (AI summaries)
• Telegram, ntfy.sh (phone notifications)
```

---

# Key Benefits Summary

```
⚙️  Automation     → No manual formatting/validation
📋 Best Practices → Standards enforced automatically
🔔 Awareness      → Know when Claude needs you
📦 Organization   → Intent-based structure
📚 Documentation  → Auto-generated PR descriptions
⚡ Productivity   → Focus on coding, not admin
```

---

# Real-World Scenario

```
Morning:
  1. Start Claude session
  2. Git context appears (session-context.sh)
  3. See last commits and uncommitted changes

During Work:
  4. Edit code → auto-formatted (auto-format.sh)
  5. Ready to commit → validation runs (commit-validator.sh)
  6. Commit → text-to-speech announces (speak-commit.sh)

Notifications:
  7. Phone buzzes with update (remote-notify.sh)
  8. Desktop notifies about permission (notify.sh)

Close Work:
  9. Finish intent → PR description generated (/intent-finish)
  10. Session saved when you close (save-summary-basic.sh)
```

---

# Customization Options

```
Edit Hook Scripts:
  git clone https://github.com/sejas/ai-code-skills.git
  vi hooks/commit-validator.sh
  claude --plugin-dir .

Configure Remote Notifications:
  cp .env.example .env
  # Add your Telegram or ntfy.sh credentials

Customize TTS Voice:
  Edit hooks/speak-commit.sh
  say -v Alex "Test"  # Male voice
  say -v Daniel "Test"  # British
```

---

# Project Structure

```
ai-code-skills/
├── .claude-plugin/
│   └── plugin.json           # Configuration
├── hooks/                    # 9 automated scripts
│   ├── commit-validator.sh
│   ├── auto-format.sh
│   ├── speak-commit.sh
│   ├── session-context.sh
│   ├── notify.sh
│   └── ...
├── commands/                 # 5 skills
│   ├── commit/
│   ├── intent-start/
│   ├── intent-finish/
│   ├── intent-list/
│   └── presentation/
└── README.md
```

---

# The Philosophy

## Bridge AI and Professional Development

```
Raw AI Capability
        ↓
    + Hooks (Automation)
    + Skills (Structure)
    + Standards (Best Practices)
    + Notifications (Awareness)
        ↓
Professional Development Workflow
```

---

# Getting Started Next Steps

1. ✅ Plugin installed and configured
2. 📖 Review workflow-overview.html
3. 🚀 Start with `/intent-start` on next project
4. 🔔 Configure remote notifications if needed
5. 📱 Share presentation with team using `/presentation`
6. 🎯 Adopt intent-driven development

---

# Resources

```
📚 Documentation
   github.com/sejas/ai-code-skills

🔗 View Configuration
   cat .claude-plugin/plugin.json

📖 This Overview
   workflow-overview.html

🎯 Your Settings
   ~/.claude/CLAUDE.md

💬 For Help
   /help in Claude Code
```

---

# Questions?

## Dev Workflow Plugin v0.2.0

**By:** Antonio Sejas
**License:** MIT
**Updated:** January 2026

```
Ready to supercharge your development workflow? 🚀
Start with: /intent-start
```

---

# Appendix: Hook Reference Table

| Hook | Type | When | Purpose |
|------|------|------|---------|
| commit-validator.sh | PreToolUse | Before commits | Validates format |
| auto-format.sh | PostToolUse | After edits | Auto-formats code |
| speak-commit.sh | PostToolUse | After commits | Audio announcement |
| session-context.sh | SessionStart | Session begins | Git context |
| save-summary-basic.sh | SessionEnd | Session ends | Activity log |
| save-summary.py | SessionEnd | Session ends | AI summary |
| notify.sh | Notification | On events | Desktop alerts |
| remote-notify.sh | Notification | On events | Phone alerts |

---

# Appendix: Skill Reference

| Skill | Invocation | Purpose |
|-------|-----------|---------|
| commit | /commit | Generate commit message |
| intent-start | /intent-start | Begin tracked feature |
| intent-finish | /intent-finish | Complete & document |
| intent-list | /intent-list | View all open intents |
| presentation | /presentation | Create Marp slides |
