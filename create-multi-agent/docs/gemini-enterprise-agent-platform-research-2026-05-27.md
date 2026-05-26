# Gemini Enterprise Agent Platform 調査メモ

調査日: 2026-05-27 JST  
対象: Gemini Enterprise Agent Platform / Agent Runtime / Agent Development Kit / A2A / Agent Gateway / Memory Bank / Sessions / Observability / Evaluation / Gemini Enterprise 連携

## 1. 要約

Gemini Enterprise Agent Platform は、Google Cloud が Gemini Enterprise と Vertex AI のエージェント関連機能を束ねて提示している、企業向け AI エージェント開発・運用基盤である。単体の「エージェント実行環境」ではなく、エージェントの作成、デプロイ、状態管理、長期記憶、評価、監視、ガバナンス、ディスカバリ、他エージェント連携を含むプラットフォームとして設計されている。

公式ドキュメント上の整理では、主要機能は大きく `Build`、`Scale`、`Govern`、`Optimize` に分かれる。Build は Agent Studio、ADK、Agent Garden、Managed Agents API、RAG/検索/ツール連携を含む。Scale は Agent Runtime、Sessions、Memory Bank、Code Execution、Example Store、ストリーミング、ネットワーク制御を含む。Govern は Agent Registry、Agent Identity、Agent Gateway、IAM、Model Armor、安全性ポリシーを含む。Optimize はトレース、ログ、評価、プロンプト最適化、Example Store を中心にする。

「Agent Runtime」は、以前 `Vertex AI Agent Engine` または API 上の `ReasoningEngine` として扱われていた機能の後継・再編に見える。公式 API や Python SDK には互換性のため `reasoningEngines`、`agent_engines` などの名前が残っている。教材や実装で名称を扱う場合は、プロダクト表示名として `Agent Runtime`、API/SDK 互換名として `ReasoningEngine` / `Agent Engine` が残る、という整理が安全である。

## 2. 主要な一次情報

