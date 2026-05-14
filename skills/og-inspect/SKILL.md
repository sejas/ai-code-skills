---
name: og-inspect
description: Inspect a URL's Open Graph and Twitter Card metadata and render a styled HTML page showing how the link unfurls on Facebook, X/Twitter, LinkedIn, Slack/Discord, and Tumblr. Also prints a JSON summary to stdout. Use when the user asks to "preview a link", "check OG tags", "inspect Open Graph", "see how a URL looks when shared", or invokes `/og-inspect <url>`.
user-invocable: true
allowed-tools: ["Bash", "Read", "Write"]
---

# /og-inspect — Open Graph / share-card inspector

Given a URL, fetch the page, extract Open Graph + Twitter Card metadata, render a styled HTML preview showing how the link unfurls on Facebook, X/Twitter, LinkedIn, Slack/Discord, and Tumblr, and print a JSON summary. Like https://www.opengraph.xyz/ but local.

## Workflow

1. **Get the URL.** The user invokes `/og-inspect <url>`. If no URL is provided, ask: "Which URL should I inspect?"

2. **Run the inspector.** Execute the bash block below with the URL as `$1`. It fetches the page with `curl`, parses meta tags with Python stdlib (`html.parser`), writes a styled HTML preview to `~/claude.nosync/og-previews/YYYY-MM-DD-<host>-<slug>.html`, prints the absolute path of the HTML file to stderr, and prints the JSON summary to stdout.

3. **Open the HTML file** in the default browser with `open "<path>"`.

4. **Print the JSON** result to the terminal (it is already on stdout from step 2 — relay it to the user).

## The script

Run this with the URL as the first argument. Treat the URL as untrusted input — the script already does shell-safe quoting and no `eval`.

