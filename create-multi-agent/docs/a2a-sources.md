# A2A 調査ソース一覧

調査日: 2026-05-27

## 公式・一次情報

- https://a2a-protocol.org/latest/
  - Linux Foundation 配下の現行 A2A 公式サイト。A2A は Google により作られ、Linux Foundation に donated された open standard と説明される。
- https://a2a-protocol.org/latest/announcing-1.0/
  - v1.0 announcement。production-ready、multi-protocol bindings、version negotiation、signed Agent Cards、multi-tenancy、TSC 参加企業など。
- https://a2a-protocol.org/latest/specification/
  - 現行仕様。operations、data model、protocol bindings、security、Agent Card、JSON-RPC/gRPC/HTTP+JSON、examples。
- https://a2a-protocol.org/latest/topics/key-concepts/
  - core actors、Agent Card、Task、Message、Part、Artifact、interaction mechanisms。
- https://a2a-protocol.org/latest/topics/agent-discovery/
  - well-known URI、registry、direct configuration、Agent Card 保護、caching。
- https://a2a-protocol.org/latest/topics/life-of-a-task/
  - Message vs Task、contextId、task immutability、follow-up/refinement、parallel tasks。
- https://a2a-protocol.org/latest/topics/streaming-and-async/
  - SSE streaming、push notifications、webhook security。
- https://a2a-protocol.org/latest/topics/a2a-and-mcp/
  - A2A と MCP の責務分担。agent-to-tool と agent-to-agent の区別。
- https://github.com/a2aproject/A2A
  - 公式 GitHub repository。
- https://github.com/a2aproject/a2a-python
  - 公式 Python SDK。

## Google / Google Cloud

- https://cloud.google.com/blog/ja/products/ai-machine-learning/a2a-a-new-era-of-agent-interoperability
  - Google Cloud 公式ブログ日本語版。2025-04-10。A2A 発表、設計原則、MCP 補完、Agent Card、task、artifact、collaboration、採用ユースケース、パートナー。
- https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/
  - Google Developers Blog 原文。2025-04-09。A2A 発表の一次情報。
- https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade/
  - Google Cloud Blog。2025-08-01。v0.3、gRPC、signed security cards、Python SDK、150+ organizations、developer toolkit。
- https://docs.cloud.google.com/run/docs/ai/a2a-agents
  - Cloud Run 上の A2A agent overview。AI agents と A2A の関係、Cloud Run hosting の文脈。
- https://docs.cloud.google.com/run/docs/deploy-a2a-agents
  - Cloud Run への deploy guide。IAM、Secret Manager、in-memory TaskStore、AlloyDB、A2A inspector、CLI test。
- https://google.github.io/adk-docs/a2a/
  - ADK with A2A。ADK で A2A multi-agent system を作る導線。
- https://google.github.io/adk-docs/a2a/intro/
  - ADK の A2A intro。local sub-agents と remote A2A agents の使い分け、A2AServer、RemoteA2aAgent。

## Codelabs

- https://codelabs.developers.google.com/codelabs/create-multi-agents-adk-a2a?hl=ja
  - 指定 codelab。特に「6. A2A の概要」と「10. A2A エージェントを作成する」を参照。ADK multi-agent app を Agent Runtime に deploy し、A2A agent として expose する。
- https://codelabs.developers.google.com/intro-a2a-purchasing-concierge
  - Purchasing Concierge codelab。Cloud Run と Agent Engine 上で remote seller agents と concierge を連携させる例。

## ユーザー記事・二次情報

- https://zenn.dev/hakoten/articles/06557100337fb3
  - 日本語の概要記事。Agent Card、Task、Artifact、Message、Part、MCP との関係を TypeScript 風の構造と JSON 例で説明。初期仕様ベースのため、現行仕様との差分に注意。
- https://medium.com/google-cloud/exploring-agent2agent-a2a-protocol-with-purchasing-concierge-use-case-on-cloud-run-36f4b896eadf
  - Google Cloud Community の実装記事。ADK、LangGraph、CrewAI、Cloud Run、pizza/burger seller agents、Agent Card discovery logs。
- https://www.ibm.com/think/topics/agent2agent-protocol
  - IBM Think の概説。Linux Foundation への移管、ACP/MCP との比較、privacy/security/integration 観点。
- https://www.builder.io/blog/a2a-protocol
  - Builder.io の解説。A2A を tiny open standard / discover-authenticate-stream-result の文脈で紹介。

## 保存画像

- `images/google-cloud-a2a-header.png`
  - Source image: https://storage.googleapis.com/gweb-cloudblog-publish/images/a2a-header.max-1700x1700.png
  - Page: https://cloud.google.com/blog/ja/products/ai-machine-learning/a2a-a-new-era-of-agent-interoperability
- `images/google-cloud-a2a-mcp-complement.png`
  - Source image: https://storage.googleapis.com/gweb-cloudblog-publish/images/image1_yEPzdSr.original.max-1900x1900.png
  - Page: https://cloud.google.com/blog/ja/products/ai-machine-learning/a2a-a-new-era-of-agent-interoperability
- `images/google-cloud-a2a-how-it-works.png`
  - Source image: https://storage.googleapis.com/gweb-cloudblog-publish/images/image5_VkAG0Kd.original.max-2000x2000.png
  - Page: https://cloud.google.com/blog/ja/products/ai-machine-learning/a2a-a-new-era-of-agent-interoperability
- `images/google-cloud-a2a-recruiting-use-case.png`
  - Source image: https://storage.googleapis.com/gweb-cloudblog-publish/images/image4_UjaxwpH.max-1300x1300.png
  - Page: https://cloud.google.com/blog/ja/products/ai-machine-learning/a2a-a-new-era-of-agent-interoperability
- `images/codelab-adk-positioning.png`
  - Source image: https://codelabs.developers.google.com/static/codelabs/create-multi-agents-adk-a2a/img/e97ad3e26ceb7a2f.png
  - Page: https://codelabs.developers.google.com/codelabs/create-multi-agents-adk-a2a?hl=ja
- `images/codelab-agent-runtime-reference-architecture.png`
  - Source image: https://codelabs.developers.google.com/static/codelabs/create-multi-agents-adk-a2a/img/d8eb74a6d8a055f9.png
  - Page: https://codelabs.developers.google.com/codelabs/create-multi-agents-adk-a2a?hl=ja
- `images/codelab-image-scoring-agent-flow.png`
  - Source image: https://codelabs.developers.google.com/static/codelabs/create-multi-agents-adk-a2a/img/bfed5e21e0b66d26.png
  - Page: https://codelabs.developers.google.com/codelabs/create-multi-agents-adk-a2a?hl=ja
