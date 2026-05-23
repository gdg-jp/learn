---
marp: true
theme: gdg
paginate: true
size: 16:9
---

<script>
/* PowerPoint-style auto-shrink: iteratively reduce a slide's font size
   until its content stops overflowing. Also keeps the explicit opt-in
   <div class="fit">…</div> wrapper for finer-grained scaling. */
(() => {
  const MIN_FONT_PX = 12;
  const CODE_MIN_FONT_PX = 9;
  const STEP = 0.96;
  const MAX_ITERS = 40;
  const TOLERANCE = 1;
  let scheduled = false;

  const overflows = (el) =>
    el.scrollHeight > el.clientHeight + TOLERANCE ||
    el.scrollWidth  > el.clientWidth  + TOLERANCE;

  const shrinkElement = (el, minFontPx, shouldShrink = () => overflows(el)) => {
    if (!shouldShrink()) return;
    const base = parseFloat(getComputedStyle(el).fontSize) || 18;
    let size = base;
    for (let i = 0; i < MAX_ITERS && shouldShrink() && size > minFontPx; i++) {
      size *= STEP;
      el.style.fontSize = `${size}px`;
    }
  };

  const shrinkCodeBlocks = (section) => {
    for (const pre of section.querySelectorAll("pre")) {
      shrinkElement(pre, CODE_MIN_FONT_PX, () => overflows(pre) || overflows(section));
    }
  };

  const shrinkSection = (section) => {
    if (section.dataset.autofit === "skip") return;
    shrinkElement(section, MIN_FONT_PX, () => overflows(section));
  };

  const scaleFitBlocks = (root) => {
    for (const fit of root.querySelectorAll(".fit")) {
      if (!fit.scrollHeight) continue;
      const ratio = Math.min(1, fit.clientHeight / fit.scrollHeight);
      fit.style.transformOrigin = "top left";
      fit.style.transform = `scale(${ratio})`;
    }
  };

  const processSection = (section) => {
    if (!section.clientWidth || !section.clientHeight) return;
    scaleFitBlocks(section);
    shrinkCodeBlocks(section);
    shrinkSection(section);
  };

  const processVisibleSections = () => {
    scheduled = false;
    for (const section of document.querySelectorAll("section")) processSection(section);
  };

  const schedule = () => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => requestAnimationFrame(processVisibleSections));
  };

  window.addEventListener("load", schedule);
  window.addEventListener("resize", schedule);
  new MutationObserver(schedule).observe(document.documentElement, {
    subtree: true,
    attributes: true,
    attributeFilter: ["class"],
  });
  schedule();
})();
</script>

<style>
/* Set once per deck — drives the colored university name on every title slide. */
:root { --gdg-university: 'University of Osaka'; }

.cover-qr {
  position: absolute;
  right: 110px;
  top: 184px;
  width: 310px;
  padding: 22px;
  background: #fff;
  border: 2px solid var(--gdg-line);
  border-radius: 8px;
}

.cover-label {
  position: absolute;
  right: 106px;
  top: 540px;
  width: 360px;
  text-align: center;
  font-size: 22px;
  font-weight: 700;
  color: var(--gdg-ink);
}

.note {
  color: var(--gdg-muted);
  font-size: 18px;
}

.large-img {
  width: 100%;
  max-height: 500px;
  object-fit: contain;
}

.image-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 22px;
  margin-top: 18px;
}

.image-row figure {
  margin: 0;
  padding: 14px;
  background: #fff;
  border: 1px solid var(--gdg-line);
  border-radius: 8px;
}

.image-row img {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: 6px;
}

.image-row figcaption {
  margin-top: 8px;
  color: var(--gdg-muted);
  font-size: 17px;
  text-align: center;
}

.pill {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 999px;
  background: #E8F0FE;
  color: var(--gdg-blue);
  font-weight: 700;
  font-size: 16px;
}

.big-number {
  font-size: 58px;
  line-height: 1;
  font-weight: 700;
  color: var(--gdg-blue);
}
</style>

<!-- _class: title -->
<!-- _paginate: false -->

# Lyria 3 Pro で<br>音楽生成を<br>体験しよう

15 分ハンズオン / Media Studio

<img class="cover-qr" src="../img/codelab-qr-code.png" alt="コードラボの QR コード">
<div class="cover-label">コードラボはこちら</div>

---

## 今日のゴール

<div class="container" style="align-items: center; gap: 48px;">

<div class="col" style="flex: 0 0 38%;">

- ブラウザだけで音楽を 1 曲生成します
- プロンプトを足して、聴こえ方の変化を確認します
- 画像とテキストを組み合わせて、曲の方向性を伝えます

<p class="note">うまい曲を作るより、モデルに何を伝えると変わるかを体験します</p>

</div>

<div class="col" style="flex: 1 1 62%;">

