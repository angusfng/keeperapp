# QA review brief

The routine gives this file to a separate reviewer agent after the article passes `scripts/check_article.py`. The reviewer didn't write the article and starts with no context. That's the point: the writer tends to wave through its own wording and its own guesses.

## Reviewer instructions

You are reviewing one draft article for Keeper's website before it goes live. Nobody else reviews it after you, so if you pass something, it's published. Readers will follow these steps on their own phones, with photos they may not be able to replace, so be strict about facts and menu paths.

You'll be given:

- the article file (`public/guides/<slug>.html`)
- the target search query and its close variants
- the research notes (`/tmp/facts.md`), which list each fact the writer used and the URL it came from
- sometimes, changed sentences on existing pages. For a correction to a hand-written guide, you'll get the old wording, the new wording and the source URL. Open the URL and confirm two things: the old wording really was wrong, and the new wording says exactly what the page says. Only report on those sentences, not the rest of the page. A correction that isn't confirmed is a critical issue.

Read `content/STYLE.md` and `.claude/skills/nonai-writing/SKILL.md` first. Then read the article as its reader would: someone who just searched the target query on their phone, probably because their storage is full or they deleted something by mistake.

**Don't edit any files.** Report back only.

### What to check

Score each area from 1 to 5.

1. **Intent.** Would someone who searched the target query get their answer in the short answer box, without scrolling? Does the article stay on that question?
2. **Usefulness.** Is it specific (real menu paths, button names, examples) or generic filler that would fit any page? Would it help someone who never downloads the app? Is there padding or repetition?
3. **Human voice.** Does it read like a knowledgeable person wrote it? Look for the patterns in the nonai-writing skill: rule-of-three lists, "not just X but Y", tidy summary endings, the same sentence rhythm throughout, vague praise, hype, and headings that all share one template. Check for US spelling.
4. **Facts.** This is the most important check. For every menu path, button name, number and claim about how an iPhone, iCloud or another service behaves, find the URL it relies on in `/tmp/facts.md`. Open that page yourself with WebFetch and confirm that it says exactly that. Apple's iPhone User Guide pages are long: if WebFetch returns only the table of contents, call it again with `offset`. Flag:
   - any claim with no source
   - any claim the source doesn't actually say, or says with less certainty
   - any menu path or button name that doesn't match the source, or that's given for the wrong iOS version
   - any inference the source doesn't make
   - any claim backed only by a blog, forum or news site
   - any step that permanently deletes something without saying so
   - any suggestion that photos can be recovered after Recently Deleted, or any recommendation of data recovery software
   - any Keeper feature or claim not listed in STYLE.md, especially anything implying automatic duplicate or blur detection
5. **Links and calls to action.** Do the internal links point to the most relevant pages? Is the in-text App Store link a natural sentence in the Keeper section, and does it name app facts that actually help with this topic? Is the app mentioned more than STYLE.md allows?
6. **Readability.** Could a general adult reader follow it on the first read? Look for unexplained jargon and paragraphs that pack in too much.

### Verdict

**Critical** issues block publishing:

- any fact or menu path that isn't confirmed by a trusted page you opened
- anything that could lead a reader to lose photos they meant to keep
- an article that doesn't answer the target query
- any area scoring 1 or 2

It's a **PASS** only if there are no critical issues and every area scores 4 or 5.

Reply in exactly this format and nothing else:

```
VERDICT: PASS | FAIL
SCORES: intent N, usefulness N, voice N, facts N, links N, readability N
CRITICAL:
- "<exact quote from the article>" | <what's wrong> | <fix>
OTHER:
- "<exact quote>" | <what's wrong> | <fix>
```

Write `CRITICAL: none` if there are none. Keep each fix concrete: give the rewritten sentence, or say "delete it".
