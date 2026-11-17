#!/usr/bin/env python3
"""Pull Google Search Console data for keeperphoto.app and print a Markdown report.

Credentials (first one found wins):
  GSC_SERVICE_ACCOUNT_JSON         service account key, as raw JSON or base64-encoded JSON
  GOOGLE_APPLICATION_CREDENTIALS   path to a service account key file

Optional:
  GSC_SITE_URL   Search Console property, e.g. "sc-domain:keeperphoto.app" or "https://keeperphoto.app/". Ignored
                 unless it names keeperphoto.app.
                 If unset, the first property the account can see that mentions
                 keeperphoto.app is used.

Requires: pip install google-auth requests

Usage:
  python3 scripts/gsc_report.py [--days 28] [--json out.json]
"""

import argparse
import base64
import datetime as dt
import json
import os
import sys
from urllib.parse import quote

from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
API = "https://searchconsole.googleapis.com/webmasters/v3"
DOMAIN = "keeperphoto.app"
# Search Console data usually lags by two to three days.
LAG_DAYS = 3


def load_credentials():
    raw = os.environ.get("GSC_SERVICE_ACCOUNT_JSON", "").strip()
    if raw:
        if not raw.startswith("{"):
            raw = base64.b64decode(raw).decode()
        return service_account.Credentials.from_service_account_info(json.loads(raw), scopes=SCOPES)
    path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if path:
        return service_account.Credentials.from_service_account_file(path, scopes=SCOPES)
    sys.exit("No credentials: set GSC_SERVICE_ACCOUNT_JSON or GOOGLE_APPLICATION_CREDENTIALS.")


def pick_site(session):
    # The cloud environment is shared with other sites, so only honour an override
    # that is actually for this domain.
    configured = os.environ.get("GSC_SITE_URL", "")
    if DOMAIN in configured:
        return configured
    resp = session.get(f"{API}/sites")
    resp.raise_for_status()
    sites = [s["siteUrl"] for s in resp.json().get("siteEntry", []) if DOMAIN in s["siteUrl"]]
    if not sites:
        sys.exit(
            f"The service account can't see a {DOMAIN} property. Add its email as a user "
            "in Search Console (Settings > Users and permissions)."
        )
    # Prefer the domain property, which covers every URL variant.
    sites.sort(key=lambda s: not s.startswith("sc-domain:"))
    return sites[0]


def query(session, site, start, end, dimensions, row_limit=500):
    body = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "dimensions": dimensions,
        "rowLimit": row_limit,
        "dataState": "final",
    }
    resp = session.post(f"{API}/sites/{quote(site, safe='')}/searchAnalytics/query", json=body)
    resp.raise_for_status()
    rows = []
    for r in resp.json().get("rows", []):
        row = dict(zip(dimensions, r.get("keys", [])))
        row.update(
            clicks=int(r["clicks"]),
            impressions=int(r["impressions"]),
            ctr=round(r["ctr"] * 100, 1),
            position=round(r["position"], 1),
        )
        rows.append(row)
    return rows


def table(rows, cols, limit):
    if not rows:
        return "_No data._\n"
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows[:limit]:
        cells = []
        for c in cols:
            v = r.get(c, "")
            if c == "page":
                v = v.replace(f"https://{DOMAIN}", "") or "/"
            cells.append(str(v).replace("|", "/"))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--json", help="also write the raw rows to this file")
    args = ap.parse_args()

    session = AuthorizedSession(load_credentials())
    site = pick_site(session)

    end = dt.date.today() - dt.timedelta(days=LAG_DAYS)
    start = end - dt.timedelta(days=args.days - 1)
    prev_end = start - dt.timedelta(days=1)
    prev_start = prev_end - dt.timedelta(days=args.days - 1)

    totals = query(session, site, start, end, ["date"], row_limit=1000)
    queries = query(session, site, start, end, ["query"], row_limit=1000)
    prev_queries = query(session, site, prev_start, prev_end, ["query"], row_limit=1000)
    pages = query(session, site, start, end, ["page"], row_limit=500)
    query_pages = query(session, site, start, end, ["query", "page"], row_limit=1000)

    prev_by_query = {r["query"]: r for r in prev_queries}
    for r in queries:
        p = prev_by_query.get(r["query"])
        r["prev_impressions"] = p["impressions"] if p else 0

    by_impr = sorted(queries, key=lambda r: -r["impressions"])
    # Queries Google already associates with the site but where we rank off page one
    # or earn few clicks: the best signal for new or improved content.
    opportunities = sorted(
        (r for r in queries if r["impressions"] >= 3 and (r["position"] > 8 or r["ctr"] < 2)),
        key=lambda r: -r["impressions"],
    )
    rising = sorted(
        (r for r in queries if r["impressions"] > r["prev_impressions"] and r["impressions"] >= 3),
        key=lambda r: -(r["impressions"] - r["prev_impressions"]),
    )

    clicks = sum(r["clicks"] for r in totals)
    impressions = sum(r["impressions"] for r in totals)

    print(f"# Search Console report: {site}\n")
    print(f"Period: {start} to {end} ({args.days} days, compared with {prev_start} to {prev_end})\n")
    print(f"- Clicks: {clicks}\n- Impressions: {impressions}\n- Distinct queries: {len(queries)}\n- Pages with impressions: {len(pages)}\n")
    print("## Content opportunities (impressions but weak position or CTR)\n")
    print(table(opportunities, ["query", "impressions", "clicks", "ctr", "position"], 60))
    print("## Rising queries (more impressions than the previous period)\n")
    print(table(rising, ["query", "impressions", "prev_impressions", "position"], 30))
    print("## Top queries by impressions\n")
    print(table(by_impr, ["query", "impressions", "clicks", "ctr", "position"], 100))
    # Pages that already rank on page one or near it but rarely get clicked: the
    # title and description are the likely problem, not the content.
    low_ctr = sorted(
        (r for r in pages if r["impressions"] >= 100 and r["position"] <= 15 and r["ctr"] < 1),
        key=lambda r: -r["impressions"],
    )
    print("## Low click rate (100+ impressions, position 15 or better, CTR under 1%)\n")
    print(table(low_ctr, ["page", "impressions", "clicks", "ctr", "position"], 20) if low_ctr else "None.\n")
    print("## Pages\n")
    print(table(sorted(pages, key=lambda r: -r["impressions"]), ["page", "impressions", "clicks", "ctr", "position"], 50))
    print("## Which page ranks for which query\n")
    print(table(sorted(query_pages, key=lambda r: -r["impressions"]), ["query", "page", "impressions", "position"], 120))

    if args.json:
        with open(args.json, "w") as f:
            json.dump(
                {"site": site, "start": str(start), "end": str(end), "queries": queries,
                 "pages": pages, "query_pages": query_pages},
                f,
                indent=2,
            )


if __name__ == "__main__":
    main()