```bash
set -uo pipefail

URL="${1:-}"
if [ -z "$URL" ]; then
  echo "usage: og-inspect <url>" >&2
  exit 1
fi
# Normalize: prepend https:// if no scheme
if ! printf '%s' "$URL" | grep -qE '^https?://'; then
  URL="https://$URL"
fi

OUTDIR="$HOME/claude.nosync/og-previews"
mkdir -p "$OUTDIR"
TMP_HTML="$(mktemp -t og-inspect.XXXXXX).html"
TMP_META="$(mktemp -t og-inspect.XXXXXX).meta"
TMP_JSON="$(mktemp -t og-inspect.XXXXXX).json"
TMP_PATH="$(mktemp -t og-inspect.XXXXXX).path"
trap 'rm -f "$TMP_HTML" "$TMP_META" "$TMP_JSON" "$TMP_PATH"' EXIT

# Fetch. Always emit the meta file even on failure so Python can render a stub.
# On TLS verification failure (curl exit 60), retry with -k and flag a warning.
TLS_INSECURE=0
CURL_COMMON=( -sSL
  -A "Mozilla/5.0 (compatible; OGInspectBot/1.0)"
  -H "Accept: text/html,application/xhtml+xml"
  --max-time 15
  --max-filesize 5000000
  -w '%{http_code}\n%{url_effective}\n%{content_type}\n'
  -o "$TMP_HTML" )
curl "${CURL_COMMON[@]}" "$URL" > "$TMP_META" 2>/dev/null
RC=$?
if [ "$RC" -eq 60 ]; then
  TLS_INSECURE=1
  curl -k "${CURL_COMMON[@]}" "$URL" > "$TMP_META" 2>/dev/null
  RC=$?
fi
if [ "$RC" -ne 0 ]; then
  printf '0\n%s\n\n' "$URL" > "$TMP_META"
fi

# Parse + render. Python writes JSON to TMP_JSON and the output filepath to TMP_PATH.
python3 - "$URL" "$TMP_HTML" "$TMP_META" "$OUTDIR" "$TLS_INSECURE" >"$TMP_JSON" 2>"$TMP_PATH" <<'PY'
import sys, os, json, html, re
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

orig_url, tmp_html, tmp_meta, outdir, tls_insecure = sys.argv[1:6]
tls_insecure = tls_insecure == "1"

with open(tmp_meta) as f:
    lines = f.read().splitlines()
status_str = lines[0] if len(lines) > 0 else "0"
final_url  = lines[1] if len(lines) > 1 and lines[1] else orig_url
ctype      = lines[2] if len(lines) > 2 else ""

# Decode body with charset detection (file may be missing/empty if curl failed)
try:
    with open(tmp_html, "rb") as f:
        raw = f.read()
except FileNotFoundError:
    raw = b""
charset = None
m = re.search(r"charset=([\w\-]+)", ctype, re.I)
if m: charset = m.group(1)
if not charset:
    mm = re.search(rb'<meta[^>]+charset=["\']?([\w\-]+)', raw[:4096], re.I)
    if mm:
        try: charset = mm.group(1).decode("ascii")
        except Exception: pass
charset = charset or "utf-8"
try:
    text = raw.decode(charset, errors="replace")
except LookupError:
    text = raw.decode("utf-8", errors="replace")
text = text.replace("\x00", "")

class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.metas, self.links = [], []
        self.title = None
        self._in_title = False
        self._title_parts = []
    def handle_starttag(self, tag, attrs):
        d = {k.lower(): v for k, v in attrs}
        if tag == "meta":
            prop = d.get("property") or d.get("name") or d.get("itemprop")
            content = d.get("content")
            if prop and content is not None:
                self.metas.append((prop.lower(), content))
        elif tag == "link":
            rel, href = d.get("rel"), d.get("href")
            if rel and href: self.links.append((rel.lower(), href))
        elif tag == "title":
            self._in_title = True
    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
            if self.title is None:
                self.title = "".join(self._title_parts).strip()
    def handle_data(self, data):
        if self._in_title: self._title_parts.append(data)

p = MetaParser()
try: p.feed(text)
except Exception: pass

def collect(prefix):
    out = {}
    for k, v in p.metas:
        if k == prefix or k.startswith(prefix + ":"):
            sub = k[len(prefix):].lstrip(":") or "_"
            out.setdefault(sub, v.strip())
    return out

og = collect("og")
tw = collect("twitter")

def by_name(n):
    for k, v in p.metas:
        if k == n: return v.strip()
    return None

def resolve(u):
    if not u: return None
    try: return urljoin(final_url, u)
    except Exception: return u

for d in (og, tw):
    if d.get("image"): d["image"] = resolve(d["image"])
    if d.get("url"):   d["url"]   = resolve(d["url"])

canonical = favicon = apple_icon = None
for rel, href in p.links:
    rels = rel.split()
    if "canonical"        in rels and not canonical:  canonical  = resolve(href)
    if "icon"             in rels and not favicon:    favicon    = resolve(href)
    if "apple-touch-icon" in rels and not apple_icon: apple_icon = resolve(href)

other = {
    "title":       p.title,
    "description": by_name("description"),
    "author":      by_name("author"),
    "theme_color": by_name("theme-color"),
    "canonical":   canonical,
    "favicon":     favicon or apple_icon,
}

warnings = []
if not og.get("title"):       warnings.append("missing og:title")
if not og.get("description"): warnings.append("missing og:description")
if not og.get("image"):       warnings.append("missing og:image")
if not tw.get("card"):        warnings.append("missing twitter:card")
if status_str == "0":
    warnings.append("fetch failed (network, DNS, timeout, or size cap)")
elif status_str != "200":
    warnings.append(f"HTTP status {status_str}")
if ctype and "html" not in ctype.lower():
    warnings.append(f"non-HTML content-type: {ctype}")
if tls_insecure:
    warnings.append("TLS verification failed — refetched with -k (cert mismatch or self-signed)")

status_int = int(status_str) if status_str.isdigit() else 0

result = {
    "url":          orig_url,
    "final_url":    final_url,
    "fetched_at":   datetime.now(timezone.utc).isoformat(),
    "status":       status_int,
    "content_type": ctype,
    "tls_insecure": tls_insecure,
    "warnings":     warnings,
    "og":           og,
    "twitter":      tw,
    "other":        other,
}

# Filename
parsed = urlparse(final_url)
host = (parsed.hostname or "unknown").lower()
if host.startswith("www."): host = host[4:]
host_slug = re.sub(r"[^a-z0-9]+", "-", host).strip("-") or "unknown"
seg = (parsed.path.strip("/").split("/", 1)[0] or "root")[:30]
path_slug = re.sub(r"[^a-z0-9]+", "-", seg.lower()).strip("-") or "root"
fname = f"{datetime.now().strftime('%Y-%m-%d')}-{host_slug}-{path_slug}.html"
fpath = os.path.join(outdir, fname)

# HTML rendering
def esc(s):
    return html.escape("" if s is None else str(s), quote=True)

def img_or_placeholder(url, alt=""):
    if url:
        return f'<img src="{esc(url)}" alt="{esc(alt)}" loading="lazy" referrerpolicy="no-referrer">'
    return '<div class="img-placeholder">no image</div>'

def table_rows(d):
    if not d:
        return '<tr><td colspan="2" class="missing">— no tags found —</td></tr>'
    rows = []
    for k, v in sorted(d.items()):
        rows.append(f'<tr><th>{esc(k)}</th><td title="{esc(v)}">{esc(v)}</td></tr>')
    return "".join(rows)

source_domain = host
og_title = og.get("title")       or other.get("title") or "(no title)"
og_desc  = og.get("description") or other.get("description") or ""
og_img   = og.get("image")
og_site  = og.get("site_name")   or source_domain

tw_card   = (tw.get("card") or "summary").lower()
tw_title  = tw.get("title") or og_title
tw_desc   = tw.get("description") or og_desc
tw_img    = tw.get("image") or og_img
tw_handle = tw.get("site") or ""

warnings_html = ""
if warnings:
    items = "".join(f"<li>{esc(w)}</li>" for w in warnings)
    warnings_html = f'<div class="warnings"><strong>Warnings</strong><ul>{items}</ul></div>'

final_url_row = ""
if final_url != orig_url:
    final_url_row = (
        f'<div class="url">Final: '
        f'<a href="{esc(final_url)}" target="_blank" rel="noopener">{esc(final_url)}</a></div>'
    )

tw_handle_html = f' · {esc(tw_handle)}' if tw_handle else ''
tw_card_class = 'twitter-lg' if tw_card == 'summary_large_image' else 'twitter-sm'

json_str = json.dumps(result, indent=2, ensure_ascii=False)

html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>OG Inspect — {esc(source_domain)}</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
       background:#0d1117; color:#e6edf3; max-width:1200px; margin:0 auto;
       padding:2rem 1.5rem 4rem; line-height:1.5 }}
header h1 {{ font-size:1.4rem; color:#58a6ff; margin-bottom:.4rem }}
header .url {{ color:#8b949e; font-family:'SF Mono','Fira Code',monospace; font-size:.85rem; word-break:break-all; margin-top:.2rem }}
header .url a {{ color:#58a6ff; text-decoration:none }}
header .url a:hover {{ text-decoration:underline }}
.warnings {{ background:#3d2a14; border:1px solid #9e6a03; border-radius:6px;
             padding:.75rem 1rem; margin:1rem 0; color:#f0b429 }}
.warnings ul {{ margin:.25rem 0 0 1.25rem }}
.warnings li {{ font-size:.85rem }}
h2 {{ color:#58a6ff; margin:2rem 0 .75rem; font-size:1.1rem;
      border-bottom:1px solid #30363d; padding-bottom:.4rem }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(340px,1fr)); gap:1.25rem }}
.card {{ background:#161b22; border:1px solid #30363d; border-radius:8px; overflow:hidden;
         display:flex; flex-direction:column }}
.card .platform {{ background:#0d1117; border-bottom:1px solid #30363d; padding:.4rem .75rem;
                   font-size:.7rem; text-transform:uppercase; letter-spacing:.05em;
                   color:#8b949e; font-weight:600 }}
.card img, .card .img-placeholder {{ width:100%; aspect-ratio:1.91/1; object-fit:cover;
                                     background:#0d1117; display:flex; align-items:center;
                                     justify-content:center; color:#484f58; font-size:.8rem }}
.card .body {{ padding:.75rem 1rem 1rem }}
.card .domain {{ color:#8b949e; font-size:.7rem; text-transform:uppercase;
                 letter-spacing:.04em; margin-bottom:.25rem }}
.card .title {{ color:#e6edf3; font-weight:600; font-size:1rem; margin:.1rem 0 .4rem; line-height:1.3 }}
.card .desc {{ color:#8b949e; font-size:.85rem; display:-webkit-box;
               -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden }}

.card.twitter-sm {{ flex-direction:row }}
.card.twitter-sm > .platform {{ display:none }}
.card.twitter-sm img, .card.twitter-sm .img-placeholder {{ width:120px; height:120px;
                                                            aspect-ratio:auto; flex-shrink:0 }}
.card.twitter-sm .body {{ padding:.6rem .75rem; min-width:0; flex:1 }}
.card.twitter-sm .title {{ font-size:.9rem }}
.card.twitter-sm .desc {{ font-size:.8rem; -webkit-line-clamp:2 }}
.twitter-wrap > .platform {{ background:#0d1117; border:1px solid #30363d; border-bottom:none;
                              border-radius:8px 8px 0 0; padding:.4rem .75rem; font-size:.7rem;
                              text-transform:uppercase; letter-spacing:.05em; color:#8b949e; font-weight:600 }}
.twitter-wrap .card.twitter-sm {{ border-radius:0 0 8px 8px; border-top:none }}

.slack-wrap {{ background:#161b22; border:1px solid #30363d; border-radius:8px; padding:.75rem 1rem }}
.slack-wrap .platform {{ color:#8b949e; font-size:.7rem; text-transform:uppercase;
                          letter-spacing:.05em; margin-bottom:.6rem; font-weight:600 }}
.card.slack {{ background:transparent; border:none; border-left:4px solid #58a6ff;
               padding-left:.75rem; border-radius:0; flex-direction:row;
               align-items:flex-start; gap:.75rem }}
.card.slack .body {{ padding:0; flex:1; min-width:0 }}
.card.slack .domain {{ font-size:.7rem; color:#8b949e; text-transform:none; letter-spacing:0 }}
.card.slack .title {{ color:#58a6ff; font-weight:600; font-size:.9rem; margin:.15rem 0 .25rem }}
.card.slack .desc {{ font-size:.8rem; color:#c9d1d9; -webkit-line-clamp:3 }}
.card.slack img, .card.slack .img-placeholder {{ width:90px; height:90px; flex-shrink:0;
                                                  border-radius:6px; aspect-ratio:auto }}

.card.tumblr {{ background:#001935; border-color:#001935; position:relative }}
.card.tumblr img, .card.tumblr .img-placeholder {{ aspect-ratio:1/1 }}
.card.tumblr .body {{ background:linear-gradient(to top, rgba(0,25,53,.96), transparent 90%);
                       margin-top:-4rem; position:relative; padding-top:3rem }}
.card.tumblr .domain {{ background:#fff; color:#001935; display:inline-block;
                         padding:.2rem .5rem; border-radius:3px; font-weight:700; font-size:.65rem }}
.card.tumblr .title {{ color:#fff }}

table {{ border-collapse:collapse; width:100%; margin:.5rem 0 1.5rem; font-size:.85rem }}
th, td {{ border:1px solid #30363d; padding:.4rem .6rem; text-align:left; vertical-align:top }}
th {{ background:#161b22; color:#58a6ff; font-family:'SF Mono','Fira Code',monospace;
      font-weight:500; width:30%; white-space:nowrap }}
td {{ font-family:'SF Mono','Fira Code',monospace; word-break:break-all; color:#c9d1d9 }}
.missing {{ color:#484f58; font-style:italic }}
pre.json {{ background:#161b22; border:1px solid #30363d; border-radius:6px; padding:1rem;
            overflow:auto; font-size:.8rem; color:#c9d1d9; max-height:400px;
            font-family:'SF Mono','Fira Code',monospace }}
.copy-btn {{ position:fixed; top:1.5rem; right:1.5rem; background:#238636; color:#fff; border:none;
             padding:.5rem 1rem; border-radius:6px; cursor:pointer; font-size:.85rem;
             font-weight:500; transition:background .2s; z-index:10 }}
.copy-btn:hover {{ background:#2ea043 }}
.copy-btn.copied {{ background:#1f6feb }}

@media (max-width: 720px) {{
  .grid {{ grid-template-columns:1fr }}
  .copy-btn {{ top:auto; bottom:1rem; right:1rem }}
  body {{ padding:1rem .75rem 4rem }}
}}
</style>
</head>
<body>
<button class="copy-btn" onclick="copyJSON()">Copy JSON</button>
<header>
  <h1>OG Inspect — {esc(source_domain)}</h1>
  <div class="url">URL: <a href="{esc(orig_url)}" target="_blank" rel="noopener">{esc(orig_url)}</a></div>
  {final_url_row}
  <div class="url">HTTP {esc(status_str)} · {esc(ctype) or '—'}</div>
  {warnings_html}
</header>

<h2>Platform previews</h2>
<div class="grid">

  <div class="card facebook">
    <div class="platform">Facebook / Open Graph</div>
    {img_or_placeholder(og_img, og.get("image_alt") or og_title)}
    <div class="body">
      <div class="domain">{esc(source_domain)}</div>
      <div class="title">{esc(og_title)}</div>
      <div class="desc">{esc(og_desc)}</div>
    </div>
  </div>

  <div class="twitter-wrap">
    <div class="platform">X / Twitter ({esc(tw_card)})</div>
    <div class="card {tw_card_class}">
      <div class="platform">X / Twitter</div>
      {img_or_placeholder(tw_img, tw.get("image_alt") or tw_title)}
      <div class="body">
        <div class="title">{esc(tw_title)}</div>
        <div class="desc">{esc(tw_desc)}</div>
        <div class="domain">{esc(source_domain)}{tw_handle_html}</div>
      </div>
    </div>
  </div>

  <div class="card linkedin">
    <div class="platform">LinkedIn</div>
    {img_or_placeholder(og_img, og_title)}
    <div class="body">
      <div class="title">{esc(og_title)}</div>
      <div class="domain">{esc(source_domain)}</div>
    </div>
  </div>

  <div class="slack-wrap">
    <div class="platform">Slack / Discord unfurl</div>
    <div class="card slack">
      <div class="body">
        <div class="domain">{esc(og_site)}</div>
        <div class="title">{esc(og_title)}</div>
        <div class="desc">{esc(og_desc)}</div>
      </div>
      {img_or_placeholder(og_img, og_title)}
    </div>
  </div>

  <div class="card tumblr">
    <div class="platform">Tumblr</div>
    {img_or_placeholder(og_img, og_title)}
    <div class="body">
      <div class="domain">{esc(source_domain)}</div>
      <div class="title">{esc(og_title)}</div>
    </div>
  </div>

</div>

<h2>Open Graph tags</h2>
<table>{table_rows(og)}</table>

<h2>Twitter Card tags</h2>
<table>{table_rows(tw)}</table>

<h2>Other metadata</h2>
<table>{table_rows({k: v for k, v in other.items() if v})}</table>

<h2>Raw JSON</h2>
<pre class="json" id="json-blob">{esc(json_str)}</pre>

<script>
const rawJSON = document.getElementById('json-blob').textContent;
function copyJSON() {{
  navigator.clipboard.writeText(rawJSON).then(() => {{
    const btn = document.querySelector('.copy-btn');
    btn.textContent = 'Copied!'; btn.classList.add('copied');
    setTimeout(() => {{ btn.textContent = 'Copy JSON'; btn.classList.remove('copied'); }}, 2000);
  }});
}}
</script>
</body>
</html>
"""

os.makedirs(outdir, exist_ok=True)
with open(fpath, "w", encoding="utf-8") as f:
    f.write(html_doc)

# Filepath on stderr, JSON on stdout
print(fpath, file=sys.stderr)
print(json_str)
PY

HTML_PATH="$(cat "$TMP_PATH")"
# Print JSON to terminal so callers can pipe to jq, etc.
cat "$TMP_JSON"
echo "" >&2
echo "→ $HTML_PATH" >&2
open "$HTML_PATH"
```

