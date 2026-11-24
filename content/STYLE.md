# Writing style for Keeper articles

Readers are adults, mostly in the US, with an iPhone that's full or close to it: someone who just saw "iPhone Storage Full", someone paying for iCloud storage they'd rather not, someone who deleted a photo by mistake, someone with 30,000 photos who doesn't know where to start. Write the way a friend who knows iPhones well would explain it: clear, calm and specific, never salesy and never alarming.

Also follow `.claude/skills/nonai-writing/SKILL.md`, which lists the patterns that make text read as AI-generated. If it conflicts with this file, this file wins.

`scripts/check_article.py` enforces the mechanical rules below. Passing it is the minimum. Reading like a real person wrote it is the actual goal.

## US English

- US spelling: color, organize, recognize, favorite, gray, center, analyze, toward, labeled, canceled.
- Dates as November 18, 2026. Sizes as 5 GB, 250 MB (a space between the number and the unit).
- Straight apostrophes are fine. In HTML attributes, write `'` as `&#x27;`, as the hand-written guides do.

## Sound like a person, not a model

- No em dashes (—) anywhere, and no spaced en dashes ( – ). Use a full stop, comma, colon or brackets instead.
- No middle dots (·) as separators. Use commas or separate sentences.
- No emojis and no exclamation marks.
- Lead with the answer. The first sentence of each section should answer its heading.
- Vary sentence length. Some short. Some longer with a real detail in them.
- Be specific: real menu paths, real button names, real examples ("ten tries at the same sunset", "a screenshot of a boarding pass from 2022") instead of vague advice ("remove unwanted photos").
- Prefer plain verbs: use, check, delete, open, tap, keep, move. Not leverage, utilize, empower, elevate, foster, unlock your, optimize your life.
- Don't announce what you're about to say ("In this article we'll explore..."). Just say it.
- Don't wrap up with a summary paragraph that repeats everything. End on the last useful point.
- Avoid stock phrases: delve, dive into, journey, landscape, realm, tapestry, seamless, robust, crucial, vital, comprehensive, game-changer, it's important to note, it's worth noting, whether you're a... or a..., look no further, ever wondered, rest assured, in conclusion, furthermore, moreover, plethora, myriad, embark, ultimate guide, a testament to, precious memories, digital clutter, declutter your life, effortlessly, hassle-free.
- No fear and no hype: don't say a full phone is "a disaster waiting to happen", and don't promise "gigabytes in seconds".
- Contractions (you're, don't, it's) are good.
- Don't overuse lists. Numbered lists are right for steps on a phone. Explanations go in paragraphs.
- Don't use the same structure every time. Some articles suit step-by-step, some a comparison table, some a short "it depends" explainer. Vary the openings too.

## Accuracy rules

People follow these steps on their own phone, sometimes with irreplaceable photos. Get it right or leave it out.

- Every menu path, button name, number, limit or claim about how an iPhone, iCloud or another service behaves must come from a page you actually opened during this run, linked inline and listed in the Sources box.
- Trusted sources (the checker's list in `scripts/check_article.py`): support.apple.com (support articles and the iPhone, iPad and Mac User Guides), developer.apple.com and apple.com legal and privacy pages for Apple. For other services, the maker's own help pages: support.google.com (Google Photos, Google One), support.microsoft.com (OneDrive, Windows Photos), Amazon Photos help, help.dropbox.com, Samsung support. Blogs, forums, Reddit and tech news sites are never a source, even when they're right.
- iOS changes every year. When Apple gives different steps for different iOS versions, give each one and label it ("iOS 27 or later", "iOS 26 or earlier"). Don't present one version's steps as universal.
- State only what the source says. Don't infer, and don't add certainty the source doesn't have. If Apple doesn't say what happens in a case, say that plainly rather than guessing.
- Any step that permanently removes photos (deleting from Recently Deleted, turning off a sync setting, erasing a device) must say clearly that it's permanent or point to Apple's warning, and suggest a backup first when Apple does.
- Never tell readers that a deleted photo can be recovered after it has left Recently Deleted. Don't recommend data recovery software.
- Keep what Apple's tools do separate from what Keeper does.

## Facts about Keeper you may state

- An iPhone and iPad app (App Store name "Swipe Photo Cleaner: Keeper"), for iOS and iPadOS 18 or later. Free to download; a weekly or yearly subscription is needed to use it. Don't quote prices.
- It shows the photos and videos in your library one at a time, full screen. Swipe right to keep, swipe left to delete. There are keep and delete buttons too.
- Undo brings back the last swipe while you're still in the session.
- Nothing is deleted while you swipe. Choices are queued and only applied when you tap Save. iOS then asks you to confirm the deletion once.
- Deleted photos go to the Recently Deleted album in the Photos app, like any other deletion. With iCloud Photos on, deleting in Keeper deletes on all devices, the same as the Photos app.
- Ways to start a session: Shuffle (a random spot), Pick a Photo, Oldest First, Newest First, or browse by month and clear one month at a time. A session can be limited to one album.
- On This Day: photos taken on today's date in earlier years.
- Shows the date, place and camera for each photo. Plays videos and Live Photos.
- A strip of thumbnails lets you jump back to any photo in the session.
- After saving, it shows how many photos you kept and deleted and how much storage was freed. Lifetime stats (kept, deleted, storage freed, percent of library reviewed) and a daily streak.
- Resume from Last picks up where you left off.
- Works with limited photo access: it only sees the photos you allowed.
- Photos never leave the device. No account, no ads.
- Available in 12 languages.
- Keeper does NOT find duplicates, blurry photos or screenshots automatically, and doesn't compress or back up photos. Never imply it does.

Don't invent anything else: no ratings, user numbers, speed claims ("clean 1,000 photos in 5 minutes") or results.

## Other apps

Only comparison articles talk about other photo apps, under the rules in `content/PLAYBOOK.md`. Facts about another app come from its App Store page or its developer's own site, opened that day. No ratings, prices, download numbers or reviews, nothing negative that its own listing doesn't say, and no claim that it lacks a feature. Be fair: if another app does a job better than Keeper, say so.

## Mentioning the app

Mention Keeper naturally once in the article text, in the Keeper section, with the in-text App Store link. Comparison articles are the exception: Keeper gets its own entry alongside the other apps (see "Comparison articles" in `content/PLAYBOOK.md`), still with only one in-text App Store link. The closing band is already in the template. The article must be genuinely useful to someone who never downloads the app.
