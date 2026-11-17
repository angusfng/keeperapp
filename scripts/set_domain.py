#!/usr/bin/env python3
"""Move the site to a new domain: rewrites every absolute URL in public/, content/ and scripts/.

Usage:
  python3 scripts/set_domain.py keeperphoto.app

Then also: add the custom domain to the Cloudflare Pages project, add the new
Search Console property and give the service account access (content/SETUP.md),
update the routine's prompt, and point the app's privacy link at the new domain
in a future app update (keep the old pages.dev address working).
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OLD = re.search(r'HOST = "([^"]+)"', (ROOT / "scripts/notify_search_engines.py").read_text()).group(1)
NEW = sys.argv[1].strip().removeprefix("https://").rstrip("/")
if NEW == OLD:
    sys.exit(f"already on {OLD}")
changed = 0
for folder in ("public", "content", "scripts"):
    for path in (ROOT / folder).rglob("*"):
        if path.suffix not in {".html", ".xml", ".txt", ".md", ".py", ".json", ".webmanifest"} or path.name == "set_domain.py":
            continue
        text = path.read_text()
        if OLD in text:
            path.write_text(text.replace(OLD, NEW))
            changed += 1
print(f"{OLD} -> {NEW}: {changed} files changed")
