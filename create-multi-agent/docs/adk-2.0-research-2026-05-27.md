# Agent Development Kit 2.0 調査メモ

調査日: 2026-05-27 JST  
対象: Google Agent Development Kit (ADK) 2.0、Graph-based agent workflows、指定 codelab、Google Cloud / Google Developers 公式ブログ、ユーザー記事

## 要点

- 2026-05-27 時点の公式 ADK docs では、ADK Python 2.0.0 は 2026-05-19 に GA とされている。検索結果や一部ユーザー記事には Alpha/Beta と書かれた古い情報が残っているため、状態確認は公式 docs / PyPI を優先する。
- ADK 2.0 の中心は Workflow Runtime。従来の階層型 agent executor から、Agents / Tools / Functions を workflow graph の node として評価する実行エンジンに移った。
- 2.0 の主要機能は Graph-based workflows、Dynamic workflows、Collaborative workflows。いずれも「LLM に手順を守らせる」より「コードで制御構造を持つ」方向へ寄っている。
- 指定 codelab は ADK 2.0 専用ではなく、ADK の multi-agent、Vertex AI Agent Engine / Agent Runtime、A2A の実践導入として有用。2.0 の graph workflow 概念は公式 ADK docs 側で補う必要がある。
- Google Cloud 側の資料では、ADK は Gemini / Vertex AI / Agent Runtime / Cloud Run / GKE / BigQuery / MCP / A2A と接続する開発フレームワークとして位置づけられている。
- ユーザー記事は 2.0 の理解補助には使えるが、Alpha/Beta 表記、インストール方法、対応言語、production readiness は古い記述が混在する。

## 公式情報で確認した ADK 2.0 の現在地

公式 ADK docs の ADK 2.0 ページは、ADK Python 2.0.0 GA release として 2026-05-19 を明記している。2.0 の新機能として次を挙げている。

- Graph-based workflows: タスクの routing と execution をより明示的に制御する deterministic workflow。
- Dynamic workflows: 反復ループや複雑な条件分岐を Python コードで表現する workflow。
- Collaborative workflows: coordinator agent と複数 subagent による複雑な agent architecture。

参照:

- [Welcome to ADK 2.0](https://adk.dev/2.0/)
- [google-adk on PyPI](https://pypi.org/project/google-adk/)
- [ADK release notes](https://adk.dev/release-notes/)

### 1.x から 2.0 への破壊的変更

公式 docs の互換性セクションで重要なのは次。

- Event schema に `node_info` と `output` が追加される。独自 `BaseSessionService` や厳格な JSON schema validation を持つ downstream client は更新が必要。
- `BaseAgent` は `BaseNode` の subclass になり、Agents は Workflow Graph engine 内の node として評価される。1.x で `_run_async_impl()` や `generate_content()` の override に execution logic / telemetry を入れていた場合、2.0 では workflow engine に bypass される可能性がある。
- session events へ手動で append する実装は避ける。2.0 では event emission を workflow runner が管理する。
- 例外を広く catch すると、2.0 の automatic retry や HITL pause を妨げる。tool 内の broad `except Exception:` や `BaseException` catch は再検討が必要。

参照: [Welcome to ADK 2.0 - compatibility](https://adk.dev/2.0/)

## Graph-based agent workflows

Graph-based workflow は、process workflow を code 上の graph として定義する仕組み。各 step は execution Node で、node は Agent、Tool、関数、human input、別 Workflow になれる。

保存画像:

- `images/adk-graph-workflow-design.svg`: graph workflow の基本設計図
- `images/adk-prompts-to-graphs.svg`: prompt-based 手順を graph に分解する図
- `images/adk-graph-router.svg`: routing workflow の図
- `images/adk-graph-joinnode.svg`: parallel task の join 図
- `images/adk-nested-workflows.svg`: nested workflow 図

### Workflow / edges / START

公式例では `Workflow(name=..., edges=[...])` で graph を作る。`START` から node を並べると sequential workflow になり、複数の `START` row を持つと並列開始になる。

Graph-based approach の利点:

- Routing logic を明示的に map できる。
- Branching と state management を workflow に含められる。
- 生成 AI を呼ばずに関数や Tool を chain できる。
- prompt だけに頼るより予測可能性が高い。

参照:

- [Graph-based agent workflows](https://adk.dev/graphs/)
- [Build graph routes for agent workflows](https://adk.dev/graphs/routes/)

### Node

Workflow graph の node は Event を consume / emit する。Function node は通常の関数として書けるが、出力は `Event(output=...)`、user-facing response は `Event(message=...)`、永続化したい値は `Event(state=...)` を使う。

重要な制約:

- `Event.output` は node execution あたり 1 payload のみ。
- `message` はユーザーへ出す情報やユーザー入力依頼に使う。node 間データ渡しの標準には `output` を使う。
- schema を使って node input/output を構造化できる。

参照: [Data handling for agent workflows](https://adk.dev/graphs/data-handling/)

### Branch / router

Branching は、通常 FunctionNode が route value を含む `Event(route=...)` を返し、`edges` の後続 row で route value と target node を map する。

この点は LangGraph と近い見た目になるが、ADK では Agent / Tool / Function / Workflow が Google ADK runtime の Event / Session / Tool ecosystem と直接つながる。

参照: [Graph routes - Route branches and conditional execution](https://adk.dev/graphs/routes/)

### Parallel / JoinNode

並列実行は複数 path を fan out し、`JoinNode` で upstream node の output を待って集約する。公式 docs は、upstream node のどれかが output を出さないと JoinNode が進まず workflow execution が止まるため、failsafe output を入れるよう注意している。

参照: [Graph routes - Parallel tasks](https://adk.dev/graphs/routes/)

### Nested Workflow

複雑な処理は `Workflow` 自体を parent workflow の node にできる。Nested workflow は最後の leaf node の output を parent へ bubble up する。再利用可能な workflow 部品として切り出せる点が重要。

参照: [Graph routes - Nested workflows](https://adk.dev/graphs/routes/)

### Graph workflow の制限

公式 docs は graph-based workflows が次と互換でないと明記している。

- Live Streaming functionality
- 一部 third-party integrations

また、graph-based workflow 内に Agent / LlmAgent を入れる場合は task または single-turn mode にする必要がある。ただし ADK Python v2.0.0 では graph-based workflow で collaborative `task` mode は disabled とされているため、この点は実装時に最新 docs / release notes を確認する必要がある。

参照:

- [Graph-based agent workflows - Known limitations](https://adk.dev/graphs/)
- [Collaborative workflows](https://adk.dev/workflows/collaboration/)

## Dynamic workflows

Dynamic workflow は、static graph が複雑になりすぎる場合に、Python の loop / conditional / recursion / async flow を使って workflow を書く方法。

公式 docs の説明では、benefit は次。

- `while` / `if` / recursion / `async/await` で柔軟な control flow を書ける。
- `@node` decorator で関数を workflow node にできる。
- `ctx.run_node(...)` で node を関数のように呼ぶ。
- Automatic checkpointing により、resume 時に成功済み sub-node を skip できる。
- parent node の中に lower-level node を包み、workflow graph を読みやすく保てる。

参照: [Dynamic agent workflows](https://adk.dev/graphs/dynamic/)

## Human-in-the-loop

Graph-based workflow は `RequestInput` を使って human input node を含められる。これは AI model を使わず workflow を pause し、ユーザー入力を受けて次 node へ渡す。

`RequestInput` の主な設定:

- `message`: ユーザーへ見せる説明
- `payload`: 入力依頼に添える structured data
- `response_schema`: human response が従うべき schema

注意点として、`response_schema` はユーザー応答を自動整形しない。structured input UI を用意するか、別 Agent node で unstructured response を整形する設計が必要。

参照: [Human input for agent workflows](https://adk.dev/graphs/human-input/)

## Collaborative workflows

Collaborative agent team は、coordinator agent が subagent に task を委譲し、subagent 完了後に parent へ戻る構造。ADK 2.0 では subagent の mode が重要になる。

Mode:

- `chat`: デフォルト。user と自由にやり取りし、parent への return は manual transfer。
- `task`: clarification のための user interaction を許可し、task 完了時に automatic return。
- `single_turn`: user interaction なし。automatic return。複数 task の parallel execution が可能。

公式 docs の注意:

- `mode` は subagent 用。root agent へ設定しない。
- ADK Python v2.0.0 では graph-based workflow 内で `task` mode は disabled。
- Agent context isolation と control transfer を設計上考慮する必要がある。

保存画像:

- `images/cloudblog-agent-hierarchy.png`: agent hierarchy
- `images/cloudblog-workflow-agents.png`: workflow agent patterns
- `images/cloudblog-subagent-vs-agenttool.png`: subagent と AgentTool の比較

参照:

- [Build collaborative agent teams](https://adk.dev/workflows/collaboration/)
- [Building Collaborative AI: A Developer's Guide to Multi-Agent Systems with ADK](https://cloud.google.com/blog/topics/developers-practitioners/building-collaborative-ai-a-developers-guide-to-multi-agent-systems-with-adk/)

## Agent Runtime / 実行 / デプロイ

ADK runtime の公式 docs は、開発中の実行方法として次を挙げる。

- `adk web`: browser-based interface で agent と対話。
- `adk run`: terminal で agent と対話。
- `adk api_server`: REST API として agent を expose。
- Ambient Agents: event を非同期に処理する autonomous agent。

参照: [Agent Runtime](https://adk.dev/runtime/)

### Google Cloud 側の位置づけ

Google Cloud docs は ADK を、enterprise scale で reliable AI agents を build / debug / deploy する open-source framework と説明している。Agent Runtime、Cloud Run、GKE への scale が想定されている。

Agent Engine / Agent Runtime では、ADK agent を `AdkApp` として扱い、deploy 後は managed sessions を利用できる。主な operation として streaming query、session create/list/get/delete、memory add/search が挙げられている。

参照:

- [Agent Development Kit - Gemini Enterprise Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/adk)
- [Deploy an agent - Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/deploy)
- [Use an Agent Development Kit agent](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)
- [Manage sessions with Agent Development Kit](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/sessions/manage-sessions-adk)
- [Build and deploy an AI agent to Cloud Run using ADK](https://docs.cloud.google.com/run/docs/ai/build-and-deploy-ai-agents/deploy-adk-agent)

## A2A と ADK

ADK docs は A2A protocol と連携する multi-agent system を公式に扱っている。A2A の本質は、異なる framework / vendor の agent 間で capability discovery と task communication を標準化すること。

指定 codelab では、ADK agent を A2A agent として公開し、`.well-known/agent.json` または agent card を確認して、curl で request を送る流れを扱う。ADK 側は `adk api_server --a2a --port 8001 remote_a2a` を使う。

A2A 公式仕様では、core operations、Agent Card、Task、Message、Artifact、streaming、push notification、auth/security、JSON-RPC / gRPC bindings などが定義されている。

参照:

- [ADK with Agent2Agent (A2A) Protocol](https://adk.dev/a2a/)
- [A2A Protocol specification](https://a2a-protocol.org/latest/specification/)
- [指定 codelab](https://codelabs.developers.google.com/codelabs/create-multi-agents-adk-a2a?hl=ja)

## 指定 codelab の調査

Codelab:

- [ADK を使用してマルチエージェント システムを作成し、Agent Runtime にデプロイして、A2A プロトコルを使用する](https://codelabs.developers.google.com/codelabs/create-multi-agents-adk-a2a?hl=ja)
- 英語タイトル: Create multi agent system with ADK, deploy in Agent Engine and get started with A2A protocol

目的:

- image prompt から画像生成し、その画像が prompt を満たすか評価する multi-agent application を作る。
- 不満足なら再生成し、条件を満たすまで複数 agent が協調する。
- ADK の multi-agent system、Google Cloud 上の Agent Runtime / Agent Engine deployment、A2A protocol の基礎を学ぶ。

「4. Agent Development Kit の概要」セクションで挙げられている ADK の価値:

- Multi-Agent Systems: specialized agents を hierarchy として compose。
- Rich Tool Ecosystem: built-in tools、custom functions、LangChain / CrewAI tool integration、他 agent を tool として使う。
- Flexible Orchestration: `SequentialAgent` / `ParallelAgent` / `LoopAgent` と LLM-driven dynamic routing。
- Integrated Developer Experience: CLI と interactive dev UI。
- Built-in Evaluation: final response と execution trajectory を test case で評価。
- Deployment Ready: local、Vertex AI Agent Engine、Cloud Run、Docker へ deploy。

保存画像:

- `images/codelab-adk-positioning.png`: ADK の位置づけ図
- `images/codelab-agent-runtime-reference-architecture.png`: agent reference architecture
- `images/codelab-adk-dev-ui-output.png`: ADK Dev UI の出力例

注意:

- Codelab の workflow 表現は主に ADK 1.x 系の `SequentialAgent` / `ParallelAgent` / `LoopAgent` と Agent Engine / A2A の実践。ADK 2.0 の `Workflow(edges=...)` graph API や `@node` dynamic workflow の説明は公式 ADK docs を別途読む必要がある。

## Google Cloud / Google Developers Blog から見える実装パターン

### Multi-agentic systems using Google ADK

記事:

- [Build multi-agentic systems using Google ADK](https://cloud.google.com/blog/products/ai-machine-learning/build-multi-agentic-systems-using-google-adk)

主な学び:

- Coordinator subagent 方式は簡単な routing には効くが、「flight の後に hotel」のような multi-step orchestration では止まりやすい。
- Specialized agents を `AgentTool` として root agent の toolset に入れると、root agent が複数 tool を順に使って broader task を遂行しやすい。
- Self-regulating workflow では、生成、並列処理、review、validation を組み合わせる。

保存画像:

- `images/cloudblog-coordinator-subagents.png`
- `images/cloudblog-agenttools-dispatcher.png`
- `images/cloudblog-self-regulating-workflow.png`

### Collaborative AI guide

記事:

- [Building Collaborative AI: A Developer's Guide to Multi-Agent Systems with ADK](https://cloud.google.com/blog/topics/developers-practitioners/building-collaborative-ai-a-developers-guide-to-multi-agent-systems-with-adk/)

主な学び:

- Multi-Agent System は decentralized control、local views、emergent behavior で説明される。
- ADK の agent categories として LLM Agents、Workflow Agents、Custom Agents が紹介される。
- Agent hierarchy は parent / sub-agent と single parent rule を持つ。
- Communication mechanisms は shared state、delegation、explicit invocation。
- Sub-Agent と AgentTool は別物。Sub-Agent は hierarchy に常駐する member、AgentTool は必要時に呼ぶ外部 expert と考えると整理しやすい。

### Deep research agent

記事:

- [How to build a deep research agent for lead generation using Google's ADK](https://cloud.google.com/blog/products/ai-machine-learning/build-a-deep-research-agent-with-google-adk)

主な学び:

- root agent の前に intent extractor を置き、user request を structured data に変換する。
- SequentialAgent 内で research orchestrator が company ごとの mini-pipeline を parallel に回す。
- 複雑な workflow を `AgentTool` として root agent から single function call のように扱う。
- callback で session state を更新し、複数 turn の flow を維持する。

### Long-running agents

記事:

- [Build Long-running AI agents that pause, resume, and never lose context with ADK](https://developers.googleblog.com/build-long-running-ai-agents-that-pause-resume-and-never-lose-context-with-adk/)

主な学び:

- long-running workflow は conversation history ではなく明示的な state machine で現在 step を持つ。
- session state から step を読み、resume / persistent sessions / memory bank と組み合わせる。
- ADK 2.0 の checkpoint/resume 思想と相性がよい。

### Agent Builder / production 運用

記事:

- [Build and manage multi-system agents with Vertex AI](https://cloud.google.com/blog/products/ai-machine-learning/build-and-manage-multi-system-agents-with-vertex-ai)
- [More ways to build, scale, and govern AI agents with Vertex AI Agent Builder](https://cloud.google.com/blog/products/ai-machine-learning/more-ways-to-build-and-scale-ai-agents-with-vertex-ai-agent-builder)

主な学び:

- ADK は Google Agentspace / Customer Engagement Suite の agent と同系統の framework と説明される。
- Agent Engine は managed runtime、session / memory、security / governance、observability と組み合わせて production へ寄せる位置づけ。
- Google Cloud ブログでは PayPal の事例として、ADK CLI / visual tools による interaction inspection、state changes、multi-agent workflow tracing が挙げられている。

### BigQuery Agent Analytics

記事:

- [From interaction to insight: Announcing BigQuery Agent Analytics for the Google ADK](https://cloud.google.com/blog/products/data-analytics/introducing-bigquery-agent-analytics)

主な学び:

- ADK plugin として agent interaction data を BigQuery に stream し、user interaction、cost、performance、成功/失敗 path を分析する。
- Agent 評価と observability は ADK の production 化で重要な周辺機能。

## 評価・観測・デバッグ

ADK docs の evaluation は、final response quality だけでなく trajectory と tool use を見る設計。test file と evalset file の 2 approach が説明され、evalset は複数 session / multi-turn conversation に向く。

参照:

- [Why Evaluate Agents](https://adk.dev/evaluate/)
- [BigQuery Agent Analytics](https://cloud.google.com/blog/products/data-analytics/introducing-bigquery-agent-analytics)

運用観点で見るべきもの:

- final response
- tool calls / arguments
- intermediate responses
- session state
- trace view
- latency / error / token usage / tool call metrics
- user paths and drop-off points

## ユーザー記事・外部記事の整理

### SFEIR Institute

記事:

- [ADK 2.0 : Google passe aux workflows d'agents déterministes](https://institute.sfeir.com/fr/articles/google-adk-2-agent-development-kit-workflows-multi-agents/)

主な内容:

- ADK 2.0 を Alpha として紹介し、Graph workflows、Collaborative agents、Dynamic workflows の 3 点を整理。
- LangGraph / CrewAI との比較表があり、Google Cloud native integration を ADK の強みとしている。
- Production にはまだ慎重という記述があるが、調査時点では公式 docs は GA に更新済み。記事公開時点の Alpha 情報として扱うべき。

### Medium / Ali Arsanjani

記事:

- [ADK 2.0: From Chatbots to Collaborative, Deterministic AI Workflows](https://dr-arsanjani.medium.com/adk-2-0-from-chatbots-to-collaborative-deterministic-ai-workflows-c8656f3beab4)

主な内容:

- Prompt engineering から agentic software engineering への移行として ADK 2.0 を説明。
- Graph-based workflows、collaborative multi-agent architectures、deterministic routing を enterprise governance の文脈で評価。
- ただし API 名の記述は official docs の現行 `Workflow` / `BaseNode` 系と照合して読む必要がある。

### Zenn / SoftBank Next '26 現地レポート

記事:

- [エージェント開発が"もっと身近"に感じる — ADK 2.0とAgents CLIで変わる開発体験](https://zenn.dev/softbank/articles/23407724c9f943)

主な内容:

- Next '26 の文脈で ADK 2.0 と Agents CLI を紹介。
- Graph-based Agents を nodes & edges で declarative に workflow 定義するものとして整理。
- 現地レポートとして product surface / developer experience の把握に向く。

### Zenn / graph-based execution hands-on

記事:

- [Google ADK 2.0 のグラフベース実行を実際に動かしてみた](https://zenn.dev/yohei_data/articles/0059aaea6ea288)

主な内容:

- ADK 2.0 の Workflow / Nodes & Edges を hands-on で触った記録。
- 公式 docs の理解を補う体験談として有用。ただし記事内の Beta 表記や API detail は調査時点の公式 docs と突き合わせる。

### ChatForest review / AgentWiki

記事:

- [Google ADK 2.0 Review — Graph Workflows, Mobile Agents, and Where It Fits](https://chatforest.com/reviews/google-adk-2-agent-development-kit-review/)
- [Google ADK (Agent Development Kit): ADK 2.0 Overview](https://agentwiki.org/google_adk)

主な内容:

- ChatForest は I/O 2026 の文脈や Android / Gemini Nano への言及があるが、公式 docs で今回確認した ADK 2.0 core と完全には重ならない。周辺情報として扱う。
- AgentWiki は overview として便利だが、star 数や最新状態は変わるため、GitHub / PyPI / official docs で確認する。

## 調査から得た設計上の論点

### ADK 2.0 は LangGraph 対抗というより Google runtime 統合込みの workflow runtime

Graph / route / branch / join / nested workflow は LangGraph 的な発想と近い。しかし ADK は Agent Runtime、Agent Engine、Gemini、Vertex AI、A2A、MCP、Cloud Run、BigQuery analytics と結びつく点が主な差分。

### Sub-Agent と AgentTool の使い分けが重要

- 常に team hierarchy の一部として parent が管理するなら Sub-Agent。
- root agent が必要時に専門処理を呼び出すだけなら AgentTool。
- Google Cloud Blog の travel planner 例では、単純な delegation は multi-step task で止まりやすく、AgentTool 化が有効な場合がある。

### Prompt に手順を書くより workflow と state をコードに寄せる

公式 graph docs、dynamic docs、long-running agents blog は共通して、手順、状態、resume point、routing を prompt 外へ出す方向を示している。ADK 2.0 の価値は「agent を software engineering の制御対象に戻す」点にある。

### Production 化では session schema / event schema / observability を早期に見る

2.0 migration では Event schema が変わる。Agent Engine deployment、managed sessions、memory、BigQuery Agent Analytics、evaluation、trace view を早期に組み込まないと、multi-agent workflow の失敗原因が見えにくい。

### 2.0 の情報は古い Alpha/Beta 記述が残っている

検索結果、ブログ、ユーザー記事には 2026-03 から 2026-04 の Alpha/Beta 情報が残る。調査時点では公式 docs / PyPI は 2.0.0 GA を示している。特に install command、対応 Python version、production readiness、対応言語は公式 docs と PyPI を再確認する。

## 画像一覧

| Local file | Source |
| --- | --- |
| `images/adk-graph-workflow-design.svg` | https://adk.dev/assets/workflow-design.svg |
| `images/adk-prompts-to-graphs.svg` | https://adk.dev/assets/prompts-to-graphs.svg |
| `images/adk-graph-router.svg` | https://adk.dev/assets/graph-workflow-router.svg |
| `images/adk-graph-joinnode.svg` | https://adk.dev/assets/graph-joinnode.svg |
| `images/adk-nested-workflows.svg` | https://adk.dev/assets/graph-workflow-nodes.svg |
| `images/codelab-adk-positioning.png` | https://codelabs.developers.google.com/static/codelabs/create-multi-agents-adk-a2a/img/e97ad3e26ceb7a2f.png?hl=ja |
| `images/codelab-agent-runtime-reference-architecture.png` | https://codelabs.developers.google.com/static/codelabs/create-multi-agents-adk-a2a/img/d8eb74a6d8a055f9.png?hl=ja |
| `images/codelab-adk-dev-ui-output.png` | https://codelabs.developers.google.com/static/codelabs/create-multi-agents-adk-a2a/img/c159623ad45f37cf.png?hl=ja |
| `images/cloudblog-coordinator-subagents.png` | https://storage.googleapis.com/gweb-cloudblog-publish/images/1_Fig1_et7jsZ5.max-1300x1300.png |
| `images/cloudblog-agenttools-dispatcher.png` | https://storage.googleapis.com/gweb-cloudblog-publish/images/1_Fig2_SBLwlN8.max-1600x1600.png |
| `images/cloudblog-self-regulating-workflow.png` | https://storage.googleapis.com/gweb-cloudblog-publish/images/3_Fig3.max-1300x1300.png |
| `images/cloudblog-agent-hierarchy.png` | https://storage.googleapis.com/gweb-cloudblog-publish/images/mutliagent_blog_visual_2.max-1000x1000.png |
| `images/cloudblog-workflow-agents.png` | https://storage.googleapis.com/gweb-cloudblog-publish/images/6_zyKwPKJ.max-2000x2000.png |
| `images/cloudblog-subagent-vs-agenttool.png` | https://storage.googleapis.com/gweb-cloudblog-publish/images/mutliagent_blog_visual_12.max-1000x1000.png |

各画像の `.meta` ファイルにも source URL と取得元ページを記録した。