<svg viewBox="0 0 780 430" style="width: 100%; height: 430px;" role="img" aria-label="ハンズオンの流れ">
  <defs>
    <marker id="arrow-goal" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">
      <path d="M2,2 L10,6 L2,10 Z" fill="#3c4043"/>
    </marker>
  </defs>
  <rect x="20" y="40" width="180" height="130" rx="14" fill="#E8F0FE" stroke="#4285F4" stroke-width="3"/>
  <text x="110" y="92" text-anchor="middle" font-size="24" font-weight="700">開く</text>
  <text x="110" y="130" text-anchor="middle" font-size="18">Media Studio</text>
  <line x1="212" y1="105" x2="285" y2="105" stroke="#3c4043" stroke-width="4" marker-end="url(#arrow-goal)"/>
  <rect x="300" y="40" width="180" height="130" rx="14" fill="#E6F4EA" stroke="#34A853" stroke-width="3"/>
  <text x="390" y="92" text-anchor="middle" font-size="24" font-weight="700">作る</text>
  <text x="390" y="130" text-anchor="middle" font-size="18">Text to Music</text>
  <line x1="492" y1="105" x2="565" y2="105" stroke="#3c4043" stroke-width="4" marker-end="url(#arrow-goal)"/>
  <rect x="580" y="40" width="180" height="130" rx="14" fill="#FEF7E0" stroke="#FBBC04" stroke-width="3"/>
  <text x="670" y="92" text-anchor="middle" font-size="24" font-weight="700">聴く</text>
  <text x="670" y="130" text-anchor="middle" font-size="18">変化を言葉にする</text>
  <line x1="670" y1="182" x2="670" y2="248" stroke="#3c4043" stroke-width="4" marker-end="url(#arrow-goal)"/>
  <rect x="580" y="265" width="180" height="130" rx="14" fill="#FCE8E6" stroke="#EA4335" stroke-width="3"/>
  <text x="670" y="317" text-anchor="middle" font-size="24" font-weight="700">足す</text>
  <text x="670" y="355" text-anchor="middle" font-size="18">画像 + 指示</text>
  <line x1="568" y1="330" x2="495" y2="330" stroke="#3c4043" stroke-width="4" marker-end="url(#arrow-goal)"/>
  <rect x="300" y="265" width="180" height="130" rx="14" fill="#FFFFFF" stroke="#DADCE0" stroke-width="3"/>
  <text x="390" y="317" text-anchor="middle" font-size="24" font-weight="700">比べる</text>
  <text x="390" y="355" text-anchor="middle" font-size="18">プロンプト改善</text>
  <line x1="288" y1="330" x2="215" y2="330" stroke="#3c4043" stroke-width="4" marker-end="url(#arrow-goal)"/>
  <rect x="20" y="265" width="180" height="130" rx="14" fill="#FFFFFF" stroke="#DADCE0" stroke-width="3"/>
  <text x="110" y="317" text-anchor="middle" font-size="24" font-weight="700">共有</text>
  <text x="110" y="355" text-anchor="middle" font-size="18">気づきを持ち帰る</text>
</svg>

</div>

</div>

---

## 15 分の進め方

| 時間 | やること | ゴール |
| --- | --- | --- |
| 0:00 | QR からコードラボを開く | 手順を見られる |
| 0:02 | アカウントとプロジェクトを確認 | `lyria-hands-on` に入れる |
| 0:05 | 短いプロンプトで生成 | まず 1 曲聴ける |
| 0:09 | プロンプトを指示書にする | ジャンル・楽器・テンポを指定できる |
| 0:12 | 画像から雰囲気を足す | 画像 + テキストを試せる |
| 0:15 | まとめ | 次に試す観点が分かる |

---

<!-- _class: section -->

# 01. Lyria を知る

---

## Lyria とは

<div class="container" style="align-items: center; gap: 44px;">

<div class="col" style="flex: 0 0 36%;">

<span class="pill">Google DeepMind</span>

Lyria は、テキストや画像から音楽を生成する Google の音楽生成モデルファミリーです

- 今日使うのは `Lyria 3 Pro`
- Media Studio からブラウザで試せます
- 開発者向けには Gemini API / Vertex AI でも使われます

</div>

<div class="col" style="flex: 1 1 64%;">

<svg viewBox="0 0 780 450" style="width: 100%; height: 450px;" role="img" aria-label="Lyria の入力と出力">
  <defs>
    <marker id="arrow-lyria" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">
      <path d="M2,2 L10,6 L2,10 Z" fill="#4285F4"/>
    </marker>
  </defs>
  <rect x="30" y="64" width="180" height="120" rx="16" fill="#E8F0FE" stroke="#4285F4" stroke-width="3"/>
  <text x="120" y="118" text-anchor="middle" font-size="24" font-weight="700">テキスト</text>
  <text x="120" y="152" text-anchor="middle" font-size="17">ジャンル / 雰囲気</text>
  <rect x="30" y="270" width="180" height="120" rx="16" fill="#FEF7E0" stroke="#FBBC04" stroke-width="3"/>
  <text x="120" y="324" text-anchor="middle" font-size="24" font-weight="700">画像</text>
  <text x="120" y="358" text-anchor="middle" font-size="17">色 / 世界観</text>
  <line x1="224" y1="124" x2="330" y2="202" stroke="#4285F4" stroke-width="5" marker-end="url(#arrow-lyria)"/>
  <line x1="224" y1="330" x2="330" y2="248" stroke="#4285F4" stroke-width="5" marker-end="url(#arrow-lyria)"/>
  <rect x="330" y="145" width="190" height="160" rx="24" fill="#FFFFFF" stroke="#34A853" stroke-width="4"/>
  <text x="425" y="214" text-anchor="middle" font-size="32" font-weight="700">Lyria</text>
  <path d="M370 250 C390 220, 410 280, 430 250 S470 250, 490 250" fill="none" stroke="#34A853" stroke-width="6" stroke-linecap="round"/>
  <line x1="536" y1="225" x2="640" y2="225" stroke="#4285F4" stroke-width="5" marker-end="url(#arrow-lyria)"/>
  <rect x="650" y="145" width="110" height="160" rx="18" fill="#FCE8E6" stroke="#EA4335" stroke-width="3"/>
  <text x="705" y="205" text-anchor="middle" font-size="25" font-weight="700">音楽</text>
  <text x="705" y="240" text-anchor="middle" font-size="17">MP3 / WAV</text>
</svg>

</div>

</div>

<footer>出典: Google Cloud Lyria docs / Google AI Developers Lyria 3 docs</footer>

---

## Lyria 3 Pro の位置づけ

<div class="container" style="align-items: stretch; gap: 34px;">

<div class="col" style="flex: 0 0 34%;">

Google の公式情報では、用途に合わせてモデルや提供面が分かれています

- `Lyria 3 Clip`: 短いクリップ向け
- `Lyria 3 Pro`: 数分程度の曲、構成のある生成向け
- Media Studio / AI Studio / Gemini API / Vertex AI などから利用

