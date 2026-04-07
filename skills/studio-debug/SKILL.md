---
name: studio-debug
description: Debug WordPress Studio local sites — inspect SQLite database, check logs, troubleshoot plugins/themes, and diagnose common issues in the Studio local environment.
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - Task
  - AskUserQuestion
---

# Studio Debug

You are helping the user debug a WordPress site running in the **WordPress Studio** local environment.

## Environment Context

- **Runtime:** WordPress Studio (Electron-based local WordPress)
- **Database:** SQLite via `sqlite-database-integration` mu-plugin
- **DB file:** `wp-content/database/.ht.sqlite`
- **No MySQL/MariaDB** — all queries go through the SQLite translation layer
- **PHP runs** via the bundled PHP within Studio

## Workflow

1. **Identify the site directory**
   - Check if the user provided a path or if the current working directory is a WordPress site
   - Look for `wp-config.php` and `wp-content/database/.ht.sqlite` to confirm it's a Studio site
   - If ambiguous, ask the user which site to debug

2. **Understand the problem**
   - Ask the user what issue they're experiencing if not already clear
   - Common categories: white screen, plugin error, theme issue, database corruption, REST API failure, slow performance, PHP errors

3. **Gather diagnostics** (run relevant checks in parallel where possible)

   ### PHP Error Logs
   - Check `wp-content/debug.log` if it exists
   - Check for `define('WP_DEBUG', true)` and `define('WP_DEBUG_LOG', true)` in `wp-config.php`
   - If debug logging is not enabled, suggest enabling it and offer the diff

   ### Database Inspection
   - Use `sqlite3` CLI to query the SQLite database directly:
     ```
     sqlite3 wp-content/database/.ht.sqlite
     ```
   - Useful queries:
     - `.tables` — list all tables
     - `SELECT option_name, option_value FROM wp_options WHERE option_name IN ('siteurl', 'home', 'active_plugins', 'stylesheet', 'template');` — core site settings
     - `SELECT option_name, option_value FROM wp_options WHERE option_name = 'active_plugins';` — check active plugins (PHP serialized)
     - `PRAGMA integrity_check;` — check database health
     - `PRAGMA table_info(wp_options);` — inspect table schema
   - Always quote the database path and use `-readonly` flag when just reading

   ### Plugin & Theme State
   - Read `wp-content/database/.ht.sqlite` active_plugins option to see what's active
   - Check `wp-content/plugins/` for installed plugins
   - Check `wp-content/themes/` for installed themes
   - Look for fatal errors in plugin/theme code if suspected

   ### WordPress Configuration
   - Read `wp-config.php` for misconfigurations
   - Check for conflicting constants or wrong paths
   - Verify `DB_DIR` and `DB_FILE` constants if present

   ### SQLite Integration Health
   - Check `wp-content/mu-plugins/` for the SQLite integration plugin files
   - Look for `wp-content/db.php` drop-in — this is critical for SQLite to work
   - Verify the SQLite integration version

   ### File Permissions & Structure
   - Verify `wp-content/database/` directory exists and is writable
   - Check `.ht.sqlite` file size (0 bytes = likely corrupted/empty)
   - Look for `.ht.sqlite-journal` or `.ht.sqlite-wal` files (WAL mode indicators)

4. **Diagnose and report**
   - Summarize findings clearly
   - Highlight the root cause if identifiable
   - Provide actionable fix suggestions with diffs when modifying files

5. **Fix (if requested)**
   - For database issues: provide SQL commands to run
   - For config issues: show diffs of wp-config.php changes
   - For plugin issues: suggest deactivation via database if WP admin is inaccessible:
     ```sql
     UPDATE wp_options SET option_value = 'a:0:{}' WHERE option_name = 'active_plugins';
     ```
   - For theme issues: reset to default theme via database:
     ```sql
     UPDATE wp_options SET option_value = 'twentytwentyfive' WHERE option_name = 'stylesheet';
     UPDATE wp_options SET option_value = 'twentytwentyfive' WHERE option_name = 'template';
     ```

## Common Studio Debug Scenarios

### White Screen of Death (WSOD)
1. Enable WP_DEBUG in wp-config.php
2. Check debug.log
3. Try deactivating all plugins via DB
4. Switch to default theme via DB

