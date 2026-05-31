---
marp: true
theme: gdg
paginate: true
size: 16:9
title: ADK x A2A x Agent Runtime で作るマルチエージェント AI
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

.kicker {
  color: var(--gdg-blue);
  font-weight: 700;
  letter-spacing: 0;
}

.big {
  font-size: 2.15em;
  line-height: 1.08;
  font-weight: 780;
}

.caption {
  color: #5f6368;
  font-size: .78em;
}

.flow {
  display: flex;
  align-items: stretch;
  justify-content: center;
  gap: 18px;
  margin-top: 28px;
}

.flow .node {
  flex: 1;
  padding: 22px 18px;
  border: 3px solid var(--gdg-blue);
  border-radius: 8px;
  background: #fff;
  font-size: 1.05em;
  font-weight: 700;
  text-align: center;
}

.flow .arrow {
  align-self: center;
  color: var(--gdg-blue);
  font-size: 2.2em;
  font-weight: 800;
}

.chip-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  margin-top: 22px;
}

.chip-grid.two { grid-template-columns: repeat(2, 1fr); }
.chip-grid.four { grid-template-columns: repeat(4, 1fr); }

.chip {
  min-height: 64px;
  padding: 14px 16px;
  border-left: 6px solid var(--gdg-blue);
  border-radius: 8px;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  font-weight: 650;
  line-height: 1.28;
}

.chip.green { border-color: var(--gdg-green); }
.chip.yellow { border-color: var(--gdg-yellow); }
.chip.red { border-color: var(--gdg-red); }
.chip.small { font-size: .82em; min-height: 48px; padding: 10px 12px; }

.matrix {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-top: 26px;
}

.matrix .cell {
  padding: 18px;
  border-top: 5px solid var(--gdg-blue);
  border-radius: 8px;
  background: #f8f9fa;
  min-height: 150px;
}

.matrix .cell h3 {
  margin: 0 0 10px 0;
  font-size: 1.05em;
}

.matrix .cell p {
  margin: 0;
  font-size: .78em;
  line-height: 1.35;
}

.state-map {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
  margin-top: 22px;
}

.state-map div {
  border: 2px solid #dadce0;
  border-radius: 8px;
  padding: 12px;
  font-size: .78em;
  font-weight: 650;
  background: #fff;
}

.title h1 {
  font-size: 2.5em;
  line-height: 1.08;
  max-width: 700px;
}
</style>

<!-- _class: title -->
<!-- _paginate: false -->

![bg right:40% contain](img/codelab_ogp.png)

<h1 style="font-size: 2.5em; line-height: 1.08; max-width: 700px;">
ADK x A2A x<br>Agent Runtime で作る<br><strong>マルチエージェント AI</strong>
</h1>

GDG on Campus University of Osaka

---

<!-- _class: lead -->

# 1 つの巨大 prompt から<br>**分割して動く Workflow** へ

---

## このコードラボの着地点

<div class="big">旅行計画 AI が、候補探しから旅しおり画像まで進めます</div>

<div class="flow">
  <div class="node">このコードラボで作るもの</div>
  <div class="arrow">→</div>
  <div class="node">このコードラボで学ぶこと</div>
  <div class="arrow">→</div>
  <div class="node">必要なもの</div>
</div>

<div class="chip-grid two">
  <div class="chip green">前提知識</div>
  <div class="chip red">このコードラボで扱わないこと</div>
</div>

---

<!-- _class: section -->

# 01. 全体アーキテクチャ

---

<!-- _class: split -->

## Coordinator Workflow の流れを確認する

![w:560](img/step2-coordinator-workflow-architecture.png)

<div class="big">入力を構造化し、候補、評価、選択、旅程、画像へ渡します</div>

---

## session.state に保存するデータを確認する

<div class="state-map">
  <div>raw_user_query</div>
  <div>travel_request</div>
  <div>clarification_rounds</div>
  <div>travel_options</div>
  <div>research_reports</div>
  <div>coordinator_recommendation</div>
  <div>selected_option_id</div>
  <div>selected_option_context</div>
  <div>itinerary_markdown</div>
  <div>illustrator_prompt</div>
</div>

<p class="caption">planner には選ばれた候補だけを渡し、情報の混線を減らします</p>

---

<!-- _class: section yellow -->

# 02. セットアップ

---

## セットアップの 5 ステップ

<div class="flow">
  <div class="node">セットアップフォームに回答する</div>
  <div class="arrow">→</div>
  <div class="node">Google Cloud Shell を開く</div>
  <div class="arrow">→</div>
  <div class="node">setup script を実行する</div>
  <div class="arrow">→</div>
  <div class="node">環境変数を設定する</div>
  <div class="arrow">→</div>
  <div class="node">ADK を import できることを確認する</div>