</div>

<div class="col" style="flex: 1 1 66%;">

<svg viewBox="0 0 820 430" style="width: 100%; height: 430px;" role="img" aria-label="Lyria モデルの比較">
  <rect x="30" y="40" width="220" height="310" rx="16" fill="#E8F0FE" stroke="#4285F4" stroke-width="3"/>
  <text x="140" y="92" text-anchor="middle" font-size="27" font-weight="700">Lyria 3 Clip</text>
  <text x="140" y="142" text-anchor="middle" font-size="52" font-weight="700" fill="#4285F4">30s</text>
  <text x="140" y="190" text-anchor="middle" font-size="19">ループ / 下書き</text>
  <text x="140" y="225" text-anchor="middle" font-size="19">SNS / プレビュー</text>
  <text x="140" y="276" text-anchor="middle" font-size="17" fill="#5F6368">速く試す</text>
  <rect x="300" y="40" width="250" height="310" rx="16" fill="#E6F4EA" stroke="#34A853" stroke-width="4"/>
  <text x="425" y="92" text-anchor="middle" font-size="29" font-weight="700">Lyria 3 Pro</text>
  <text x="425" y="142" text-anchor="middle" font-size="50" font-weight="700" fill="#34A853">数分</text>
  <text x="425" y="190" text-anchor="middle" font-size="19">Verse / Chorus</text>
  <text x="425" y="225" text-anchor="middle" font-size="19">Bridge / 展開</text>
  <text x="425" y="276" text-anchor="middle" font-size="17" fill="#5F6368">構成まで試す</text>
  <rect x="600" y="40" width="190" height="310" rx="16" fill="#FEF7E0" stroke="#FBBC04" stroke-width="3"/>
  <text x="695" y="92" text-anchor="middle" font-size="26" font-weight="700">Lyria 2</text>
  <text x="695" y="142" text-anchor="middle" font-size="45" font-weight="700" fill="#FBBC04">32.8s</text>
  <text x="695" y="190" text-anchor="middle" font-size="19">Cloud GA docs</text>
  <text x="695" y="225" text-anchor="middle" font-size="19">`lyria-002`</text>
  <text x="695" y="276" text-anchor="middle" font-size="17" fill="#5F6368">現行 GA 情報</text>
  <text x="410" y="395" text-anchor="middle" font-size="18" fill="#5F6368">今日の画面に表示されるモデル名を確認して選びます</text>
</svg>

</div>

</div>

<footer>出典: Google AI Developers Lyria 3 docs / Google Cloud Lyria API docs</footer>

---

## パフォーマンス: まず見る数字

<div class="container" style="align-items: center; gap: 42px;">

<div class="col" style="flex: 0 0 35%;">

Cloud の GA ドキュメントと、Lyria 3 Pro の公開プレビュー情報では前提が違います

- Cloud GA docs は `lyria-002` の数値
- Lyria 3 Pro は数分程度の曲と構成指定が中心
- 今日の進行では、画面の `Lyria 3 Pro` を選びます

</div>

<div class="col" style="flex: 1 1 65%;">

<svg viewBox="0 0 820 430" style="width: 100%; height: 430px;" role="img" aria-label="Lyria の主要なパフォーマンス情報">
  <rect x="45" y="70" width="330" height="270" rx="18" fill="#FEF7E0" stroke="#FBBC04" stroke-width="4"/>
  <text x="210" y="122" text-anchor="middle" font-size="27" font-weight="700">Cloud GA docs</text>
  <text x="210" y="162" text-anchor="middle" font-size="20">Lyria 2 / `lyria-002`</text>
  <text x="210" y="224" text-anchor="middle" font-size="46" font-weight="700" fill="#FBBC04">32.8 秒</text>
  <text x="210" y="272" text-anchor="middle" font-size="20">通常 10〜20 秒で生成</text>
  <text x="210" y="305" text-anchor="middle" font-size="20">48 kHz WAV / en-us prompt</text>
  <rect x="445" y="70" width="330" height="270" rx="18" fill="#E6F4EA" stroke="#34A853" stroke-width="4"/>
  <text x="610" y="122" text-anchor="middle" font-size="29" font-weight="700">Lyria 3 Pro</text>
  <text x="610" y="162" text-anchor="middle" font-size="20">公開プレビュー情報</text>
  <text x="610" y="224" text-anchor="middle" font-size="46" font-weight="700" fill="#34A853">数分程度</text>
  <text x="610" y="272" text-anchor="middle" font-size="20">テキスト + 画像</text>
  <text x="610" y="305" text-anchor="middle" font-size="20">44.1 kHz stereo / MP3, WAV</text>
</svg>

</div>

</div>

<footer>出典: Google Cloud Lyria docs / Google AI Developers Lyria 3 docs / Google Blog</footer>

---

## 制限事項: 進行で覚えること

<div class="container" style="align-items: center; gap: 44px;">

<div class="col" style="flex: 0 0 36%;">

- 混雑時は生成がキューに入ることがあります
- プロンプトや生成結果は安全フィルタで止まる場合があります
- 出力は必ず自分の耳で確認します
- 今日は英語プロンプトを使うと進めやすいです

<p class="note">仕様はモデルと提供面で変わるため、最新の画面と公式ドキュメントを確認します</p>

</div>

<div class="col" style="flex: 1 1 64%;">

