# Keeper site

Marketing site, SEO guides, support and privacy pages for the Keeper iOS app ("Swipe Photo Cleaner: Keeper", App Store id6793817811). Live at https://keeper-photo-cleaner.pages.dev.

This repo was renamed from `keeper-web` to `keeperapp`; GitHub still redirects the old name. The local checkout lives at `~/projects/keeper-web`.

## Deploy

Push to `main`. The Cloudflare Pages project `keeper-photo-cleaner` is connected to this repo and serves `public/` with no build step (`wrangler.toml` sets `pages_build_output_dir`). Other branches get preview deployments.

The app links to `/privacy` on this address (paywall, Settings, App Store description, Superwall paywall), so `public/privacy.html` must stay at that URL.

The root `index.html` and `privacy.html` are redirect stubs for the old GitHub Pages address (angusfng.github.io/keeperapp), which still serves the repo root. Cloudflare never serves them.

Preview locally with `wrangler pages dev public --port 8788` (clean URLs like `/support` work there, unlike a plain static server).

## Pages

- `public/index.html`: homepage. Its FAQ is duplicated in the FAQPage JSON-LD in the head, so change both together
  - `public/landing.css`: homepage-only layout (hero, swipe demo, how it works, dark feature band, bento, privacy, FAQ)
  - `public/landing.js`: the draggable polaroid swipe demo in the hero (pointer, buttons, arrow keys, undo) and scroll reveal. The demo's photo sizes are made up
- `public/styles.css`: shared styles. Colour tokens mirror `keeper/DesignSystem/Theme.swift` in the app (warm `#F6F2EA` background, accent blue, keep green, delete red, amber glow, the always-dark immersive `#0B0B0D`). Type uses `ui-rounded` (SF Pro Rounded on Apple devices) for headings like the app
- `public/guides/`: SEO guides at clean URLs (`/guides/recently-deleted-photos-iphone` from `recently-deleted-photos-iphone.html`; the hub is `/guides/`). The four hand-written guides are sourced from Apple Support pages opened on 2026-11-18:
  - `how-to-delete-photos-on-iphone.html`, `free-up-iphone-storage-photos.html`, `recently-deleted-photos-iphone.html`, `delete-photos-from-iphone-not-icloud.html`
  - Every page's footer carries the same guides list, so a new hand-written guide means adding it to every footer, the hub, `sitemap.xml`, `llms.txt` and the related cards of the guides it fits with. Routine articles only go in the hub (below `ARTICLES:START`), sitemap and llms.txt
- `public/photo-storage-calculator.html`: free calculator (space Photos uses / item count x share deleted). Inline script, saves inputs in `localStorage` (`keeper-calc`)
- `public/support.html`, `public/privacy.html` (wording kept from the live policy; update the date when it changes), `public/404.html`
- `public/assets/screens/*.webp`: app screenshots from `keeper/marketing/screenshots/captures/iphone` (`cwebp -q 82 -resize 603 0`)
- `public/assets/photos/*.webp`: demo photos from `keeper/marketing/creative-assets/photos` (Unsplash License, credits in `keeper/marketing/screenshots/photo-credits.txt`)
- `public/assets/og.png`: 1200x630 share image, rendered with headless Chrome
- `public/assets/qr-app-store.svg`: QR code straight to the App Store listing. Regenerate with `python3 scripts/make_qr.py <url> public/assets/qr-app-store.svg` (no dependencies; verified with CoreImage). `qr-dock.js` shows it as a floating card to desktop visitors
- `public/_redirects`: `/app` and `/download` go to the App Store listing
- `public/_headers`: security headers plus cache rules (assets 7 days, CSS and JS 4 hours). When you change a shared CSS or JS file, bump its `?v=` everywhere it's referenced, including `content/article-template.html`
- `public/robots.txt`, `public/sitemap.xml` (homepage lists its screenshots as image entries; update `lastmod` when a page changes), `public/llms.txt` (plain-text summary for AI search)
- Icons: `favicon.ico`, `assets/apple-touch-icon.png`, `assets/icon-192.png`, `assets/app-icon.png`, made from the app's `AppIcon-light.png` with `sips`

## Article routine

A Claude routine publishes up to three SEO articles a week (Tuesday, Thursday and Saturday mornings, Sydney time) to `public/guides/`, modelled on the Sleep Tiles and DrivePrep NSW ones. It picks topics from Search Console (`scripts/gsc_report.py`), or Google autocomplete (`scripts/suggest.py`) when Search Console has nothing with enough demand, writes from `content/article-template.html`, must pass `scripts/check_article.py` and a separate QA reviewer, then pushes to `main`. `content/` and `scripts/` are never deployed.

- `content/PLAYBOOK.md`: the steps every run follows
- `content/STYLE.md`: voice, US English, sourcing rules (Apple Support and makers' help pages only) and the Keeper facts an article may state
- `content/QA.md`: the reviewer brief
- `content/log.md`: everything published, newest first
- `content/topics.md`: backlog ideas
- `content/SETUP.md`: Search Console access and how to test the routine

## Moving to a custom domain

`python3 scripts/set_domain.py <domain>` rewrites every absolute URL. Then add the domain to the Pages project, add a Search Console Domain property for it (see `content/SETUP.md`), update the routine prompt, and keep `keeper-photo-cleaner.pages.dev/privacy` working because shipped app builds link to it.