</div>

<div class="big" style="margin-top: 34px;">Cloud Shell で同じ環境から始めます</div>

<div class="chip-grid two">
  <div class="chip small red">二段階認証が必要な方へ</div>
</div>

---

<!-- _class: section green -->

# 03. ADK の考え方

---

<!-- _class: split -->

## グラフベースのワークフロー

![w:540](img/step3-adk-graph-workflow-design.png)

<div class="chip-grid two">
  <div class="chip small">ルートシーケンス</div>
  <div class="chip small green">ルート分岐と条件付き実行</div>
  <div class="chip small yellow">並列タスク: fan out と join</div>
  <div class="chip small red">ネストされたワークフロー</div>
</div>

---

## Workflow の制御パターン

<div class="matrix">
  <div class="cell"><h3>データの受け渡し</h3><p>node 間の成果物を state に残します</p></div>
  <div class="cell"><h3>Dynamic workflow</h3><p>入力や状態で次の処理を変えます</p></div>
  <div class="cell"><h3>Collaborative workflow</h3><p>人と agent が交互に進めます</p></div>
  <div class="cell"><h3>Human input</h3><p>足りない情報を人に聞きます</p></div>
</div>

<div class="chip-grid two">
  <div class="chip small">モード設定</div>
  <div class="chip small green">Session、State、Memory</div>
</div>

---

<!-- _class: split -->

## Session、State、Memory

![w:520](img/step3-adk-session-state-memory.png)

<div class="chip-grid">
  <div class="chip small">Session: 現在の会話スレッド</div>
  <div class="chip small green">State (`session.state`): 現在の会話内のデータ</div>
  <div class="chip small yellow">Memory: session をまたいで検索できる情報</div>
</div>

---

<!-- _class: section red -->

# 04. A2A

---

<!-- _class: split -->

## A2A とは

![w:520](img/step4-a2a-actors.png)

<div class="big">別プロセスの specialist agent を、Agent Card 経由で呼び出します</div>

---

## Why Use the A2A Protocol

<div class="chip-grid two">
  <div class="chip">Problems that A2A Solves</div>
  <div class="chip green">A2A Example Scenario</div>
  <div class="chip yellow">Core Benefits of A2A</div>
  <div class="chip red">A2A とローカル sub-agent の使い分け</div>
  <div class="chip">Core Concepts in A2A</div>
  <div class="chip green">Agent Discovery と security</div>
</div>

---

<!-- _class: split -->

## A2A Request Lifecycle

![w:560](img/step4-a2a-request-lifecycle.png)

<div class="big">discover → auth → message → stream</div>

---

<!-- _class: section -->

# 05. Gemini Enterprise Agent Platform

---

<!-- _class: split -->

## Gemini Enterprise Agent Platform とは

![w:560](img/geap.svg)

<div class="big">Build / Scale / Govern / Optimize を 1 つの面で扱います</div>

---

## エージェントを構築する（Agents - Build）

<div class="chip-grid">
  <div class="chip">ADK と Agent Studio</div>
  <div class="chip green">データ、ツール、エージェント間連携</div>
  <div class="chip yellow">このリポジトリで実装するもの</div>
</div>

<div class="big" style="margin-top: 34px;">実装する場所を先にそろえます</div>

---

## エージェントを本番運用に載せる（Agents - Scale）

<div class="chip-grid">
  <div class="chip">Agent Runtime</div>
  <div class="chip green">Sessions と Memory Bank</div>
  <div class="chip yellow">このコードラボでのデプロイ順序</div>
</div>

---

## エージェントを統制する（Agents - Govern）

<div class="chip-grid two">
  <div class="chip red">Agent Registry と Agent Gateway</div>
  <div class="chip">Identity、Policy、Security</div>
</div>

<div class="big" style="margin-top: 34px;">誰が、何を、どの agent に許すか</div>

---

## エージェントを改善する（Agents - Optimize）

<div class="chip-grid two">
  <div class="chip green">Observability</div>
  <div class="chip yellow">Evaluation と Example Store</div>
</div>

<div class="big" style="margin-top: 34px;">動かして終わりではなく、測って直します</div>

---

<!-- _class: section green -->

# 06. Coordinator を実装する

---

## Clarify Agent を実装する

<div class="flow">
  <div class="node">clarify_models.py を作成する</div>
  <div class="arrow">→</div>
  <div class="node">clarify.py を作成する</div>
  <div class="arrow">→</div>
  <div class="node">agent.py を最小 Workflow に更新する</div>
  <div class="arrow">→</div>
  <div class="node">Clarify Agent の動作を確認する</div>
</div>

---

## Strategist と Research の Fan-out / Fan-in を実装する