<svg viewBox="0 0 780 430" style="width: 100%; height: 430px;" role="img" aria-label="生成時に気をつける制限事項">
  <rect x="55" y="65" width="300" height="120" rx="16" fill="#E8F0FE" stroke="#4285F4" stroke-width="3"/>
  <text x="205" y="112" text-anchor="middle" font-size="24" font-weight="700">待ち時間</text>
  <text x="205" y="150" text-anchor="middle" font-size="18">混雑時はキューに入る</text>
  <rect x="425" y="65" width="300" height="120" rx="16" fill="#FCE8E6" stroke="#EA4335" stroke-width="3"/>
  <text x="575" y="112" text-anchor="middle" font-size="24" font-weight="700">安全フィルタ</text>
  <text x="575" y="150" text-anchor="middle" font-size="18">一部の入力や出力は止まる</text>
  <rect x="55" y="245" width="300" height="120" rx="16" fill="#FEF7E0" stroke="#FBBC04" stroke-width="3"/>
  <text x="205" y="292" text-anchor="middle" font-size="24" font-weight="700">モデル差分</text>
  <text x="205" y="330" text-anchor="middle" font-size="18">Lyria 2 と 3 Pro で仕様が違う</text>
  <rect x="425" y="245" width="300" height="120" rx="16" fill="#E6F4EA" stroke="#34A853" stroke-width="3"/>
  <text x="575" y="292" text-anchor="middle" font-size="24" font-weight="700">人の確認</text>
  <text x="575" y="330" text-anchor="middle" font-size="18">狙いに合うか聴いて判断</text>
</svg>

</div>

</div>

<footer>出典: Google Cloud Lyria docs / Google AI Developers Lyria 3 docs / Google Blog</footer>

---

## 生成 AI 音楽で気をつけること

<div class="container" style="align-items: center; gap: 46px;">

<div class="col" style="flex: 0 0 36%;">

- 生成結果は毎回チェックします
- 特定アーティストの模倣を狙わないようにします
- 安全フィルタでプロンプトや出力がブロックされる場合があります
- Google AI 生成音声には SynthID が埋め込まれます

</div>

<div class="col" style="flex: 1 1 64%;">

<svg viewBox="0 0 780 430" style="width: 100%; height: 430px;" role="img" aria-label="責任ある生成の流れ">
  <defs>
    <marker id="arrow-safe" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">
      <path d="M2,2 L10,6 L2,10 Z" fill="#3c4043"/>
    </marker>
  </defs>
  <rect x="35" y="110" width="150" height="120" rx="14" fill="#E8F0FE" stroke="#4285F4" stroke-width="3"/>
  <text x="110" y="160" text-anchor="middle" font-size="22" font-weight="700">Prompt</text>
  <text x="110" y="194" text-anchor="middle" font-size="16">意図を明確に</text>
  <line x1="197" y1="170" x2="280" y2="170" stroke="#3c4043" stroke-width="4" marker-end="url(#arrow-safe)"/>
  <rect x="295" y="80" width="190" height="180" rx="18" fill="#FFFFFF" stroke="#DADCE0" stroke-width="3"/>
  <text x="390" y="132" text-anchor="middle" font-size="22" font-weight="700">Safety checks</text>
  <text x="390" y="170" text-anchor="middle" font-size="16">不適切な内容</text>
  <text x="390" y="198" text-anchor="middle" font-size="16">既存表現の保護</text>
  <text x="390" y="226" text-anchor="middle" font-size="16">利用ポリシー</text>
  <line x1="500" y1="170" x2="583" y2="170" stroke="#3c4043" stroke-width="4" marker-end="url(#arrow-safe)"/>
  <rect x="600" y="110" width="150" height="120" rx="14" fill="#E6F4EA" stroke="#34A853" stroke-width="3"/>
  <text x="675" y="160" text-anchor="middle" font-size="22" font-weight="700">Audio</text>
  <text x="675" y="194" text-anchor="middle" font-size="16">SynthID</text>
  <path d="M105 300 C145 270, 175 335, 215 300 S285 300, 325 300 S395 300, 435 300 S505 300, 545 300 S615 300, 655 300" fill="none" stroke="#4285F4" stroke-width="7" stroke-linecap="round"/>
  <text x="390" y="360" text-anchor="middle" font-size="21" fill="#5F6368">作ったら、必ず自分の耳で確認します</text>
</svg>

</div>

</div>

<footer>出典: Google Cloud Lyria prompt guide / Google DeepMind Lyria page</footer>

---

## Suno AI などとの違い

<div class="container" style="align-items: stretch; gap: 34px;">

<div class="col" style="background: #fff; border-top: 6px solid var(--gdg-blue); border-radius: 8px; padding: 24px;">

### Lyria 3 Pro / Media Studio

- Google Cloud / Vertex AI / AI Studio / Gemini API から使えます
- テキストや画像から、構成のある音楽生成を試せます
- SynthID や Google Cloud の管理面とつながります
- 今日のハンズオンはこの流れです

</div>

<div class="col" style="background: #fff; border-top: 6px solid var(--gdg-green); border-radius: 8px; padding: 24px;">

### Suno

- Suno Web アプリや Studio が主な入口です
- 歌詞、ボーカル、音声アップロードなどの制作機能があります
- Studio ではマルチトラック、Stem、録音、Export などを扱えます
- 曲作りの UI を重視する時に向きます

</div>

</div>

<div style="margin-top: 24px; padding: 18px 24px; background: #F8F9FA; border-left: 5px solid var(--gdg-yellow); font-size: 22px;">
優劣ではなく、入口と設計思想の違いです。今日は Google Cloud 上で扱える Lyria を触ります
</div>

<footer>出典: Google AI Developers / Google Blog / Suno Help Center</footer>

---

<!-- _class: section green -->

# 02. ハンズオン

---

## まずコードラボを開きます

<div class="container" style="align-items: center; gap: 50px;">

<div class="col" style="flex: 0 0 42%;">

1. QR コードを読み取ります
2. `try-lyria` のコードラボを開きます
3. 画面を開いたまま、スライドの指示に沿って進めます

<p class="note">進行に詰まったら、早めにメンターへ画面を見せてください</p>

</div>

<div class="col" style="flex: 1 1 58%; text-align: center;">

<img src="../img/codelab-qr-code.png" alt="コードラボの QR コード" style="width: 360px; background: #fff; padding: 24px; border: 2px solid var(--gdg-line); border-radius: 8px;">

