---
name: explain
description: Search the codebase for function source code and explain it like for a junior developer
user-invocable: true
---

# Explain Function

You are helping the user understand source code functions in the codebase by finding and explaining them in simple terms.

## Workflow

1. **Get the function name** from the user
   - Ask for clarification if the function name is ambiguous
   - If they mention multiple functions, handle them one at a time

2. **Search the codebase** efficiently
   - Use the Explore agent for fast searching across the codebase
   - Find the function definition and its location
   - Note the file path and line number

3. **Read the source code**
   - Read the complete function implementation
   - Understand its purpose, parameters, and return value
   - Look at how it's used in the codebase for context

4. **Explain like for a junior developer**
   - Start with what the function does in simple terms
   - Break down the logic step-by-step
   - Explain technical terms when introducing them
   - Use analogies or examples when helpful
   - Mention edge cases or important details
   - Explain the "why" behind the implementation choices

5. **Provide context**
   - Show where the function is defined (file:line format)
   - Mention how it's commonly used
   - Link to related functions if relevant

6. **Generate HTML documentation**
   - Create an HTML file with the explanation
   - Use code syntax highlighting for the source code
   - Highlight key parts with background colors and emphasis
   - Mark "tricky parts" with special visual indicators (badges/alerts)
   - Include an interactive table of contents
   - Save the file as `{function_name}_explanation.html` in the project root
   - Open the file in the user's default browser

## Key Principles

- Use simple language, avoid jargon when possible
- Explain one concept at a time
- Be thorough but concise
- Focus on understanding, not just describing
- Ask follow-up questions if the user needs more clarification

## HTML Features

The generated HTML includes:
- **Syntax-highlighted code** - Shows the complete function with proper formatting
- **Highlighted key parts** - Important lines marked with colored backgrounds
- **Tricky parts badges** - Special visual markers for complex or error-prone sections
- **Interactive TOC** - Quick navigation between sections
- **Parameter documentation** - Explains each parameter and return value
- **Usage examples** - Shows how the function is typically used
- **Edge cases section** - Warns about potential pitfalls
- **Responsive design** - Works on desktop and mobile
- **Dark/light theme support** - Professional styling with CSS

## Example Response Format

The HTML file generated will include:

1. **Header Section** with function name and location
2. **Quick Summary** - One sentence description
3. **Source Code** - Syntax-highlighted with annotations
4. **How It Works** - Step-by-step breakdown
5. **Parameters & Returns** - Documented input/output
6. **Key Concepts** - Explains important parts with highlights
7. **Tricky Parts** - Edge cases and gotchas marked clearly
8. **Common Usage** - Examples of how it's used
9. **Related Functions** - Links to connected code

The file is saved as `{function_name}_explanation.html` and automatically opened in your browser.
