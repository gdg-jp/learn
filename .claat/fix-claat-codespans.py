#!/usr/bin/env python3
"""Post-process claat-exported index.html files.

Eight fixes are applied:

1. Escape unescaped HTML tags inside inline <code>...</code> spans. claat's
   markdown renderer leaves backtick spans like `<html>` as
   `<code><html></code>`, which the browser parses as real <html>/<body>/<head>
   tags and breaks the document. We rewrite them to `<code>&lt;html&gt;</code>`.

2. Wrap blockquote-style note paragraphs in <aside class="..."> boxes. Older
   claat versions converted `> **Note:** ...` markdown into
   `<aside class="note">...</aside>`; the current version emits a plain <p>,
   so the styled callout box is lost. We re-wrap any
   `<p><strong>Keyword:</strong>...</p>` whose keyword matches a known callout
   label, including an immediately following <ul>/<ol> list when present.

3. Wrap <pre> code blocks with a toolbar that provides copy and light/dark
   theme buttons.

4. Repair markdown links left behind when claat strips standalone <button>
   wrappers. Button syntax such as `<button>\n[label](url)\n</button>` can
   otherwise become plain text instead of a `<paper-button>`.

5. Inject local CSS and JS that make code blocks light by default, style the
   toolbar buttons, preserve the dark-mode toggle, and add a full outline to
   callouts.

6. Add the repository favicon from assets/favicon.png.

7. Convert bare http(s) URLs in prose into links.

8. Inject Open Graph meta tags from the source claat markdown. og:title uses
   the first H1, og:description uses the summary frontmatter, and og:image uses
   the first markdown image, preferring claat's exported image path when it can
   be matched by alt text.
"""

import argparse
import html as html_lib
import json
import os
import re
import sys
from pathlib import Path

ASIDE_KEYWORDS = {
    "Note": "warning",
    "Notice": "warning",
    "Tip": "special",
    "Tips": "special",
    "Hint": "special",
    "補足": "special",
    "Warning": "warning",
    "Warn": "warning",
    "Caution": "warning",
    "Troubleshooting": "troubleshooting",
}

SKIP_LINKIFY_TAGS = {"a", "code", "pre", "script", "style"}
TRAILING_URL_PUNCTUATION = ".,;:!?)\\]}、。！？）】」』"

STYLE_ID = "claat-local-preprocessor-style"
SCRIPT_ID = "claat-local-preprocessor-script"
FAVICON_ID = "claat-local-favicon"
OGP_META_ID_PREFIX = "claat-local-ogp-"

CODE_TOOLBAR = """<div class="claat-code-toolbar" aria-label="Code block actions">
  <button class="claat-code-button claat-toggle-code-theme" type="button" aria-label="Use dark code theme" title="Use dark code theme">
    <span class="material-icons" aria-hidden="true">dark_mode</span>
  </button>
  <button class="claat-code-button claat-copy-code" type="button" aria-label="Copy code" title="Copy code">
    <span class="material-icons" aria-hidden="true">content_copy</span>
  </button>
</div>"""

