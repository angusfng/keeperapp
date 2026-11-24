# Article playbook

A scheduled Claude routine follows this file three times a week (Tuesday, Thursday and Saturday mornings, Sydney time). Each run publishes at most one new article to keeperphoto.app by pushing to `main`, and Cloudflare Pages deploys it within a minute or two. There's no human review before it goes live, so every step here matters.

The site lives in `public/`. Everything in `content/` and `scripts/` is for the routine and is never deployed.

Read `content/STYLE.md` and `.claude/skills/nonai-writing/SKILL.md` before writing anything. Both apply to every article. Where they differ, STYLE.md wins.

Readers follow these steps on their own phones. A wrong menu path or a wrong claim about what deleting does can cost someone their photos. Accuracy beats volume every time: a skipped run is fine, a weak or wrong page is not.

## 1. Get the data

```bash
python3 -m pip install -q --ignore-installed cffi cryptography google-auth requests 2>&1 | grep -v "root. user" || true
python3 scripts/gsc_report.py > /tmp/gsc.md
python3 scripts/suggest.py > /tmp/suggest.md || true
```

Read `/tmp/gsc.md`. If the report script fails (missing credentials, no network, no property access), stop. Publish nothing and commit nothing. End with the exact error and the likely fix (see `content/SETUP.md`). Search Console access is a hard requirement, even while the site is too new to have much data in it.

`/tmp/suggest.md` lists Google autocomplete suggestions (US English) for photo cleanup and iPhone storage topics. If it failed, carry on without it.

### Tuesday: fix a title that doesn't get clicked

On Tuesday runs only (`TZ=Australia/Sydney date +%u` prints `2`), do this before step 2, as well as the rest of the run. A page that ranks on page one but rarely gets clicked usually has a title or description that doesn't match what people searched, or doesn't show they'll find the answer there.

1. Take the first page in the report's "Low click rate" table whose title hasn't changed in the last 28 days. Check `content/log.md` for `title` rows. If the table says "None", or every page in it changed recently, skip this section. (While the site is new, expect it to say "None".)
2. Look up that page's queries in "Which page ranks for which query". Note the words people use and what they want (a number, a how-to, a comparison).
3. Rewrite the `<title>` (up to 62 characters before " | Keeper") and the meta description (110 to 155 characters). Put the main query near the start, and say specifically what the page gives them. Copy the new title to `og:title`, `twitter:title` and the JSON-LD `headline`, and the description to `og:description`, `twitter:description` and the JSON-LD `description`. Use only facts already on the page and backed by its sources. No hype, no clickbait, and nothing the page doesn't deliver, like "free".
4. Don't change the URL, H1 or body. Update the page's `dateModified` and its sitemap `lastmod`.
5. Add a log row with `title` in the slug column. In the notes, give the page, the old and new title, and its impressions, clicks, CTR and position from today's report, so a later run can tell if it worked. If a page's CTR has dropped 4 weeks after a title change, put the old title back.
6. Send the new title and description to the QA reviewer in step 7 as changed sentences, along with the page's source URLs. If no article is published today, still run the review for them. If it fails, revert the change.

## 2. Pick one topic

Read `content/log.md` (everything already published) and skim the titles and headings of every page in `public/guides/`.

Choose in this order:

1. A query from "Content opportunities" or "Rising queries" that no existing page answers well. Group close variants ("how to delete all photos on iphone", "how to delete all pictures from iphone") into one topic.
2. A query that an existing page ranks for at positions 8 to 30, where a focused article would serve the searcher better than the broad page it currently lands on.
3. Only if nothing from 1 or 2 clears the minimum demand bar below: a topic from `/tmp/suggest.md`. Search Console only shows searches the site already appears for, and a new site appears for very few, so this is how the site reaches new questions. It must:
   - group at least 3 related suggestions into one question (for example "how to delete screenshots on iphone", "delete all screenshots iphone" and "how to delete screenshots on iphone at once"), which shows real search demand. Suggestions surfaced by more than one seed are the strongest.
   - be a lasting question someone asks about their own photos or storage: deleting, recovering and hiding photos, Recently Deleted, duplicates, screenshots, videos and Live Photos, iPhone and iCloud storage, iCloud Photos settings, moving photos to a computer or another service, and organizing a camera roll.
   - have a clear answer on a trusted source (see STYLE.md)
   - suit someone with a full camera roll, so the Keeper section is genuinely useful

   Write "Google autocomplete" in the log row's source column, and list the suggestions in the notes.

