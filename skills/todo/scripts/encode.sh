#!/bin/bash
# URL-encode a string for use in Things 3 URL scheme
urlencode() {
  python3 -c "import urllib.parse; print(urllib.parse.quote('''$1''', safe=''))"
}