### Database Locked Error
- Check for stale `.ht.sqlite-journal` files
- Verify no other process has the DB open
- Run `PRAGMA integrity_check;`

### REST API / wp-json Not Working
- Check `wp_options` for `permalink_structure`
- Verify `.htaccess` or rewrite rules (Studio handles this internally)
- Check for plugin conflicts blocking REST routes

### Plugin Activation Crash
- Read `active_plugins` from wp_options
- Deactivate the offending plugin via SQL
- Check plugin code for fatal errors

### Plugin Conflict Preventing Site Start (Bisect)
When a site won't start and you suspect a plugin conflict, run the **plugin bisect script** to automatically find the offending plugin(s). This deactivates each active plugin one at a time, attempts to start the site, and reports which plugin(s) are preventing the site from starting.

1. Save the bisect script to a temp file
2. Run it with `bash /tmp/studio-bisect.sh`
3. Report the results

**Bisect script:**
```bash
#!/bin/bash
# This script deactivates all active plugins one by one and checks if the site starts successfully after each deactivation.

set -euo pipefail

echo "Fetching active plugins..."
raw_output=$(studio wp plugin list --status=active --fields=name --format=json 2>/dev/null || true)

# Extract the JSON array from the noisy output (find the first [...] block)
json=$(echo "$raw_output" | grep -oE '\[.*\]' | head -1)

if [[ -z "$json" ]]; then
  echo "❌ Failed to parse plugin list. Raw output:"
  echo "$raw_output"
  exit 1
fi

# Parse plugin names from JSON
plugins=()
while IFS= read -r line; do
  plugins+=("$line")
done < <(echo "$json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data:
    print(p['name'])
")

if [[ ${#plugins[@]} -eq 0 ]]; then
  echo "❌ No active plugins found."
  exit 1
fi

echo "Found ${#plugins[@]} active plugins:"
printf "  - %s\n" "${plugins[@]}"
echo ""

conflicting=()

for plugin in "${plugins[@]}"; do
  echo "=========================================="
  echo "Testing: $plugin"
  echo "=========================================="

  echo "⏸  Deactivating $plugin..."
  if ! studio wp plugin deactivate "$plugin" 2>/dev/null; then
    echo "⚠️  Failed to deactivate $plugin, skipping."
    continue
  fi

  echo "🚀 Starting site..."
  if studio site start 2>/dev/null; then
    echo ""
    echo "🎯 Conflicting plugin found: $plugin"
    conflicting+=("$plugin")
    echo "🛑 Stopping site..."
    studio site stop 2>/dev/null || true
  else
    echo "❌ Site still fails without $plugin."
  fi

  echo "🔄 Reactivating $plugin..."
  studio wp plugin activate "$plugin" 2>/dev/null || true
  echo ""
done

echo "=========================================="
echo "RESULTS"
echo "=========================================="

if [[ ${#conflicting[@]} -gt 0 ]]; then
  echo "🎯 Conflicting plugins found (${#conflicting[@]}):"
  for p in "${conflicting[@]}"; do
    echo "  ❌ $p"
  done
else
  echo "✅ No single conflicting plugin found."
  echo "   The issue may involve multiple plugins interacting."
fi
```

To run: save to a temp file and execute with `bash /tmp/studio-bisect.sh`

### Site URL Mismatch
- Query `siteurl` and `home` from wp_options
- Update if they don't match Studio's expected localhost URL

## SQLite-Specific Debugging

The SQLite translation layer can cause issues that wouldn't appear with MySQL:

- **Unsupported MySQL functions** — Some plugins use MySQL-specific functions that the translation layer doesn't handle
- **Transaction locking** — SQLite uses file-level locking, not row-level
- **Data type differences** — SQLite is more permissive with types
- **LIKE operator** — Case sensitivity differs from MySQL defaults

To check for translation errors:
```sql
SELECT * FROM _mysql_data_types_cache LIMIT 20;
```

## Important Rules

- Always use `-readonly` flag with sqlite3 when only reading data
- Never modify the database without explicit user confirmation
- Always show diffs before suggesting file changes
- When showing SQL fixes, explain what each query does
- If the database might be corrupted, suggest backing it up first before any writes
- Prefer non-destructive diagnostics first, fixes second