Prefer topics closest to what the app does (deleting photos, clearing a camera roll, freeing up storage, Recently Deleted). Those bring readers who want a photo cleaner.

Skip anything that:

- is about data recovery after a photo is permanently gone, jailbreaking, hacking, spying on someone else's phone, or getting into someone else's account.
- is about Android-only features, unless the question is about moving photos between Android and iPhone and the maker documents the steps.
- is a deal, news or anything dated ("2026", "this week"). App roundups and app-versus-app pages are allowed only as comparison articles (below), never as a standalone review of a competing app.
- is a brand or navigational query for another product, unless it's a how-to the maker documents (for example how to move photos to Google Photos, from Google's help pages).
- would compete with an existing page. If a hand-written guide already ranks in the top 15 for the query, the new article must answer a different, specific question within that topic, link to that guide, and the guide must link back (step 5.3). Never target the exact query a hand-written guide is ranking for.
- overlaps an article in `content/log.md`. Two pages chasing the same search compete with each other. If today's best query belongs to an existing article, improve that article instead (step 6) and pick a different topic for the new one.
- you can't back with trusted sources.

The four hand-written guides are `how-to-delete-photos-on-iphone`, `free-up-iphone-storage-photos`, `recently-deleted-photos-iphone` and `delete-photos-from-iphone-not-icloud`.

**Minimum demand.** For topics from Search Console, the topic's query group (the target query plus the close variants you'd fold into it) must have at least 10 impressions in total in the report's 28 days. `content/topics.md` ideas count only if they match a Search Console query group that clears this bar, or an autocomplete group that meets the rules in option 3.

### Comparison articles

People also search for apps: "best photo cleaner app for iphone", "best app to delete photos on iphone", "tinder for photos app", "app to clean up camera roll", "<app> alternatives". These readers are the closest to downloading a photo cleaner, so the site answers them with honest comparison articles.

