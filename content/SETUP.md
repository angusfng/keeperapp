# Article routine: setup

The routine is "Keeper SEO article (Tue/Thu/Sat)" on claude.ai (Code > Routines). It runs at 20:00 UTC on Monday, Wednesday and Friday: 7am on Tuesday, Thursday and Saturday in Sydney during daylight saving, and 6am from April to October. It uses the Default cloud environment and Opus 5.5, the same as the Sleep Tiles and DrivePrep NSW routines, on different days so the three never run at once.

## Search Console access

The routine shares DrivePrep's read-and-submit service account, whose key is already in the Default environment as `GSC_SERVICE_ACCOUNT_JSON`. It needs access to this site's property too:

1. In https://search.google.com/search-console, add a property. A pages.dev address can't be a Domain property, so choose **URL prefix** and enter `https://keeper-photo-cleaner.pages.dev/`.
2. Verify it with the **HTML tag** method: copy the `<meta name="google-site-verification" ...>` tag into the `<head>` of `public/index.html`, push, wait a minute for the deploy, then click Verify. (If the site moves to its own domain, add a Domain property instead and verify it with a DNS record.)
3. Settings > Users and permissions > Add user. Paste `gsc-reader@driveprep-seo-512112.iam.gserviceaccount.com` and choose **Full**. Full lets the routine resubmit the sitemap after each article. Restricted is enough for the report only.
4. Sitemaps > add `sitemap.xml`.

If the report fails with "The service account can't see a keeper-photo-cleaner.pages.dev property", step 3 is missing.

The environment is shared with other sites, so `gsc_report.py` ignores a `GSC_SITE_URL` that doesn't name this site's host.

## Other requirements

- Network: the environment must reach `oauth2.googleapis.com`, `searchconsole.googleapis.com`, `suggestqueries.google.com`, `api.indexnow.org`, `support.apple.com` and PyPI. The other routines already need the same.
- Pushes: the routine pushes straight to `main` of `angusfng/keeperapp`. If runs end with a push rejected or limited to `claude/` branches, allow unrestricted branch pushes for this repository.
- IndexNow: the key file is `public/56b133d003635e73895b1792e00dbded.txt`. Don't delete it.

## Test it

Use **Run now** on the routine page. Then check that the run's final message gives an article URL (or says why it published nothing) and says Search Console data was available, that the page is live a minute or two later, and that `content/log.md` has a new row.

Optionally, test the key locally first:

```bash
GOOGLE_APPLICATION_CREDENTIALS=~/Downloads/driveprep-seo-xxxx.json python3 scripts/gsc_report.py | head -40
```
