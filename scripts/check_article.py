#!/usr/bin/env python3
"""Check articles in guides/ before they're published.

Usage:
  python3 scripts/check_article.py public/guides/some-slug.html [...]
  python3 scripts/check_article.py            # checks every routine article in public/guides/

The four hand-written guides (ROOT_GUIDES) use a different layout and aren't checked.

Exits non-zero and lists every problem if any check fails. Standard library only.
"""

import html
import json
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
SITE = "https://keeperphoto.app"
# Sources a fact may come from: the maker's own documentation for how a device,
# app or service works.
TRUSTED = (
    "support.apple.com", "developer.apple.com", "apple.com/legal", "apple.com/icloud",
    "apple.com/privacy", "support.google.com", "support.microsoft.com", "learn.microsoft.com",
    "amazon.com/gp/help", "help.dropbox.com", "support.samsung.com", "samsung.com/us/support",
)
ROOT_GUIDES = {
    "how-to-delete-photos-on-iphone", "free-up-iphone-storage-photos",
    "recently-deleted-photos-iphone", "delete-photos-from-iphone-not-icloud",
}
MIN_WORDS = 600
# A general adult audience: aim for about a grade 8 or 9 reading level.
MAX_GRADE = 9.0
MAX_SENTENCE_WORDS = 32
APP_URL = "https://apps.apple.com/app/id6793817811"

# The site is written in US English. Flag British and Australian spellings and slang.
NON_US_TERMS = [
    r"colour", r"centres?", r"metres?", r"behaviours?", r"favourite",
    r"programme", r"practis(e|es|ed|ing)", r"organis(e|es|ed|ing|ation)",
    r"recognis(e|es|ed|ing)", r"prioritis(e|es|ed|ing)", r"optimis(e|es|ed|ing|ation)",
    r"minimis(e|es|ed|ing)", r"realis(e|es|ed|ing)", r"analys(e|es|ed|ing)",
    r"apologis", r"fibre", r"grey", r"mum", r"jumper", r"fortnight",
    r"whilst", r"amongst", r"labelled", r"travelled", r"modelled",
    r"enrol", r"defence", r"paediatric", r"haemo", r"oestrogen",
]
AI_PHRASES = [
    "delve", "dive into", "deep dive", "navigat", "journey", "landscape", "realm", "tapestry",
    "seamless", "robust", "crucial", "vital", "comprehensive", "game-changer", "game changer",
    "it's important to note", "it’s important to note", "it's worth noting", "it’s worth noting",
    "whether you're a", "whether you’re a", "look no further", "ever wondered", "rest assured",
    "in conclusion", "furthermore", "moreover", "plethora", "myriad", "embark", "buckle up",
    "hit the road", "ultimate guide", "a testament", "unlock your", "unlock the", "elevate", "empower", "leverage",
    "utilis", "utiliz", "foster", "in today's", "in today’s", "fast-paced", "picture this",
    "let's explore", "let’s explore", "in this article", "in this guide we", "game plan",
    "level up", "supercharge", "say goodbye", "worry not", "declutter your life",
    "digital clutter", "precious memories", "treasured memories", "hassle-free", "effortlessly",
    # From .claude/skills/nonai-writing (Wikipedia's "Signs of AI writing").
    "serves as", "stands as", "boasts", "testament", "pivotal", "underscore", "showcasing",
    "valuable insights", "resonates with", "evolving landscape", "setting the stage",
    "it's not just", "it’s not just", "not only", "in summary", "overall,", "ultimately,",
    "experts argue", "experts say", "multifaceted", "meticulous", "intricate", "interplay",
    "garner", "bolster", "i hope this helps", "great question", "certainly",
]


class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.hrefs, self.jsonld = set(), [], []
        self.h1 = 0
        self.title = ""
        self.meta = {}
        self.canonical = ""
        self.summaries, self.faq_answers = [], []
        self._stack = []
        self._buf = None
        self._in_main = False
        self.main_text = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "href" in a:
            self.hrefs.append(a["href"])
        if tag == "h1":
            self.h1 += 1
        if tag == "meta" and a.get("name"):
            self.meta[a["name"]] = a.get("content", "")
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href", "")
        if tag == "main":
            self._in_main = True
        if tag in ("script", "style", "svg"):
            self._skip += 1
        if tag in ("title", "summary") or (tag == "script" and a.get("type") == "application/ld+json"):
            self._buf = []
            self._stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "main":
            self._in_main = False
        if tag in ("script", "style", "svg"):
            self._skip = max(0, self._skip - 1)
        if self._stack and self._stack[-1] == tag:
            text = "".join(self._buf).strip()
            self._stack.pop()
            self._buf = None
            if tag == "title":
                self.title = text
            elif tag == "summary":
                self.summaries.append(text)
            elif tag == "script":
                self.jsonld.append(text)

    def handle_data(self, data):
        if self._buf is not None:
            self._buf.append(data)
        if self._in_main and not self._skip:
            self.main_text.append(data)