LOCAL_STYLE = f"""<style id="{STYLE_ID}">
  google-codelab-step .instructions .claat-code-block {{
    position: relative;
    margin: 16px 0;
    background: #f1f3f4;
    border-radius: 0;
    overflow: hidden;
  }}

  google-codelab-step .instructions .claat-code-block pre {{
    margin: 0;
    padding: 18px 88px 18px 18px;
    color: #37474f;
    background: #f1f3f4;
    border-radius: 0;
  }}

  google-codelab-step .instructions .claat-code-block pre > code {{
    color: inherit;
    background: transparent;
    padding: 0;
  }}

  google-codelab-step .instructions .claat-code-toolbar {{
    position: absolute;
    top: 16px;
    right: 16px;
    z-index: 1;
    display: flex;
    gap: 14px;
    align-items: center;
  }}

  google-codelab-step .instructions .claat-code-button {{
    width: 24px;
    height: 24px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    margin: 0;
    border: 0;
    border-radius: 50%;
    color: #202124;
    background: transparent;
    cursor: pointer;
  }}

  google-codelab-step .instructions .claat-code-button:hover,
  google-codelab-step .instructions .claat-code-button:focus-visible {{
    background: rgba(60, 64, 67, 0.12);
    outline: none;
  }}

  google-codelab-step .instructions .claat-code-button .material-icons {{
    margin: 0;
    font-size: 24px;
    line-height: 1;
  }}

  google-codelab-step .instructions .claat-code-block pre .pln,
  google-codelab-step .instructions .claat-code-block pre .pun {{
    color: #37474f;
  }}

  google-codelab-step .instructions .claat-code-block pre .kwd,
  google-codelab-step .instructions .claat-code-block pre .typ,
  google-codelab-step .instructions .claat-code-block pre .tag {{
    color: #9334e6;
  }}

  google-codelab-step .instructions .claat-code-block pre .str,
  google-codelab-step .instructions .claat-code-block pre .atv {{
    color: #188038;
  }}

  google-codelab-step .instructions .claat-code-block pre .com {{
    color: #5f6368;
  }}

  google-codelab-step .instructions .claat-code-block pre .atn,
  google-codelab-step .instructions .claat-code-block pre .lit,
  google-codelab-step .instructions .claat-code-block pre .dec {{
    color: #1967d2;
  }}

  google-codelab-step .instructions .claat-code-block[data-code-theme="dark"] {{
    background: #28323f;
  }}

  google-codelab-step .instructions .claat-code-block[data-code-theme="dark"] pre {{
    color: #f8f9fa;
    background: #28323f;
  }}

  google-codelab-step .instructions .claat-code-block[data-code-theme="dark"] .claat-code-button {{
    color: #f8f9fa;
  }}

  google-codelab-step .instructions .claat-code-block[data-code-theme="dark"] .claat-code-button:hover,
  google-codelab-step .instructions .claat-code-block[data-code-theme="dark"] .claat-code-button:focus-visible {{
    background: rgba(248, 249, 250, 0.16);
  }}

  google-codelab-step .instructions .claat-code-block[data-code-theme="dark"] pre .str,
  google-codelab-step .instructions .claat-code-block[data-code-theme="dark"] pre .atv {{
    color: #34a853;
  }}

  google-codelab-step .instructions .claat-code-block[data-code-theme="dark"] pre .kwd {{
    color: #f538a0;
  }}

  google-codelab-step .instructions .claat-code-block[data-code-theme="dark"] pre .com {{
    color: #bdc1c6;
  }}

  google-codelab-step .instructions .claat-code-block[data-code-theme="dark"] pre .typ,
  google-codelab-step .instructions .claat-code-block[data-code-theme="dark"] pre .tag {{
    color: #24c1e0;
  }}

  google-codelab-step .instructions .claat-code-block[data-code-theme="dark"] pre .lit,
  google-codelab-step .instructions .claat-code-block[data-code-theme="dark"] pre .dec {{
    color: #4285f4;
  }}

  google-codelab-step .instructions .claat-code-block[data-code-theme="dark"] pre .pln,
  google-codelab-step .instructions .claat-code-block[data-code-theme="dark"] pre .pun {{
    color: #f8f9fa;
  }}

  google-codelab:not([theme="minimal"]) google-codelab-step .instructions aside.warning {{
    border: 1px solid #ea8600;
    border-left-width: 4px;
  }}

  google-codelab:not([theme="minimal"]) google-codelab-step .instructions aside.troubleshooting {{
    border: 1px solid #d93025;
    border-left-width: 4px;
    border-color: #d93025;
    background: #fce8e6;
    color: #212124;
  }}

  google-codelab:not([theme="minimal"]) google-codelab-step .instructions aside.special,
  google-codelab:not([theme="minimal"]) google-codelab-step .instructions aside.tip {{
    border: 1px solid #137333;
    border-left-width: 4px;
  }}

  @media (max-width: 640px) {{
    google-codelab-step .instructions .claat-code-block pre {{
      padding: 56px 14px 16px;
    }}
  }}
</style>"""

