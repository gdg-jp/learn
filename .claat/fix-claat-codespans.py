#!/usr/bin/env python3
"""Post-process claat-exported index.html files.

Four fixes are applied:

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

4. Inject local CSS and JS that make code blocks light by default, style the
   toolbar buttons, preserve the dark-mode toggle, and add a full outline to
   callouts.
"""

import re
import sys

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
    "Troubleshooting": "warning",
}

STYLE_ID = "claat-local-preprocessor-style"
SCRIPT_ID = "claat-local-preprocessor-script"

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


def inject_local_assets(html: str) -> tuple[str, int, int]:
    n_style = 0
    n_script = 0

    if f'id="{STYLE_ID}"' not in html:
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


def fix(html: str) -> tuple[str, int, int, int, int, int]:
    html, n_code = escape_codespans(html)
    html, n_aside = wrap_asides(html)
    html, n_blocks = wrap_code_blocks(html)
    html, n_style, n_script = inject_local_assets(html)
    return html, n_code, n_aside, n_blocks, n_style, n_script


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: fix-claat-codespans.py <html-file>...", file=sys.stderr)
        return 2
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8") as f:
            original = f.read()
        fixed, n_code, n_aside, n_blocks, n_style, n_script = fix(original)
        if fixed != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(fixed)
        print(
            f"{path}: fixed {n_code} code spans, wrapped {n_aside} asides, "
            f"enhanced {n_blocks} code blocks, injected {n_style} styles and {n_script} scripts"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
