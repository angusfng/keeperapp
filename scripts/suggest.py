#!/usr/bin/env python3
"""List Google autocomplete suggestions (US English) for photo cleanup and iPhone storage topics.

Search Console only shows queries the site already appears for, and a new site
appears for very few. Autocomplete shows what people actually type, so it finds
topics the site hasn't touched yet. A phrase only appears in autocomplete once
enough people search it, which makes it a rough demand signal, and a phrase that
several seeds surface is a stronger one.

Usage:
    python3 scripts/suggest.py                    # all seed phrases
    python3 scripts/suggest.py "delete photos from"    # extra seeds of your own
"""

import json
import sys
import time
import urllib.parse
import urllib.request

ENDPOINT = "https://suggestqueries.google.com/complete/search?client=firefox&hl=en-US&gl=us&q="

SEEDS = [
    # Deleting photos
    "how to delete photos on iphone",
    "delete photos iphone",
    "delete all photos",
    "how to delete multiple photos",
    "recently deleted",
    "recover deleted photos iphone",
    "permanently delete photos",
    "delete photos from iphone but not icloud",
    "delete duplicate photos",
    "delete screenshots iphone",
    # Storage
    "iphone storage full",
    "free up storage on iphone",
    "free up space on iphone",
    "iphone storage photos",
    "optimize iphone storage",
    "icloud storage full",
    "icloud photos",
    "system data iphone",
    # Organizing and cleanup
    "camera roll",
    "clean up camera roll",
    "declutter photos",
    "organize photos on iphone",
    "photo cleaner app",
    "swipe photo",
    "how to back up photos",
    "transfer photos from iphone to",
    "google photos",
    "live photos",
    # Question openers
    "how to clean up iphone",
    "why is my iphone storage",
    "how many photos can",
    "how much storage do photos",
    "does deleting photos",
    "can you recover",
]


def suggestions(seed):
    req = urllib.request.Request(ENDPOINT + urllib.parse.quote(seed), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8", "replace"))
    return [s for s in data[1] if s.lower() != seed.lower()]


def main():
    seeds = SEEDS + sys.argv[1:]
    seen = {}
    failures = 0
    for seed in seeds:
        try:
            found = suggestions(seed)
        except Exception as exc:  # network errors shouldn't stop the run
            failures += 1
            print(f"<!-- {seed}: {exc} -->", file=sys.stderr)
            continue
        for s in found:
            seen.setdefault(s, []).append(seed)
        time.sleep(0.5)

    if failures == len(seeds):
        sys.exit("autocomplete unavailable: every request failed")

    print("# Google autocomplete suggestions (US English)\n")
    print("Each line is a phrase people search, with the seed that surfaced it.")
    print("Phrases surfaced by more than one seed come first.\n")
    for s, from_seeds in sorted(seen.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        print(f"- {s}  ({', '.join(from_seeds)})")


if __name__ == "__main__":
    main()