- **When.** On Saturday runs (`TZ=Australia/Sydney date +%u` prints `6`), write a comparison article instead of a how-to if a comparison query group meets the minimum demand bar and no comparison went out in the last 6 days (look for `Type: comparison` in the log notes). On other days, write one only if Search Console shows a comparison query group with 10+ impressions. Never more than one a week.
- **Shapes.** (a) "Best apps to <job> on iPhone" for one job: deleting photos fast, clearing a camera roll, finding duplicates, freeing up storage. (b) "<App> alternatives" for a photo cleanup app that shows up in Search Console or autocomplete. (c) "Keeper vs <App>" only when Search Console shows people searching for both. Each page targets a different query. Never two pages for the same one.
- **Which apps.** 4 to 6 entries: the built-in Photos app tools (always, first or second, because they're free and many readers need nothing else), Keeper, and 2 to 4 other iPhone apps made for that job, found on the App Store (use WebSearch with `site:apps.apple.com`). Pick apps that are currently listed and clearly built for the job. Never pick an app because it looks weak.
- **Sources.** Facts about another app come only from its App Store page (apps.apple.com) or its developer's own website, opened in this run, and go in `/tmp/facts.md` like any other fact. Facts about the Photos app come from Apple Support as usual. Keeper facts come only from STYLE.md.
- **What you may say about another app:** what its App Store description or developer site says it does, whether it's free or offers in-app purchases (as its App Store page shows), its iOS requirement, and its App Privacy label headings as shown (for example "Data Not Collected" or "Data Used to Track You"). When a claim is the developer's own, say so ("its App Store listing says it can...").
- **What you may not say:** star ratings, review counts, download numbers, rankings or prices (they change daily and differ by country); anything from user reviews, Reddit or tech blogs; that an app lacks a feature (you may say its listing doesn't mention it); that it's slow, buggy, unsafe or a scam; anything about the company behind it. Don't copy its description. Summarize in your own words.
- **Fairness.** Start the lede with this disclosure, word for word: "Keeper is our app, so we've stuck to what each app's own App Store listing says." Give every entry the same fields in the comparison table: what it's for, how you review photos, price model, iOS requirement and privacy label. Give each app an honest "good for" line. Say plainly when another app suits a job better, for example a duplicate finder for duplicates, because Keeper doesn't find them. Don't crown an overall winner. Group the advice by need ("If you want to...").
- **Keeper's entry.** List Keeper first only when the query is about swiping or reviewing photos one at a time, which is what it does. Otherwise order entries by how well they fit the query.
- **Titles.** "Best Apps to Delete Photos on iPhone" style. No year in the slug or title, no "#1", and the number in the title (if any) must match the entries.
- **Structure.** Use the same template. The short answer names the options by need. Sections: how the apps were picked (one short paragraph), the comparison table, a short section per app (or grouped), and how to do the job with no extra app. In place of a separate Keeper section, Keeper gets its own entry like the others, with the one in-text App Store link. Add `data-type="comparison"` to the `<article>` tag so the checker runs its extra checks, and start the log row's notes with `Type: comparison`.
- **Freshness.** Apps change. In every maintenance run, a comparison article whose `dateModified` is more than 60 days old comes first: reopen each app's listing, update or cut whatever changed, drop apps no longer on the App Store, and update `dateModified` and the sitemap `lastmod`.

**If no topic qualifies, don't write a new article.** Do a maintenance run instead:

1. Do step 6, choosing the existing article or hand-written guide with the most impressions for queries it doesn't fully answer. Add the missing section or FAQ item to an article, or make step 5.4 corrections to a hand-written guide. Keep to the same sourcing rules.
2. Run steps 7 to 9 for the changed page. In the QA prompt, list the new or changed sentences.
3. Add a log row with `maintenance` in the slug column, the page you improved, the queries it was missing, and why no new topic qualified.

If nothing is worth improving either, commit nothing (apart from a Tuesday title fix) and end with a short report saying so.

## 3. Research

Open sources with WebFetch, from the trusted list in STYLE.md. Use WebSearch to find the right page if you need to, but only take facts from pages you actually opened in this run. For how an iPhone, iCloud or the Photos app works, use Apple's own pages (support.apple.com articles and the iPhone User Guide). For other services, use the maker's own help pages. Apple's iPhone User Guide pages are long: if WebFetch returns only the table of contents, call it again with `offset` to read the article text, or use the matching support.apple.com/en-us/NNNNNN article.

Menu paths change between iOS versions. When Apple gives different steps for different versions, give both and say which is which. Never write a path you haven't seen on an Apple page today.

Save each fact you'll use, with the URL it came from, to `/tmp/facts.md` (one line each: `- <fact> | <url>`). The QA reviewer in step 7 checks the article against this file, so a fact that isn't in it will fail review. If two sources disagree, say so plainly or leave the fact out. Don't average them or pick the more dramatic one.

For facts about Keeper itself, use only the list in STYLE.md.

## 4. Write the article

1. Pick a short, descriptive slug in lowercase with hyphens, close to the search query (e.g. `how-to-delete-screenshots-on-iphone`). Don't add dates.
2. Copy `content/article-template.html` to `public/guides/<slug>.html`.
3. Fill in every `{{PLACEHOLDER}}` and delete every `TEMPLATE` comment:
   - SEO_TITLE: up to 62 characters, matching how people search. The page adds " | Keeper" after it. Title case is fine, as the hand-written guides use it.
   - H1: can be more natural than the SEO title. Use it in the breadcrumb JSON-LD too.
   - META_DESCRIPTION: 110 to 155 characters, saying what the reader will learn. In the HTML attributes, write apostrophes as `&#x27;`. In JSON-LD, use a plain `'`.
   - LEDE: one or two sentences under the H1 saying what the page covers.
   - DATE_ISO is today's date in Sydney. Get it with `TZ=Australia/Sydney date +%F`, because the routine runs early in the morning Sydney time, while it's still the previous day in UTC. DATE_HUMAN uses the format November 11, 2026.
   - SHORT_ANSWER: two or three sentences that fully answer the main question, with the key number if there is one.
   - 4 to 6 sections. One is the Keeper section: the general advice first (what anyone can do in Photos or Settings), then Keeper named once with the in-text App Store link and only the app facts that help with this topic. The others should be useful on their own.
   - 3 to 5 FAQ items. The FAQPage JSON-LD must match the visible questions and answers, with plain text and no HTML.
   - Sources: every page you used, each with a short note on what it covers.
   - More guides: exactly 3 cards linking to the most relevant existing guides, articles or the `/photo-storage-calculator`. When a section talks about how much space photos use or how much a cleanup would free, link the calculator in the text as well.

   - CTA_HEADING and CTA_BODY: a short closing line tied to the topic, the same shape as the hand-written guides ("Delete the right photos, faster."). No hype.
4. Put the target query where search engines weigh it most, in natural wording, never stuffed: the slug, the SEO title (near the start), the H1, the first sentence of the short answer, and at least one H2. Phrase H2s and FAQ questions the way people actually search, using the question-style queries from the report or autocomplete.
5. Aim for 800 to 1,400 words in the body. Long enough to fully answer the question, and no padding.
6. Write at about a grade 8 or 9 reading level: short sentences, everyday words, and every acronym spelled out the first time (HRV, REM). The checker fails a reading grade above 9 and any sentence over 32 words.
7. Use a table where it helps the reader compare (options side by side, steps by iOS version), with `class="score-table"` inside `<div class="table-scroll">` and a `<caption class="sr">`.

## 5. Wire it into the site

1. `public/guides/index.html`: add a card right after the `<!-- ARTICLES:START ... -->` line, so the newest comes first:

   ```html
           <li><a href="/guides/<slug>"><strong>Short title</strong><span>One-line description.</span></a></li>
   ```

2. `public/sitemap.xml`: add `<url><loc>https://keeperphoto.app/guides/<slug></loc><lastmod>YYYY-MM-DD</lastmod></url>` after the last guide entry, indented to match. Also update the `/guides/` entry's `lastmod` to today.
3. `public/llms.txt`: add `- [<H1>](https://keeperphoto.app/guides/<slug>)` at the end of the Guides list.
4. Add one natural in-text link to the new article from the hand-written guide it relates to most. Add one short sentence at the end of the most relevant section, for example "For the quickest way to clear them, see <a href=\"/guides/<slug>\">how to delete screenshots on iPhone</a>." Apart from step 5.5 corrections, don't change anything else in that guide. Skip this if the guide already links to an article on the same topic. Also add one in-text link from the most relevant earlier article, if one fits, and update that article's `dateModified`, visible "Updated" date and sitemap `lastmod`.
5. **Correct factual errors in the hand-written guides.** If a trusted page you opened today contradicts something a hand-written guide says, fix it:
   - Only change what the source proves wrong. Rewrite that sentence (and its JSON-LD copy, if there is one) to say exactly what the source says, in the guide's voice. Don't restructure or rewrite anything that's still accurate.
   - Never change a statement about how Keeper itself works. If one looks wrong, note it in the log row for the owner.
   - Add the fact and its URL to `/tmp/facts.md`, update the guide's `dateModified` and its sitemap `lastmod`, and list the correction in the log row's notes with the old and new wording.
   - If you can't confirm the correct fact on a trusted page, don't edit. Note the suspected error in the log row instead.
6. If you used a topic from `content/topics.md`, tick it off there (`- [x]`).
7. Add a row to the top of the table in `content/log.md`.

## 6. Improve an existing article (at most one per run)

In the report's "Pages" and "Which page ranks for which query" tables, find `/guides/` articles published more than 4 weeks ago (see `content/log.md`). If one is getting impressions but sits at positions 8 to 20, add the section or FAQ item that answers the queries it ranks for but doesn't fully cover. If an article older than 8 weeks has no impressions at all, note it in the log row so the owner can see it. Don't delete or rewrite it.

If step 2 found a query that clearly belongs to an article already in `public/guides/`, add a short section or FAQ item that answers it, sourced the same way. Update that page's `dateModified`, its visible "Updated" date and its sitemap `lastmod`. Mention it in the log row's notes. Don't rewrite the hand-written guides (beyond the step 5.4 link and step 5.5 corrections) or the homepage.

## 7. Check

```bash
python3 scripts/check_article.py
```

Fix everything it reports and rerun until every article passes. Then do the "Quick review pass" from `.claude/skills/nonai-writing/SKILL.md` on every visible sentence, including the headings, short answer, FAQ answers, card blurbs and CTA.

### Source check before review

Most failed reviews come from sentences that go a little past what the source says: your own comparison between two sources, your own arithmetic on a source's number, a conclusion the source doesn't draw, or a unit or word the source doesn't use (for example "percentage points" when the source says "%"). Before the QA review, go through every factual sentence in the article, including the short answer, FAQ answers and JSON-LD, and match it to a line in `/tmp/facts.md`. If the sentence says more than that line, cut it back to what the line says or delete it. Don't add a new fact to `/tmp/facts.md` unless you opened its page in this run.

### Independent QA review

Then send the article to a separate reviewer using the Agent tool (general-purpose subagent). Don't review it yourself and call that QA. Give the reviewer this prompt, with the slug and queries filled in:

> Follow the reviewer instructions in content/QA.md. Article: public/guides/<slug>.html. Target query: "<query>". Close variants: <variants>. Research notes: /tmp/facts.md. Don't edit any files.

Don't pass on your own opinion of the article, or hints about what to look for.

- **PASS:** fix any OTHER items that are quick and clearly right, rerun the checker, add "QA: <n> review(s)" to the log row's notes, and go to step 8.
- **FAIL:** fix every CRITICAL item, and the OTHER items. For a CRITICAL item about a fact or claim, delete the sentence, or replace it with wording that says only what a line in `/tmp/facts.md` says. Don't reword it into a new claim: rewording is how new problems get in. Delete it everywhere it appears (body, short answer, FAQ, JSON-LD). Rerun the checker until it passes. Then start a **new** reviewer with the same prompt. Don't reuse the old one, and don't tell it what you changed.
- At most 3 reviews in total. If the third review still fails, go to the salvage step below. Don't start a fourth review.

### Salvage after a third failed review

A third FAIL doesn't throw the article away. Deleting a sentence can't add an unsourced claim, so you can still publish once the flagged sentences are gone:

1. Salvage is allowed only if the third review's CRITICAL items are all specific sentences to fix or delete, the article still answers the target query, and no area other than facts scored 1 or 2. Otherwise skip to point 5.
2. Delete every sentence quoted in a CRITICAL item, everywhere it appears (body, short answer, FAQ answers, FAQPage JSON-LD, meta description). Delete only. Don't add, rewrite or replace any wording, apart from the smallest change needed so the paragraph around a cut still reads correctly, like dropping a "Also," that now has nothing before it. Never bring in a new fact.
3. If a cut leaves a section or FAQ answer empty or meaningless, delete the whole section or FAQ item (and its JSON-LD entry). The article needs at least 3 sections and 3 FAQ items after the cuts.
4. Rerun the checker. If it passes, the short answer still answers the target query, and the article still has at least 3 sections and 3 FAQ items, publish it in step 8. Add "QA: 3 reviews, salvaged" to the log row's notes, and list every deleted sentence in the log row's notes and in your final report.
5. If salvage isn't allowed or doesn't work, revert the new article and everything added for it in step 5, and do a maintenance run from step 2 instead, so the run still improves something. Report the remaining CRITICAL items too.

Salvage covers the new article only. A changed sentence on an existing page that fails review still gets reverted, as described below.

If you also changed an existing page in steps 5.4, 5.5 or 6 or the Tuesday title fix, the reviewer only needs to check the new or changed sentences in it. Add them to the prompt as a list of quotes, giving the page and, for each step 5.5 correction, the old wording and the URL that supports the new wording. A correction that fails review gets reverted, not reworded on a guess.

## 8. Publish

Only touch `public/guides/`, `public/sitemap.xml`, `public/llms.txt` and `content/`. Never edit `public/index.html`, `landing.css`, `landing.js`, `styles.css`, `qr-dock.js`, `photo-storage-calculator.html`, `_headers`, `_redirects`, `robots.txt`, `privacy.html` or `support.html`. In the hand-written guides, only add the single step 5.4 sentence, make step 5.5 corrections and make the Tuesday title fix.

```bash
git add public/guides public/sitemap.xml public/llms.txt content
git commit -m "Add article: <H1>"
git push origin HEAD:main
```

If the push is rejected, run `git pull --rebase origin main` and push again.

Once the push succeeds, tell search engines about the new page, plus any page you updated:

```bash
python3 scripts/notify_search_engines.py https://keeperphoto.app/guides/<slug> [other updated URLs]
```

This resubmits the sitemap to Google and sends the URLs to IndexNow (Bing and others). It never blocks publishing. Include its output in your report. If Google says it needs Full permission, say so plainly, because the owner has to change that in Search Console.

## 9. Report

Finish with a few lines: the article's URL (`https://keeperphoto.app/guides/<slug>`), the target query, where the topic came from and why you picked it, any existing page you improved, any title you changed (old and new), whether Search Console data was available, and how many QA reviews it took, with the final scores.
