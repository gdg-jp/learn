# ADK 2.0 調査ソース一覧

調査日: 2026-05-27 JST

## 公式 ADK docs

- [Welcome to ADK 2.0](https://adk.dev/2.0/)  
  ADK Python 2.0.0 GA、主要機能、1.x compatibility / breaking changes。
- [Graph-based agent workflows](https://adk.dev/graphs/)  
  Graph workflow の概要、prompt-based agent から graph-based workflow への移行、known limitations。
- [Build graph routes for agent workflows](https://adk.dev/graphs/routes/)  
  Node、edges syntax、route sequence、branch、parallel fan-out / JoinNode、nested workflow。
- [Data handling for agent workflows](https://adk.dev/graphs/data-handling/)  
  Event、`output` / `message` / `state`、schema による構造化。
- [Human input for agent workflows](https://adk.dev/graphs/human-input/)  
  `RequestInput`、HITL node、response schema。
- [Dynamic agent workflows](https://adk.dev/graphs/dynamic/)  
  `@node`、`ctx.run_node`、loop / conditional / recursion、checkpointing。
- [Build collaborative agent teams](https://adk.dev/workflows/collaboration/)  
  coordinator / subagents、`chat` / `task` / `single_turn` mode、制約。
- [Agent Runtime](https://adk.dev/runtime/)  
  `adk web`、`adk run`、`adk api_server`、Ambient Agents、runtime reference。
- [Why Evaluate Agents](https://adk.dev/evaluate/)  
  final response と trajectory / tool use の評価、test file、evalset。
- [ADK with Agent2Agent (A2A) Protocol](https://adk.dev/a2a/)  
  ADK agent を A2A で expose / consume するガイド入口。
- [ADK release notes](https://adk.dev/release-notes/)  
  言語別 release notes への入口。
- [google-adk on PyPI](https://pypi.org/project/google-adk/)  
  2.0.0 の upload date、project description、extras、release history。

## 指定 codelab

- [ADK を使用してマルチエージェント システムを作成し、Agent Runtime にデプロイして、A2A プロトコルを使用する](https://codelabs.developers.google.com/codelabs/create-multi-agents-adk-a2a?hl=ja)  
  指定された codelab。ADK 概要、multi-agent image scoring、Agent Runtime deployment、A2A expose/test。

## Google Cloud docs

- [Agent Development Kit - Gemini Enterprise Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/adk)  
  Google Cloud 側の ADK overview。最終更新 2026-05-21。
- [Develop an Agent Development Kit agent](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/develop/adk)  
  Agent Engine 向け ADK agent development。
- [Deploy an agent - Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/deploy)  
  Agent Engine deployment、requirements、resource config、permissions。
- [Use an Agent Development Kit agent](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)  
  `AdkApp` の supported operations、managed sessions。
- [Manage sessions with Agent Development Kit](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/sessions/manage-sessions-adk)  
  Agent Engine Sessions と ADK の接続。
- [Build and deploy an AI agent to Cloud Run using ADK](https://docs.cloud.google.com/run/docs/ai/build-and-deploy-ai-agents/deploy-adk-agent)  
  Cloud Run への ADK agent deployment。

## A2A 公式

- [A2A Protocol specification](https://a2a-protocol.org/latest/specification/)  
  Agent Card、Task、Message、Artifact、streaming、push notification、auth、JSON-RPC / gRPC binding。

## Google Cloud / Google Developers Blogs

- [Build multi-agentic systems using Google ADK](https://cloud.google.com/blog/products/ai-machine-learning/build-multi-agentic-systems-using-google-adk)  
  Coordinator subagents、AgentTool dispatcher、self-regulating workflow。
- [Building Collaborative AI: A Developer's Guide to Multi-Agent Systems with ADK](https://cloud.google.com/blog/topics/developers-practitioners/building-collaborative-ai-a-developers-guide-to-multi-agent-systems-with-adk/)  
  MAS 概念、agent categories、agent hierarchy、workflow agents、communication mechanisms。
- [Build and manage multi-system agents with Vertex AI](https://cloud.google.com/blog/products/ai-machine-learning/build-and-manage-multi-system-agents-with-vertex-ai)  
  ADK / Agent Garden / Agent Engine / A2A の発表文脈。
- [More ways to build, scale, and govern AI agents with Vertex AI Agent Builder](https://cloud.google.com/blog/products/ai-machine-learning/more-ways-to-build-and-scale-ai-agents-with-vertex-ai-agent-builder)  
  Agent Builder、ADK adoption、visual tools、production governance。
- [From interaction to insight: Announcing BigQuery Agent Analytics for the Google ADK](https://cloud.google.com/blog/products/data-analytics/introducing-bigquery-agent-analytics)  
  ADK interaction data を BigQuery に stream する analytics plugin。
- [How to build a deep research agent for lead generation using Google's ADK](https://cloud.google.com/blog/products/ai-machine-learning/build-a-deep-research-agent-with-google-adk)  
  Deep research / lead generation agent、AgentTool、callback state management。
- [Build Long-running AI agents that pause, resume, and never lose context with ADK](https://developers.googleblog.com/build-long-running-ai-agents-that-pause-resume-and-never-lose-context-with-adk/)  
  Durable state machine、persistent sessions、resume。

## ユーザー記事・外部記事

- [ADK 2.0 : Google passe aux workflows d'agents déterministes](https://institute.sfeir.com/fr/articles/google-adk-2-agent-development-kit-workflows-multi-agents/)  
  Alpha 時点の ADK 2.0 概説。Graph / collaborative / dynamic、LangGraph / CrewAI 比較。
- [ADK 2.0: From Chatbots to Collaborative, Deterministic AI Workflows](https://dr-arsanjani.medium.com/adk-2-0-from-chatbots-to-collaborative-deterministic-ai-workflows-c8656f3beab4)  
  Agentic software engineering、deterministic routing、enterprise governance の観点。
- [エージェント開発が"もっと身近"に感じる - ADK 2.0とAgents CLIで変わる開発体験](https://zenn.dev/softbank/articles/23407724c9f943)  
  Google Cloud Next '26 現地レポート。Graph-based Agents / Agents CLI。
- [Google ADK 2.0 のグラフベース実行を実際に動かしてみた](https://zenn.dev/yohei_data/articles/0059aaea6ea288)  
  Workflow / Nodes & Edges の hands-on 記録。
- [Google ADK 2.0 Review - Graph Workflows, Mobile Agents, and Where It Fits](https://chatforest.com/reviews/google-adk-2-agent-development-kit-review/)  
  外部 review。I/O 2026 文脈、graph workflow、mobile agents への言及。
- [Google ADK (Agent Development Kit): ADK 2.0 Overview](https://agentwiki.org/google_adk)  
  Agent knowledge base 形式の overview。最新性は公式 docs と照合が必要。

## 画像ソース

画像の source URL は `images/*.meta` に個別に記録済み。

