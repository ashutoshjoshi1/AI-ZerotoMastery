"""Build the course website from content/.

    python tools/build.py               write the site into the repository root
    python tools/build.py --check       build into a temporary folder; fail if the committed site differs
    python tools/build.py --out DIR     write the site somewhere else (for previews)

Needs Python 3.10+ with Pygments, and Node.js with KaTeX installed in tools/ (`cd tools && npm install`).
See docs/AUTHORING.md for the source format.
"""
import argparse
import colorsys
import hashlib
import html
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
LANG_LABEL = {
    "python": "Python", "bash": "Terminal", "console": "Terminal", "shell": "Terminal", "text": "Text",
    "json": "JSON", "toml": "TOML", "yaml": "YAML", "html": "HTML", "javascript": "JavaScript", "sql": "SQL",
    "dockerfile": "Dockerfile", "ini": "Config", "diff": "Diff", "pycon": "Python session", "http": "HTTP",
    "powershell": "PowerShell", "markdown": "Markdown", "xml": "XML", "jsonld": "JSON",
}
RUNNABLE = {"python", "bash", "console", "shell", "pycon", "powershell", "sql", "javascript"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr",
        "path", "rect", "circle", "line", "polyline", "polygon", "ellipse", "stop", "use"}
WARNINGS = []


def warn(msg):
    WARNINGS.append(msg)


def esc(s):
    return html.escape(str(s), quote=True)


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def slugify(value):
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value)


def matching_end(s, start, tag):
    """Index just past the element that opens at s[start], balancing nested `tag` elements."""
    depth, i = 0, start
    opener, closer = re.compile(rf"<{tag}\b"), f"</{tag}>"
    while True:
        o = opener.search(s, i)
        c = s.find(closer, i)
        if c == -1:
            raise ValueError(f"unclosed <{tag}> near: {s[start:start + 80]!r}")
        if o and o.start() < c:
            depth += 1
            i = o.end()
        else:
            depth -= 1
            i = c + len(closer)
            if depth == 0:
                return i


def replace_blocks(s, opener, tag, fn):
    """Replace every balanced element whose opening tag starts with `opener`."""
    out, i = [], 0
    while True:
        a = s.find(opener, i)
        if a == -1:
            out.append(s[i:])
            return "".join(out)
        end = matching_end(s, a, tag)
        out.append(s[i:a] + fn(s[a:end]))
        i = end


# ----------------------------------------------------------------------------- colours

def oklch_to_rgb(L, C, h):
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l_ = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    lin = (4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
           -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
           -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_)
    return lin


def in_gamut(lin):
    return all(-1e-4 <= x <= 1.0001 for x in lin)


def to_hex(lin):
    def gamma(x):
        x = min(1.0, max(0.0, x))
        return 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055
    return "#" + "".join(f"{round(gamma(x) * 255):02x}" for x in lin)


def oklch_hex(L, C, h):
    while C > 0 and not in_gamut(oklch_to_rgb(L, C, h)):
        C -= 0.002
    return to_hex(oklch_to_rgb(L, max(C, 0), h))


def luminance(hexcol):
    def ch(c):
        c = int(c, 16) / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(hexcol[i:i + 2]) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def lesson_colours(t):
    """A colour per lesson along the spectrum, violet (t=0) to deep red (t=1)."""
    hue = 305 - 283 * t
    accent = oklch_hex(0.62, 0.21, hue)
    L = 0.50
    text_light = oklch_hex(L, 0.19, hue)
    while contrast(text_light, "#ffffff") < 4.8 and L > 0.2:
        L -= 0.01
        text_light = oklch_hex(L, 0.19, hue)
    L = 0.80
    text_dark = oklch_hex(L, 0.15, hue)
    while contrast(text_dark, "#121a22") < 6.5 and L < 0.97:
        L += 0.01
        text_dark = oklch_hex(L, 0.15, hue)
    return accent, text_light, text_dark


# ----------------------------------------------------------------------------- loading

class Lesson:
    def __init__(self, slug, meta, body, path):
        self.slug, self.meta, self.body, self.path = slug, meta, body, path
        self.title = meta["title"]
        self.short = meta.get("short") or self.title
        self.sessions = meta["sessions"]

    @property
    def href(self):
        return f"lessons/{self.num}-{self.slug}.html"

    @property
    def notebook(self):
        return f"notebooks/{self.num}-{self.slug}.ipynb"

    @property
    def solutions(self):
        return f"notebooks/solutions/{self.num}-{self.slug}-solutions.ipynb"

    @property
    def style(self):
        return f"--lc:{self.lc};--lct:{self.lct};--lctd:{self.lctd}"


def read_lesson(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"\s*<!--(.*?)-->", text, re.S)
    if not m:
        raise SystemExit(f"{path}: missing the metadata comment at the top (see docs/AUTHORING.md)")
    try:
        meta = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        raise SystemExit(f"{path}: metadata is not valid JSON: {e}")
    for key in ("title", "summary", "sessions"):
        if key not in meta:
            raise SystemExit(f"{path}: metadata needs '{key}'")
    return Lesson(path.stem, meta, text[m.end():].strip("\n"), path)