- Google Cloud Blog: [次世代のエージェントを推進する Gemini Enterprise Agent Platform を発表](https://cloud.google.com/blog/ja/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform)
- Google Cloud Docs: [Agent Platform overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/overview)
- Google Cloud Docs: [Build agents and apps with Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build)
- Google Cloud Docs: [Scale agents with Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale)
- Google Cloud Docs: [Govern agents with Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern)
- Google Cloud Docs: [Optimize agents with Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize)
- Google Cloud Docs: [Agent Runtime overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime)
- Google Cloud Docs: [Sessions overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sessions)
- Google Cloud Docs: [Memory Bank overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank)
- Google Cloud Docs: [Agent Gateway overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/gateways/agent-gateway-overview)
- Google Codelab: [ADK を使用してマルチエージェント システムを作成し、Agent Runtime にデプロイして、A2A プロトコルを使用する](https://codelabs.developers.google.com/codelabs/create-multi-agents-adk-a2a?hl=ja)
- ADK Docs: [Agent Development Kit](https://google.github.io/adk-docs/)
- A2A Protocol: [Agent2Agent Protocol Specification](https://a2a-protocol.org/latest/specification/)

## 3. Platform の構成

### 3.1 Build

Build 領域は、エージェントの設計・実装・接続・社内知識の取り込みを扱う。

- Agent Studio: Gemini Enterprise 上のノーコード/ローコード型のエージェント作成・テスト UI。モデル比較、プロンプト調整、ツールやデータソース接続を UI で扱う。
- Agent Development Kit: Google のオープンソース SDK。Python/Java/Go を対象に、マルチエージェント、ツール、コールバック、評価、デプロイ連携を扱う。公式ドキュメントでは ADK 2.0 が Gemini Enterprise Agent Platform の中心的な開発手段として扱われている。
- Agent Garden: サンプルエージェント、テンプレート、パートナー提供エージェントを探して試すためのカタログ。G-gen 記事ではプレビューとして紹介されている。
- Managed Agents API: Google が管理するエージェント・エージェントテンプレートを API 経由で利用する仕組み。プレビュー扱いの記述が多い。
- RAG Engine / Vector Search / Agent Search: エージェントが自社データを利用するための検索・RAG 基盤。
- MCP / A2A: ツール連携は MCP、エージェント間連携は A2A という棲み分けで説明されることが多い。
- Auth Manager / Skill Registry: 認可済み接続やツール/スキルの登録・再利用を支える周辺機能として扱われる。

### 3.2 Scale

Scale 領域は、作ったエージェントを本番運用できる形に載せる部分である。

- Agent Runtime: フルマネージドなエージェント実行基盤。ADK、LangChain、LangGraph、AG2、LlamaIndex、カスタムフレームワークなどのエージェントをデプロイ対象にできる。
- Sessions: 会話単位の状態、イベント履歴、ランタイム状態を保存・取得するサービス。ADK エージェントを Agent Runtime にデプロイする場合は標準的に使われる。
- Memory Bank: ユーザーごとの長期記憶。複数セッションをまたいだユーザー嗜好や過去文脈の利用に使う。Sessions が短期状態、Memory Bank が長期記憶という分担。
- Code Execution: エージェントのコード実行用サンドボックス。安全な隔離環境でデータ分析やコード生成/実行を行う用途。
- Example Store: 成功/失敗例やデモンストレーションを保存し、few-shot、評価、改善に使うためのストア。
- Bidirectional Streaming: リアルタイム音声/映像/テキストなどを伴うインタラクションで使うストリーミング API。
- Private Service Connect: 企業ネットワーク内で Agent Runtime に接続するためのネットワーク制御。

### 3.3 Govern

Govern 領域は、エージェントの発見、認証、ポリシー、セキュリティ、監査を扱う。

- Agent Registry: エージェントを登録し、メタデータ、カード、エンドポイント、所有者、利用可否を管理する。
- Agent Identity: エージェントごとの ID と権限境界を扱う。ユーザー代理、サービスアカウント、ワークロード ID、IAM と組み合わせて扱う。
- Agent Gateway: エージェント間通信やクライアントからエージェントへの通信を制御するゲートウェイ。A2A を前提にしたアクセス制御、ポリシー、テレメトリ、監査、Cloud Logging/Trace 連携が中心。
- Model Armor: プロンプトインジェクション、不適切内容、機密情報漏えいなどの安全性対策を適用するサービス。
- IAM / Audit Logs / VPC Service Controls / CMEK など: Vertex AI/Google Cloud 側の標準的なセキュリティ・監査・暗号化機能と組み合わせる。

Agent Gateway は 2026-05 時点の複数記事でプレビューまたは Private Preview として扱われている。G-gen 記事では、Agent Runtime と Gemini Enterprise のトラフィックは自動的に Agent Gateway 経由でルーティングされる一方、Cloud Run や GKE などから明示的に Agent Gateway を経由させる一般手順は公式ドキュメント上まだ限定的だと整理している。

### 3.4 Optimize

Optimize 領域は、エージェントの品質、速度、コスト、安全性を継続的に改善するための機能群である。

- Observability: Agent Runtime、ADK、Gemini Enterprise と連携したトレース/ログ/メトリクス。
- Trace: ユーザー要求からモデル呼び出し、ツール呼び出し、サブエージェント呼び出しまでを追う。
- Evaluation: オフライン評価、シミュレーション、オンライン評価、品質アラート。
- Prompt Optimizer: プロンプト改善を支援する機能。
- Example Store: 評価や改善用の具体例保存にも使われる。

## 4. Agent Runtime

Agent Runtime は、エージェントを Google Cloud 上にデプロイして運用するためのフルマネージド実行環境である。従来の Web サービスとして Cloud Run/GKE に載せることも可能だが、Agent Runtime はエージェント固有の機能を組み込んでいる点が違う。

主な特徴:

- フレームワーク非依存のエージェント実行基盤として説明される。
- ADK エージェントは SDK から比較的直接デプロイできる。
- LangChain、LangGraph、AG2、LlamaIndex、カスタム Python アプリも対象になり得る。
- セッション管理、Memory Bank、トレース、評価、ストリーミング、認証、スケーリングと組み合わせやすい。
- API 名や SDK 名には `ReasoningEngine` / `agent_engines` が残っている。

実装時の注意:

- デプロイ対象の依存関係は明示的に固定する必要がある。`requirements.txt` または SDK の `requirements` 指定が重要。
- 公式ドキュメントでは Python ベースのデプロイ例が中心である。
- Dockerfile、コンテナイメージ、ソースコード、Developer Connect 連携など複数のデプロイ経路がある。
- デプロイ後は IAM 権限、サービスアカウント、呼び出し元認証、API 有効化を明示的に設計する必要がある。

## 5. Sessions と Memory Bank

Sessions と Memory Bank は混同しやすいが、用途が異なる。

| 機能 | 主な対象 | ライフサイクル | 典型用途 |
|---|---|---|---|
| Sessions | 1つの会話・1つのタスク | 短期 | 会話履歴、現在の状態、ツール実行イベント、途中結果 |
| Memory Bank | ユーザーまたは主体ごとの長期記憶 | 長期 | ユーザー嗜好、過去の会話から抽出した永続的情報、パーソナライズ |

ADK では Memory Bank 連携のために `VertexAiMemoryBankService` が提供されている。G-gen 記事でも、ADK エージェントの場合はツールやコールバックとして Memory Bank を組み込めると整理されている。その他のフレームワークでは API 経由で利用する形になる。

設計上の論点:

- Memory Bank に何を保存してよいかは、プライバシー、同意、保持期間、削除要求に直結する。
- Sessions と Memory Bank を自動的にすべて同期する設計は危険で、長期記憶として残す情報の選別が必要。
- Memory Bank は利便性向上と同時に、誤った記憶・古い記憶・過剰なパーソナライズの問題を持つ。

## 6. A2A と MCP

A2A は Agent2Agent の略で、エージェント間通信のためのオープンプロトコルとして扱われている。MCP が「モデル/エージェントがツールやデータソースを呼び出す」文脈で語られるのに対し、A2A は「エージェントが別のエージェントに依頼する」文脈で使われる。

A2A の主要概念:

- Agent Card: エージェントの能力、認証、エンドポイント、入出力形式などを公開するメタデータ。
- Task / Message / Artifact: 依頼、会話、成果物を表す単位。
- JSON-RPC / HTTP / SSE など: 実装上の通信方式として扱われる。
- エージェント内部の実装は隠蔽できるため、相手が ADK、LangGraph、別クラウド、オンプレミスでも連携モデルを作れる。

Gemini Enterprise Agent Platform では、Agent Gateway、Agent Registry、Gemini Enterprise のエージェント発見/利用体験と A2A が強く関連する。

## 7. 指定 Codelab の位置付け

指定 Codelab「ADK を使用してマルチエージェント システムを作成し、Agent Runtime にデプロイして、A2A プロトコルを使用する」は、Agent Runtime の概念理解に加えて、ADK と A2A を組み合わせた実装パスを示す実践資料である。

この Codelab で確認できる要点:

- ADK はエージェント開発フレームワークとして位置付けられる。
- Agent Runtime はエージェントを管理・デプロイ・呼び出し可能にする実行基盤として扱われる。
- 複数エージェントをサービスとして分け、A2A で連携する構成が示される。
- Agent Card を公開し、別エージェントから発見・呼び出しできる構成が紹介される。
- Agent Runtime に載せることで、Cloud 側の認証、スケーリング、管理機能と接続しやすくなる。

保存画像:

- `images/codelab-adk-positioning.png`
- `images/codelab-agent-runtime-reference-architecture.png`
- `images/codelab-multi-agent-flow.png`

## 8. 公式発表ブログの整理

Google Cloud 公式ブログは、Gemini Enterprise Agent Platform を「企業がエージェントを構築し、管理し、改善するための包括的な基盤」として打ち出している。発表記事では、エージェントの作成から本番運用までを統合する文脈が強い。

ブログで目立つ論点:

- Gemini Enterprise と Agent Platform の一体化。
- ADK、Agent2Agent、MCP などのオープンなエコシステムを重視。
- 顧客事例として Burns & McDonnell、Color、Comcast、Geotab、ぐるなびなどが紹介される。
- 「Build / Scale / Govern / Optimize」の4分類で機能を見せている。
- 企業導入では、単なるチャットボットではなく、ワークフロー、専門エージェント、エージェント間協調、監査可能性が中心テーマになる。

保存画像:

- `images/google-cloud-blog-gemini-enterprise-agent-platform-hero.jpg`
- `images/google-cloud-blog-agent-platform-value-pillars.jpg`
- `images/google-cloud-blog-customer-use-cases.jpg`

## 9. G-gen 記事の整理

G-gen「Gemini Enterprise Agent Platformを徹底解説！」は、2026-05 時点の日本語解説として非常に情報量が多い。公式ドキュメントの各機能を横断し、UI やプレビュー機能の位置付けを補っている。

特に有用な整理:

- Agent Studio は Gemini Enterprise 側の UI 体験として説明される。
- Agent Garden にはサンプルエージェントやパートナー提供エージェントが並ぶ。
- Agent Runtime は旧 Vertex AI Agent Engine の後継的な位置付けとして説明される。
- Sessions は単一セッションの状態、Memory Bank は複数セッションをまたぐ長期記憶として区別される。
- Agent Gateway は Agent Registry と組み合わせて使われ、アクセス制御・テレメトリ・Cloud Logging/Trace 連携を担う。
- 一部機能は Preview / Private Preview として扱われており、正式提供状況の確認が必要。

同じ G-gen の「Vertex AI Agent Engineを徹底解説！」も、旧名称時代の Agent Runtime 理解に役立つ。SDK 名、`ReasoningEngine` API、デプロイ・呼び出し・セッションの実装差分を確認する補助資料になる。

保存画像:

- `images/ggen-agent-platform-overview.png`
- `images/ggen-memory-bank-overview.png`
- `images/ggen-agent-gateway-modes.png`

## 10. 周辺記事・二次情報

Computerworld の Gemini Enterprise 関連記事では、Gemini Enterprise が企業内ワークフローと AI エージェントを統合する方向性が強調されている。Google Cloud の公式ブログよりも、業務アプリや協調ワークフローへの導入文脈に寄せた見方になっている。

二次情報を読む際の注意:

- `Gemini Enterprise` と `Gemini Enterprise Agent Platform` が混ざって語られることがある。
- `Agent Engine`、`Reasoning Engine`、`Agent Runtime` の名称が記事時点により異なる。
- Preview / Private Preview の機能が、正式提供済みの機能と同列に扱われることがある。
- UI 名称やコンソールの導線は短期間で変わりやすい。

## 11. プレビュー・名称・API 互換性の注意

2026-05 時点で、以下は特に注意が必要である。

- Agent Runtime の API/SDK 名に `ReasoningEngine` / `agent_engines` が残る。
- Agent Gateway はドキュメントや記事上でプレビュー扱いの表現が目立つ。
- Agent Garden、Managed Agents API、Skill Registry などはプレビュー扱いまたは提供範囲が限定的に見える。
- Gemini Enterprise のエディション、Google Cloud プロジェクト、Vertex AI API、Discovery Engine API、IAM ロールなどにより利用可能機能が変わる可能性がある。
- Codelab の手順は、API 名・リージョン・SDK バージョン・コンソール画面の変更に影響されやすい。

## 12. 技術採用時の確認リスト

実装・検証に入る前に確認すべき項目:

- 対象リージョンで Agent Runtime / Memory Bank / Agent Gateway / Gemini Enterprise 連携が使えるか。
- 利用する機能が GA、Preview、Private Preview のどれか。
- SDK バージョンと API 名称の対応。特に `vertexai.preview.reasoning_engines` と `google.genai` 系の使い分け。
- 認証方式。ユーザー代理、サービスアカウント、エージェント ID、OAuth、IAM の境界。
- Agent Runtime に載せるか、Cloud Run/GKE 等に載せて A2A/MCP を自前管理するか。
- Sessions と Memory Bank の保存範囲、保持期間、削除運用。
- Agent Gateway を利用する場合、Agent Registry への登録、Agent Card、ポリシー、ログ/トレース連携の設計。
- 評価データ、Example Store、オンライン評価、監視アラートをどこまで入れるか。

## 13. コンポーネント別ソースマップ

公式Docsのナビゲーションから確認できる主要ページを、調査対象ごとに整理する。

### Build

| 領域 | 主要ページ | 調査観点 |
|---|---|---|
| Build overview | [Build](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build) | Build 領域の全体像 |
| Agent Runtime 開発 | [Runtime overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime) | Agent Runtime 向けエージェント開発 |
| Runtime setup | [Setup](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime/setup) | SDK/API/プロジェクト準備 |
| Runtime quickstart | [Develop with agent frameworks](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime/quickstart) | フレームワーク利用の導入 |
| ADK | [ADK overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/adk) | ADK の位置付け |
| ADK on Runtime | [Quickstart: ADK on Agent Runtime](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime/quickstart-adk) | ADK エージェントの実装と Runtime 連携 |
| A2A agent | [Create an A2A agent](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime/create-an-a2a-agent) | Agent Card / A2A 実装 |
| LangChain | [Create a LangChain agent](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime/create-a-langchain-agent) | LangChain 連携 |
| LangGraph | [Create a LangGraph agent](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime/create-a-langgraph-agent) | LangGraph 連携 |
| AG2 | [Create an AG2 agent](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime/create-an-ag2-agent) | AG2 連携 |
| LlamaIndex | [Create a LlamaIndex agent](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime/create-a-llamaindex-agent) | LlamaIndex 連携 |
| Custom agent | [Create a custom agent](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime/create-a-custom-agent) | 独自エージェント |
| Agent Garden | [Agent Garden](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/agent-garden) | サンプル/テンプレート/パートナーエージェント |
| Managed Agents | [Managed Agents overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents) | Google 管理エージェント |
| Skill Registry | [Skill Registry](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/skill-registry) | スキル登録・再利用 |
| RAG Engine | [RAG overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/rag-engine/rag-overview) | RAG 基盤 |
| Vector Search | [Vector Search overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/vector-search/overview) | ベクトル検索 |
| Agent Search | [Use Agent Search](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/vertex-ai-search) | エンタープライズ検索連携 |

### Scale

| 領域 | 主要ページ | 調査観点 |
|---|---|---|
| Scale overview | [Scale](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale) | Scale 領域の全体像 |
| Deploy agents | [Deploy agents](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/deploy-an-agent) | Agent Runtime へのデプロイ |
| Manage deployed agents | [Manage deployed agents](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/manage-deployed-agents) | デプロイ済みエージェント管理 |
| Agent access | [Manage agent access](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/manage-agent-access) | 呼び出し権限 |
| Revisions/traffic | [Manage revisions and traffic](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/manage-revisions-and-traffic) | リビジョン・トラフィック分割 |
| Tracing | [Set up tracing](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/tracing) | Runtime トレース設定 |
| Logging | [Set up logging](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/logging) | ログ設定 |
| Monitoring | [Set up monitoring](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/monitoring) | メトリクス・監視 |
| Use agents | [Use an agent](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/use-an-agent) | Runtime 上のエージェント呼び出し |
| A2A use | [Use an A2A agent](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/use-an-a2a-agent) | A2A エージェント呼び出し |
| Agent Identity | [Agent Identity with Agent Runtime](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/agent-identity) | Runtime と ID |
| Gateway routing | [Route traffic through Agent Gateway](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/agent-gateway-runtime-deploy) | Runtime から Gateway へのルーティング |
| Streaming | [Bidirectional streaming](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/bidirectional-streaming) | 双方向ストリーミング |
| PSC | [Private Service Connect interfaces](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/private-service-connect-interface) | プライベート接続 |
| Sessions | [Sessions overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sessions) | 短期状態管理 |
| Sessions with ADK | [Manage sessions with ADK](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sessions/manage-with-adk) | ADK からの Session 利用 |
| Sessions with API | [Manage sessions using API](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sessions/manage-with-api) | API からの Session 利用 |
| Memory Bank | [Memory Bank overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank) | 長期記憶 |
| Memory setup | [Set up Memory Bank](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/setup) | 初期設定 |
| Memory API | [Memory Bank API quickstart](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/api-quickstart) | API 利用 |
| Memory ADK | [Memory Bank ADK quickstart](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/adk-quickstart) | ADK 連携 |
| Code Execution | [Code Execution overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sandbox/code-execution-overview) | サンドボックス実行 |

### Govern

| 領域 | 主要ページ | 調査観点 |
|---|---|---|
| Govern overview | [Govern](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern) | Govern 領域の全体像 |
| Safety | [Safety](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/safety) | Responsible AI |
| Share agent | [Share an agent](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/share-agent) | 共有 |
| Agent Identity | [Agent Identity overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/agent-identity-overview) | ID と権限 |
| Agent Registry | [Agent Registry](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/agent-registry) | エージェント登録 |
| Policies | [Policies overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/policies/overview) | ポリシー |
| IAM policies | [Create IAM policies](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/policies/assign-identity-iam) | IAM 制御 |
| Semantic governance | [Configure semantic governance policies](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/policies/configure-semantic-governance) | 意味ベースの制御 |
| Agent Gateway | [Agent Gateway overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/gateways/agent-gateway-overview) | Gateway 全体像 |
| Gateway setup | [Set up an Agent Gateway](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/gateways/set-up-agent-gateway) | 初期設定 |
| Delegated auth | [Delegate authorization](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/gateways/delegate-authorization) | 委任認可 |
| Gateway monitoring | [Monitor Agent Gateway traffic](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/gateways/monitor-agent-gateway) | Gateway 監視 |
| Gemini Enterprise routing | [Route Gemini Enterprise traffic through Agent Gateway](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/gateways/agent-gateway-ge-deploy) | Gemini Enterprise 連携 |
| Model Armor | [Configure Model Armor on a gateway](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/configure-model-armor) | 入出力安全性 |
| Security findings | [View security findings](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/view-security-findings) | Security Command Center 等 |

### Optimize

| 領域 | 主要ページ | 調査観点 |
|---|---|---|
| Optimize overview | [Optimize](https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize) | Optimize 領域の全体像 |
| Observability | [Observability overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize/observability/overview) | トレース/ログ/関係図 |
| Traces | [View agent traces](https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize/observability/traces) | 実行詳細 |
| Topology | [View agent relationships](https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize/observability/topology) | エージェント関係 |
| Evaluation | [Agent evaluation](https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize/evaluation/agent-evaluation) | 評価全体像 |
| Evaluate agents | [Evaluate your agents](https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize/evaluation/evaluate-agents) | 評価実行 |
| Offline eval | [Run Offline Evaluations](https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize/evaluation/evaluate-offline) | オフライン評価 |
| Simulation | [Simulate agent behavior](https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize/evaluation/evaluate-simulated) | シミュレーション評価 |
| Online monitors | [Continuous evaluation with Online Monitors](https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize/evaluation/evaluate-online) | オンライン評価 |
| Metrics | [Manage evaluation metrics](https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize/evaluation/manage-metrics) | 評価指標 |
| Quality alerts | [Configure quality alerts](https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize/evaluation/quality-alerts) | 品質アラート |
| Prompt optimization | [Optimize agent prompts](https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize/evaluation/optimize-agent) | プロンプト改善 |
| Example Store | [Example Store overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize/example-store/overview) | 例・デモ保存 |

## 14. 保存した画像一覧

各画像の横にある `.meta` ファイルに、ダウンロード元ページ、直接URL、メモを記録した。

| ファイル | 出典 |
|---|---|
| `images/google-cloud-blog-gemini-enterprise-agent-platform-hero.jpg` | Google Cloud Blog |
| `images/google-cloud-blog-agent-platform-value-pillars.jpg` | Google Cloud Blog |
| `images/google-cloud-blog-customer-use-cases.jpg` | Google Cloud Blog |
| `images/official-docs-geap-architecture.png` | Google Cloud Docs Agent Platform overview |
| `images/official-docs-memory-bank-concept.png` | Google Cloud Docs Memory Bank |
| `images/official-docs-agent-gateway-modes.png` | Google Cloud Docs Agent Gateway |
| `images/official-docs-agent-gateway-access-control.png` | Google Cloud Docs Agent Gateway |
| `images/codelab-adk-positioning.png` | Google Codelab |
| `images/codelab-agent-runtime-reference-architecture.png` | Google Codelab |
| `images/codelab-multi-agent-flow.png` | Google Codelab |
| `images/ggen-agent-platform-overview.png` | G-gen Tech Blog |
| `images/ggen-memory-bank-overview.png` | G-gen Tech Blog |
| `images/ggen-agent-gateway-modes.png` | G-gen Tech Blog |

## 15. 出典一覧

### 公式ドキュメント

- [Agent Platform overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/overview)
- [Build agents and apps with Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build)
- [Scale agents with Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale)
- [Govern agents with Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern)
- [Optimize agents with Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/optimize)
- [Agent Runtime overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime)
- [Deploy agents to Agent Runtime](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/deploy-an-agent)
- [Sessions overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sessions)
- [Memory Bank overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank)
- [Agent Gateway overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/gateways/agent-gateway-overview)
- [A2A Protocol Specification](https://a2a-protocol.org/latest/specification/)
- [Agent Development Kit documentation](https://google.github.io/adk-docs/)

### Codelab

- [ADK を使用してマルチエージェント システムを作成し、Agent Runtime にデプロイして、A2A プロトコルを使用する](https://codelabs.developers.google.com/codelabs/create-multi-agents-adk-a2a?hl=ja)
- [Secure cross-cloud agentic AI applications with Agent Platform](https://codelabs.developers.google.com/next26/aiinfra-learning-pod/screen1-securing-cross-cloud-agentic)

### Google Cloud Blog

- [次世代のエージェントを推進する Gemini Enterprise Agent Platform を発表](https://cloud.google.com/blog/ja/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform)
- [Build multi-agent systems with Google's Agent Development Kit](https://cloud.google.com/blog/products/ai-machine-learning/build-multi-agent-systems-with-adk)
- [Announcing the Agent2Agent Protocol](https://cloud.google.com/blog/products/ai-machine-learning/a2a-a-new-era-of-agent-interoperability)

### ユーザー記事・二次情報

- [G-gen: Gemini Enterprise Agent Platformを徹底解説！](https://blog.g-gen.co.jp/entry/gemini-enterprise-agent-platform-explained)
- [G-gen: Vertex AI Agent Engineを徹底解説！](https://blog.g-gen.co.jp/entry/vertex-ai-agent-engine-explained)
- [Computerworld: Gemini Enterprise update brings AI agents into collaborative workflows](https://www.computerworld.com/article/4161990/gemini-enterprise-update-brings-ai-agents-into-collaborative-workflows.html)