## What the output contains

- **Header** — original URL, final URL after redirects, HTTP status, content-type, and a warnings banner listing any missing OG/Twitter tags.
- **Platform previews grid** — five faithful HTML mockups:
  - Facebook / Open Graph card (large image on top)
  - X / Twitter card (auto-picks `summary` vs `summary_large_image` layout)
  - LinkedIn link preview
  - Slack / Discord unfurl (left color bar, image thumbnail right)
  - Tumblr (square image with title overlay)
- **Raw metadata tables** — sorted `property → value` for Open Graph, Twitter Card, and Other (title, description, author, canonical, favicon, theme-color).
- **Raw JSON** at the bottom + **"Copy JSON"** button (top-right).
- **Stdout** also receives the JSON for piping (`/og-inspect <url> | jq .og`).

## Rules and edge cases

- **HTML escape everything** placed into the rendered page — the script uses `html.escape(..., quote=True)` on every user-controlled string. Do not bypass that.
- **Images load by URL** (`<img src>`) with `loading="lazy"` and `referrerpolicy="no-referrer"`. No bytes are downloaded by the script.
- **Relative URLs** (image, canonical, favicon) are resolved against the **final** URL via `urllib.parse.urljoin`.
- **Charset detection:** HTTP `Content-Type` first → `<meta charset>` in the first 4 KB → UTF-8 fallback. Null bytes are stripped.
- **Errors are non-fatal:** network failures, 4xx/5xx, non-HTML content, and zero metadata all still produce an HTML page with a warnings banner so the user has something to look at. Status `0` means curl failed entirely (DNS, timeout, size cap).
- **Body cap 5 MB, timeout 15 s** — set via `curl --max-filesize` and `--max-time`.
- **URLs behind auth or a WAF** (e.g., authenticated Twitter pages, LinkedIn feed) often return login walls; the script will note this via missing tags but cannot bypass it.
- **Do not pass shell metacharacters** in the URL via unquoted variables — the script always quotes `"$URL"`.

## Allowed tools

Bash, Read, Write.