</div>

</div>

---

![bg right:64% fit](../img/step2-email-registration.svg)

## Google Form で登録

まだ登録していない人だけ進めます

- Google Cloud にログインする Gmail を入力します
- 運営が `lyria-hands-on` に IAM ユーザーとして追加します
- 登録完了後に Media Studio へ進みます

<p class="note">別アカウントを入力すると、プロジェクトが見えません</p>

---

![bg right:64% fit](../img/step3-media-studio.svg)

## Media Studio を開く

確認する場所は 3 つです

1. 右上の Google アカウント
2. プロジェクト `lyria-hands-on`
3. モデル `Lyria 3 Pro`

<p class="note">違うプロジェクトでは生成しません</p>

---

## スマートフォンで開く場合

<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; align-items: end;">
  <div style="text-align: center;">
    <img src="../img/screenshot_01_android_desktop_mode.png" alt="Android Chrome でデスクトップ用サイトを表示する" style="height: 440px; max-width: 100%; object-fit: contain; border: 1px solid var(--gdg-line); border-radius: 8px;">
    <p style="margin: 10px 0 0; font-size: 18px; font-weight: 700;">Android</p>
  </div>
  <div style="text-align: center;">
    <img src="../img/screenshot_02_iphone_desktop_mode_1.png" alt="iPhone Safari でページメニューを開く" style="height: 440px; max-width: 100%; object-fit: contain; border: 1px solid var(--gdg-line); border-radius: 8px;">
    <p style="margin: 10px 0 0; font-size: 18px; font-weight: 700;">iPhone 1</p>
  </div>
  <div style="text-align: center;">
    <img src="../img/screenshot_02_iphone_desktop_mode_2.png" alt="iPhone Safari でデスクトップ用Webサイトを表示を選ぶ" style="height: 440px; max-width: 100%; object-fit: contain; border: 1px solid var(--gdg-line); border-radius: 8px;">
    <p style="margin: 10px 0 0; font-size: 18px; font-weight: 700;">iPhone 2</p>
  </div>
  <div style="text-align: center;">
    <img src="../img/screenshot_02_iphone_desktop_mode_3.png" alt="iPhone Safari でデスクトップ表示になった状態" style="height: 440px; max-width: 100%; object-fit: contain; border: 1px solid var(--gdg-line); border-radius: 8px;">
    <p style="margin: 10px 0 0; font-size: 18px; font-weight: 700;">iPhone 3</p>
  </div>
</div>

<p class="note">スマートフォンでは、ブラウザのメニューからデスクトップ用サイトを表示します</p>

---

## ここで止まったら

| 症状 | よくある原因 | 対応 |
| --- | --- | --- |
| プロジェクトが見えない | メール未登録 / 別アカウント | アカウントを切り替える、またはメンターに相談 |
| 権限エラー | IAM 反映待ち | 画面を見せて確認 |
| Lyria 3 Pro が見えない | UI 更新 / 選択欄の見落とし | ページを再読み込みして確認 |

---

![bg right:64% fit](../img/step4-first-prompt.svg)

## 最初の曲を作る

まずは細かく考えず、1 回生成します

```text
Energetic electronic dance music with bright synth leads,
punchy drums, and a cheerful festival atmosphere.
Clean mix, upbeat rhythm.
```

<p class="note">結果が想像と違っても OK。ここから調整します</p>

---

## プロンプト入力欄に貼り付ける

<div style="text-align: center;">
  <img src="../img/screenshot_03_input_prompt_to_media_studio.png" alt="Media Studio のプロンプト入力欄にテキストを入力する" style="height: 520px; max-width: 100%; object-fit: contain; border: 1px solid var(--gdg-line); border-radius: 8px;">
</div>

---

## 生成された曲を再生する

<div style="text-align: center;">
  <img src="../img/screenshot_04_tap_play_button.png" alt="生成された曲の再生ボタンを押す" style="height: 520px; max-width: 100%; object-fit: contain; border: 1px solid var(--gdg-line); border-radius: 8px;">
</div>

---

## 聴いたら、3 つだけ言葉にします

<div class="container" style="align-items: center; gap: 46px;">

<div class="col" style="flex: 0 0 36%;">

再生して、次の観点でメモします

- 明るい / 暗い
- 速い / ゆっくり
- どんな楽器が目立つか

<p class="note">音楽経験は不要です。聴こえたまま言葉にします</p>

</div>

<div class="col" style="flex: 1 1 64%;">

<svg viewBox="0 0 780 430" style="width: 100%; height: 430px;" role="img" aria-label="聴き比べの観点">
  <rect x="70" y="70" width="180" height="260" rx="18" fill="#E8F0FE" stroke="#4285F4" stroke-width="3"/>
  <text x="160" y="140" text-anchor="middle" font-size="28" font-weight="700">Mood</text>
  <text x="160" y="190" text-anchor="middle" font-size="22">明るい</text>
  <text x="160" y="225" text-anchor="middle" font-size="22">暗い</text>
  <text x="160" y="260" text-anchor="middle" font-size="22">緊張感</text>
  <rect x="300" y="70" width="180" height="260" rx="18" fill="#E6F4EA" stroke="#34A853" stroke-width="3"/>
  <text x="390" y="140" text-anchor="middle" font-size="28" font-weight="700">Tempo</text>
  <text x="390" y="190" text-anchor="middle" font-size="22">速い</text>
  <text x="390" y="225" text-anchor="middle" font-size="22">ゆっくり</text>
  <text x="390" y="260" text-anchor="middle" font-size="22">一定 / 変化</text>
  <rect x="530" y="70" width="180" height="260" rx="18" fill="#FEF7E0" stroke="#FBBC04" stroke-width="3"/>
  <text x="620" y="140" text-anchor="middle" font-size="28" font-weight="700">Sound</text>
  <text x="620" y="190" text-anchor="middle" font-size="22">シンセ</text>
  <text x="620" y="225" text-anchor="middle" font-size="22">ピアノ</text>
  <text x="620" y="260" text-anchor="middle" font-size="22">ドラム</text>
