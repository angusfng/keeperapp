#!/usr/bin/env python3
"""Tell search engines about new or updated pages after a publish.

1. Resubmits sitemap.xml to Google Search Console. This needs the service
   account to have "Full" permission on the property (Restricted is read-only).
2. Sends the given URLs to IndexNow, which Bing, Yandex and others use to
   crawl new pages quickly. The key file lives at the site root.

Each step is independent. A failure is reported but never stops the other.

Credentials: same as gsc_report.py (GSC_SERVICE_ACCOUNT_JSON or
GOOGLE_APPLICATION_CREDENTIALS). Requires: pip install google-auth requests

Usage:
  python3 scripts/notify_search_engines.py https://keeper-photo-cleaner.pages.dev/guides/<slug> [more URLs]
"""

import base64
import json
import os
import sys
from urllib.parse import quote

import requests

HOST = "keeper-photo-cleaner.pages.dev"
SITEMAP = f"https://{HOST}/sitemap.xml"
INDEXNOW_KEY = "56b133d003635e73895b1792e00dbded"


def google_credentials():
    from google.oauth2 import service_account

    scopes = ["https://www.googleapis.com/auth/webmasters"]
    raw = os.environ.get("GSC_SERVICE_ACCOUNT_JSON", "").strip()
    if raw:
        if not raw.startswith("{"):
            raw = base64.b64decode(raw).decode()
        return service_account.Credentials.from_service_account_info(json.loads(raw), scopes=scopes)
    path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if path:
        return service_account.Credentials.from_service_account_file(path, scopes=scopes)
    return None


def submit_sitemap():
    from google.auth.transport.requests import AuthorizedSession

    creds = google_credentials()
    if creds is None:
        return "Google: skipped (no credentials)"
    session = AuthorizedSession(creds)
    # Use whichever property the account can see for this host, preferring a
    # domain property (sc-domain:) over a URL-prefix one.
    resp = session.get("https://searchconsole.googleapis.com/webmasters/v3/sites")
    resp.raise_for_status()
    sites = [s["siteUrl"] for s in resp.json().get("siteEntry", []) if HOST in s["siteUrl"]]
    if not sites:
        return f"Google: FAILED (the service account can't see a {HOST} property)"
    sites.sort(key=lambda s: not s.startswith("sc-domain:"))
    SITE = sites[0]
    url = (
        "https://searchconsole.googleapis.com/webmasters/v3/sites/"
        f"{quote(SITE, safe='')}/sitemaps/{quote(SITEMAP, safe='')}"
    )
    resp = session.put(url)
    if resp.ok:
        return f"Google: sitemap submitted ({SITEMAP})"
    if resp.status_code == 403:
        return (
            "Google: FAILED (403). The service account needs Full permission in "
            "Search Console > Settings > Users and permissions."
        )
    return f"Google: FAILED ({resp.status_code}) {resp.text[:200]}"


def ping_indexnow(urls):
    if not urls:
        return "IndexNow: skipped (no URLs given)"
    body = {
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"https://{HOST}/{INDEXNOW_KEY}.txt",
        "urlList": urls,
    }
    try:
        resp = requests.post("https://api.indexnow.org/indexnow", json=body, timeout=30)
    except requests.RequestException as e:
        return f"IndexNow: FAILED ({e})"
    # 200 = accepted, 202 = accepted and key validation pending.
    if resp.status_code in (200, 202):
        return f"IndexNow: submitted {len(urls)} URL(s) ({resp.status_code})"
    return f"IndexNow: FAILED ({resp.status_code}) {resp.text[:200]}"


def main():
    urls = [u for u in sys.argv[1:] if u.startswith(f"https://{HOST}/")]
    for step in (submit_sitemap, lambda: ping_indexnow(urls)):
        try:
            print(step())
        except Exception as e:  # never block a publish on notification
            print(f"FAILED: {e}")


if __name__ == "__main__":
    main()