<div class="flow">
  <div class="node">candidates_models.py を作成する</div>
  <div class="arrow">→</div>
  <div class="node">candidates.py を作成する</div>
  <div class="arrow">→</div>
  <div class="node">candidate_workflow を agent.py に追加する</div>
</div>

<div class="chip-grid two">
  <div class="chip small green">How grounding with Google Search works</div>
  <div class="chip small yellow">research_reports が state に保存されることを確認する</div>
</div>

---

<!-- _class: split -->

## Grounding のデータフロー

![w:560](img/google_search_grd_dataflow.png)

<div class="big">候補ごとに検索し、結果を fan-in して評価へ渡します</div>

---

<!-- _class: section red -->

# 07. A2A Specialist

---

## Specialist Agents を A2A サービスとして実装する

<div class="chip-grid">
  <div class="chip">comfort_agent を作成する</div>
  <div class="chip green">risk_agent を作成する</div>
  <div class="chip yellow">experience_agent を作成する</div>
  <div class="chip red">Specialist Agents の Agent Card を確認する</div>
  <div class="chip">Specialist Agents の動作を確認する</div>
</div>

---

## Multi-Agent Evaluation を実装する

<div class="flow">
  <div class="node">evaluation_models.py を作成する</div>
  <div class="arrow">→</div>
  <div class="node">RemoteA2aAgent を定義する</div>
  <div class="arrow">→</div>
  <div class="node">evaluation_agent を作成する</div>
</div>

<div class="chip-grid two">
  <div class="chip small yellow">evaluation フェーズを candidate_workflow に追加する</div>
  <div class="chip small green">coordinator_recommendation が state に保存されることを確認する</div>
</div>

---

<!-- _class: section yellow -->

# 08. 選択、旅程、画像生成

---

## User Selection と Replan 分岐を実装する

<div class="chip-grid two">
  <div class="chip">planner_models.py を作成する</div>
  <div class="chip green">planner.py に選択提示ノードを作成する</div>
  <div class="chip yellow">route_user_selection を実装する</div>
  <div class="chip red">build_replan_input を実装する</div>
  <div class="chip">agent.py に選択と再提案の分岐を追加する</div>
  <div class="chip green">上位 3 案の提示と再提案ループを確認する</div>
</div>

---

## Planner で詳細旅程を生成する

<div class="flow">
  <div class="node">SelectedOptionContext を追加する</div>
  <div class="arrow">→</div>
  <div class="node">build_planner_input を実装する</div>
  <div class="arrow">→</div>
  <div class="node">store_itinerary_markdown を実装する</div>
</div>

<div class="chip-grid two">
  <div class="chip small yellow">planner フェーズを agent.py に追加する</div>
  <div class="chip small green">itinerary_markdown が state に保存されることを確認する</div>
</div>

---

## Illustrator で旅しおり画像を生成する

<div class="chip-grid">
  <div class="chip">illustrator.py を作成する</div>
  <div class="chip green">illustrator_prompt_agent を作成する</div>
  <div class="chip yellow">illustrator_agent を作成する</div>
  <div class="chip red">illustrator フェーズを agent.py に追加する</div>
  <div class="chip">旅しおり画像が生成されることを確認する</div>
</div>

---

<!-- _class: section -->

# 09. 実行とデプロイ

---

## ローカルで完成したマルチエージェントを実行する

<div class="chip-grid two">
  <div class="chip">全テストを実行する</div>
  <div class="chip green">Specialist、Coordinator、ADK Web を起動する</div>
  <div class="chip yellow">明確な依頼を送る</div>
  <div class="chip red">情報不足の依頼を送る</div>
  <div class="chip">再提案を試す</div>
  <div class="chip green">ADK Web の Inspector で state を確認する</div>
</div>

---

## Agent Runtime にデプロイする

<div class="flow">
  <div class="node">Google Cloud 認証を確認する</div>
  <div class="arrow">→</div>
  <div class="node">deploy_all.sh を実行する</div>
  <div class="arrow">→</div>
  <div class="node">Runtime A2A URL を確認する</div>
  <div class="arrow">→</div>
  <div class="node">Runtime 上の Agent Card を確認する</div>
</div>

---

<!-- _class: section green -->

# 10. Team Challenge

---

## Team Challenge: Specialist Agent を改善する

<div class="chip-grid">
  <div class="chip">改善方針を決める</div>
  <div class="chip green">specialist 用 tool を確認する</div>
  <div class="chip yellow">agent に tool を追加する</div>
  <div class="chip red">新しい specialist を追加する</div>
  <div class="chip">改善結果を確認する</div>
</div>

---

## Team Challenge: Specialist Agent を差し替える

<div class="chip-grid">
  <div class="chip red">specialist をデプロイする</div>
  <div class="chip">他のメンバーの specialist に切り替える</div>
  <div class="chip green">Runtime が使えない場合</div>