</svg>

</div>

</div>

---

![bg fit](../img/step5-prompt-recipe.svg)

---

## プロンプトは「制作指示書」

短い感想より、音として変えたい要素を書きます

```text
Modern city pop with nostalgic 80s synth textures.
Mood: bright, nostalgic, and relaxed.
Instruments: warm electric piano, slap bass, clean guitar,
and disco-inspired drums.
Tempo: upbeat, around 115 BPM.
Structure: short intro, catchy main section, gentle outro.
Production: clean mix with soft reverb.
```

---

## 何を書くと変わりやすいか

<div class="container" style="align-items: center; gap: 38px;">

<div class="col" style="flex: 0 0 34%;">

- **Genre**: 曲全体の方向性
- **Mood**: 明るさや緊張感
- **Instruments**: 目立つ音色
- **Tempo**: ノリや速さ
- **Structure**: 展開
- **Production**: 音の質感

</div>

<div class="col" style="flex: 1 1 66%;">

<svg viewBox="0 0 820 430" style="width: 100%; height: 430px;" role="img" aria-label="プロンプト要素のミキサー">
  <rect x="40" y="50" width="740" height="300" rx="18" fill="#FFFFFF" stroke="#DADCE0" stroke-width="3"/>
  <text x="410" y="102" text-anchor="middle" font-size="28" font-weight="700">Prompt Mixer</text>
  <g font-size="18" font-weight="700">
    <text x="105" y="330" text-anchor="middle">Genre</text>
    <text x="225" y="330" text-anchor="middle">Mood</text>
    <text x="345" y="330" text-anchor="middle">Inst.</text>
    <text x="465" y="330" text-anchor="middle">Tempo</text>
    <text x="585" y="330" text-anchor="middle">Structure</text>
    <text x="705" y="330" text-anchor="middle">Mix</text>
  </g>
  <g stroke-width="10" stroke-linecap="round">
    <line x1="105" y1="145" x2="105" y2="270" stroke="#DADCE0"/>
    <line x1="105" y1="205" x2="105" y2="270" stroke="#4285F4"/>
    <circle cx="105" cy="205" r="16" fill="#4285F4"/>
    <line x1="225" y1="145" x2="225" y2="270" stroke="#DADCE0"/>
    <line x1="225" y1="180" x2="225" y2="270" stroke="#34A853"/>
    <circle cx="225" cy="180" r="16" fill="#34A853"/>
    <line x1="345" y1="145" x2="345" y2="270" stroke="#DADCE0"/>
    <line x1="345" y1="225" x2="345" y2="270" stroke="#FBBC04"/>
    <circle cx="345" cy="225" r="16" fill="#FBBC04"/>
    <line x1="465" y1="145" x2="465" y2="270" stroke="#DADCE0"/>
    <line x1="465" y1="170" x2="465" y2="270" stroke="#EA4335"/>
    <circle cx="465" cy="170" r="16" fill="#EA4335"/>
    <line x1="585" y1="145" x2="585" y2="270" stroke="#DADCE0"/>
    <line x1="585" y1="240" x2="585" y2="270" stroke="#4285F4"/>
    <circle cx="585" cy="240" r="16" fill="#4285F4"/>
    <line x1="705" y1="145" x2="705" y2="270" stroke="#DADCE0"/>
    <line x1="705" y1="195" x2="705" y2="270" stroke="#34A853"/>
    <circle cx="705" cy="195" r="16" fill="#34A853"/>
  </g>
</svg>

</div>

</div>

<footer>出典: Google Cloud Lyria prompt guide</footer>

---

## Negative prompt で避けたい要素を書く

<div class="container" style="align-items: center; gap: 42px;">

<div class="col" style="flex: 0 0 38%;">

入れてほしくないものを短く指定します

```text
harsh noise,
aggressive distortion,
sudden volume changes
```

<p class="note">「何を避けたいか」を明確にします</p>

</div>

<div class="col" style="flex: 1 1 62%;">

<svg viewBox="0 0 780 430" style="width: 100%; height: 430px;" role="img" aria-label="Negative prompt の使い方">
  <defs>
    <marker id="arrow-neg" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">
      <path d="M2,2 L10,6 L2,10 Z" fill="#3c4043"/>
    </marker>
  </defs>
  <rect x="50" y="80" width="210" height="220" rx="18" fill="#E8F0FE" stroke="#4285F4" stroke-width="3"/>
  <text x="155" y="140" text-anchor="middle" font-size="24" font-weight="700">欲しい音</text>
  <text x="155" y="190" text-anchor="middle" font-size="20">relaxed piano</text>
  <text x="155" y="225" text-anchor="middle" font-size="20">soft drums</text>
  <text x="155" y="260" text-anchor="middle" font-size="20">clean mix</text>
  <line x1="276" y1="190" x2="363" y2="190" stroke="#3c4043" stroke-width="4" marker-end="url(#arrow-neg)"/>
  <rect x="380" y="80" width="210" height="220" rx="18" fill="#FCE8E6" stroke="#EA4335" stroke-width="3"/>
  <text x="485" y="140" text-anchor="middle" font-size="24" font-weight="700">避けたい音</text>
  <text x="485" y="190" text-anchor="middle" font-size="20">noise</text>
  <text x="485" y="225" text-anchor="middle" font-size="20">distortion</text>
  <text x="485" y="260" text-anchor="middle" font-size="20">sudden changes</text>
  <circle cx="655" cy="190" r="62" fill="#E6F4EA" stroke="#34A853" stroke-width="4"/>
  <text x="655" y="182" text-anchor="middle" font-size="24" font-weight="700">生成</text>
  <text x="655" y="216" text-anchor="middle" font-size="18">方向を絞る</text>
