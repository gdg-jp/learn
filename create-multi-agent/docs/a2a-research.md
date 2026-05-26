# A2A 調査メモ

調査日: 2026-05-27

このメモは、Agent2Agent Protocol (A2A) について、公式ドキュメント、Google Codelabs、Google Cloud 公式ブログ、Google/Cloud Run/ADK ドキュメント、ユーザー記事を横断して調査したものです。教材化や演習設計は意図せず、現時点で把握すべき事実、仕様、差分、注意点を整理する。

## 結論

A2A は、異なるベンダー、フレームワーク、言語、実行環境で作られた AI エージェント同士が、互いの内部実装を公開せずに発見、通信、タスク委譲、成果物交換を行うためのオープン標準である。Google が 2025-04-09 に発表し、その後 Linux Foundation 配下の `a2aproject` / `a2a-protocol.org` に移行した。現行公式ドキュメントでは v1.0 が production-ready な安定版として扱われている。

A2A はエージェント実装フレームワークではなく、エージェント間通信のアプリケーションレベルのプロトコルである。ADK、LangGraph、CrewAI、Semantic Kernel、独自実装などの上に載る相互運用レイヤーと見るのが正確である。

MCP との関係は競合ではなく補完である。MCP は主に「エージェントとツール、API、リソース」の接続を標準化する。一方 A2A は「エージェントとエージェント」の発見、会話、タスク管理、成果物交換を標準化する。実システムでは、各エージェント内部で MCP を使い、エージェント間では A2A を使う構成が想定されている。

## 現在の位置づけと時系列

- 2025-04-09: Google Developers Blog / Google Cloud Blog で A2A 発表。50 以上のテクノロジーパートナーと主要サービスプロバイダーが参加すると説明された。
- 2025-04-10: Google Cloud 公式ブログ日本語版が公開。MCP を補完し、HTTP、SSE、JSON-RPC など既存標準を使う設計原則が示された。
- 2025-08-01: Google Cloud Blog が v0.3 と開発者ツール群を発表。gRPC support、security card signing、Python SDK の client side support、150 以上の組織によるエコシステム拡大が説明された。
- 2026 時点: 公式サイトは `a2a-protocol.org`。v1.0 は、複数 protocol bindings、version negotiation、signed Agent Cards、multi-tenancy、より明確な enterprise deployment 要件を含む production-ready 版として案内されている。

## 基本概念

### 主要アクター

- User: 人間または自動化サービス。ゴールや依頼を開始する。
- A2A Client: ユーザーに代わって A2A Server に要求を送るアプリ、サービス、または別の AI エージェント。
- A2A Server / Remote Agent: A2A 準拠エンドポイントを公開するエージェントまたはエージェントシステム。クライアントから見れば内部状態、メモリ、ツール、推論過程を見せない opaque な相手である。

### 通信要素

- Agent Card: エージェントの ID、説明、提供者、endpoint、capabilities、skills、入出力モード、認証要件などを記述する JSON metadata。発見と接続判断の中心。
- Message: client と agent の 1 turn の通信。role と parts を持つ。
- Part: message や artifact の最小 content unit。text、file/raw bytes、URL、structured data などを表す。MIME type、filename、metadata を持てる。
- Task: stateful な作業単位。長時間処理、multi-turn、human-in-the-loop、非同期更新を追跡するための中心オブジェクト。
- Artifact: task の結果として生成される具体的な成果物。文書、画像、構造化データなど。
- Context: 複数の task や message をまとめる `contextId`。同じゴールや会話の継続性を表す。
- Extension: 基本仕様を壊さずに追加機能を宣言する仕組み。

## Agent Card と discovery

A2A の discovery は Agent Card を中心に設計されている。公開エージェントの場合、現行ドキュメントでは well-known URI として `https://{agent-server-domain}/.well-known/agent-card.json` が推奨される。

ただし古い codelab や記事、ADK の一部サンプルでは `/.well-known/agent.json` が使われている。調査対象の Google Codelab でも、ADK の `RemoteA2aAgent` が `http://localhost:8001/a2a/image_scoring/.well-known/agent.json` を参照している。したがって、現行仕様を新規に参照する場合は `agent-card.json` を優先しつつ、既存サンプルや SDK の実装で `agent.json` が残っている可能性に注意する。

Agent Card の discovery パターンは主に次の 3 種類である。