def load_course(skip_missing=False):
    course = json.loads((CONTENT / "course.json").read_text(encoding="utf-8"))
    lessons, parts = [], []
    for pi, part in enumerate(course["parts"]):
        p = {"index": pi, "roman": ROMAN[pi], "name": part["name"], "desc": part["desc"], "lessons": []}
        for slug in part["lessons"]:
            path = CONTENT / "lessons" / f"{slug}.html"
            if not path.exists():
                if skip_missing:
                    warn(f"skipping missing lesson {slug}")
                    continue
                raise SystemExit(f"{path} does not exist (listed in content/course.json)")
            lesson = read_lesson(path)
            lesson.part = p
            p["lessons"].append(lesson)
            lessons.append(lesson)
        if p["lessons"]:
            parts.append(p)
    for i, p in enumerate(parts):
        p["index"], p["roman"] = i, ROMAN[i]
    n = len(lessons)
    for i, lesson in enumerate(lessons):
        lesson.index = i
        lesson.num = f"{i:02d}"
        t = i / max(1, n - 1)
        lesson.lc, lesson.lct, lesson.lctd = lesson_colours(t)
        lesson.nm = round(400 + 300 * t)
        lesson.prev = lessons[i - 1] if i else None
        lesson.next = lessons[i + 1] if i + 1 < n else None
    for p in parts:
        mid = p["lessons"][len(p["lessons"]) // 2]
        p["colour"] = mid.lc
        p["sessions"] = sum(len(l.sessions) for l in p["lessons"])
    by_slug = {l.slug: l for l in lessons}
    return course, parts, lessons, by_slug


# ----------------------------------------------------------------------------- maths

INLINE_MATH = re.compile(r"\\\((.+?)\\\)", re.S)
DISPLAY_MATH = re.compile(r"\\\[(.+?)\\\]", re.S)
CODE_BLOCK = re.compile(r'<pre([^>]*)><code class="language-([\w+-]+)">(.*?)</code></pre>', re.S)
INLINE_CODE = re.compile(r"<code\b[^>]*>.*?</code>", re.S)


class Maths:
    def __init__(self):
        self.wanted, self.done = {}, {}

    def collect(self, text):
        text = INLINE_CODE.sub("", CODE_BLOCK.sub("", text))
        for m in DISPLAY_MATH.finditer(text):
            self.wanted[(html.unescape(m.group(1)).strip(), True)] = None
        for m in INLINE_MATH.finditer(text):
            self.wanted[(html.unescape(m.group(1)).strip(), False)] = None

    def render_all(self):
        items = [k for k in self.wanted if k not in self.done]
        if not items:
            return
        script = Path(__file__).with_name("katex_render.mjs")
        if not (Path(__file__).parent / "node_modules" / "katex").exists():
            raise SystemExit("KaTeX is not installed. Run `npm install` in the tools/ folder once.")
        try:
            proc = subprocess.run(["node", str(script)], input=json.dumps([{"tex": t, "display": d} for t, d in items]),
                                  capture_output=True, text=True, encoding="utf-8", check=True)
        except FileNotFoundError:
            raise SystemExit("Node.js is needed to render maths. Install it from nodejs.org.")
        except subprocess.CalledProcessError as e:
            raise SystemExit("KaTeX failed: " + e.stderr)
        for key, res in zip(items, json.loads(proc.stdout)):
            if "error" in res:
                warn(f"maths error in {key[0]!r}: {res['error']}")
                self.done[key] = f'<code class="tex-error">{esc(key[0])}</code>'
            else:
                self.done[key] = res["html"]

    def html(self, tex, display):
        return self.done[(html.unescape(tex).strip(), display)]


# ----------------------------------------------------------------------------- lesson body

class Rendered:
    pass


def render_code_block(attrs, lang, code, is_output):
    raw = html.unescape(code)
    try:
        lexer = get_lexer_by_name(lang)
    except Exception:
        warn(f"unknown code language {lang!r}")
        lexer = get_lexer_by_name("text")
    spans = highlight(raw, lexer, HtmlFormatter(nowrap=True)).rstrip("\n")
    fm = re.search(r'data-file="([^"]*)"', attrs)
    label = fm.group(1) if fm else ("Output" if is_output else LANG_LABEL.get(lang, lang.title()))
    kind = " is-output" if is_output else ""
    return (f'<div class="highlight{kind}" data-lang="{esc(lang)}"><div class="code-head">'
            f'<span class="code-label">{esc(label)}</span></div><pre><code>{spans}</code></pre></div>')


def expand_quiz(block):
    qs = re.findall(r'<div class="q">(.*?)</div>', block, re.S)
    out = []
    for n, q in enumerate(qs, 1):
        prompt = re.search(r"<p>(.*?)</p>", q, re.S).group(1)
        options = re.findall(r"<li( class=\"correct\")?>(.*?)</li>", q, re.S)
        why = re.search(r'<p class="why">(.*?)</p>', q, re.S)
        if sum(1 for c, _ in options if c) != 1:
            warn(f"quiz question {n} needs exactly one correct option: {strip_tags(prompt)[:60]}")
        opts = "".join(f'<li><button type="button" class="quiz-opt" data-correct="{1 if c else 0}">{t}</button></li>'
                       for c, t in options)
        out.append(f'<div class="quiz-q" data-q>\n<p class="quiz-prompt"><span class="quiz-num">{n}.</span> {prompt}</p>\n'
                   f'<ol class="quiz-options" type="A">{opts}</ol>\n'
                   f'<p class="quiz-expl" hidden>{why.group(1) if why else ""}</p>\n</div>')
    return '<div class="quiz" data-quiz>\n' + "\n".join(out) + '\n<p class="quiz-score" aria-live="polite"></p></div>'


class TabCounter:
    n = 0


def expand_tabs(block):
    TabCounter.n += 1
    k = TabCounter.n
    secs = re.findall(r'<section data-tab="([^"]*)">(.*?)</section>', block, re.S)
    if len(secs) > 4:
        warn("tab sets support at most four tabs")
    inputs = "".join(f'<input{" checked" if i == 0 else ""} id="tab-{k}-{i}" name="tab-{k}" type="radio">' for i in range(len(secs)))
    labels = "".join(f'<label for="tab-{k}-{i}">{name}</label>' for i, (name, _) in enumerate(secs))
    blocks = "".join(f'<div class="tabbed-block">\n{body.strip()}\n</div>' for _, body in secs)
    return f'<div class="tabbed-set">{inputs}<div class="tabbed-labels">{labels}</div><div class="tabbed-content">{blocks}</div></div>'


def render_lesson_body(lesson, ctx, maths, search_mode=False):
    """Return (html, toc, sections) for a lesson body. In search mode, maths and code become plain text."""
    src = lesson.body
    root = "../"
    codes = []

    def protect_code(m):
        codes.append(m.groups())
        return f"\x00C{len(codes) - 1}\x00"
    src = CODE_BLOCK.sub(protect_code, src)
    inline = []

    def protect_inline(m):
        inline.append(m.group(0))
        return f"\x00I{len(inline) - 1}\x00"
    src = INLINE_CODE.sub(protect_inline, src)

    if search_mode:
        src = DISPLAY_MATH.sub(lambda m: " " + html.unescape(m.group(1)) + " ", src)
        src = INLINE_MATH.sub(lambda m: html.unescape(m.group(1)), src)
    else:
        src = DISPLAY_MATH.sub(lambda m: '<div class="math-block">' + maths.html(m.group(1), True) + "</div>", src)
        src = INLINE_MATH.sub(lambda m: maths.html(m.group(1), False), src)

    src = replace_blocks(src, '<div class="quiz">', "div", expand_quiz)
    src = replace_blocks(src, '<div class="tabs">', "div", expand_tabs)

    src = resolve_refs(src, ctx, root, lesson.slug)

    # session dividers
    sessions = lesson.sessions
    markers = [int(x) for x in re.findall(r'<hr data-session="(\d+)">', src)]
    if markers and markers != list(range(2, len(sessions) + 1)):
        warn(f"{lesson.slug}: session markers {markers} do not match {len(sessions)} sessions")

    def divider(m):
        k = int(m.group(1))
        if not 2 <= k <= len(sessions):
            return ""
        return (f'<div class="session-break" id="session-{k}">'
                f'<label class="sb-done"><input type="checkbox" data-session="{lesson.slug}:{k - 2}">'
                f'<span>Done with session {k - 1}: {esc(sessions[k - 2])}</span></label>'
                f'<p class="sb-next"><span class="sb-kicker">Session {k} of {len(sessions)}</span>{esc(sessions[k - 1])}</p></div>')
    src = re.sub(r'<hr data-session="(\d+)">', divider, src)
    if markers:
        src = (f'<p class="session-start" id="session-1"><span class="sb-kicker">Session 1 of {len(sessions)}</span>'
               f'{esc(sessions[0])}</p>\n' + src)

    # exercises: say where to do them
    def exercise(m):
        title = m.group(1)
        clean = strip_tags(title)
        return (f'<div class="admonition exercise">\n<p class="admonition-title">{title}</p>\n'
                f'<p class="exercise-where"><span class="chip">At your computer</span> '
                f'<code>{lesson.notebook.split("/", 1)[1]}</code>, cell “{esc(clean)}”</p>')
    src = re.sub(r'<div class="admonition exercise">\s*<p class="admonition-title">(.*?)</p>', exercise, src, flags=re.S)

    # headings
    toc, seen = [], set()

    def heading(m):
        tag, attrs, inner = m.group(1), m.group(2) or "", m.group(3)
        idm = re.search(r'id="([^"]+)"', attrs)
        text = strip_tags(inner).strip()
        hid = idm.group(1) if idm else slugify(text)
        base, k = hid, 2
        while hid in seen:
            hid, k = f"{base}-{k}", k + 1
        seen.add(hid)
        if tag in ("h2", "h3"):
            toc.append((tag, hid, text))
        return f'<{tag} id="{hid}">{inner}<a class="headerlink" href="#{hid}" aria-label="Link to this section">#</a></{tag}>'
    src = re.sub(r"<(h[2-4])(\s[^>]*)?>(.*?)</\1>", heading, src, flags=re.S)

    # tables scroll sideways on narrow screens
    src = re.sub(r"<table>(.*?)</table>", r'<div class="table-wrap"><table>\1</table></div>', src, flags=re.S)
    src = src.replace("<figure>", '<figure class="fig">')

    src = re.sub(r"\x00I(\d+)\x00", lambda m: inline[int(m.group(1))], src)

    def restore(m):
        idx = int(m.group(1))
        attrs, lang, code = codes[idx]
        if search_mode:
            return "\n" + html.unescape(code) + "\n"
        # A text block straight after runnable code is that code's output.
        before = src[:m.start()]
        follows_code = idx > 0 and before.rstrip().endswith(f"\x00C{idx - 1}\x00")
        is_output = lang == "text" and follows_code and codes[idx - 1][1] in RUNNABLE
        return render_code_block(attrs, lang, code, is_output)
    src = re.sub(r"\x00C(\d+)\x00", restore, src)
    return src, toc


def check_balance(name, s):
    stack = []
    for m in re.finditer(r"<(/?)([a-zA-Z][\w-]*)\b[^>]*?(/?)>", re.sub(r"<!--.*?-->", "", s, flags=re.S)):
        closing, tag, selfclose = m.group(1), m.group(2).lower(), m.group(3)
        if tag in VOID or selfclose:
            continue
        if not closing:
            stack.append(tag)
        elif stack and stack[-1] == tag:
            stack.pop()
        elif tag in stack:
            warn(f"{name}: </{tag}> closes over <{stack[-1]}>")
            while stack and stack.pop() != tag:
                pass
        elif tag != "p":
            warn(f"{name}: stray </{tag}>")
    if stack:
        warn(f"{name}: unclosed {stack[-5:]}")


# ----------------------------------------------------------------------------- page chrome

ICONS = {
    "menu": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/></svg>',
    "search": '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M15.5 15.5 21 21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    "close": '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    "prev": '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M15 5l-7 7 7 7" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "next": '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M9 5l7 7-7 7" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "laptop": '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><rect x="4" y="5" width="16" height="11" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M2 19h20" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
}

BOOT = ('<script>try{var d=document.documentElement,s=JSON.parse(localStorage.getItem("aie-prefs")||"{}");'
        'if(s.theme&&s.theme!=="auto")d.setAttribute("data-theme",s.theme);if(s.size)d.setAttribute("data-size",s.size);'
        'if(s.font)d.setAttribute("data-font",s.font);}catch(e){}</script>')


def page(ctx, *, title, root, body_class, page_id, main, description, toc_html="", needs_math=False, current=None, extra=""):
    v = ctx["v"]
    course = ctx["course"]
    full_title = f"{title} | {course['title']}" if title != course["title"] else f"{course['title']}: {course['tagline']}"
    css_math = f'<link rel="stylesheet" href="{root}assets/katex/katex.min.css">\n' if needs_math else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="theme-color" content="#f4f6f8" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#121a22" media="(prefers-color-scheme: dark)">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website">
<link rel="icon" href="{root}assets/icons/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{root}assets/icons/apple-touch-icon.png">
<link rel="manifest" href="{root}manifest.webmanifest">
<link rel="stylesheet" href="{root}assets/fonts/fonts.css">
{css_math}<link rel="stylesheet" href="{root}assets/style.css?v={v}">
{BOOT}
</head>
<body class="{body_class}" data-root="{root}" data-page="{esc(page_id)}">
<a class="skip" href="#main">Skip to content</a>
{topbar(ctx, root)}
{strip(ctx, root, current)}
<div class="layout">
{course_map(ctx, root, current, page_id)}
<div class="scrim" hidden></div>
<main id="main" tabindex="-1">
{main}
</main>
{toc_html}
</div>
{extra}{settings_dialog()}
<script src="{root}assets/course-data.js?v={v}"></script>
<script src="{root}assets/app.js?v={v}"></script>
</body>
</html>
"""


def topbar(ctx, root):
    c = ctx["course"]
    return f"""<header class="topbar">
<button class="icon-btn nav-toggle" type="button" aria-label="Show course map" aria-controls="course-map" aria-expanded="false">{ICONS['menu']}</button>
<a class="brand" href="{root}index.html">{esc(c['title'])}<span>{esc(c['tagline'])}</span></a>
<div class="search" role="search">
<input id="search-input" type="search" placeholder="Search the course" autocomplete="off" aria-label="Search the course" enterkeyhint="search">
<button class="icon-btn search-close" type="button" aria-label="Close search">{ICONS['close']}</button>
<div class="search-results" hidden></div>
</div>
<button class="icon-btn search-toggle" type="button" aria-label="Search the course">{ICONS['search']}</button>
<button class="icon-btn settings-toggle" type="button" aria-label="Reading settings and progress sync" aria-haspopup="dialog"><span class="aa" aria-hidden="true">Aa</span></button>
</header>"""


def strip(ctx, root, current):
    segs = []
    for l in ctx["lessons"]:
        cur = " is-current" if current is l else ""
        segs.append(f'<a class="seg{cur}" href="{root}{l.href}" data-lesson="{l.slug}" data-sessions="{len(l.sessions)}" '
                    f'style="--lc:{l.lc}" title="{l.num} {esc(l.title)}" tabindex="-1"></a>')
    return f'<div class="spectrum-strip" aria-hidden="true">{"".join(segs)}<span class="read-progress"></span></div>'


def course_map(ctx, root, current, page_id):
    def page_link(href, label, pid):
        cur = ' aria-current="page"' if pid == page_id else ""
        return f'<li><a href="{root}{href}"{cur}>{label}</a></li>'
    pages = "".join([page_link("index.html", "Course home", "home"), page_link("schedule.html", "Daily schedule", "schedule"),
                     page_link("glossary.html", "Glossary", "glossary"), page_link("resources.html", "Further resources", "resources")])
    parts = []
    for p in ctx["parts"]:
        items = []
        for l in p["lessons"]:
            cur = ' aria-current="page"' if current is l else ""
            items.append(f'<li><a href="{root}{l.href}" data-lesson="{l.slug}" data-sessions="{len(l.sessions)}" style="--lc:{l.lc}"{cur}>'
                         f'<span class="dot" aria-hidden="true"></span><span class="num">{l.num}</span><span class="t">{esc(l.short)}</span></a></li>')
        parts.append(f'<section class="map-part" style="--pc:{p["colour"]}">\n<p class="map-part-name"><span class="roman">{p["roman"]}</span> {esc(p["name"])}</p><ol>\n'
                     + "\n".join(items) + "\n</ol></section>")
    return f'<nav class="course-map" id="course-map" aria-label="Course map">\n<ul class="map-pages">{pages}</ul>\n' + "\n".join(parts) + "\n</nav>"


def toc_block(toc, cls="toc", title="On this page"):
    if not toc:
        return ""
    out, open_sub = [], False
    for tag, hid, text in toc:
        if tag == "h2":
            if open_sub:
                out.append("</ul></li>")
                open_sub = False
            elif out:
                out.append("</li>")
            out.append(f'<li><a href="#{hid}">{esc(text)}</a>')
        else:
            if not open_sub:
                out.append("<ul>")
                open_sub = True
            out.append(f'<li><a href="#{hid}">{esc(text)}</a></li>')
    out.append("</ul></li>" if open_sub else "</li>")
    return f'<aside class="{cls}" aria-label="{title}"><p class="toc-title">{title}</p><ul>{"".join(out)}</ul></aside>'


def settings_dialog():
    return """<dialog class="settings" aria-labelledby="settings-title">
<form method="dialog" class="settings-inner">
<div class="settings-head"><h2 id="settings-title">Reading settings</h2><button class="icon-btn" value="close" aria-label="Close">""" + ICONS["close"] + """</button></div>
<fieldset><legend>Theme</legend><div class="seg-ctl" data-pref="theme"><button type="button" value="auto">Auto</button><button type="button" value="light">Light</button><button type="button" value="dark">Dark</button></div></fieldset>
<fieldset><legend>Text size</legend><div class="seg-ctl" data-pref="size"><button type="button" value="s" aria-label="Small">A</button><button type="button" value="m" aria-label="Medium">A</button><button type="button" value="l" aria-label="Large">A</button><button type="button" value="xl" aria-label="Extra large">A</button></div></fieldset>
<fieldset><legend>Typeface</legend><div class="seg-ctl" data-pref="font"><button type="button" value="serif">Literata</button><button type="button" value="sans">Atkinson Hyperlegible</button></div></fieldset>
<fieldset class="sync"><legend>Progress on your other devices</legend>
<p>Your ticks live in this browser. To carry them to your phone or computer, open this link there:</p>
<div class="sync-row"><input class="sync-link" type="text" readonly aria-label="Sync link"><button type="button" class="btn-small sync-copy">Copy</button><button type="button" class="btn-small sync-share" hidden>Share</button></div>
<p class="sync-note">Opening the link adds these ticks to the ones already there; nothing is removed.</p>
</fieldset>
<fieldset class="offline" hidden><legend>Offline reading</legend>
<p class="offline-status">Lessons you open are saved for reading without a connection.</p>
<button type="button" class="btn-small offline-all">Save every lesson for offline reading</button>
</fieldset>
</form>
</dialog>"""


# ----------------------------------------------------------------------------- pages

def lesson_page(lesson, ctx, maths):
    body, toc = render_lesson_body(lesson, ctx, maths)
    check_balance(lesson.path.name, body)
    root = "../"
    meta = lesson.meta
    search_text, _ = render_lesson_body(lesson, ctx, maths, search_mode=True)
    words = len(strip_tags(re.sub(r"<pre>.*?</pre>", "", search_text, flags=re.S)).split())
    code_lines = sum(html.unescape(c[2]).count("\n") + 1 for c in CODE_BLOCK.findall(lesson.body))
    minutes = max(5, round((words / 230 + code_lines / 14) / 5) * 5)
    n_code = len(CODE_BLOCK.findall(lesson.body))
    n_ex = lesson.body.count('class="admonition exercise"')
    lesson.read_minutes, lesson.words = minutes, words
    lesson.search_text = search_text

    sessions = "".join(f'<li><label><input type="checkbox" data-session="{lesson.slug}:{i}"><span>{esc(s)}</span></label></li>'
                       for i, s in enumerate(lesson.sessions))
    objectives = ""
    if meta.get("objectives"):
        objectives = ('<section class="objectives"><h2 class="mini">By the end you will be able to</h2><ul>'
                      + "".join(f"<li>{o}</li>" for o in meta["objectives"]) + "</ul></section>")
    prereq = ""
    pre = [ctx["by_slug"][s] for s in meta.get("prerequisites", []) if s in ctx["by_slug"]]
    for s in meta.get("prerequisites", []):
        if s not in ctx["by_slug"]:
            warn(f"{lesson.slug}: unknown prerequisite {s!r}")
    if pre:
        prereq = ('<p class="prereq"><strong>Before you start:</strong> '
                  + ", ".join(f'<a href="{root}{p.href}">{p.num} {esc(p.short)}</a>' for p in pre) + "</p>")
    repo, branch = ctx["course"]["repo"], ctx["course"]["branch"]
    colab = f"https://colab.research.google.com/github/{repo}/blob/{branch}/{lesson.notebook}"
    github = f"https://github.com/{repo}/blob/{branch}/{lesson.notebook}"
    nb_name = lesson.notebook.split("/", 1)[1]
    handson = f"""<aside class="handson" aria-label="Hands-on notebook">
<p class="handson-title">{ICONS['laptop']} Hands-on at your computer</p>
<p>Read here on any screen. When a <span class="chip">At your computer</span> exercise comes up, open <code>notebooks/{nb_name}</code> in JupyterLab or VS Code and run the cells under the same heading.</p>
<p class="handson-runs"><strong>Runs on:</strong> {esc(meta.get('runs_on', 'Any computer (CPU).'))}</p>
<p class="handson-links"><a href="{colab}" rel="noopener">Open in Colab</a><a href="{github}" rel="noopener">View on GitHub</a><a href="{root}{lesson.notebook}" download>Download notebook</a><a href="{root}{lesson.solutions}" download>Solutions</a></p>
</aside>"""
    stats = (f'<p class="lesson-meta"><span>{len(lesson.sessions)} sessions</span><span>about {minutes} min of reading</span>'
             f'<span>{n_code} code examples</span><span>{n_ex} hands-on exercise{"s" if n_ex != 1 else ""}</span></p>')
    last = len(lesson.sessions)
    has_markers = '<hr data-session="' in lesson.body
    final_tick = ""
    if has_markers:
        final_tick = (f'<label class="sb-done final"><input type="checkbox" data-session="{lesson.slug}:{last - 1}">'
                      f'<span>Done with session {last}: {esc(lesson.sessions[-1])}</span></label>')
    pager = []
    if lesson.prev:
        pager.append(f'<a class="prev" href="{root}{lesson.prev.href}"><span>Previous</span>{lesson.prev.num} {esc(lesson.prev.title)}</a>')
    if lesson.next:
        pager.append(f'<a class="next" href="{root}{lesson.next.href}"><span>Next</span>{lesson.next.num} {esc(lesson.next.title)}</a>')
    toc_aside = toc_block(toc)
    sheet_toc = toc_block(toc, cls="toc-sheet-list", title="Contents")
    part = lesson.part
    main = f"""<article class="lesson" data-lesson="{lesson.slug}" style="{lesson.style}">
<header class="lesson-head">
<p class="lesson-part"><span class="swatch" aria-hidden="true"></span>Part {part['roman']}, {esc(part['name'])} <span class="wl">{lesson.nm} nm</span></p>
<h1><span class="lesson-num">{lesson.num}</span> {esc(lesson.title)}</h1>
<p class="lesson-summary">{meta['summary']}</p>
{stats}
{objectives}
{prereq}
<div class="study-plan">
<p class="plan-title">Study plan: {len(lesson.sessions)} sessions of about an hour</p>
<ol class="sessions">{sessions}</ol>
<p class="plan-note">Tick a session when you finish it. Ticks are saved in this browser; use <button type="button" class="linklike open-settings">sync</button> to carry them to another device.</p>
</div>
{handson}
<p class="resume" hidden><button type="button" class="btn-small resume-btn">Jump back to where you stopped</button></p>
</header>
<div class="prose">
{body}
</div>
<footer class="lesson-foot">
{final_tick}
<button type="button" class="complete-btn" data-complete="{lesson.slug}" data-sessions="{last}">Mark all sessions done</button>
<nav class="pager" aria-label="Lesson navigation">{''.join(pager)}</nav>
</footer>
</article>"""
    prev_link = f'<a class="lb-btn" href="{root}{lesson.prev.href}" aria-label="Previous lesson: {esc(lesson.prev.title)}">{ICONS["prev"]}</a>' if lesson.prev else '<span class="lb-btn" aria-hidden="true"></span>'
    next_link = f'<a class="lb-btn" href="{root}{lesson.next.href}" aria-label="Next lesson: {esc(lesson.next.title)}">{ICONS["next"]}</a>' if lesson.next else '<span class="lb-btn" aria-hidden="true"></span>'
    extra = f"""<nav class="lesson-bar" aria-label="Lesson">
{prev_link}
<button type="button" class="lb-toc" aria-expanded="false" aria-controls="toc-sheet"><span class="lb-where">{lesson.num} · <span class="lb-section">{esc(lesson.short)}</span></span><span class="lb-pct" aria-hidden="true"><span></span></span></button>
{next_link}
</nav>
<div class="toc-sheet" id="toc-sheet" hidden><div class="toc-sheet-inner">{sheet_toc}</div></div>
"""
    return page(ctx, title=lesson.title, root=root, body_class="is-lesson", page_id=lesson.slug, main=main,
                description=strip_tags(meta["summary"]), toc_html=toc_aside, needs_math="katex" in body,
                current=lesson, extra=extra)


def spectrum_svg(ctx, root):
    lessons = ctx["lessons"]
    n = len(lessons)
    x0, x1 = 40, 960
    parts = ['<svg class="spectrum" viewBox="0 0 1000 230" role="img" aria-labelledby="spec-title spec-desc">'
             '<title id="spec-title">The course as a spectrum</title>'
             '<desc id="spec-desc">Each vertical line is a lesson, from violet for the first to deep red for the last. '
             'Taller lines have more sessions. Lines brighten as you complete sessions.</desc>'
             f'<line class="axis" x1="30" y1="190" x2="970" y2="190"/>']
    for nm in range(400, 701, 50):
        x = x0 + (x1 - x0) * (nm - 400) / 300
        parts.append(f'<line class="tick" x1="{x:.1f}" y1="190" x2="{x:.1f}" y2="196"/><text class="tick-label" x="{x:.1f}" y="212" text-anchor="middle">{nm}</text>')
    parts.append('<text class="tick-label unit" x="970" y="230" text-anchor="end">nm</text>')
    for l in lessons:
        x = x0 + (x1 - x0) * l.index / max(1, n - 1)
        h = 70 + 16 * len(l.sessions)
        y = 190 - h
        parts.append(f'<a href="{root}{l.href}" class="line" data-lesson="{l.slug}" data-sessions="{len(l.sessions)}"><title>{l.num} {esc(l.title)}</title>'
                     f'<rect class="glow" x="{x - 7:.1f}" y="{y}" width="14" height="{h}" fill="{l.lc}"/>'
                     f'<rect class="core" x="{x - 2.5:.1f}" y="{y}" width="5" height="{h}" fill="{l.lc}"/>'
                     f'<text class="line-num" x="{x:.1f}" y="{y - 8}" text-anchor="middle">{l.num}</text></a>')
    parts.append("</svg>")
    return "".join(parts)


def fill(text, ctx):
    return re.sub(r"\{\{(\w+)\}\}", lambda m: str(ctx["vars"][m.group(1)]), text)


def home_page(ctx):
    root = ""
    v = ctx["vars"]
    intro = fill((CONTENT / "pages" / "home.html").read_text(encoding="utf-8"), ctx)
    intro, toc = render_page_body(intro, ctx, "home")
    blocks = []
    for p in ctx["parts"]:
        items = []
        for l in p["lessons"]:
            items.append(f'<li style="{l.style}"><a href="{l.href}" data-lesson="{l.slug}" data-sessions="{len(l.sessions)}">'
                         f'<span class="num">{l.num}</span> {esc(l.title)}</a><span class="meta">{len(l.sessions)} sessions · {l.read_minutes} min read</span>'
                         f'<p>{l.meta["summary"]}</p></li>')
        blocks.append(f'<section class="part-block" style="--pc:{p["colour"]}"><h3><span class="roman">{p["roman"]}</span> {esc(p["name"])}</h3>'
                      f'<p class="part-desc">{esc(p["desc"])} <span class="meta">{p["sessions"]} sessions</span></p><ol class="part-lessons">{"".join(items)}</ol></section>')
    main = f"""<div class="home">
<section class="hero">
<h1>AI engineering, from zero to mastery</h1>
<p class="hero-lede">{v['lessons']} lessons in {v['sessions']} sessions of about an hour each. Python and maths first, then machine learning, deep learning and transformers, then the craft of building, evaluating and shipping systems on large language models, and finally the wider field of AI. Read on any screen; practise in a Jupyter notebook on your computer.</p>
<figure class="hero-figure">
{spectrum_svg(ctx, root)}
<figcaption>Each line is a lesson, laid out along the visible spectrum from your first session (violet) to mastery (deep red). Lines brighten as you tick off sessions.</figcaption>
</figure>
<div class="hero-actions">
<a class="btn-primary" id="continue-link" href="{ctx['lessons'][0].href}">Start lesson 00</a>
<p class="progress-text" id="progress-text">0 of {v['sessions']} sessions done</p>
</div>
<p class="resume-home" hidden><a class="resume-home-link" href="#"></a></p>
</section>
<section class="prose home-intro">
{intro}
</section>
<section class="parts">
<h2 id="the-route">The route</h2>
{''.join(blocks)}
</section>
</div>"""
    return page(ctx, title=ctx["course"]["title"], root=root, body_class="is-home is-loading", page_id="home", main=main,
                description=ctx["course"]["description"])


def resolve_refs(src, ctx, root, where):
    def ref(m):
        target = ctx["by_slug"].get(m.group(1))
        if not target:
            warn(f"{where}: data-ref to unknown lesson {m.group(1)!r}")
            return m.group(1)
        return f'<a class="ref" href="{root}{target.href}" title="Lesson {target.num}: {esc(target.title)}">{target.num}</a>'
    return re.sub(r'<a data-ref="([^"]+)"></a>', ref, src)


def render_page_body(src, ctx=None, where="page"):
    if ctx is not None:
        src = resolve_refs(src, ctx, "", where)
    toc, seen = [], set()

    def heading(m):
        tag, attrs, inner = m.group(1), m.group(2) or "", m.group(3)
        idm = re.search(r'id="([^"]+)"', attrs)
        hid = idm.group(1) if idm else slugify(strip_tags(inner))
        while hid in seen:
            hid += "-x"
        seen.add(hid)
        toc.append((tag, hid, strip_tags(inner)))
        return f'<{tag} id="{hid}">{inner}<a class="headerlink" href="#{hid}" aria-label="Link to this section">#</a></{tag}>'
    src = re.sub(r"<(h[23])(\s[^>]*)?>(.*?)</\1>", heading, src, flags=re.S)
    src = re.sub(r"<table>(.*?)</table>", r'<div class="table-wrap"><table>\1</table></div>', src, flags=re.S)
    return src, toc


def plain_page(ctx, *, page_id, title, intro, body, description, toc=True):
    rendered, t = render_page_body(body, ctx, page_id)
    main = f'<div class="prose plain-page">\n<h1>{esc(title)}</h1>\n{intro}\n{rendered}\n</div>'
    return page(ctx, title=title, root="", body_class="is-page", page_id=page_id, main=main,
                description=description, toc_html=toc_block(t) if toc else "")


def schedule_page(ctx):
    v = ctx["vars"]
    per = ctx["course"].get("sessions_per_week", 5)
    rows, day = [], 0
    for l in ctx["lessons"]:
        for i, s in enumerate(l.sessions):
            if day % per == 0:
                if rows:
                    rows.append("</ol></section>")
                w = day // per + 1
                rows.append(f'<section class="week" aria-labelledby="week-{w}"><h2 id="week-{w}">Week {w}</h2><ol class="days">')
            day += 1
            rows.append(f'<li class="day-row" style="{l.style}"><label><input type="checkbox" data-session="{l.slug}:{i}" aria-label="Day {day} done">'
                        f'<span class="day-num">Day {day}</span><span class="day-body"><a href="{l.href}">{l.num} {esc(l.short)}</a>'
                        f'<span class="day-title">Session {i + 1} of {len(l.sessions)}: {esc(s)}</span></span></label></li>')
    rows.append("</ol></section>")
    roman = {p["name"]: p["roman"] for p in ctx["parts"]}
    wider = roman.get("The wider field")
    intro = (f"<p>The whole course as {v['sessions']} one-hour sessions. At five sessions a week that is about {v['weeks5']} weeks; "
             f"at seven a week, about {v['weeks7']} weeks. These checkboxes are the same ones you see in each lesson, so ticking either place records the same progress.</p>"
             "<p>Some sessions will run long, especially the hands-on ones from the deep learning lessons onwards. Let them. "
             "Splitting a session over two days is better than skipping the exercise.</p>")
    if wider:
        intro += (f"<p>The lessons in part {wider}, the wider field, stand on their own. Take them in order, pick the ones your work needs, "
                  "or interleave them with the parts before.</p>")
    main = f'<div class="prose schedule-page">\n<h1>Daily schedule</h1>\n{intro}\n{"".join(rows)}\n</div>'
    return page(ctx, title="Daily schedule", root="", body_class="is-page", page_id="schedule", main=main,
                description="The whole course laid out as one-hour daily sessions.")


def glossary_page(ctx):
    entries = []
    for l in ctx["lessons"]:
        for g in l.meta.get("glossary", []):
            others = [ctx["by_slug"][s] for s in g.get("also", []) if s in ctx["by_slug"]]
            entries.append((g["term"], g["def"], [l] + others))
    entries.sort(key=lambda e: e[0].lower().lstrip("("))
    seen = {}
    for term, _, ls in entries:
        key = term.lower()
        if key in seen:
            warn(f"glossary term {term!r} defined in both {seen[key]} and {ls[0].slug}")
        seen[key] = ls[0].slug
    groups = {}
    for term, d, ls in entries:
        letter = term[0].upper() if term[0].isalpha() else "#"
        groups.setdefault(letter, []).append((term, d, ls))
    jump = "".join(f'<a href="#{k.lower() if k != "#" else "num"}">{k}</a>' for k in groups)
    body = []
    for k, items in groups.items():
        gid = k.lower() if k != "#" else "num"
        dl = "".join(f'<div class="g-entry" id="term-{slugify(t)}"><dt>{esc(t)}</dt><dd>{esc(d)} '
                     + " ".join(f'<a class="g-lesson" href="{l.href}" title="{esc(l.title)}">{l.num}</a>' for l in sorted(ls, key=lambda x: x.index))
                     + "</dd></div>"
                     for t, d, ls in items)
        body.append(f'<section class="g-letter"><h2 id="{gid}">{k}</h2><dl>{dl}</dl></section>')
    ctx["glossary_entries"] = entries
    intro = (f'<p>{len(entries)} terms you will meet in the course, in plain language. The number after each definition is the lesson that teaches it.</p>'
             f'<div class="g-tools"><input type="search" class="g-filter" placeholder="Filter terms" aria-label="Filter glossary terms"><nav class="g-jump" aria-label="Jump to letter">{jump}</nav></div>')
    main = f'<div class="prose glossary-page">\n<h1>Glossary</h1>\n{intro}\n{"".join(body)}\n<p class="g-empty" hidden>No terms match.</p>\n</div>'
    return page(ctx, title="Glossary", root="", body_class="is-page", page_id="glossary", main=main,
                description="Terms used in the AI Engineering course, in plain language.")


def simple_page(ctx, page_id, title, html_body, description):
    main = f'<div class="prose plain-page">\n<h1>{esc(title)}</h1>\n{html_body}\n</div>'
    return page(ctx, title=title, root=ctx.get("abs_root", ""), body_class="is-page", page_id=page_id, main=main, description=description)


# ----------------------------------------------------------------------------- data files

def course_data(ctx):
    data = {
        "version": ctx["content_hash"],
        "repo": ctx["course"]["repo"],
        "site_url": ctx["course"]["site_url"],
        "lessons": [{"slug": l.slug, "id": l.num, "title": l.title, "short": l.short, "href": l.href,
                     "sessions": len(l.sessions), "color": l.lc} for l in ctx["lessons"]],
    }
    return "window.COURSE=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"


def search_index(ctx):
    docs = []
    for l in ctx["lessons"]:
        text = l.search_text
        pieces = re.split(r'(<h[23] id="[^"]+">.*?</h[23]>)', text, flags=re.S)
        docs.append({"h": l.href, "p": f"{l.num} {l.title}", "s": "", "t": " ".join(strip_tags(pieces[0]).split())[:600] or l.meta["summary"]})
        for i in range(1, len(pieces), 2):
            m = re.match(r'<h[23] id="([^"]+)">(.*?)<a class="headerlink"', pieces[i], re.S)
            body = " ".join(strip_tags(pieces[i + 1] if i + 1 < len(pieces) else "").split())
            docs.append({"h": f"{l.href}#{m.group(1)}", "p": f"{l.num} {l.title}", "s": strip_tags(m.group(2)).strip(), "t": body[:2400]})
    for term, d, _ in ctx["glossary_entries"]:
        docs.append({"h": f"glossary.html#term-{slugify(term)}", "p": "Glossary", "s": term, "t": d})
    return "window.COURSE_SEARCH=" + json.dumps(docs, ensure_ascii=False, separators=(",", ":")) + ";\n"


def manifest(ctx):
    c = ctx["course"]
    return json.dumps({
        "name": f"{c['title']}: {c['tagline']}",
        "short_name": c["title"],
        "description": c["description"],
        "start_url": "./index.html",
        "scope": "./",
        "display": "standalone",
        "background_color": "#f4f6f8",
        "theme_color": "#18222d",
        "icons": [
            {"src": "assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "assets/icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
            {"src": "assets/icons/icon.svg", "sizes": "any", "type": "image/svg+xml"},
        ],
    }, indent=2) + "\n"


def service_worker(ctx, shell, pages):
    return f"""// Generated by tools/build.py. Caches the site so lessons can be read offline once opened.
const VERSION = "{ctx['site_hash']}";
const SHELL = "shell-" + VERSION;
const PAGES = "pages";
const ASSETS = "assets";
const SHELL_URLS = {json.dumps(shell)};
const ALL_PAGES = {json.dumps(pages)};

self.addEventListener("install", (e) => {{
  e.waitUntil(caches.open(SHELL).then((c) => c.addAll(SHELL_URLS)).then(() => self.skipWaiting()));
}});

self.addEventListener("activate", (e) => {{
  e.waitUntil(caches.keys().then((keys) => Promise.all(
    keys.filter((k) => k.startsWith("shell-") && k !== SHELL).map((k) => caches.delete(k))
  )).then(() => self.clients.claim()));
}});

function isPage(req) {{
  return req.mode === "navigate" || (req.headers.get("accept") || "").includes("text/html");
}}

self.addEventListener("fetch", (e) => {{
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  if (isPage(req)) {{
    // Network first, so you always get the newest lesson when online; the cache when not.
    e.respondWith(fetch(req).then((res) => {{
      if (res.ok) {{ const copy = res.clone(); caches.open(PAGES).then((c) => c.put(req, copy)); }}
      return res;
    }}).catch(() => caches.match(req, {{ ignoreSearch: true }}).then((hit) => hit || caches.match("offline.html"))));
    return;
  }}
  // Assets are versioned by query string, so the cache can answer first.
  e.respondWith(caches.match(req).then((hit) => hit || fetch(req).then((res) => {{
    if (res.ok) {{ const copy = res.clone(); caches.open(ASSETS).then((c) => c.put(req, copy)); }}
    return res;
  }})));
}});

self.addEventListener("message", (e) => {{
  if (!e.data || e.data.type !== "cache-all") return;
  const urls = ALL_PAGES.concat(e.data.extra || []);
  let done = 0;
  const report = () => e.source && e.source.postMessage({{ type: "cache-progress", done: done, total: urls.length }});
  e.waitUntil(caches.open(PAGES).then((pages) => Promise.all(urls.map((u) =>
    fetch(u).then((res) => {{ if (res.ok) return (u.endsWith(".html") ? pages : caches.open(ASSETS).then((a) => a)).then((c) => c.put(u, res)); }})
      .catch(() => {{}}).then(() => {{ done++; report(); }})
  ))));
}});
"""


def offline_page(ctx):
    body = ('<p>You are offline, and this page has not been saved on this device yet.</p>'
            '<p>Pages you have opened before still work. To keep the whole course with you, open <strong>Reading settings</strong> '
            '(the <span class="aa">Aa</span> button) while online and choose <em>Save every lesson for offline reading</em>.</p>'
            '<p><a href="index.html">Go to the course home</a></p>')
    return simple_page(ctx, "offline", "Not available offline yet", body, "Offline fallback page.")


def not_found_page(ctx):
    base = ctx["course"]["site_url"].rstrip("/") + "/"
    ctx["abs_root"] = base
    body = ('<p>That page does not exist. The lessons may have been renumbered; search above, or start from the '
            f'<a href="{base}index.html">course home</a>.</p>')
    out = simple_page(ctx, "404", "Page not found", body, "Page not found.")
    ctx.pop("abs_root")
    return out


# ----------------------------------------------------------------------------- notebooks

NB_HEADER_MARK = "<!-- course-header -->"


def notebook_header(lesson, ctx, solutions):
    c = ctx["course"]
    site = c["site_url"].rstrip("/") + "/"
    rel = "../../" if solutions else "../"
    nb = lesson.solutions if solutions else lesson.notebook
    colab = f"https://colab.research.google.com/github/{c['repo']}/blob/{c['branch']}/{nb}"
    if solutions:
        first = (f"*Worked solutions for lesson {lesson.num}. Read the lesson [online]({site}{lesson.href}) or "
                 f"[offline]({rel}{lesson.href}). The exercise version without solutions is `../{lesson.notebook.split('/', 1)[1]}`.*")
    else:
        first = (f"*Companion notebook for lesson {lesson.num}. Read the lesson [online]({site}{lesson.href}) "
                 f"(it works well on a phone) or [offline]({rel}{lesson.href}). Worked solutions are in "
                 f"`solutions/{lesson.solutions.split('/')[-1]}`; try each exercise first.*")
    text = (f"{NB_HEADER_MARK}\n# Lesson {lesson.num}: {lesson.title}\n\n{first}\n\n"
            f'<a href="{colab}"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>\n\n'
            f"{strip_tags(lesson.meta['summary'])}\n\n"
            f"**Runs on:** {lesson.meta.get('runs_on', 'Any computer (CPU).')}\n\n"
            "**How to use it:** read a section of the lesson, then run the matching cells here, in order. Each exercise has a "
            "cell titled *Hands-on* with the same name as in the lesson. Change numbers, break things on purpose, and note what "
            "happens in your learning log. Cells that need an API key, a GPU or a download say so in their first line.")
    return text


def sync_notebooks(ctx, out_root, written):
    for lesson in ctx["lessons"]:
        for solutions in (False, True):
            rel = lesson.solutions if solutions else lesson.notebook
            path = ROOT / rel
            if not path.exists():
                others = list((ROOT / rel).parent.glob(f"*-{lesson.slug}{'-solutions' if solutions else ''}.ipynb"))
                warn(f"missing notebook {rel}" + (f" (found {others[0].name}; rename it)" if others else ""))
                continue
            nb = json.loads(path.read_text(encoding="utf-8"))
            header = notebook_header(lesson, ctx, solutions)
            lines = header.split("\n")
            cell = {"cell_type": "markdown", "metadata": {}, "source": [l + "\n" for l in lines[:-1]] + [lines[-1]]}
            if nb["cells"] and nb["cells"][0]["cell_type"] == "markdown":
                cell["metadata"] = nb["cells"][0].get("metadata", {})
                if "id" in nb["cells"][0]:
                    cell["id"] = nb["cells"][0]["id"]
                nb["cells"][0] = cell
            else:
                nb["cells"].insert(0, cell)
            text = json.dumps(nb, indent=1, ensure_ascii=False) + "\n"
            write(out_root / rel, text, written)


def update_marked(rel, marker, content, out_root, written):
    """Replace the text between <!-- marker:start --> and <!-- marker:end --> in a Markdown file."""
    path = ROOT / rel
    if not path.exists():
        warn(f"{rel} does not exist")
        return
    text = path.read_text(encoding="utf-8")
    start, end = f"<!-- {marker}:start -->", f"<!-- {marker}:end -->"
    if start not in text:
        warn(f"{rel} has no {marker} markers; not updated")
        return
    block = start + "\n" + content.strip("\n") + "\n" + end
    text = re.sub(re.escape(start) + r".*?" + re.escape(end), lambda m: block, text, flags=re.S)
    write(out_root / rel, text, written)


def markdown_tables(ctx, out_root, written):
    rows = ["| Notebook | Lesson | Runs on |", "|---|---|---|"]
    for l in ctx["lessons"]:
        name = l.notebook.split("/", 1)[1]
        rows.append(f"| [{name}]({name}) | {l.title} | {l.meta.get('runs_on', 'Any computer (CPU).')} |")
    update_marked("notebooks/README.md", "notebook-table", "\n".join(rows), out_root, written)

    site = ctx["course"]["site_url"].rstrip("/") + "/"
    lines = []
    for p in ctx["parts"]:
        lines.append(f"\n**Part {p['roman']}: {p['name']}.** {p['desc']}\n")
        lines.append("| # | Lesson | Sessions | Notebook |")
        lines.append("|---|---|---|---|")
        for l in p["lessons"]:
            nb = l.notebook.split("/", 1)[1]
            lines.append(f"| {l.num} | [{l.title}]({site}{l.href}) | {len(l.sessions)} | [{nb}]({l.notebook}) |")
    v = ctx["vars"]
    intro = (f"{v['lessons']} lessons in {v['sessions']} sessions of about an hour each: about {v['weeks5']} weeks at "
             f"five sessions a week.\n")
    update_marked("README.md", "lessons", intro + "\n".join(lines), out_root, written)


# ----------------------------------------------------------------------------- links

def check_links(out_root, files):
    pages = {p: (out_root / p).read_text(encoding="utf-8") for p in files if p.endswith(".html")}
    ids = {p: set(re.findall(r'\sid="([^"]+)"', t)) for p, t in pages.items()}
    for p, t in pages.items():
        base = Path(p).parent
        for href in re.findall(r'\shref="([^"]+)"', t):
            if re.match(r"^(https?:|mailto:|data:|#$)", href) or href.startswith("javascript"):
                continue
            path, _, frag = href.partition("#")
            path = path.split("?", 1)[0]
            target = (base / path).as_posix() if path else p
            target = re.sub(r"(^|/)\./", r"\1", target)
            while "/../" in "/" + target:
                target = re.sub(r"(^|/)[^/]+/\.\./", r"\1", target, count=1)
            if path and not (out_root / target).exists():
                warn(f"{p}: broken link {href}")
            elif frag and target in ids and frag not in ids[target]:
                warn(f"{p}: missing anchor {href}")


# ----------------------------------------------------------------------------- main

def write(path, text, written):
    path.parent.mkdir(parents=True, exist_ok=True)
    rel = path.relative_to(written["root"]).as_posix()
    written["files"].append(rel)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return
    path.write_text(text, encoding="utf-8", newline="\n")
    written["changed"].append(rel)


def build(out_root, skip_missing=False):
    course, parts, lessons, by_slug = load_course(skip_missing)
    total = sum(len(l.sessions) for l in lessons)
    ctx = {"course": course, "parts": parts, "lessons": lessons, "by_slug": by_slug,
           "vars": {"lessons": len(lessons), "sessions": total, "weeks5": math.ceil(total / 5), "weeks7": math.ceil(total / 7),
                    "site_url": course["site_url"], "parts": len(parts), "repo": course["repo"]}}
    maths = Maths()
    sources = [l.body for l in lessons]
    for s in sources:
        maths.collect(s)
    maths.render_all()

    content_hash = hashlib.sha1()
    for p in sorted(CONTENT.rglob("*")):
        if p.is_file():
            content_hash.update(p.read_bytes())
    ctx["content_hash"] = content_hash.hexdigest()[:10]

    written = {"root": out_root, "files": [], "changed": []}
    if out_root != ROOT:
        for d in ("assets",):
            shutil.copytree(ROOT / d, out_root / d, dirs_exist_ok=True)

    # Render lesson pages first (this also computes reading times and search text).
    lesson_html = {}
    ctx["v"] = "0"
    for l in lessons:
        TabCounter.n = 0
        lesson_page(l, ctx, maths)  # dry run for metadata; re-rendered below with the asset version
    glossary_html = glossary_page(ctx)
    data_js = course_data(ctx)
    write(out_root / "assets" / "course-data.js", data_js, written)
    write(out_root / "assets" / "search-index.js", search_index(ctx), written)
    h = hashlib.sha1()
    for p in ("assets/style.css", "assets/app.js"):
        h.update((ROOT / p).read_bytes())
    h.update(data_js.encode())
    ctx["v"] = h.hexdigest()[:8]

    for l in lessons:
        TabCounter.n = 0
        lesson_html[l.href] = lesson_page(l, ctx, maths)
        write(out_root / l.href, lesson_html[l.href], written)
    write(out_root / "index.html", home_page(ctx), written)
    write(out_root / "schedule.html", schedule_page(ctx), written)
    write(out_root / "glossary.html", glossary_page(ctx), written)
    resources = fill((CONTENT / "pages" / "resources.html").read_text(encoding="utf-8"), ctx)
    write(out_root / "resources.html", plain_page(ctx, page_id="resources", title="Further resources", intro="", body=resources,
                                                  description="Books, courses, papers and tools for going deeper."), written)
    write(out_root / "offline.html", offline_page(ctx), written)
    write(out_root / "404.html", not_found_page(ctx), written)
    write(out_root / "manifest.webmanifest", manifest(ctx), written)

    page_files = [f for f in written["files"] if f.endswith(".html") and f not in ("404.html",)]
    site_hash = hashlib.sha1("".join((out_root / f).read_text(encoding="utf-8") for f in sorted(page_files)).encode()).hexdigest()[:10]
    ctx["site_hash"] = site_hash
    v = ctx["v"]
    fonts = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "assets" / "fonts").glob("*.woff2"))
    shell = (["./", "index.html", "offline.html", "assets/fonts/fonts.css", f"assets/style.css?v={v}", f"assets/app.js?v={v}",
              f"assets/course-data.js?v={v}", "assets/icons/icon.svg", "manifest.webmanifest"] + fonts)
    katex_assets = ["assets/katex/katex.min.css"] + sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "assets" / "katex" / "fonts").glob("*.woff2"))
    all_pages = sorted(page_files) + katex_assets + ["assets/search-index.js?v=" + v]
    write(out_root / "sw.js", service_worker(ctx, shell, all_pages), written)
    write(out_root / ".nojekyll", "", written)

    sync_notebooks(ctx, out_root, written)
    markdown_tables(ctx, out_root, written)
    check_links(out_root, written["files"])
    return ctx, written


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, help="write the site here instead of the repository root")
    ap.add_argument("--check", action="store_true", help="fail if the committed site is out of date")
    ap.add_argument("--skip-missing", action="store_true", help="leave out lessons whose source file does not exist yet")
    args = ap.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            shutil.copytree(ROOT / "notebooks", tmp / "notebooks")
            _, written = build(tmp, args.skip_missing)
            stale = [f for f in written["files"] if not (ROOT / f).exists() or
                     (ROOT / f).read_text(encoding="utf-8") != (tmp / f).read_text(encoding="utf-8")]
        for w in WARNINGS:
            print("warning:", w)
        if stale:
            print("The built site is out of date. Run `python tools/build.py` and commit the result. Stale files:")
            for f in stale:
                print("  " + f)
            sys.exit(1)
        print(f"Site is up to date ({len(written['files'])} files).")
        sys.exit(1 if WARNINGS else 0)
    out = (args.out or ROOT).resolve()
    ctx, written = build(out, args.skip_missing)
    for w in WARNINGS:
        print("warning:", w)
    print(f"Built {len(ctx['lessons'])} lessons, {ctx['vars']['sessions']} sessions; "
          f"{len(written['changed'])} of {len(written['files'])} files changed.")


if __name__ == "__main__":
    main()