</svg>

</div>

</div>

<footer>出典: Google Cloud Lyria prompt guide</footer>

---

<!-- _class: section yellow -->

# 03. 画像から音楽へ

---

![bg right:64% fit](../img/step6-image-to-music.svg)

## 画像を 1 枚選ぶ

画像は、言葉にしづらい雰囲気を伝える材料です

- 色、明暗、構図、季節感
- 場所や時間帯
- 静けさ、熱量、空気感

<p class="note">テキストでは、ジャンルや楽器など画像だけでは分からない指示を補います</p>

---

## サンプル画像から選んでも OK

<div class="image-row">
  <figure>
    <img src="../img/sample-jazz.png" alt="ジャズクラブのサンプル画像">
    <figcaption>Jazz / 小さなクラブ</figcaption>
  </figure>
  <figure>
    <img src="../img/sample-orchestra.png" alt="オーケストラホールのサンプル画像">
    <figcaption>Orchestra / ホール</figcaption>
  </figure>
  <figure>
    <img src="../img/sample-sea.png" alt="朝の海辺のサンプル画像">
    <figcaption>Sea / 朝の海</figcaption>
  </figure>
</div>

<p class="note">手元に画像がない人は、コードラボからサンプル画像をダウンロードして使います</p>

---

## 画像を追加する

<div style="text-align: center;">
  <img src="../img/screenshot_05_add_image.png" alt="Media Studio に画像を追加する" style="height: 520px; max-width: 100%; object-fit: contain; border: 1px solid var(--gdg-line); border-radius: 8px;">
</div>

---

## 画像 + テキストの例

```text
Emotional future bass inspired by neon city nightlife.
Bright synth chords, soft vocal chops, deep bass,
and a hopeful mood.
```

画像が伝えるもの:

- ネオンの色、夜の雰囲気、街のスピード感

テキストで補うもの:

- ジャンル、楽器、テンポ、音の方向性

---

## 余裕がある人は試してみる

<div class="fit">

| 方向性 | Prompt |
| --- | --- |
| EDM | `Festival EDM with energetic synth leads, huge drops, punchy kick drums, and emotional chord progressions.` |
| Lo-fi | `Relaxed lo-fi hip hop with dusty vinyl texture, mellow piano, soft drums, and rainy night atmosphere.` |
| Cinematic | `Epic cinematic orchestral music with rising strings, deep percussion, and emotional brass swells.` |
| Anime opening | `Emotional anime opening theme with fast drums, bright guitars, uplifting energy, and a dramatic chorus.` |

聴き比べる時は、1 回に変える要素を 1〜2 個に絞ります

</div>

---

## 困ったときの戻り先

<div class="container" style="align-items: center; gap: 44px;">

<div class="col" style="flex: 0 0 36%;">

- まずページを再読み込みします
- アカウントとプロジェクトを確認します
- 生成が遅い時は少し待ちます
- 迷ったら短いプロンプトに戻します

</div>

<div class="col" style="flex: 1 1 64%;">

<svg viewBox="0 0 780 430" style="width: 100%; height: 430px;" role="img" aria-label="トラブル対応の流れ">
  <defs>
    <marker id="arrow-help" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">
      <path d="M2,2 L10,6 L2,10 Z" fill="#3c4043"/>
    </marker>
  </defs>
  <rect x="55" y="70" width="170" height="110" rx="14" fill="#E8F0FE" stroke="#4285F4" stroke-width="3"/>
  <text x="140" y="135" text-anchor="middle" font-size="23" font-weight="700">Reload</text>
  <line x1="238" y1="125" x2="320" y2="125" stroke="#3c4043" stroke-width="4" marker-end="url(#arrow-help)"/>
  <rect x="335" y="70" width="170" height="110" rx="14" fill="#E6F4EA" stroke="#34A853" stroke-width="3"/>
  <text x="420" y="135" text-anchor="middle" font-size="23" font-weight="700">Account</text>
  <line x1="518" y1="125" x2="600" y2="125" stroke="#3c4043" stroke-width="4" marker-end="url(#arrow-help)"/>
  <rect x="615" y="70" width="140" height="110" rx="14" fill="#FEF7E0" stroke="#FBBC04" stroke-width="3"/>
  <text x="685" y="135" text-anchor="middle" font-size="23" font-weight="700">Wait</text>
  <line x1="685" y1="194" x2="685" y2="263" stroke="#3c4043" stroke-width="4" marker-end="url(#arrow-help)"/>
  <rect x="540" y="280" width="215" height="110" rx="14" fill="#FCE8E6" stroke="#EA4335" stroke-width="3"/>
  <text x="648" y="345" text-anchor="middle" font-size="23" font-weight="700">Mentor に相談</text>
  <line x1="525" y1="335" x2="428" y2="335" stroke="#3c4043" stroke-width="4" marker-end="url(#arrow-help)"/>
  <rect x="220" y="280" width="190" height="110" rx="14" fill="#FFFFFF" stroke="#DADCE0" stroke-width="3"/>
  <text x="315" y="345" text-anchor="middle" font-size="23" font-weight="700">短く戻す</text>
</svg>

</div>

</div>

---

## 参加者の皆さんが作った音楽を流してみてください

<div class="container" style="align-items: center; gap: 42px;">

<div class="col" style="flex: 0 0 34%;">

時間があれば、会場で聴き比べます

- 1 人 20〜30 秒だけ再生します
- 使ったプロンプトを一言で紹介します
- 変えたところ、良かった音を共有します

<p class="note">完成度より、違いが聴こえることを楽しみます</p>

</div>

<div class="col" style="flex: 1 1 66%;">