- Well-known URI: パブリックまたはドメイン単位で自動発見したい agent に向く。
- Curated registry / catalog: 企業内カタログ、marketplace、agent registry など。skills や tags で検索し、権限制御も行う。
- Direct configuration / private discovery: 環境変数、設定ファイル、ハードコード、独自 API など。静的な接続や開発時に向くが、動的発見には弱い。

Agent Card は内部 endpoint、sensitive skill、認証要件などを含み得るため、公開範囲を設計する必要がある。現行ドキュメントは、詳細情報を authenticated extended agent card として分離すること、Agent Card 配信 endpoint に OAuth 2.0、mTLS、ネットワーク制限などの保護をかけること、静的秘密情報を Agent Card に埋め込まないことを推奨している。

## プロトコルと操作

現行 v1.0 では、A2A は canonical data model、abstract operations、protocol bindings の 3 層で説明される。仕様の中心は protobuf model で、生成された JSON artifacts は tooling/documentation 用とされる。

主要 operation は次の通り。

- `SendMessage`: 新しい interaction を開始、または既存 context/task に続けて message を送る。
- `SendStreamingMessage`: message を送り、同時に task updates を stream で受け取る。
- `GetTask`: task の現在状態、履歴、artifact を取得する。
- `ListTasks`: context や状態に基づいて task を一覧する。
- `CancelTask`: cancel 可能な task を中断する。
- `SubscribeToTask`: 進行中 task の stream に再接続する。
- Push notification config operations: 長時間 task の webhook 通知設定を作成、取得、一覧、削除する。
- `GetExtendedAgentCard`: 認証後に詳細な Agent Card を取得する。

古い記事では `tasks/send`、`tasks/get` などの JSON-RPC method 名が使われている。現行仕様・SDK では `SendMessage` / `message/send` 系の命名に移行しているため、旧記事の payload は概念理解用として扱う。

## Task lifecycle

A2A は、すぐ返せる応答と長時間処理を分けて扱う。Agent は incoming message に対して stateless `Message` を返すことも、stateful `Task` を開始することもできる。

Task は `working`、`input-required`、`auth-required`、`completed`、`canceled`、`rejected`、`failed` などの状態を取り得る。terminal state に到達した task は再開せず、追加依頼や refinement は同じ `contextId` 内の新しい task として扱う。これにより、入力、出力、artifact、状態遷移の追跡が明確になる。

`contextId` は関連する task と message をまとめる。例えば「画像を生成する task」の完了後、「その画像の船を赤くする」という refinement は、元 task を参照しつつ同じ context 内に新しい task として作られる。

## Streaming と非同期

A2A は長時間 task を前提にしている。更新の受け取り方は主に 3 つある。

- Polling: client が `GetTask` で状態を確認する。
- SSE streaming: server が `text/event-stream` で status update や artifact chunks を送る。Agent Card の `capabilities.streaming` が true である必要がある。
- Push notifications: client が webhook URL を登録し、server が重要な状態変化時に POST する。mobile client、serverless、数分から数日かかる task など、接続を維持しづらい場合に向く。

Push notifications は SSRF や DDoS amplifier になり得るため、server 側は webhook URL を検証し、client webhook への認証を行う必要がある。client 側も送信元検証、署名や token 検証、timestamp/nonce による replay 対策、key rotation を考慮する。

## セキュリティ

A2A は独自認証方式を発明するのではなく、既存の Web security を前提にする。Transport security、server identity verification、client authentication、authorization、in-task authorization などが仕様上の論点である。

Agent Card では OpenAPI 系の security scheme と近い形で API key、HTTP auth、OAuth 2.0、OpenID Connect、mTLS などを表現できる。credentials は通常 A2A payload の中ではなく HTTP header 等で渡す。

v1.0 では signed Agent Cards が重要になっている。Agent Card は JWS で署名でき、署名前に JSON Canonicalization Scheme (RFC 8785) で canonicalize する。これにより、Agent Card の改ざん検出と provider identity の検証が可能になる。

Opaque execution も重要なセキュリティ・プライバシー上の性質である。A2A では agent は capability、skills、messages、tasks、artifacts を通じて連携するが、内部 memory、tool implementation、chain-of-thought、proprietary logic を共有する必要はない。

## A2A と MCP

公式ドキュメントは、MCP と A2A を次のように切り分ける。

