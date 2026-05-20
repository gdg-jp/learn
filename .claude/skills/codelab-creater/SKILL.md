---
name: codelab-creater
description: Use this skill whenever the user asks to create a codelab, a hands-on lab, a step-by-step tutorial, or workshop materials in this repository. Covers the claat markdown format — frontmatter, steps, Duration, callout boxes, code blocks, and image conventions — so new codelabs match the GDG on Campus University of Osaka style. Trigger even when the user says "write a tutorial", "make a hands-on doc", "claat を作って", or "コードラボを作りたい"; in this repo, step-by-step workshop guides always mean claat format.
---

# codelab-creater

Every codelab in this repo is a `claat.md` file inside `<content-name>/` that gets exported to `index.html` via `make claat`. Look at `portfolio-2026/claat.md` for a full worked example. This skill covers the claat markdown conventions; the build pipeline is in `CLAUDE.md`.

## Workflow

1. Create `<content-name>/claat.md` and `<content-name>/img/` for images.
2. Write the file using the conventions below.
3. Build: `make claat <content-name>/claat.md <content-name>`
4. Verify the generated `index.html` looks right (check callout boxes and code spans especially).

---

## File structure

```
<content-name>/
  claat.md          ← you write this
  index.html        ← generated (committed)
  libs/             ← generated (committed)
  img/              ← screenshots and diagrams you provide
```

---

## Frontmatter (required — goes at the very top, no fences)

```
summary: One-line description shown in the codelab gallery
id: kebab-case-unique-id
categories: Web
environments: Web
status: Published
feedback link: https://github.com/googlecodelabs/your-first-pwapp/issues
author: GDG on Campus University of Osaka
```

`id` becomes the codelab's internal identifier. Use kebab-case matching the directory name.

---

## Document-level title

The first `#` heading is the codelab title shown at the top of the lab page.

```markdown
# ワークショップのタイトル
```

---

## Steps

Each `##` heading starts a new step. The text after `##` is the step title displayed in the sidebar navigation.

```markdown
## Step 1: 環境の準備
Duration: 0:15:00

ステップの本文をここに書く。
```

`Duration: H:MM:SS` is required on the first line of each step's body. It drives the estimated time shown in the UI. Add it to every step — omitting it makes the progress bar inaccurate.

Sub-headings within a step use `###`.

---

## Callout boxes

`> **Keyword:** text` becomes a styled aside box. The fix-claat-codespans.py postprocessor handles the conversion. Recognized keywords (first word after `>`):

| Keyword(s)                          | Box style  |
|-------------------------------------|------------|
| `Note`, `Notice`, `補足`            | Info (blue)|
| `Tip`, `Tips`, `Hint`               | Success (green) |
| `Warning`, `Warn`, `Caution`        | Warning (red) |
| `Troubleshooting`                   | Warning (red) |

Multi-line callouts: indent continuation lines with `>`.

```markdown
> **Troubleshooting:** インストールがうまくいかない場合は、
> 以下の点を確認してください。
> - ネットワーク接続を確認する
> - 管理者権限で実行する
```

---

## Code blocks

Use fenced code blocks with a language specifier — the renderer does syntax highlighting.

```markdown
`index.html`

```html
<!DOCTYPE html>
<html>
…
</html>
```
```

Inline code uses single backticks: `` `<h1>` ``. The postprocessor escapes raw HTML tags inside inline code so they render correctly.

---

## Images

```markdown
![スクリーンショットの説明](img/step2-1.png)
```

Place all images in `<content-name>/img/`. Use descriptive alt text that also works as a caption. Name files after the step they appear in: `step2-1.png`, `step2-2.png`, etc.

### Screenshot placeholders

For UI steps where you need a real screenshot but don't have one yet, write a placeholder comment immediately below the image line:

```markdown
![VSCode でファイルを新規作成する手順](img/step2-1.png)
<!-- TODO: screenshot — VSCode explorer, new file icon highlighted -->
```

The codelab will build fine with a missing image (it shows a broken-image icon); replace the placeholder before publishing.

### When to add figures

Every step that asks the participant to perform a UI action benefits from a screenshot. A good rule: one screenshot per `###` sub-section that changes something visible on screen. Concept-explanation sections (no UI action) can have a diagram instead.

### Generated diagrams — use the gen-image skill

For architecture diagrams, flow charts, or concept illustrations (not screenshots of real software), invoke `/gen-image` to produce a figure. Prompt design principles for this repo:

- **Font:** Google Sans for Latin text; Noto Sans JP for Japanese text
- **Icons:** Use Google Material icons for generic UI concepts; use official Google Product icons (Chrome, Firebase, GitHub, etc.) when referring to specific products
- **Style:** Clean, flat, white or light-grey background, GDG brand colors (`#4285F4` blue, `#34A853` green, `#EA4335` red, `#FBBC04` yellow)
- Place the generated image in `img/` and reference it with the standard `![...](img/...)` syntax

Aim for roughly one figure every 2–3 sub-sections in instructional content — enough to orient the reader visually without overwhelming the text.

---

## Buttons

To render a styled link button:

```markdown
<button>
  [ボタンラベル](https://example.com/url)
</button>
```

---

## Links and inline markup

Standard Markdown: `[text](url)`, `**bold**`, `*italic*`. These all render normally.

---

## Final step convention

End every codelab with a summary step:

```markdown
## まとめと次のステップ
Duration: 0:05:00

このワークショップで学んだこと：
* 箇条書きで振り返る
* …

### Next Steps
…
```

---

## Build and verify

```bash
make claat <content-name>/claat.md <content-name>
```

After building, open `<content-name>/index.html` in a browser and check:
- Callout boxes render with color (not plain `>` text)
- Inline `<code>` containing HTML tags shows `&lt;…&gt;`, not raw tags
- Images load (or show the placeholder broken-image icon as expected)
- Step durations appear in the sidebar

If callouts are plain text, the aside keywords may not match — check the keyword list above and `CLAUDE.md`'s `ASIDE_KEYWORDS` dict.