<svg viewBox="0 0 820 430" style="width: 100%; height: 430px;" role="img" aria-label="参加者の音楽を会場で聴く流れ">
  <defs>
    <marker id="arrow-share" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">
      <path d="M2,2 L10,6 L2,10 Z" fill="#3c4043"/>
    </marker>
  </defs>
  <rect x="50" y="90" width="170" height="220" rx="22" fill="#E8F0FE" stroke="#4285F4" stroke-width="4"/>
  <circle cx="135" cy="150" r="34" fill="#4285F4"/>
  <text x="135" y="160" text-anchor="middle" font-size="30" fill="#fff" font-weight="700">1</text>
  <text x="135" y="225" text-anchor="middle" font-size="26" font-weight="700">Play</text>
  <text x="135" y="262" text-anchor="middle" font-size="20">20〜30 秒</text>
  <line x1="240" y1="200" x2="330" y2="200" stroke="#3c4043" stroke-width="5" marker-end="url(#arrow-share)"/>
  <rect x="350" y="90" width="170" height="220" rx="22" fill="#E6F4EA" stroke="#34A853" stroke-width="4"/>
  <circle cx="435" cy="150" r="34" fill="#34A853"/>
  <text x="435" y="160" text-anchor="middle" font-size="30" fill="#fff" font-weight="700">2</text>
  <text x="435" y="225" text-anchor="middle" font-size="26" font-weight="700">Prompt</text>
  <text x="435" y="262" text-anchor="middle" font-size="20">一言で紹介</text>
  <line x1="540" y1="200" x2="630" y2="200" stroke="#3c4043" stroke-width="5" marker-end="url(#arrow-share)"/>
  <rect x="650" y="90" width="140" height="220" rx="22" fill="#FEF7E0" stroke="#FBBC04" stroke-width="4"/>
  <circle cx="720" cy="150" r="34" fill="#FBBC04"/>
  <text x="720" y="160" text-anchor="middle" font-size="30" fill="#1A1A1A" font-weight="700">3</text>
  <text x="720" y="225" text-anchor="middle" font-size="26" font-weight="700">Share</text>
  <text x="720" y="262" text-anchor="middle" font-size="20">違いを聴く</text>
  <path d="M160 350 C260 385, 570 385, 700 350" fill="none" stroke="#EA4335" stroke-width="6" stroke-linecap="round"/>
  <text x="430" y="405" text-anchor="middle" font-size="26" font-weight="700">同じモデルでも、言葉と画像で音が変わる</text>
</svg>

</div>

</div>

---

## 今日のまとめ

<div class="container" style="align-items: center; gap: 42px;">

<div class="col" style="flex: 0 0 38%;">

この 3 つができれば OK!

- Media Studio で Lyria 3 Pro を選べる
- 英語プロンプトから曲を生成できる
- ジャンル、楽器、テンポ、画像で方向性を変えられる

</div>

<div class="col" style="flex: 1 1 62%;">

<svg viewBox="0 0 780 430" style="width: 100%; height: 430px;" role="img" aria-label="学んだことのまとめ">
  <circle cx="180" cy="215" r="115" fill="#E8F0FE" stroke="#4285F4" stroke-width="4"/>
  <text x="180" y="200" text-anchor="middle" font-size="26" font-weight="700">Open</text>
  <text x="180" y="238" text-anchor="middle" font-size="19">Media Studio</text>
  <circle cx="390" cy="215" r="115" fill="#E6F4EA" stroke="#34A853" stroke-width="4"/>
  <text x="390" y="200" text-anchor="middle" font-size="26" font-weight="700">Prompt</text>
  <text x="390" y="238" text-anchor="middle" font-size="19">指示書にする</text>
  <circle cx="600" cy="215" r="115" fill="#FEF7E0" stroke="#FBBC04" stroke-width="4"/>
  <text x="600" y="200" text-anchor="middle" font-size="26" font-weight="700">Listen</text>
  <text x="600" y="238" text-anchor="middle" font-size="19">聴き比べる</text>
</svg>

</div>

</div>

---

## 次のステップ

- Lyria のプロンプトガイドを読んで、指定できる要素を増やします
- Gemini API / Vertex AI のドキュメントで API 利用を試します
- 生成結果は用途に合わせて確認し、必要なら作り直します

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 30px;">
  <div style="padding: 20px; border-top: 4px solid var(--gdg-blue); background: #fff; border-radius: 8px;">
    <h3 style="margin-top: 0;">Prompt</h3>
    <p>ジャンル、ムード、楽器、テンポを足す</p>
  </div>
  <div style="padding: 20px; border-top: 4px solid var(--gdg-green); background: #fff; border-radius: 8px;">
    <h3 style="margin-top: 0;">Image</h3>
    <p>写真から雰囲気を借りる</p>
  </div>
  <div style="padding: 20px; border-top: 4px solid var(--gdg-yellow); background: #fff; border-radius: 8px;">
    <h3 style="margin-top: 0;">API</h3>
    <p>アプリや制作ツールに組み込む</p>
  </div>
</div>

---

## 参考リンク

<div class="fit">

- [Google Cloud: Lyria | AI 音楽生成ツール](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/music/generate-music?hl=ja)
- [Google Cloud: Lyria 音楽生成プロンプトガイド](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/music/music-gen-prompt-guide?hl=ja)
- [Google Cloud: Lyria API](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/model-reference/lyria-music-generation?hl=ja)
- [Google AI Developers: Generate music with Lyria 3](https://ai.google.dev/gemini-api/docs/music-generation)
- [Google Blog: Lyria 3 Pro](https://blog.google/innovation-and-ai/technology/ai/lyria-3-pro/)
- [Google DeepMind: Lyria 3](https://deepmind.google/models/lyria/)
- [Suno Help: Studio](https://help.suno.com/en/articles/7940161)
- [Suno Help: Model timeline](https://help.suno.com/en/articles/5782721)

<p class="note">2026-05-23 時点の公式情報をもとに作成しています</p>

</div>

---

<!-- _class: lead -->

# Thank you!

Questions?