- MCP: agent が database、API、function、filesystem、検索、外部リソースなどを tool/resource として使うための protocol。
- A2A: independent な agents が互いを発見し、会話し、task を委譲し、context と artifacts を交換するための protocol。

典型構成は「agent 内部は MCP、agent 間は A2A」である。自動車修理店の例では、shop manager と mechanic、parts supplier の会話や委譲は A2A、mechanic が diagnostic scanner や repair manual database を使う部分は MCP となる。

ユーザー記事では「A2A Agent Card を MCP resource として配布し、実通信は A2A で行う」構成も言及されている。これは discovery の補助として MCP を使う発想であり、A2A の主役はあくまで agent-to-agent task collaboration である。

## Google Cloud / Cloud Run

Google Cloud の Cloud Run ドキュメントは、A2A agent を Cloud Run に host する前提を説明している。Cloud Run は A2A server を containerized HTTP service として公開できるため、agent endpoint、well-known Agent Card、auth、scaling、logging、monitoring を通常の Cloud Run 運用パターンに乗せやすい。

Cloud Run の A2A deploy guide で重要な点は次の通り。

- 開発用には in-memory `TaskStore` が使えるが、container restart、scale down、redeploy で task data が失われる。
- 本番や水平 scaling では AlloyDB for PostgreSQL など persistent task storage が推奨される。
- internal Google Cloud clients や Gemini Enterprise から呼ぶ場合は `--no-allow-unauthenticated` による IAM 認証が推奨される。
- public access が必要な A2A server では、Cloud Run を unauthenticated にするだけでなく、Agent Card の `securitySchemes` / `security` に agent-level authentication 情報を正しく記述する必要がある。
- A2A inspector は Agent Card 表示、仕様 compliance validation、live chat、raw JSON-RPC messages の確認に使える。
- IAM protected Cloud Run agent をローカルから叩くには `gcloud auth print-identity-token` を Authorization header に入れる。

## ADK との関係

Google ADK は A2A を「remote agents と通信するためのプロトコル」として扱う。ADK の説明では、local sub-agent と remote A2A agent の使い分けが明確である。

- Local sub-agents: 同じ process 内の module/library 的な分割。高速で、in-memory に通信する。
- Remote agents (A2A): 別 service、別 team、別 organization、別言語、別 framework で動く agent。network 越しに formal contract で接続する。

ADK では、既存の agent を A2A server として expose する側と、`RemoteA2aAgent` で remote agent を consume する側の両方が用意されている。ADK の観点では、いったん `RemoteA2aAgent` を設定すると、remote agent を local tool/function のように扱えるよう抽象化される。

調査対象の Google Codelab では、ADK の multi-agent image scoring app を作り、Agent Runtime に deploy した後、`adk api_server --a2a --port 8001 remote_a2a` で A2A agent として公開している。Agent Card を curl で確認し、A2A endpoint に JSON payload を POST して画像生成依頼を送る流れが示されている。

## Codelab で確認できる実装上の事実

指定 codelab「6. A2A の概要」は、A2A の特徴を次の 8 点として説明している。

- universal interoperability
- capability discovery via Agent Card
- secure by default
- modality agnostic
- structured task management
- opaque execution
- existing standards: HTTP、SSE、JSON-RPC
- asynchronous communication

同 codelab の「10. A2A エージェントを作成する」では、`agents.json` に `name`、`description`、`url`、`version`、`defaultInputModes`、`defaultOutputModes`、`capabilities.streaming`、`skills` を記述し、ADK の `RemoteA2aAgent` が Agent Card URL を参照する。

この codelab は実用上有用だが、現行 v1.0 仕様とはいくつか表記が異なる可能性がある。特に `/.well-known/agent.json`、`capabilities.functions`、簡略化された POST payload などは、現行仕様の用語と突き合わせて読むべきである。

別の Google Codelab / Google Cloud Community 記事「Purchasing Concierge」では、pizza seller agent と burger seller agent を remote seller agents として Cloud Run に deploy し、concierge agent が Agent Card discovery を行う。記事のログでは、pizza は Bearer、burger は Basic と、異なる authentication scheme を Agent Card で表現している。これは A2A が multi-agent、multi-service、multi-auth の接続に向くことを示す実例である。

## ユーザー記事から得られる補足