class ProseText(HTMLParser):
    """Visible article text, with a sentence break after every block element.

    Headings, list items and table cells don't end in full stops, so without
    the breaks they'd run together into one very long "sentence".
    """

    BLOCKS = {"p", "li", "h2", "h3", "h4", "summary", "td", "th", "dt", "dd", "div", "section"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "svg"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "svg"):
            self._skip = max(0, self._skip - 1)
        if tag in self.BLOCKS:
            self.out.append(" . ")

    def handle_data(self, data):
        if not self._skip:
            self.out.append(data)


def syllables(word):
    word = word.lower().strip("’'")
    if len(word) <= 3:
        return 1
    word = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", word)
    word = re.sub(r"^y", "", word)
    return max(1, len(re.findall(r"[aeiouy]{1,2}", word)))


def readability(article_html):
    """Flesch-Kincaid grade and the over-long sentences of the article prose.

    The sources box is left out: it's mostly page titles and URLs.
    """
    prose = re.split(r'<(?:aside|div)[^>]*class="[^"]*sources', article_html)[0]
    parser = ProseText()
    parser.feed(prose)
    text = html.unescape("".join(parser.out))
    sentences = [s.strip() for s in re.split(r"[.?:;]+(?:\s|$)", text) if re.search(r"[A-Za-z]", s)]
    words = re.findall(r"[A-Za-z][A-Za-z’'-]*", text)
    if not sentences or not words:
        return 0.0, []
    grade = 0.39 * len(words) / len(sentences) + 11.8 * sum(map(syllables, words)) / len(words) - 15.59
    long = [re.sub(r"\s+", " ", s) for s in sentences if len(s.split()) > MAX_SENTENCE_WORDS]
    return grade, long