LOCAL_SCRIPT = f"""<script id="{SCRIPT_ID}">
(function () {{
  function setTheme(block, theme) {{
    var isDark = theme === 'dark';
    var toggle = block.querySelector('.claat-toggle-code-theme');
    block.dataset.codeTheme = isDark ? 'dark' : 'light';
    if (!toggle) return;
    toggle.setAttribute('aria-label', isDark ? 'Use light code theme' : 'Use dark code theme');
    toggle.setAttribute('title', isDark ? 'Use light code theme' : 'Use dark code theme');
    var icon = toggle.querySelector('.material-icons');
    if (icon) icon.textContent = isDark ? 'light_mode' : 'dark_mode';
  }}

  function copyText(text) {{
    if (navigator.clipboard && window.isSecureContext) {{
      return navigator.clipboard.writeText(text);
    }}
    var textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'fixed';
    textarea.style.top = '-9999px';
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    return Promise.resolve();
  }}

  document.addEventListener('click', function (event) {{
    var copyButton = event.target.closest('.claat-copy-code');
    var themeButton = event.target.closest('.claat-toggle-code-theme');
    if (!copyButton && !themeButton) return;

    var block = event.target.closest('.claat-code-block');
    if (!block) return;

    if (copyButton) {{
      var code = block.querySelector('pre');
      if (!code) return;
      copyText(code.innerText).then(function () {{
        var icon = copyButton.querySelector('.material-icons');
        if (!icon) return;
        icon.textContent = 'done';
        window.setTimeout(function () {{
          icon.textContent = 'content_copy';
        }}, 1200);
      }});
    }}

    if (themeButton) {{
      setTheme(block, block.dataset.codeTheme === 'dark' ? 'light' : 'dark');
    }}
  }});

  document.addEventListener('DOMContentLoaded', function () {{
    document.querySelectorAll('.claat-code-block').forEach(function (block) {{
      setTheme(block, block.dataset.codeTheme || 'light');
    }});
  }});
}}());
</script>"""


def parse_markdown_metadata(markdown: str) -> dict[str, str]:
    metadata: dict[str, str] = {}

    for line in markdown.splitlines():
        if not line.strip():
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        if key:
            metadata[key] = value.strip()

    h1 = re.search(r"^#\s+(.+?)\s*$", markdown, re.MULTILINE)
    if h1:
        metadata["title"] = h1.group(1).strip()

    image = first_markdown_image(markdown)
    if image:
        metadata["image_alt"] = image[0]
        metadata["image"] = image[1]

    return metadata


def first_markdown_image(markdown: str) -> tuple[str, str] | None:
    markdown = re.sub(r"```.*?```", "", markdown, flags=re.DOTALL)
    markdown = re.sub(r"~~~.*?~~~", "", markdown, flags=re.DOTALL)
    pattern = re.compile(
        r"!\[(?P<alt>[^\]]*)\]\("
        r"(?P<target><[^>\n]+>|[^\s)\n]+)"
        r"(?:\s+['\"][^'\"]*['\"])?"
        r"\)"
    )
    match = pattern.search(markdown)
    if not match:
        return None

    target = match.group("target").strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    return match.group("alt").strip(), target


def load_markdown_metadata(source_md: str | None) -> dict[str, str]:
    if not source_md:
        return {}

    path = Path(source_md)
    if not path.exists():
        return {}

    return parse_markdown_metadata(path.read_text(encoding="utf-8"))


