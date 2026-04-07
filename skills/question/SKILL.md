# /question - Answer a question and render as HTML

Answer the user's question, save a styled HTML page to `~/claude.nosync/questions/`, open it in the browser, and print the answer to stdout.

## Instructions

1. **Answer the question** thoroughly and accurately.

2. **Create the output directory** if it doesn't exist:
   ```
   mkdir -p ~/claude.nosync/questions
   ```

3. **Generate the filename** using today's date and a summarized slug:
   - Format: `YYYY-MM-DD-<slug>.html`
   - Slug: summarize the question into 3-5 descriptive words that capture the core topic, lowercase, remove non-alphanumeric characters (keep spaces), replace spaces with hyphens
   - The slug should read like a short title, not a truncated sentence — drop filler words like "how", "can", "I", "the", "do", "what", "is"
   - Examples:
     - "How can I improve the q function in zshrc?" → `2026-02-09-improve-zshrc-q-function.html`
     - "What is the difference between TCP and UDP?" → `2026-02-09-tcp-vs-udp-difference.html`
     - "How do I center a div in CSS?" → `2026-02-09-css-center-div.html`
     - "What is 2 + 2?" → `2026-02-09-whats-2-plus-2.html`

4. **Write a styled HTML file** to `~/claude.nosync/questions/<filename>` using the Write tool. The HTML must include:
   - The question displayed as a `<h1>` header
   - The answer written as **raw markdown** inside a `<script type="text/plain" id="raw-answer">` element (HTML-escape `<`, `>`, and `&` in the answer)
   - The raw markdown is rendered client-side with `marked.js` and sanitized with `DOMPurify` before inserting into the DOM
   - CDN libraries (load via `<script>` tags):
     - `https://cdn.jsdelivr.net/npm/marked/marked.min.js` - markdown rendering
     - `https://cdn.jsdelivr.net/npm/dompurify/dist/purify.min.js` - HTML sanitization
     - `https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js` - code highlighting
     - `https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css` - code theme
   - A **"Copy Answer"** button that copies the raw markdown answer to clipboard
   - Use this HTML structure and dark theme styling:

   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
     <meta charset="UTF-8">
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
     <title>Q: {{QUESTION}}</title>
     <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
     <style>
       * { margin: 0; padding: 0; box-sizing: border-box; }
       body {
         font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         background: #0d1117; color: #e6edf3;
         max-width: 820px; margin: 0 auto; padding: 2rem 1.5rem;
         line-height: 1.7;
       }
       h1.question {
         font-size: 1.6rem; color: #58a6ff; margin-bottom: 1.5rem;
         padding-bottom: 1rem; border-bottom: 1px solid #30363d;
       }
       #content { font-size: 1.05rem; }
       #content h1, #content h2, #content h3 { color: #58a6ff; margin: 1.5rem 0 0.75rem; }
       #content h1 { font-size: 1.5rem; }
       #content h2 { font-size: 1.3rem; }
       #content h3 { font-size: 1.15rem; }
       #content p { margin-bottom: 1rem; }
       #content ul, #content ol { margin: 0.5rem 0 1rem 1.5rem; }
       #content li { margin-bottom: 0.4rem; }
       #content pre {
         background: #161b22; border: 1px solid #30363d; border-radius: 8px;
         padding: 1rem; overflow-x: auto; margin: 1rem 0;
       }
       #content code { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 0.9em; }
       #content p code, #content li code {
         background: #161b22; padding: 0.2em 0.4em; border-radius: 4px;
       }
       #content blockquote {
         border-left: 3px solid #58a6ff; padding-left: 1rem;
         color: #8b949e; margin: 1rem 0;
       }
       #content a { color: #58a6ff; text-decoration: none; }
       #content a:hover { text-decoration: underline; }
       #content table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
       #content th, #content td {
         border: 1px solid #30363d; padding: 0.5rem 0.75rem; text-align: left;
       }
       #content th { background: #161b22; }
       .copy-btn {
         position: fixed; top: 1.5rem; right: 1.5rem;
         background: #238636; color: #fff; border: none;
         padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer;
         font-size: 0.85rem; font-weight: 500; transition: background 0.2s;
       }
       .copy-btn:hover { background: #2ea043; }
       .copy-btn.copied { background: #1f6feb; }
     </style>
   </head>
   <body>
     <button class="copy-btn" onclick="copyAnswer()">Copy Answer</button>
     <h1 class="question">{{QUESTION}}</h1>
     <div id="content"></div>
     <script type="text/plain" id="raw-answer">
       {{ANSWER_MD_HTML_ESCAPED}}
     </script>
     <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
     <script src="https://cdn.jsdelivr.net/npm/dompurify/dist/purify.min.js"></script>
     <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
     <script>
       const raw = document.getElementById('raw-answer').textContent.trim();
       marked.setOptions({ highlight: function(code, lang) {
         if (lang && hljs.getLanguage(lang)) return hljs.highlight(code, { language: lang }).value;
         return hljs.highlightAuto(code).value;
       }});
       document.getElementById('content').innerHTML = DOMPurify.sanitize(marked.parse(raw));
       function copyAnswer() {
         navigator.clipboard.writeText(raw).then(function() {
           var btn = document.querySelector('.copy-btn');
           btn.textContent = 'Copied!'; btn.classList.add('copied');
           setTimeout(function() { btn.textContent = 'Copy Answer'; btn.classList.remove('copied'); }, 2000);
         });
       }
     </script>
   </body>
   </html>
   ```

   **Critical:** The `{{QUESTION}}` and `{{ANSWER_MD_HTML_ESCAPED}}` are placeholders. Replace them with actual content. HTML-escape `<`, `>`, and `&` characters in the answer when placing it inside the `<script type="text/plain">` element.

   **Security note:** The rendered HTML is sanitized through DOMPurify before DOM insertion, preventing XSS.

5. **Open in browser:**
   ```
   open ~/claude.nosync/questions/<filename>
   ```

6. **Print the answer** to stdout as well (the raw markdown text, so it appears in the terminal).

## Allowed tools

Bash, Write, Read, Glob, Grep