def check(path):
    problems = []
    src = path.read_text()
    slug = path.stem
    p = Parser()
    p.feed(src)
    text = html.unescape(" ".join(p.main_text))
    text = re.sub(r"\s+", " ", text)
    visible = " ".join([text, p.title, p.meta.get("description", "")])
    lower = visible.lower()

    if "{{" in src or "TEMPLATE" in src:
        problems.append("template placeholders or TEMPLATE comments left in the file")
    if "—" in src:
        problems.append("contains an em dash (—)")
    if re.search(r"\s–\s", visible):
        problems.append("contains a spaced en dash ( – )")
    if "·" in visible:
        problems.append("contains a middle dot (·): use a comma or a new sentence")
    if "!" in text:
        problems.append("contains an exclamation mark")
    if re.search("[\U0001F300-\U0001FAFF☀-➿]", visible):
        problems.append("contains an emoji")

    for pat in NON_US_TERMS:
        for m in re.finditer(pat, visible, flags=re.IGNORECASE):
            problems.append(f"non-US spelling or term: '{m.group(0)}'")
    for phrase in AI_PHRASES:
        if phrase in lower:
            problems.append(f"stock AI phrase: '{phrase}'")

    words = len(re.findall(r"[A-Za-z’']+", text))
    if words < MIN_WORDS:
        problems.append(f"only {words} words in the page body (minimum {MIN_WORDS})")

    want = f"{SITE}/guides/{slug}"
    if p.canonical != want:
        problems.append(f"canonical is '{p.canonical}', expected '{want}'")
    if 'name="apple-itunes-app" content="app-id=6793817811"' not in src:
        problems.append("missing the Smart App Banner meta (apple-itunes-app)")
    if p.h1 != 1:
        problems.append(f"expected exactly one h1, found {p.h1}")
    desc = p.meta.get("description", "")
    if not 110 <= len(desc) <= 160:
        problems.append(f"meta description is {len(desc)} characters (want 110 to 160)")
    seo_title = p.title.replace(" | Keeper", "")
    if not p.title.endswith(" | Keeper"):
        problems.append("title must end with ' | Keeper'")
    if len(seo_title) > 62:
        problems.append(f"title before ' | Keeper' is {len(seo_title)} characters (max 62)")
    if slug in ROOT_GUIDES:
        problems.append("this slug belongs to a hand-written guide")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug) or re.search(r"20\d\d", slug):
        problems.append("slug must be lowercase words joined by hyphens, with no year")

    trusted = sorted({h for h in p.hrefs if any(d in h for d in TRUSTED)})
    if len(trusted) < 2:
        problems.append("needs links to at least two trusted sources (see TRUSTED)")
    if 'class="callout short-answer"' not in src:
        problems.append("missing the short answer box")
    if 'class="sources"' not in src:
        problems.append("missing the Sources box")

    for href in p.hrefs:
        if href.startswith("#") and len(href) > 1 and href[1:] not in p.ids:
            problems.append(f"broken in-page link {href}")
        if href.startswith("/") and not href.startswith("//"):
            target = href.split("#")[0].rstrip("/")
            if target and not (PUBLIC / (target.lstrip("/") + ".html")).exists() \
                    and not (PUBLIC / target.lstrip("/") / "index.html").exists() \
                    and not (PUBLIC / target.lstrip("/")).is_file():
                problems.append(f"broken internal link {href}")
        if href.startswith("http://"):
            problems.append(f"insecure link {href}")

    article_html = src.split('<div class="wrap prose">', 1)[-1].split("</article>", 1)[0]
    grade, long_sentences = readability(article_html)
    if grade > MAX_GRADE:
        problems.append(f"reading grade {grade:.1f} (max {MAX_GRADE}): use shorter sentences and plainer words")
    for sentence in long_sentences:
        problems.append(f"sentence over {MAX_SENTENCE_WORDS} words, split it: '{sentence[:120]}...'")

    prose_only = article_html.split('<div class="sources">', 1)[0]
    if APP_URL not in prose_only:
        problems.append("no in-text App Store link in the article (tracking section)")
    if prose_only.count(APP_URL) > 2:
        problems.append("more than 2 App Store links in the article text: mention the app less")
    closing = src.split('class="closing"', 1)[-1].split("</section>", 1)[0]
    if 'class="closing"' not in src or APP_URL not in closing:
        problems.append("closing section with the App Store badge is missing")
    if "Keeper" not in text:
        problems.append("the article body never mentions Keeper")
    n_h2 = len(re.findall(r"<h2[ >]", prose_only))
    if not 5 <= n_h2 <= 9:
        problems.append(f"{n_h2} h2 headings in the article (want 4 to 7 sections plus the FAQ heading)")

    faq_names = []
    for block in p.jsonld:
        try:
            data = json.loads(block)
        except json.JSONDecodeError as e:
            problems.append(f"JSON-LD doesn't parse: {e}")
            continue
        nodes = data.get("@graph", [data]) if isinstance(data, dict) else []
        for node in nodes:
            if node.get("@type") == "FAQPage":
                faq_names = [q["name"] for q in node.get("mainEntity", [])]
            if node.get("@type") == "Article":
                if node.get("headline") != seo_title:
                    problems.append("JSON-LD Article headline doesn't match the title")
                if node.get("description") != html.unescape(desc):
                    problems.append("JSON-LD Article description doesn't match the meta description")
    visible_faq = [s.strip() for s in p.summaries]
    if not 3 <= len(visible_faq) <= 5:
        problems.append(f"{len(visible_faq)} FAQ items (want 3 to 5)")
    for name in faq_names:
        if name not in visible_faq:
            problems.append(f"FAQ JSON-LD question not in visible FAQ: '{name}'")
    for name in visible_faq:
        if name not in faq_names:
            problems.append(f"visible FAQ question missing from the FAQPage JSON-LD: '{name}'")

    hub = (PUBLIC / "guides" / "index.html").read_text()
    if f'href="/guides/{slug}"' not in hub:
        problems.append("not linked from guides/index.html")
    if f"<loc>{want}</loc>" not in (PUBLIC / "sitemap.xml").read_text():
        problems.append("not listed in sitemap.xml")
    if want not in (PUBLIC / "llms.txt").read_text():
        problems.append("not listed in llms.txt")

    return problems


def main():
    paths = [pathlib.Path(a) for a in sys.argv[1:]] or sorted(
        f for f in (PUBLIC / "guides").glob("*.html")
        if f.name != "index.html" and f.stem not in ROOT_GUIDES
    )
    if not paths:
        print("No routine articles yet.")
        return
    failed = False
    for path in paths:
        problems = check(path.resolve())
        if problems:
            failed = True
            print(f"FAIL {path}")
            for prob in problems:
                print(f"  - {prob}")
        else:
            print(f"ok   {path}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
