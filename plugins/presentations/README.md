# Presentations Plugin

Generate beautiful Marp presentations directly from your intent specifications.

## Overview

This plugin creates presentation slides from intent specs, making it easy to present your work, ideas, and solutions to stakeholders. It generates both Markdown and HTML output.

## Skills

### `/presentation`

Generate a Marp presentation from an open intent.

The skill will:
1. List all open intents
2. Ask which intent to create a presentation for
3. Parse the spec into presentation slides
4. Generate both `.md` and `.html` files
5. Optionally open the presentation

**Usage:**
```
/presentation
```

## Output

Presentations are saved in your intent's `assets/` folder:

```
.sejas/open/YYYY-MM-DD-description/
└── assets/
    ├── presentation.md
    └── presentation.html (optional)
```

## Slide Structure

The generated presentation includes:
- Title slide with intent name and date
- Problem statement
- Proposed solution
- Requirements list
- Implementation details
- Demo/Results placeholder
- Questions slide

Each slide is concise and presentation-ready, not a copy of the full spec.

## Features

- **Automatic generation** - Parses spec.md and creates presentation structure
- **Marp format** - Uses Marp CLI for creating professional slides
- **Multiple formats** - Supports Markdown and HTML output
- **Customizable** - Edit the generated `presentation.md` before exporting
- **Themes** - Easily change themes (default, gaia, uncover)

## Dependencies

- **Marp CLI** - Installed automatically via npm when generating HTML
- **npx** - For running Marp CLI (included with Node.js)

## Customization

Edit `.sejas/open/YOUR_INTENT/assets/presentation.md` to customize:

### Themes

```yaml
---
marp: true
theme: gaia          # Options: default, gaia, uncover
paginate: true
---
```

### Headers/Footers

```yaml
---
marp: true
theme: default
paginate: true
header: 'Your Project'
footer: 'Slide number: %s'
---
```

## Installation

```bash
claude plugin install sejas/ai-code-skills@presentations
```

## Related Plugins

- **intents** - Create and manage intent specifications
- **development** - Development workflow automation

## License

MIT