def load_codelab_metadata(html_path: str | None) -> dict[str, str]:
    if not html_path:
        return {}

    codelab_json = Path(html_path).resolve().parent / "codelab.json"
    if not codelab_json.exists():
        return {}

    try:
        data = json.loads(codelab_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    metadata: dict[str, str] = {}
    for source_key, target_key in (("title", "title"), ("summary", "summary")):
        value = data.get(source_key)
        if isinstance(value, str):
            metadata[target_key] = value
    return metadata


def resolve_relative_asset(source: str, source_md: str | None, html_path: str | None) -> str:
    if not source or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", source) or source.startswith(("/", "#")):
        return source
    if not source_md or not html_path:
        return source

    source_path = (Path(source_md).resolve().parent / source).resolve()
    html_dir = Path(html_path).resolve().parent
    return os.path.relpath(source_path, html_dir).replace(os.sep, "/")


def attrs_from_tag(tag: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for match in re.finditer(r"([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*(['\"])(.*?)\2", tag, re.DOTALL):
        attrs[match.group(1).lower()] = html_lib.unescape(match.group(3))
    return attrs


def exported_image_src_for_alt(html: str, alt: str) -> str | None:
    if not alt:
        return None

    for match in re.finditer(r"<img\b[^>]*>", html, re.IGNORECASE):
        attrs = attrs_from_tag(match.group(0))
        if attrs.get("alt") == alt and attrs.get("src"):
            return attrs["src"]
    return None


def ogp_values(html: str, html_path: str | None, source_md: str | None) -> dict[str, str]:
    values: dict[str, str] = {}
    codelab_metadata = load_codelab_metadata(html_path)
    markdown_metadata = load_markdown_metadata(source_md)

    title = markdown_metadata.get("title") or codelab_metadata.get("title")
    if not title:
        title_match = re.search(r"<title>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
        if title_match:
            title = html_lib.unescape(re.sub(r"\s+", " ", title_match.group(1)).strip())

    description = markdown_metadata.get("summary") or codelab_metadata.get("summary")
    if not description:
        first_p = re.search(r"<google-codelab-step\b[^>]*>\s*<p>(.*?)</p>", html, re.DOTALL | re.IGNORECASE)
        if first_p:
            description = html_lib.unescape(re.sub(r"<[^>]+>", "", first_p.group(1))).strip()

    if title:
        values["og:title"] = title
    if description:
        values["og:description"] = description

    image = markdown_metadata.get("image")
    if image:
        image = exported_image_src_for_alt(html, markdown_metadata.get("image_alt", "")) or resolve_relative_asset(
            image,
            source_md,
            html_path,
        )
        values["og:image"] = image

    return values


def inject_ogp(html: str, values: dict[str, str]) -> tuple[str, int]:
    if not values:
        return html, 0

    total = 0
    for prop, value in values.items():
        meta_id = OGP_META_ID_PREFIX + prop.replace(":", "-")
        content = html_lib.escape(value, quote=True)
        tag = f'<meta id="{meta_id}" property="{prop}" content="{content}">'
        pattern = re.compile(
            r'<meta\b(?=[^>]*(?:property|name)=["\']' + re.escape(prop) + r'["\'])[^>]*>\n?',
            re.IGNORECASE,
        )
        html, n = pattern.subn("", html)
        total += n
        html, n = re.subn(
            r'(?=<(?:link|style)\b[^>]*id=["\'](?:'
            + re.escape(FAVICON_ID)
            + "|"
            + re.escape(STYLE_ID)
            + r')["\'])',
            tag + "\n",
            html,
            count=1,
            flags=re.IGNORECASE,
        )
        if n == 0:
            html, n = re.subn(r"</head>", tag + "\n</head>", html, count=1, flags=re.IGNORECASE)
        if n == 0:
            html = tag + "\n" + html
            n = 1
        total += n

    return html, total


def escape_codespans(html: str) -> tuple[str, int]:
    pattern = re.compile(r"<code>([^<>]*<[^<]*?)</code>")

    def escape(m: re.Match) -> str:
        inner = m.group(1)
        inner = inner.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f"<code>{inner}</code>"

    total = 0
    while True:
        html, n = pattern.subn(escape, html)
        if n == 0:
            return html, total
        total += n


def wrap_asides(html: str) -> tuple[str, int]:
    keys = "|".join(re.escape(k) for k in ASIDE_KEYWORDS)
    # <p><strong>Keyword:</strong>...</p> optionally followed by a single <ul>/<ol> block
    pattern = re.compile(
        r"<p><strong>(?P<kw>" + keys + r"):?</strong>"
        r"(?P<body>.*?)</p>"
        r"(?P<list>\s*<(?P<lt>ul|ol)[^>]*>.*?</(?P=lt)>)?",
        re.DOTALL,
    )

    total = 0

    def repl(m: re.Match) -> str:
        nonlocal total

        last_aside_open = html.rfind("<aside", 0, m.start())
        last_aside_close = html.rfind("</aside>", 0, m.start())
        if last_aside_open > last_aside_close:
            return m.group(0)

        klass = ASIDE_KEYWORDS[m.group("kw")]
        total += 1
        return f'<aside class="{klass}">{m.group(0)}</aside>'

    return pattern.sub(repl, html), total


def retag_troubleshooting_asides(html: str) -> tuple[str, int]:
    pattern = re.compile(
        r'<aside class="warning">(\s*<p><strong>Troubleshooting:?</strong>)',
        re.DOTALL,
    )
    return pattern.subn(r'<aside class="troubleshooting">\1', html)


def wrap_code_blocks(html: str) -> tuple[str, int]:
    if 'class="claat-code-block"' in html:
        return html, 0

    pattern = re.compile(r"(?P<pre><pre\b(?P<attrs>[^>]*)>.*?</pre>)", re.DOTALL)

    def repl(m: re.Match) -> str:
        pre = m.group("pre")
        return (
            '<div class="claat-code-block" data-code-theme="light">\n'
            f"{CODE_TOOLBAR}\n"
            f"{pre}\n"
            "</div>"
        )

    return pattern.subn(repl, html)


def repair_button_links(html: str) -> tuple[str, int]:
    br = r"<br\s*/?>"
    spacer = rf"(?:\s|{br})*"
    pattern = re.compile(
        rf"<(?P<tag>p|li)(?P<attrs>[^>]*)>"
        rf"{spacer}\[(?P<label>[^\]\n]+)\]\((?P<href>[^\s)]+)\){spacer}"
        rf"</(?P=tag)>",
        re.IGNORECASE,
    )

    def repl(m: re.Match) -> str:
        tag = m.group("tag")
        attrs = m.group("attrs")
        label = html_lib.escape(html_lib.unescape(m.group("label")))
        href = html_lib.escape(html_lib.unescape(m.group("href")), quote=True)
        button = (
            f'<a href="{href}" target="_blank">'
            f'<paper-button class="colored" raised>{label}</paper-button>'
            "</a>"
        )
        return f"<{tag}{attrs}>{button}</{tag}>"

    return pattern.subn(repl, html)


def linkify_bare_urls(html: str) -> tuple[str, int]:
    tag_pattern = re.compile(r"(<[^>]+>)")
    url_pattern = re.compile(r"https?://[^\s<>\"]+")
    stack: list[str] = []
    total = 0
    parts: list[str] = []

    def linkify_text(text: str) -> str:
        nonlocal total

        def repl(m: re.Match) -> str:
            nonlocal total
            url = m.group(0)
            trailing = ""
            while url and url[-1] in TRAILING_URL_PUNCTUATION:
                trailing = url[-1] + trailing
                url = url[:-1]
            if not url:
                return m.group(0)

            href = html_lib.escape(html_lib.unescape(url), quote=True)
            total += 1
            return f'<a href="{href}" target="_blank">{url}</a>{trailing}'

        return url_pattern.sub(repl, text)

    for part in tag_pattern.split(html):
        if not part:
            continue

        if part.startswith("<"):
            tag = re.match(r"</?\s*([a-zA-Z0-9-]+)", part)
            if tag:
                tag_name = tag.group(1).lower()
                is_end = part.startswith("</")
                is_self_closing = part.rstrip().endswith("/>")

                if tag_name in SKIP_LINKIFY_TAGS:
                    if is_end:
                        for i in range(len(stack) - 1, -1, -1):
                            if stack[i] == tag_name:
                                del stack[i:]
                                break
                    elif not is_self_closing:
                        stack.append(tag_name)

            parts.append(part)
            continue

        if stack:
            parts.append(part)
        else:
            parts.append(linkify_text(part))

    return "".join(parts), total


def favicon_href_for(html_path: str) -> str:
    repo_root = Path(__file__).resolve().parents[1]
    favicon = repo_root / "assets" / "favicon.png"
    html_dir = Path(html_path).resolve().parent
    return os.path.relpath(favicon, html_dir).replace(os.sep, "/")


def inject_favicon(html: str, href: str) -> tuple[str, int]:
    if f'id="{FAVICON_ID}"' in html:
        return html, 0

    favicon_link = f'<link id="{FAVICON_ID}" rel="icon" type="image/png" href="{href}">'
    html, n = re.subn(r"</head>", favicon_link + "\n</head>", html, count=1)
    if n == 0:
        html = favicon_link + "\n" + html
        n = 1
    return html, n


def inject_local_assets(html: str) -> tuple[str, int, int]:
    n_style = 0
    n_script = 0

    if f'id="{STYLE_ID}"' in html:
        html, n_style = re.subn(
            r'<style id="' + re.escape(STYLE_ID) + r'">.*?</style>',
            LOCAL_STYLE,
            html,
            count=1,
            flags=re.DOTALL,
        )
    else:
        html, n_style = re.subn(r"</head>", LOCAL_STYLE + "\n</head>", html, count=1)
        if n_style == 0:
            html = LOCAL_STYLE + "\n" + html
            n_style = 1

    if f'id="{SCRIPT_ID}"' not in html:
        html, n_script = re.subn(r"</body>", LOCAL_SCRIPT + "\n</body>", html, count=1)
        if n_script == 0:
            html = html + "\n" + LOCAL_SCRIPT + "\n"
            n_script = 1

    return html, n_style, n_script


def fix(
    html: str,
    html_path: str | None = None,
    source_md: str | None = None,
) -> tuple[str, int, int, int, int, int, int, int, int, int]:
    html, n_code = escape_codespans(html)
    html, n_aside = wrap_asides(html)
    html, n_retagged = retag_troubleshooting_asides(html)
    html, n_blocks = wrap_code_blocks(html)
    html, n_buttons = repair_button_links(html)
    html, n_links = linkify_bare_urls(html)
    html, n_ogp = inject_ogp(html, ogp_values(html, html_path, source_md))
    favicon_href = favicon_href_for(html_path) if html_path else "assets/favicon.png"
    html, n_favicon = inject_favicon(html, favicon_href)
    html, n_style, n_script = inject_local_assets(html)
    return html, n_code, n_aside + n_retagged, n_blocks, n_buttons, n_links, n_ogp, n_favicon, n_style, n_script


def main() -> int:
    parser = argparse.ArgumentParser(description="Post-process claat-generated HTML files.")
    parser.add_argument("--source-md", "--source", dest="source_md", help="source claat markdown file")
    parser.add_argument("html_files", nargs="*")
    args = parser.parse_args()

    if not args.html_files:
        parser.print_usage(sys.stderr)
        return 2

    for path in args.html_files:
        with open(path, encoding="utf-8") as f:
            original = f.read()
        (
            fixed,
            n_code,
            n_aside,
            n_blocks,
            n_buttons,
            n_links,
            n_ogp,
            n_favicon,
            n_style,
            n_script,
        ) = fix(original, path, args.source_md)
        if fixed != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(fixed)
        print(
            f"{path}: fixed {n_code} code spans, wrapped {n_aside} asides, "
            f"enhanced {n_blocks} code blocks, repaired {n_buttons} buttons, "
            f"linkified {n_links} URLs, "
            f"injected {n_ogp} OGP tags, {n_favicon} favicons, "
            f"{n_style} styles and {n_script} scripts"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