Zenn の「Agent2Agent（A2A)プロトコルの概要」は、Agent Card、Task、Artifact、Message、Part を日本語で具体的な TypeScript 風 interface と JSON 例で説明している。初心者向けの概念整理として有用だが、記事は発表初期の仕様を前提にしているため、`/.well-known/agent.json`、`tasks/send`、`sessionId` など、現行 v1.0 の表現と一致しない箇所がある。

Medium の Google Cloud Community 記事は、Cloud Run 上の remote seller agents と purchasing concierge の構成を実運用に近い形で示す。ADK、LangGraph、CrewAI など複数 framework を含む例として、A2A の interoperability という主張を確認しやすい。

IBM Think の解説は、A2A が Google により 2025 年 4 月に導入され、現在は Linux Foundation の open-source Agent2Agent project に housed されていること、ACP や MCP との関係、privacy/security/integration の利点を中立的に整理している。

## 仕様差分・注意点

- 古い Google GitHub Pages (`google-a2a.github.io/A2A`) や初期記事は v0.2.x 相当の内容を含む。現在は `a2a-protocol.org/latest` と `github.com/a2aproject/A2A` を優先する。
- `/.well-known/agent.json` と `/.well-known/agent-card.json` が混在している。現行 discovery docs は `agent-card.json`、ADK/codelab には `agent.json` が残る。
- `tasks/send` など旧 JSON-RPC method と、現行の `SendMessage` / `message/send` 系 naming が混在している。
- A2A は agent の品質、認可判断、policy enforcement、memory sharing、trust framework を自動で解決しない。あくまで通信、discovery、task/artifact semantics の標準である。
- Opaque execution はプライバシー上の利点だが、監査、説明責任、policy enforcement には別途 logging、trace、evaluation、governance が必要になる。
- Push notification は便利だが、SSRF、認証不備、replay、key rotation を設計しないと攻撃面が広がる。
- Cloud Run の in-memory TaskStore は local/development 向きで、本番の水平 scaling や task durability には persistent store が必要。
- Agent Card は capability advertisement であって、実際に task を安全・正確に完了できることの保証ではない。registry、署名、認証、評価、監視と組み合わせる必要がある。

## 保存した図

- `images/google-cloud-a2a-header.png`: Google Cloud 公式ブログのヘッダー画像。
- `images/google-cloud-a2a-mcp-complement.png`: A2A と MCP の補完関係を示す公式ブログ図。
- `images/google-cloud-a2a-how-it-works.png`: A2A の仕組みを示す公式ブログ図。
- `images/google-cloud-a2a-recruiting-use-case.png`: 採用ユースケースの公式ブログ図。
- `images/codelab-adk-positioning.png`: ADK の位置づけ図。
- `images/codelab-agent-runtime-reference-architecture.png`: Agent Runtime / Cloud Run 等を組み合わせたリファレンスアーキテクチャ図。
- `images/codelab-image-scoring-agent-flow.png`: image scoring multi-agent flow 図。

各画像の取得元は、同名ファイルに `.meta` を付けたファイルに記録した。

## 主要参照先

- A2A official docs: https://a2a-protocol.org/latest/
- A2A v1.0 announcement: https://a2a-protocol.org/latest/announcing-1.0/
- A2A specification: https://a2a-protocol.org/latest/specification/
- A2A GitHub: https://github.com/a2aproject/A2A
- Google Cloud 公式ブログ日本語版: https://cloud.google.com/blog/ja/products/ai-machine-learning/a2a-a-new-era-of-agent-interoperability
- Google Cloud Blog v0.3 / toolkit: https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade/
- Google Codelab: https://codelabs.developers.google.com/codelabs/create-multi-agents-adk-a2a?hl=ja
- Google Codelab Purchasing Concierge: https://codelabs.developers.google.com/intro-a2a-purchasing-concierge
- Cloud Run A2A overview: https://docs.cloud.google.com/run/docs/ai/a2a-agents
- Cloud Run A2A deploy guide: https://docs.cloud.google.com/run/docs/deploy-a2a-agents
- ADK A2A docs: https://google.github.io/adk-docs/a2a/
- Zenn 概要記事: https://zenn.dev/hakoten/articles/06557100337fb3
- Google Cloud Community Medium: https://medium.com/google-cloud/exploring-agent2agent-a2a-protocol-with-purchasing-concierge-use-case-on-cloud-run-36f4b896eadf
