# /question - Answer a question and render as HTML

Answer the user's question, save a styled HTML page to `~/claude-questions/`, open it in the browser, and print the answer to stdout.

## Instructions

1. **Answer the question** thoroughly and accurately.

2. **Create the output directory** if it doesn't exist:
   ```
   mkdir -p ~/claude-questions
   ```

3. **Generate the filename** using today's date and a summarized slug:
   - Format: `YYYY-MM-DD-<slug>.html`
   - Slug: summarize the question into 3-5 descriptive words that capture the core topic, lowercase, remove non-alphanumeric characters (keep spaces), replace spaces with hyphens
   - The slug should read like a short title, not a truncated sentence — drop filler words like "how", "can", "I", "the", "do", "what", "is"
   - Examples:
     - "How can I improve the q function in zshrc?" -> `2026-02-09-improve-zshrc-q-function.html`
     - "What is the difference between TCP and UDP?" -> `2026-02-09-tcp-vs-udp-difference.html`
     - "How do I center a div in CSS?" -> `2026-02-09-css-center-div.html`
     - "What is 2 + 2?" -> `2026-02-09-whats-2-plus-2.html`

4. **Write a styled HTML file** to `~/claude-questions/<filename>` using the Write tool. The HTML must include:
   - The question displayed as a `<h1>` header
   - The answer written as **raw markdown** inside a `<script type="text/plain" id="raw-answer">` element (HTML-escape `<`, `>`, and `&` in the answer)
   - The raw markdown is rendered client-side with `marked.js` and **sanitized with `DOMPurify`** before inserting into the DOM
   - CDN libraries (load via `<script>` tags):
     - `https://cdn.jsdelivr.net/npm/marked/marked.min.js` - markdown rendering
     - `https://cdn.jsdelivr.net/npm/dompurify/dist/purify.min.js` - HTML sanitization
     - `https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js` - code highlighting
     - `https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css` - code theme
   - A **"Copy Answer"** button that copies the raw markdown answer to clipboard
   - Use the HTML template from `${CLAUDE_PLUGIN_ROOT}/commands/question/assets/template.html`
   - Replace `{{QUESTION}}` and `{{ANSWER_MD_HTML_ESCAPED}}` placeholders with actual content
   - HTML-escape `<`, `>`, and `&` characters in the answer when placing it inside the `<script type="text/plain">` element

   **Security note:** The rendered HTML is sanitized through DOMPurify before DOM insertion, preventing XSS.

5. **Open in browser:**
   ```
   open ~/claude-questions/<filename>
   ```

6. **Print the answer** to stdout as well (the raw markdown text, so it appears in the terminal).

## Allowed tools

Bash, Write, Read, Glob, Grep