</div>

---

## Team Challenge: Illustrator の出力品質を改善する

<div class="chip-grid">
  <div class="chip yellow">改善観点を決める</div>
  <div class="chip">prompt format を改善する</div>
  <div class="chip green">画像を比較する</div>
</div>

---

<!-- _class: section red -->

# 11. 困ったとき

---

## トラブルシューティング

<div class="chip-grid">
  <div class="chip red">google_search と structured output が両立しない場合</div>
  <div class="chip">specialist に connection refused が出る場合</div>
  <div class="chip green">research_reports に option が欠ける場合</div>
  <div class="chip yellow">clarification が繰り返される場合</div>
  <div class="chip red">planner が全候補の情報を混ぜる場合</div>
</div>

---

## 成果発表と評価

<div class="chip-grid">
  <div class="chip">発表する内容</div>
  <div class="chip green">評価観点</div>
  <div class="chip yellow">ふりかえり</div>
</div>

<div class="big" style="margin-top: 34px;">チームごとに設計判断と改善結果を共有します</div>

---

## おめでとうございます！

<div class="chip-grid">
  <div class="chip green">学んだこと</div>
  <div class="chip yellow">クリーンアップ</div>
  <div class="chip">次のステップ</div>
</div>

<div class="big" style="margin-top: 34px;">ここから自分の agent に育てていきましょう!</div>

---

<!-- _class: section yellow -->

# 12. Extra

---

## Extra: 画像生成プロンプトを改善する

<div class="chip-grid">
  <div class="chip">改善する観点を決める</div>
  <div class="chip green">illustrator_prompts.py を更新する</div>
  <div class="chip yellow">illustrator.py の instruction を更新する</div>
  <div class="chip red">画像を比較する</div>
  <div class="chip">うまくいかない場合</div>
</div>

---

## Extra: Memory Bank でパーソナライズする

<div class="fit">

<div class="chip-grid two">
  <div class="chip small">追加する構成を確認する</div>
  <div class="chip small green">memory.py を作成する</div>
  <div class="chip small yellow">clarify_agent に Memory を接続する</div>
  <div class="chip small red">strategist_agent に Memory を接続する</div>
  <div class="chip small">planner_agent に Memory を接続する</div>
  <div class="chip small green">Makefile に Memory 起動ターゲットを追加する</div>
  <div class="chip small yellow">.env.example に設定を追加する</div>
  <div class="chip small red">Memory を有効にして起動する</div>
  <div class="chip small">動作を確認する</div>
  <div class="chip small green">うまくいかない場合</div>
</div>

</div>

---

## Extra: Evaluation と User Simulation を追加する

<div class="fit">

<div class="chip-grid two">
  <div class="chip small">評価したいことを決める</div>
  <div class="chip small green">evals ディレクトリを作成する</div>
  <div class="chip small yellow">travel_scenarios.json を作成する</div>
  <div class="chip small red">session_input.json を作成する</div>
  <div class="chip small">eval_config.json を作成する</div>
  <div class="chip small green">Makefile に eval ターゲットを追加する</div>
  <div class="chip small yellow">EvalSet を作成する</div>
  <div class="chip small red">User Simulation から eval case を追加する</div>
  <div class="chip small">評価を実行する</div>
  <div class="chip small green">評価を増やす</div>
</div>

</div>

---

## Extra: AgentMail で旅行プランをメール送信する

<div class="fit">

<div class="chip-grid two">
  <div class="chip small">追加する構成を確認する</div>
  <div class="chip small green">pyproject.toml に mcp を追加する</div>
  <div class="chip small yellow">agentmail.py を作成する</div>
  <div class="chip small red">illustrator_prompt を state に保存する</div>
  <div class="chip small">agent.py に AgentMail node を接続する</div>
  <div class="chip small green">.env.example に設定を追加する</div>
  <div class="chip small yellow">AgentMail tool が読み込まれることを確認する</div>
  <div class="chip small red">メール送信を試す</div>
  <div class="chip small">うまくいかない場合</div>
</div>

</div>

---

## Extra: AG-UI でフロントエンドから呼び出す

<div class="chip-grid two">
  <div class="chip small">AG-UI endpoint の役割を確認する</div>
  <div class="chip small green">ag_ui_app.py を作成する</div>
  <div class="chip small yellow">Makefile の run-ag-ui を確認する</div>
  <div class="chip small red">AG-UI server を起動する</div>
  <div class="chip small">userId の扱いを確認する</div>
  <div class="chip small green">Memory extra と組み合わせる</div>
  <div class="chip small yellow">うまくいかない場合</div>
</div>

---

<!-- _class: lead -->

# Thank you!

Questions?
