summary: Hono.js、PostgreSQL、Drizzle、Zod、Firebase Auth で掲示板 API をゼロから作るバックエンド入門
id: honojs-backend
categories: Web, TypeScript, Backend, Firebase
environments: Web
status: Draft
feedback link: https://github.com/gdg-jp/honojs-backend-example/issues
author: GDG on Campus University of Osaka

# Hono.js で掲示板バックエンド API サーバーを作ろう

## はじめに

Duration: 0:03:00

このコードラボでは、`npm create hono@latest` でプロジェクトを作るところから始めて、先に React SPA を同じ Hono サーバーから配信します。その後、Hono.js、PostgreSQL、Drizzle、Zod、Firebase Auth を使った掲示板 API サーバーを少しずつ育て、Google ログインしたユーザーだけが投稿できる掲示板にします。

![OGP](img/ogp.png)

### Discord で質問する

詰まったところ、エラー全文、スクリーンショットは Discord の `#260625-honojs-backend` に共有してください。Firebase Admin SDK の `serviceAccount.json` も、このチャンネルで講師から配布します。

> **Tips:** エラーは要約せず、そのまま貼ると原因を探しやすくなります。

### このコードラボで作るもの

単一スレッドの掲示板 API サーバーを作ります。最初はメモリ上の配列に投稿を保存し、そのあと PostgreSQL に保存先を切り替えます。

- `GET /api/posts` で投稿一覧を取得できる
- `POST /api/posts` で新しい投稿を作成できる
- 投稿を PostgreSQL に保存できる
- Zod で投稿内容を検証できる
- Firebase ID トークンでログイン済みユーザーだけ投稿できる
- React SPA を Hono サーバーから配信できる

### このコードラボで学ぶこと

- Hono.js で Web API の入口を作る方法
- HTTP リクエストとレスポンスを確認する方法
- メモリ保存と DB 保存の違いを体験する方法
- Drizzle で PostgreSQL のテーブルを定義して読み書きする方法
- Zod で API リクエストを検証する方法
- Firebase Admin SDK で ID トークンを検証する方法

### 必要なもの

- Windows または macOS の PC
- Google Chrome
- Visual Studio Code
- Node.js 24 LTS
- Git
- Docker Desktop
- Google アカウント

### 前提知識

- JavaScript または TypeScript の基本的な理解
- 配列、object、関数、非同期処理という言葉を見たことがある程度の理解
- React を少し触ったことがある程度の理解

### このコードラボで扱わないこと

- Firebase プロジェクトの作成
- React コンポーネントの詳しい作り方
- SQL migration の本格運用
- 投稿の編集、削除、複数スレッド化
- 本番デプロイ、監視、セキュリティ設計

## セットアップ

Duration: 0:20:00

このステップでは、PC に開発環境を入れます。Node.js、Git、Docker Desktop が入っていない前提で進めます。

### Windows のセットアップ手順

Windows では、ブラウザで公式サイトを開いてインストーラをダウンロードします。PowerShell は、スタートメニューで `PowerShell` と検索して開きます。

#### Node.js をインストールする

Node.js は、TypeScript や Hono サーバーを動かすために使います。公式サイトから **LTS** と書かれた Windows Installer をダウンロードして実行します。

<button>
  [Node.js LTS をダウンロード](https://nodejs.org/en/download)
</button>

インストール後、PowerShell を開き直して確認します。

```powershell
node --version
npm --version
```

`v24.x.x` と `11.x.x` のように表示されれば成功です。`node` または `npm` が見つからない場合は、PowerShell を閉じて開き直します。それでも動かない場合は PC を再起動します。

#### Git をインストールする

Git は、完成コードや各ステップの checkpoint を確認するために使います。公式の Git ダウンロードページから Windows 版をダウンロードします。

<button>
  [Git for Windows をダウンロード](https://git-scm.com/download/win)
</button>

インストーラでは、基本的にデフォルト設定で進めます。迷ったら次の項目だけ確認します。

- **Adjusting your PATH environment** は `Git from the command line and also from 3rd-party software` を選ぶ
- **Default branch name** は `main` を使う設定にする
- エディタ選択は Visual Studio Code を選べれば選ぶ

インストール後、PowerShell を開き直して確認します。

```powershell
git --version
```

`git version 2.x.x` のように表示されれば成功です。

#### Docker Desktop をインストールする

Docker Desktop は、PostgreSQL を自分の PC で起動するために使います。公式の Windows 向けインストールページを開き、**Docker Desktop for Windows** をダウンロードします。

<button>
  [Docker Desktop for Windows をダウンロード](https://docs.docker.com/desktop/setup/install/windows-install/)
</button>

インストール後、Docker Desktop を起動します。初回起動では利用規約の確認や WSL まわりの設定が表示されることがあります。画面の案内に従って進め、必要なら PC を再起動します。

Docker Desktop が起動したら、PowerShell で確認します。

```powershell
docker --version
docker compose version
```

`Docker version ...` と `Docker Compose version ...` が表示されれば成功です。

> **Troubleshooting:** `docker` コマンドが見つからない場合は、Docker Desktop が起動しているか確認し、PowerShell を開き直します。Windows では Docker Desktop のインストール後に再起動が必要になることがあります。

#### Visual Studio Code をインストールする

Visual Studio Code は、コードを編集するためのエディタです。公式サイトから Windows 版をダウンロードします。

<button>
  [Visual Studio Code をダウンロード](https://code.visualstudio.com/download)
</button>

インストール後、VS Code を開きます。メニューが英語でも問題ありません。日本語にしたい場合は、拡張機能で `Japanese Language Pack` を検索してインストールします。

### Mac のセットアップ手順

macOS では、ブラウザで公式サイトを開いてインストーラをダウンロードします。ターミナルは `Cmd + Space` で Spotlight を開き、`Terminal` と入力して起動します。

#### Node.js をインストールする

Node.js は、TypeScript や Hono サーバーを動かすために使います。公式サイトから **LTS** と書かれた macOS Installer をダウンロードして実行します。

<button>
  [Node.js LTS をダウンロード](https://nodejs.org/en/download)
</button>

インストール後、ターミナルを開き直して確認します。

```bash
node --version
npm --version
```

`v24.x.x` と `11.x.x` のように表示されれば成功です。

#### Git をインストールする

Git は、完成コードや各ステップの checkpoint を確認するために使います。macOS では、Xcode Command Line Tools を入れると Git も使えるようになります。

```bash
xcode-select --install
```

画面が表示されたら **Install** を押します。すでにインストール済みの場合は、そのまま次に進みます。

Git 公式サイトの macOS インストールページにも、複数のインストール方法がまとまっています。

<button>
  [Git の macOS インストール手順を開く](https://git-scm.com/install/mac)
</button>

インストール後、ターミナルを開き直して確認します。

```bash
git --version
```

`git version 2.x.x` のように表示されれば成功です。

#### Docker Desktop をインストールする

Docker Desktop は、PostgreSQL を自分の PC で起動するために使います。公式の Mac 向けインストールページを開き、自分の Mac に合った版を選びます。

<button>
  [Docker Desktop for Mac をダウンロード](https://docs.docker.com/desktop/setup/install/mac-install/)
</button>

Apple Silicon の Mac は **Apple silicon**、Intel Mac は **Intel chip** を選びます。ダウンロードした `.dmg` を開き、Docker を Applications フォルダへドラッグします。

Docker Desktop を起動し、初回設定を進めます。起動後、ターミナルで確認します。

```bash
docker --version
docker compose version
```

`Docker version ...` と `Docker Compose version ...` が表示されれば成功です。

> **Troubleshooting:** `docker` コマンドが見つからない場合は、Docker Desktop が起動しているか確認し、ターミナルを開き直します。

#### Visual Studio Code をインストールする

Visual Studio Code は、コードを編集するためのエディタです。公式サイトから macOS 版をダウンロードします。

<button>
  [Visual Studio Code をダウンロード](https://code.visualstudio.com/download)
</button>

ダウンロードした `.zip` を開き、`Visual Studio Code.app` を Applications フォルダへ移動します。

ターミナルから `code .` で VS Code を開きたい場合は、VS Code を起動して `Cmd + Shift + P` を押し、`Shell Command: Install 'code' command in PATH` を実行します。

## Webアプリ・バックエンド概論

Duration: 0:10:00

実装に入る前に、このコードラボで作るものの全体像を確認します。

たとえば、掲示板で投稿ボタンを押したとします。ブラウザは投稿内容を HTTP リクエストとしてバックエンドに送ります。バックエンドはログイン中のユーザーを確認し、投稿内容を検査し、データベースに保存して、結果を JSON で返します。

この一連の流れを作るのが、今回扱うバックエンド開発です。

![Webアプリケーションとバックエンドの全体像](img/webapp-backend-overview.png)

### Webアプリケーションとは

Web アプリケーションは、Web ブラウザを通して入出力するアプリケーションです。

ブラウザは HTML、CSS、JavaScript、WASM などを使って画面を表示します。ユーザーがボタンを押したり、フォームを送信したりすると、ブラウザは HTTP または HTTPS でサーバーにリクエストを送ります。

Android や iOS のネイティブアプリ、Windows や macOS のデスクトップアプリは、見た目そのものは Web ではありません。しかし、裏側では Web アプリケーションが提供する Web API を呼び出していることがよくあります。

### フロントエンドとバックエンド

フロントエンドは、ユーザーが直接触る画面を担当します。ボタン、フォーム、投稿一覧、エラーメッセージなど、ブラウザに表示される部分です。

バックエンドは、データの保存、ログイン確認、入力チェック、権限確認、外部サービス連携などを担当します。

今回の掲示板では、投稿ボタンを押すと、フロントエンドが投稿内容をバックエンドに送ります。バックエンドはその内容を確認し、必要ならデータベースに保存し、保存した結果をフロントエンドへ返します。

### URL、DNS、HTTPS

Web アプリケーションにアクセスするとき、ブラウザは URL をもとに接続先を探します。

たとえば、`https://example.com/api/posts` という URL では、`example.com` がホスト、`/api/posts` がパスです。

DNS は、`example.com` のようなドメイン名から接続先を探す仕組みです。HTTPS は、HTTP を暗号化して送る仕組みです。Web アプリにアクセスするとき、ブラウザは DNS で接続先を探し、HTTPS でサーバーと通信します。

![URL の各部分の名前](img/url-anatomy.png)

### HTTPリクエストとレスポンス

HTTP は、ブラウザやアプリとサーバーがやり取りするためのプロトコルです。

クライアントからサーバーへ送るものをリクエスト、サーバーからクライアントへ返すものをレスポンスと呼びます。リクエストには、メソッド、パス、ホスト、ヘッダー、Cookie、ボディなどが含まれます。レスポンスには、ステータスコード、ヘッダー、ボディなどが含まれます。

![HTTP メソッドとステータスコードの一覧](img/http-method-status-table.png)

### Webサーバーとアプリケーションサーバー

Web サーバーは、HTTP リクエストを受け取り、レスポンスを返すサーバーです。

`Apache`、`IIS`、`nginx` は、ルーティング、リバースプロキシ、キャッシュ、ロードバランスなどを担当することが多いソフトウェアです。いわば、通信の交通整理係です。

一方で、`Next.js`、`Hono`、`Go net/http`、`Laravel`、`Rails` などは、実際のサービスの処理を書くために使われます。UI や API の実装、ロジックの制御、データベース呼び出しなどを担当します。

クラウド環境では、Apache や nginx を直接触らないことも多くあります。Cloudflare の Pingora proxy のように、現代のクラウドインフラでは、役割ごとに独自実装のソフトウェアが動いていることもあります。ただし、Apache や nginx が担っていた「入口」「振り分け」「キャッシュ」「負荷分散」の考え方は、今でも重要です。

![Webサーバーとアプリケーションサーバーの違い](img/web-server-app-server.png)

### Hono.jsの位置づけ

Hono は、HTTP リクエストをプログラムで扱いやすくする Web アプリケーションフレームワークです。

「このパスにこのメソッドで来たら、この処理を実行する」というルーティングを書けます。認証、バリデーション、データベースアクセスなどの処理を組み合わせて、Web API を実装します。

Hono 自体がデータベースやログイン機能をすべて持っているわけではありません。それらをつなぎ、HTTP リクエストとアプリケーションの処理を結びつけるための、薄くて扱いやすい土台として使います。

### Node.jsでWebサーバーを動かす背景

昔の Web サーバーでは、リクエストごとにプロセスやスレッドを使う方式が多く、接続数が増えると待ち時間が増えやすいことがありました。

C10K 問題は、1 台のサーバーに接続するクライアントが 1 万台に達すると、サーバー性能に余裕があってもレスポンスが遅くなる問題です。

Node.js は、イベントループと非同期 I/O により、データベースや外部 API の待ち時間中に他のリクエストを処理しやすい仕組みを持っています。

ただし、これは主に I/O Bound な処理で効果を発揮します。I/O Bound な処理とは、データベース呼び出しや外部 API 呼び出しのように、サーバー外部の処理を待っている間、Web アプリケーション側ではあまり CPU を使わない処理です。

画像処理や動画変換、重い計算のように CPU を長時間使う処理は、Node.js の得意分野ではありません。今回のような Web API では、データベース呼び出しや認証確認などの I/O 待ちが多いため、Node.js と相性がよいです。

![昔の方式と Node.js の方式](img/nodejs-event-loop.png)

### Web APIとは

Web API は、HTML の画面ではなく、JSON などのデータを返す Web アプリケーションです。

フロントエンド、モバイルアプリ、デスクトップアプリ、他のサーバーなどから呼び出せます。

たとえば、「投稿を作成する」API は次のようなリクエストになります。

- HTTP メソッド: `POST`
- パス: `/api/posts`
- ヘッダー: `Authorization: Bearer JWT_TOKEN_XYZ`
- リクエストボディ: `{ "content": "今日もいい天気" }`

バックエンドはそのリクエストを受け取り、`JWT_TOKEN_XYZ` が正しいトークンか確認します。正しければ対応するユーザー情報を取得し、データベースに投稿を追加します。

最後に `200 OK` で、次のようなデータを返します。

```json
{
  "content": "今日もいい天気",
  "authorUid": "abcdef",
  "authorName": "Rei"
}
```

![HTTP リクエストとレスポンスの流れ](img/http-request-response-flow.png)

### データベース

データベースは、アプリケーションのデータを保存する場所です。よく `DB` と省略されます。

DBMS はデータベース管理システム、RDBMS はリレーショナルデータベース管理システムの略です。

RDB は、データを行と列の表形式で管理し、複数の表を関連づけて扱うデータベースです。レコードはデータの単位で、投稿データやユーザーデータなどがこれにあたります。カラムはデータの属性で、投稿文、作成日時、ユーザー ID などがこれにあたります。

PostgreSQL、MySQL などが代表的な RDBMS です。Google Cloud の Cloud SQL や AWS の Aurora は、PostgreSQL や MySQL などをクラウド上で管理しやすくしたサービスです。

NoSQL は、RDB 以外のデータベースの総称です。KVS やドキュメント指向データベースなどがあります。Firestore や DynamoDB などが代表例です。

NoSQL はアクセスパターンが合うと高速で扱いやすい一方で、複雑な関連や整合性が重要な場面では RDB が向いていることも多くあります。このコードラボでは RDB を扱います。

![RDB と NoSQL のデータ管理の違い](img/db-rdb-nosql.png)

### ログイン、認証、認可

ログインまわりでは、認証と認可が重要です。

認証は「あなたは誰か」を確認することです。認可は「あなたはその操作をしてよいか」を確認することです。

たとえば、ログイン済みでも、他人の投稿は削除できません。この場合、「ログインしているか」は認証の話で、「その投稿を削除してよいか」は認可の話です。

Web アプリでは、Cookie と Session を使う方式がよくあります。Cookie はブラウザに保存され、リクエスト時にサーバーへ送られる小さな情報です。Session は、サーバー側にログイン状態を保存し、Cookie にはその ID だけを入れる方式です。

モバイルアプリや Web API では、トークンベース認証もよく使われます。JWT ベース認証では、クライアントがトークンを送り、バックエンドがそのトークンを検証してユーザーを特定します。

今回は簡単のために Firebase Auth を使い、バックエンド側で Firebase ID トークンを検証してユーザーを特定します。

![Session 認証の流れ](img/auth-session-flow.png)

![トークンベース認証の流れ](img/auth-token-flow.png)

### バリデーション

バリデーションは、入力内容が正しいか確認する処理です。

まず、バリデーションにはフロントエンドで行われるものと、バックエンドで行われるものの 2 つがあります。

Web のフォームで送信ボタンを押した直後に赤文字が出るのは、フロントエンドのバリデーションです。JavaScript で、入力された文字列が正常かどうかをブラウザ上で判定しています。

送信ボタンを押して少し待った後にエラーが表示されるのは、バックエンドのバリデーションです。フォームの入力内容をサーバーが確認し、不正な内容があったのでエラーを返しています。

「バックエンドのバリデーションはいらないのでは?」と思いましたか？

現実では、Web API をフロントエンドの UI 以外から直接呼び出す人がいるかもしれません。たとえば、`curl` などを使えば、ブラウザの画面を通らずに Web API へリクエストを送れます。

その場合、フロントエンドの JavaScript による判定は実行されません。そもそもその JavaScript が存在しないからです。

そのため、バックエンドの Web API が門番として最終チェックをします。

フロントエンドのバリデーションは、基本的には UX を高めるためのものです。赤文字が表示されるまで 1 秒も 2 秒も待つと使いづらいので、ブラウザ上で先にチェックしています。

![フロントエンドとバックエンドのバリデーション](img/validation-frontend-backend.png)

### このコードラボで作るバックエンドの全体像

このコードラボでは、次の流れでバックエンドを作ります。

- Hono で HTTP リクエストを受け取る
- Firebase Auth のトークンを検証してユーザーを特定する
- リクエストボディをバリデーションする
- データベースにデータを保存・取得する
- 成功時は JSON を返し、失敗時は適切なステータスコードを返す

ここからは、この全体像を 1 つずつコードにしていきます。


## Hono プロジェクトを作成する

Duration: 0:10:00

ここから実装に入ります。まずは Hono の公式 starter から、新しい TypeScript プロジェクトを作成します。

> **Tips:** Hono は、Web API を作るための軽量な TypeScript フレームワークです。URL ごとに処理を書く「ルーティング」が中心で、今回のような小さな API サーバーを作り始めやすい道具です。

### 作業フォルダでプロジェクトを作成する

Windows の方は PowerShell で、macOS の方はターミナルで、作業用フォルダに移動してから進めます。

PowerShell はWindowsキーを押して Power と検索するとヒットします。  
ターミナルは Cmd + スペースキーを押してターミナル (Terminal) と検索するとヒットします。

作業用フォルダがまだない人、どのフォルダで作業すればよいかわからない人は、次のコマンドでホームディレクトリの下に `proj` フォルダを作ります。

```bash
cd ~
mkdir proj
cd proj
```

> **Tips:** `cd` は作業ディレクトリを移動するコマンドです。`~` は自分のホームディレクトリを表します。`mkdir proj` は `proj` という新しいフォルダを作ります。

`proj` フォルダに移動できたら、次を実行します。

```bash
npm create hono@latest honojs-backend-app
```

> **Tips:** `npm create` は、指定した starter から新しいプロジェクトを作るコマンドです。ここでは Hono 公式 starter を使って、`honojs-backend-app` というフォルダに最小構成の Hono アプリを作ります。

途中で質問が表示されたら、次のように選びます。

| 質問                                           | 選ぶもの |
| ---------------------------------------------- | -------- |
| `Which template do you want to use?`           | `nodejs` |
| `Do you want to install project dependencies?` | `Y`      |
| `Which package manager do you want to use?`    | `npm`    |

次のように表示されれば成功です。

```text
✔ Using target directory … honojs-backend-app
✔ Which template do you want to use? nodejs
✔ Do you want to install project dependencies? Yes
✔ Which package manager do you want to use? npm
✔ Cloning the template
✔ Installing project dependencies
🎉 Copied project files
Get started with: cd honojs-backend-app
```

`Do you want to install project dependencies?` で `Yes` を選んだ場合、`npm install` はすでに実行されています。次は作成されたフォルダに移動します。

```bash
cd honojs-backend-app
```

### VS Code で開く

次のコマンドで、作成したプロジェクトを VS Code で開きます。

```bash
code .
```

`code` コマンドが使えない場合は、VS Code のメニューから **File > Open Folder...** を選び、`honojs-backend-app` フォルダを開きます。

### 起動する

Hono starter が用意している開発用コマンドを実行します。

```bash
npm run dev
```

> **Tips:** `npm run dev` は、`package.json` の `scripts.dev` に書かれた開発用コマンドを実行します。Hono starter では、TypeScript のサーバーを起動し、変更があれば自動で再起動します。

`http://localhost:3000` のような URL が表示されたら、ブラウザで開きます。`Hello Hono!` のような文字が表示されれば成功です。

### 現時点のコードベース

この時点のディレクトリ構成は次のようになります。

```text
.
├── .gitignore
├── README.md
├── package-lock.json
├── package.json
├── src
│   └── index.ts
└── tsconfig.json
```

<button>
  [この時点のコードを見る: step-npm-create-hono](https://github.com/gdg-jp/honojs-backend-template/tree/step-npm-create-hono)
</button>

## 必要なライブラリを追加する

Duration: 0:08:00

このステップでは、後の手順で使うライブラリを先に追加します。package scripts は追加せず、Hono starter が最初から用意した `npm run dev`、`npm run build`、`npm start` を使います。DB 操作や React build には `npx` を使います。

### ライブラリを追加する

VSCode を開いて Ctrl + J (macOS は Cmd + J) を押してターミナルを開き、ターミナルから次のコマンドを実行します。

```bash
npm install @hono/node-server drizzle-orm pg zod firebase-admin
  \ react react-dom firebase @heroui/react @heroui/theme
  \ @react-aria/ssr framer-motion lucide-react

npm install -D vite @vitejs/plugin-react typescript tsx
  \ drizzle-kit @types/node @types/pg @types/react
  \ @types/react-dom tailwindcss @tailwindcss/vite
```

> **Tips:** `npm install` は、プロジェクトで使うライブラリを `node_modules` に入れ、`package.json` に記録するコマンドです。別の PC でも `npm install` すれば同じライブラリを復元できます。

> **Tips:** `-D` は「開発中だけ使うライブラリ」を意味します。`drizzle-kit` は DB 定義を反映するための開発用コマンドなので、`dependencies` ではなく `devDependencies` に入れます。

### 現時点のコードベース

この時点のディレクトリ構成は次のようになります。

```text
.
├── .gitignore
├── README.md
├── package-lock.json
├── package.json
├── src
│   └── index.ts
└── tsconfig.json
```

<button>
  [この時点のコードを見る: step-npm-install](https://github.com/gdg-jp/honojs-backend-template/tree/step-npm-install)
</button>

## React SPA を配信する

Duration: 0:17:00

このステップでは、先に React SPA を追加します。以降の API 実装では、curl に加えてブラウザからも動作確認できるようになります。React 側はこのコードラボの主役ではないため、1 ファイルを貼り付けて、Hono サーバーから配信できるようにします。

### Vite 設定を追加する

プロジェクト直下に `vite.config.ts` を作成します。

```ts:vite.config.ts
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    outDir: "dist/public",
    emptyOutDir: true
  },
  server: {
    proxy: {
      "/api": "http://localhost:3000"
    }
  }
});
```

Vite は React アプリをビルドするために使います。`proxy` は、React 開発サーバーから `/api` を呼んだときに Hono サーバーへ転送する設定です。

### Tailwind と HTML を追加する

プロジェクト直下に `tailwind.config.ts` を作成します。

```ts:tailwind.config.ts
import { heroui } from "@heroui/theme";
import type { Config } from "tailwindcss";

export default {
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx}",
    "./node_modules/@heroui/theme/dist/**/*.{js,ts,jsx,tsx}"
  ],
  plugins: [heroui()]
} satisfies Config;
```

プロジェクト直下に `style.css` を作成します。

```css:style.css
@import "tailwindcss";
@config "./tailwind.config.ts";

body {
  min-height: 100vh;
  background:
    radial-gradient(
      circle at 10% 0%,
      rgba(20, 184, 166, 0.18),
      transparent 28rem
    ),
    radial-gradient(
      circle at 85% 8%,
      rgba(244, 114, 182, 0.14),
      transparent 26rem
    ),
    #f7f8fb;
}
```

プロジェクト直下に `index.html` を作成します。

```html:index.html
<!doctype html>
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Hono.js Bulletin Board</title>
    <link rel="stylesheet" href="/style.css" />
    <script type="module" src="/src/client.tsx"></script>
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
```

### React SPA を追加する

`src/client.tsx` を作成し、次の内容を貼り付けます。

```tsx:src/client.tsx
import {
  Avatar,
  Button,
  Card,
  CardBody,
  CardHeader,
  HeroUIProvider,
  Input,
  Navbar,
  NavbarBrand,
  NavbarContent,
  Spinner,
  Textarea
} from "@heroui/react";
import { getApp, getApps, initializeApp } from "firebase/app";
import {
  GoogleAuthProvider,
  getAuth,
  onAuthStateChanged,
  signInWithPopup,
  signOut,
  type User
} from "firebase/auth";
import { Send } from "lucide-react";
import { StrictMode, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";

const firebaseConfig = {
  apiKey: "AIzaSyDUEhUzWwW8mOi4RaJCfKfhLFyQSwVbCZc",
  authDomain: "honojs-backend.firebaseapp.com",
  projectId: "honojs-backend",
  storageBucket: "honojs-backend.firebasestorage.app",
  messagingSenderId: "971208233892",
  appId: "1:971208233892:web:beb6fee5b1fefade79e731",
  measurementId: "G-7N53ZKXG6F"
};

interface Post {
  id: number;
  content: string;
  authorUid: string;
  authorName: string;
  authorPhotoUrl: string | null;
  createdAt: string;
}

const firebaseApp =
  getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);
const auth = getAuth(firebaseApp);
const provider = new GoogleAuthProvider();

const formatDate = (value: string) =>
  new Intl.DateTimeFormat("ja-JP", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));

const fetchPosts = async () => {
  const response = await fetch("/api/posts");

  if (!response.ok) {
    throw new Error("投稿一覧を取得できませんでした。");
  }

  const data = (await response.json()) as { posts: Post[] };
  return data.posts;
};

const App = () => {
  const [user, setUser] = useState<User | null>(null);
  const [authReady, setAuthReady] = useState(false);
  const [posts, setPosts] = useState<Post[]>([]);
  const [content, setContent] = useState("");
  const [isLoadingPosts, setIsLoadingPosts] = useState(true);
  const [isPosting, setIsPosting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const remaining = useMemo(() => 280 - content.length, [content]);

  useEffect(() => {
    return onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setAuthReady(true);
    });
  }, []);

  useEffect(() => {
    fetchPosts()
      .then(setPosts)
      .catch((caught: unknown) => {
        setError(
          caught instanceof Error
            ? caught.message
            : "投稿一覧を取得できませんでした。"
        );
      })
      .finally(() => {
        setIsLoadingPosts(false);
      });
  }, []);

  const handleLogin = async () => {
    setError(null);
    await signInWithPopup(auth, provider).catch((caught: unknown) => {
      setError(
        caught instanceof Error
          ? caught.message
          : "Googleログインに失敗しました。"
      );
    });
  };

  const handleSubmit = async () => {
    if (!user || content.trim().length === 0 || remaining < 0) {
      return;
    }

    setIsPosting(true);
    setError(null);

    try {
      const token = await user.getIdToken();
      const response = await fetch("/api/posts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ content })
      });

      const data = (await response.json()) as { post?: Post; error?: string };

      if (!response.ok || !data.post) {
        throw new Error(data.error ?? "投稿に失敗しました。");
      }

      setPosts((currentPosts) => [data.post as Post, ...currentPosts]);
      setContent("");
    } catch (caught) {
      setError(
        caught instanceof Error ? caught.message : "投稿に失敗しました。"
      );
    } finally {
      setIsPosting(false);
    }
  };

  if (!authReady) {
    return (
      <HeroUIProvider>
        <main className="grid min-h-screen place-items-center">
          <Spinner label="認証状態を確認しています" />
        </main>
      </HeroUIProvider>
    );
  }

  if (!user) {
    return (
      <HeroUIProvider>
        <main className="mx-auto grid min-h-screen max-w-md place-items-center px-6">
          <Card
            className="w-full border border-default-200 shadow-sm"
            radius="sm"
          >
            <CardHeader className="flex-col items-start gap-2 px-6 pt-6">
              <p className="text-sm font-medium text-primary">
                Hono.js Backend Workshop
              </p>
              <h1 className="text-2xl font-semibold tracking-normal text-foreground">
                掲示板 API にログイン
              </h1>
            </CardHeader>
            <CardBody className="gap-5 px-6 pb-6">
              <p className="text-sm leading-6 text-default-600">
                Google アカウントでログインすると、Firebase ID
                トークンを使って投稿できます。
              </p>
              {error ? (
                <div className="rounded-small border border-danger-200 bg-danger-50 px-4 py-3 text-sm text-danger-700">
                  {error}
                </div>
              ) : null}
              <Button color="primary" size="lg" onPress={handleLogin}>
                Google でログイン
              </Button>
            </CardBody>
          </Card>
        </main>
      </HeroUIProvider>
    );
  }

  return (
    <HeroUIProvider>
      <div className="min-h-screen">
        <Navbar
          className="border-b border-default-200 bg-background/80 backdrop-blur"
          maxWidth="xl"
        >
          <NavbarBrand>
            <p className="font-semibold text-foreground">掲示板 API</p>
          </NavbarBrand>
          <NavbarContent justify="end">
            <Avatar
              name={user.displayName ?? "User"}
              size="sm"
              src={user.photoURL ?? undefined}
            />
            <Button size="sm" variant="flat" onPress={() => signOut(auth)}>
              ログアウト
            </Button>
          </NavbarContent>
        </Navbar>

        <main className="mx-auto grid max-w-5xl gap-6 px-4 py-6 md:grid-cols-[22rem_1fr]">
          <section>
            <Card className="border border-default-200 shadow-sm" radius="sm">
              <CardHeader>
                <div>
                  <h2 className="text-lg font-semibold">新しい投稿</h2>
                  <p className="text-sm text-default-500">
                    280文字以内で書いてください。
                  </p>
                </div>
              </CardHeader>
              <CardBody className="gap-4">
                <Input
                  isReadOnly
                  label="投稿者"
                  value={user.displayName ?? "匿名ユーザー"}
                  variant="bordered"
                />
                <Textarea
                  label="内容"
                  minRows={5}
                  value={content}
                  variant="bordered"
                  onValueChange={setContent}
                />
                <div className="flex items-center justify-between gap-3">
                  <span
                    className={
                      remaining < 0
                        ? "text-sm text-danger"
                        : "text-sm text-default-500"
                    }
                  >
                    残り {remaining} 文字
                  </span>
                  <Button
                    color="primary"
                    endContent={<Send size={16} />}
                    isDisabled={content.trim().length === 0 || remaining < 0}
                    isLoading={isPosting}
                    onPress={handleSubmit}
                  >
                    投稿
                  </Button>
                </div>
                {error ? (
                  <div className="rounded-small border border-danger-200 bg-danger-50 px-4 py-3 text-sm text-danger-700">
                    {error}
                  </div>
                ) : null}
              </CardBody>
            </Card>
          </section>

          <section className="min-w-0">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-lg font-semibold">投稿一覧</h2>
              <span className="text-sm text-default-500">{posts.length}件</span>
            </div>
            {isLoadingPosts ? (
              <div className="grid min-h-64 place-items-center rounded-small border border-default-200 bg-background">
                <Spinner label="読み込み中" />
              </div>
            ) : posts.length === 0 ? (
              <div className="rounded-small border border-dashed border-default-300 bg-background px-6 py-12 text-center text-default-500">
                まだ投稿はありません。
              </div>
            ) : (
              <div className="grid gap-3">
                {posts.map((post) => (
                  <Card
                    key={post.id}
                    className="border border-default-200 shadow-sm"
                    radius="sm"
                  >
                    <CardBody className="gap-3">
                      <div className="flex items-center gap-3">
                        <Avatar
                          name={post.authorName}
                          size="sm"
                          src={post.authorPhotoUrl ?? undefined}
                        />
                        <div className="min-w-0">
                          <p className="truncate text-sm font-medium">
                            {post.authorName}
                          </p>
                          <p className="text-xs text-default-500">
                            {formatDate(post.createdAt)}
                          </p>
                        </div>
                      </div>
                      <p className="whitespace-pre-wrap break-words text-sm leading-6">
                        {post.content}
                      </p>
                    </CardBody>
                  </Card>
                ))}
              </div>
            )}
          </section>
        </main>
      </div>
    </HeroUIProvider>
  );
};

createRoot(document.getElementById("root") as HTMLElement).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

この React SPA は、`GET /api/posts` で投稿一覧を取得し、ログイン済みユーザーの Firebase ID トークンを `Authorization` ヘッダーに入れて `POST /api/posts` を呼びます。

### TypeScript の JSX 設定を React 用に変更する

Hono starter には、JSX を Hono 用に解釈する設定が入っている場合があります。React SPA を TypeScript でビルドできるように、`tsconfig.json` の `jsxImportSource` を React に変更します。

```diff json:tsconfig.json
     "jsx": "react-jsx",
-    "jsxImportSource": "hono/jsx",
+    "jsxImportSource": "react",
+    "rootDir": "./src",
     "outDir": "./dist"
   },
+  "include": ["src/**/*.ts", "src/**/*.tsx"],
   "exclude": ["node_modules"]
 }
```

### Hono からビルド済み SPA を配信する

`src/index.ts` を次のように変更します。

```diff ts:src/index.ts
+import { existsSync } from "node:fs";
+import { readFile } from "node:fs/promises";
+import { join } from "node:path";
import { serve } from "@hono/node-server";
+import { serveStatic } from "@hono/node-server/serve-static";
import { Hono } from "hono";
+import { logger } from "hono/logger";

+const publicDir = join(process.cwd(), "dist", "public");
+const indexHtml = join(publicDir, "index.html");

const app = new Hono();
const port = Number(process.env.PORT ?? 3000);

+app.use(logger());

-app.get("/", (c) => c.text("Hello Hono!"));
+app.get("/api/health", (c) => c.json({ ok: true }));

+app.use(
+  "/*",
+  serveStatic({
+    root: "./dist/public"
+  })
+);
+
+app.get("*", async (c) => {
+  if (c.req.path.startsWith("/api/")) {
+    return c.json({ error: "API route is not implemented yet." }, 404);
+  }
+
+  if (!existsSync(indexHtml)) {
+    return c.text(
+      "React SPA is not built yet. Run `npx vite build` first.",
+      404
+    );
+  }
+
+  return c.html(await readFile(indexHtml, "utf8"));
+});

serve(
  {
    fetch: app.fetch,
    port
  },
  (info) => {
    console.log(`Server is running on http://localhost:${info.port}`);
  }
);
```

`serveStatic` は、`dist/public` にある CSS や JavaScript を Hono から配信します。`app.get("*", ...)` は、React SPA の入口である `index.html` を返します。ただし `/api/` から始まる未実装の API は、HTML ではなく JSON の `404` を返すようにしておきます。

> **Troubleshooting:** `Error: listen EADDRINUSE: address already in use` が出た場合は、同じポートで別のサーバーが起動しています。すでに起動している `npm run dev` を `Ctrl + C` で止めるか、別のポートで `PORT=4000 npm run dev` のように起動します。

### ビルドして起動する

React SPA をビルドし、そのあと Hono サーバーをビルドします。この時点ではまだ投稿 API を作っていないため、ログイン後の投稿一覧にはエラーが表示されます。次のステップで `GET /api/posts` を作ると、画面から投稿一覧を確認できるようになります。

```bash
npx vite build
npm run build
npm start
```

ブラウザで [http://localhost:3000](http://localhost:3000) を開きます。Google ログイン画面が表示されれば成功です。

### 現時点のコードベース

この時点のディレクトリ構成は次のようになります。

```text
.
├── .gitignore
├── README.md
├── index.html
├── package-lock.json
├── package.json
├── src
│   ├── client.tsx
│   └── index.ts
├── style.css
├── tailwind.config.ts
├── tsconfig.json
└── vite.config.ts
```

<button>
  [この時点のコードを見る: step-react-spa](https://github.com/gdg-jp/honojs-backend-template/tree/step-react-spa)
</button>

## 投稿一覧 API を作る

Duration: 0:10:00

このステップでは、`GET /api/posts` を作ります。最初は DB を使わず、メモリ上の配列から投稿一覧を返します。

### post.ts を作成する

`src/post.ts` を作成し、次の内容を貼り付けます。

```ts:src/post.ts
import { Hono } from "hono";

export interface PostOutput {
  id: number;
  content: string;
  authorUid: string;
  authorName: string;
  authorPhotoUrl: string | null;
  createdAt: string;
}

const posts: PostOutput[] = [];

export const listPosts = async (): Promise<PostOutput[]> => posts;

export const postRoutes = new Hono().get("/", async (c) => {
  const rows = await listPosts();
  return c.json({ posts: rows });
});
```

`PostOutput` は、API がフロントエンドへ返す投稿の形です。今は `posts` が空配列なので、投稿一覧も空になります。

### index.ts から postRoutes を使う

`src/index.ts` を次のように変更します。

```diff ts:src/index.ts
import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { serve } from "@hono/node-server";
import { serveStatic } from "@hono/node-server/serve-static";
import { Hono } from "hono";
import { logger } from "hono/logger";
+import { postRoutes } from "./post.js";

const publicDir = join(process.cwd(), "dist", "public");
const indexHtml = join(publicDir, "index.html");

const app = new Hono();
const port = Number(process.env.PORT ?? 3000);

app.use(logger());

app.get("/api/health", (c) => c.json({ ok: true }));
+app.route("/api/posts", postRoutes);

app.use(
  "/*",
  serveStatic({
    root: "./dist/public"
  })
);

app.get("*", async (c) => {
  if (c.req.path.startsWith("/api/")) {
    return c.json({ error: "API route is not implemented yet." }, 404);
  }

  if (!existsSync(indexHtml)) {
    return c.text(
      "React SPA is not built yet. Run `npx vite build` first.",
      404
    );
  }

  return c.html(await readFile(indexHtml, "utf8"));
});

serve(
  {
    fetch: app.fetch,
    port
  },
  (info) => {
    console.log(`Server is running on http://localhost:${info.port}`);
  }
);
```

`app.route("/api/posts", postRoutes)` は、`postRoutes` に書いたルートを `/api/posts` の下にまとめて取り付けます。今回なら `postRoutes.get("/")` は `GET /api/posts` として動きます。

### curl で確認する

サーバーを起動します。すでに起動している場合は、`Ctrl + C` で止めてから起動し直します。

```bash
npm run dev
```

別のターミナルで次を実行します。

```bash
curl http://localhost:3000/api/posts
```

> **Tips:** `curl` は、ターミナルから HTTP リクエストを送るためのコマンドです。ブラウザを使わずに API のレスポンスだけを確認できるので、バックエンド開発でよく使います。

`{"posts":[]}` が返れば成功です。

### ブラウザで確認する

ブラウザで [http://localhost:3000](http://localhost:3000) を開きます。Google でログインし、掲示板画面の投稿一覧に `まだ投稿はありません。` と表示されれば成功です。

この時点で、React SPA は `GET /api/posts` を呼んでいます。API が空配列を返すので、画面にも「投稿がまだない」状態が表示されます。

### 現時点のコードベース

この時点のディレクトリ構成は次のようになります。

```text
.
├── .gitignore
├── README.md
├── index.html
├── package-lock.json
├── package.json
├── src
│   ├── client.tsx
│   ├── index.ts
│   └── post.ts
├── style.css
├── tailwind.config.ts
├── tsconfig.json
└── vite.config.ts
```

<button>
  [この時点のコードを見る: step-get-posts-memory](https://github.com/gdg-jp/honojs-backend-template/tree/step-get-posts-memory)
</button>

## 投稿作成 API を作る

Duration: 0:12:00

このステップでは、`POST /api/posts` を追加します。まだログインや DB は使わず、投稿をメモリ上の配列に保存します。

### post.ts を更新する

`src/post.ts` を次のように変更します。

```diff ts:src/post.ts
import { Hono } from "hono";

export interface PostOutput {
  id: number;
  content: string;
  authorUid: string;
  authorName: string;
  authorPhotoUrl: string | null;
  createdAt: string;
}

+export interface CreatePostInput {
+  content: string;
+  authorUid: string;
+  authorName: string;
+  authorPhotoUrl?: string;
+}

const posts: PostOutput[] = [];
+let nextId = 1;

export const listPosts = async (): Promise<PostOutput[]> => posts;

+export const createPost = async (
+  input: CreatePostInput
+): Promise<PostOutput> => {
+  const post = {
+    id: nextId,
+    content: input.content,
+    authorUid: input.authorUid,
+    authorName: input.authorName,
+    authorPhotoUrl: input.authorPhotoUrl ?? null,
+    createdAt: new Date().toISOString()
+  };
+
+  nextId += 1;
+  posts.unshift(post);
+  return post;
+};
+
 export const postRoutes = new Hono()
   .get("/", async (c) => {
     const rows = await listPosts();
     return c.json({ posts: rows });
+  })
+  .post("/", async (c) => {
+    const body = (await c.req.json().catch(() => null)) as {
+      content?: unknown;
+    } | null;
+
+    if (typeof body?.content !== "string" || body.content.trim().length === 0) {
+      return c.json({ error: "Invalid request body." }, 400);
+    }
+
+    const post = await createPost({
+      content: body.content.trim(),
+      authorUid: "temporary-user",
+      authorName: "仮ユーザー",
+      authorPhotoUrl: undefined
+    });
+
+    return c.json({ post }, 201);
   });
```

`posts.unshift(post)` は、新しい投稿を配列の先頭に追加します。掲示板では新しい投稿を上に出したいので、後ろではなく先頭に入れています。

### curl で投稿する

サーバーを起動し直します。

```bash
npm run dev
```

別のターミナルで次を実行します。

```bash
curl -X POST http://localhost:3000/api/posts \
  -H "Content-Type: application/json" \
  -d '{"content":"はじめての投稿です"}'
```

`"content":"はじめての投稿です"` を含む JSON が返れば成功です。次に一覧を取得します。

```bash
curl http://localhost:3000/api/posts
```

投稿した内容が `posts` の中に入っていれば成功です。

### ブラウザで確認する

ブラウザで [http://localhost:3000](http://localhost:3000) を開きます。Google でログインし、投稿フォームに `ブラウザからの投稿です` と入力して **投稿** ボタンを押します。

投稿一覧の先頭に入力した内容が表示されれば成功です。ブラウザからは、React SPA が `POST /api/posts` を呼び、成功した投稿を画面の一覧に追加しています。

### 現時点のコードベース

この時点のディレクトリ構成は次のようになります。

```text
.
├── .gitignore
├── README.md
├── index.html
├── package-lock.json
├── package.json
├── src
│   ├── client.tsx
│   ├── index.ts
│   └── post.ts
├── style.css
├── tailwind.config.ts
├── tsconfig.json
└── vite.config.ts
```

<button>
  [この時点のコードを見る: step-post-posts-memory](https://github.com/gdg-jp/honojs-backend-template/tree/step-post-posts-memory)
</button>

## PostgreSQL に保存する

Duration: 0:18:00

今の実装では、投稿はサーバーのメモリ上にあります。まずはその弱点を体験してから、Docker Compose、PostgreSQL、Drizzle を追加して DB に保存します。

### サーバーを再起動するとデータが消えることを確認する

投稿を1件作ったあと、サーバーを `Ctrl + C` で止めます。もう一度起動します。

```bash
npm run dev
```

別のターミナルで一覧を取得します。

```bash
curl http://localhost:3000/api/posts
```

さっき作った投稿が消えて、`{"posts":[]}` に戻ります。これは `posts` 配列が Node.js のプロセスの中だけに存在しているためです。プロセスを止めると、配列の中身も消えます。

ブラウザでも [http://localhost:3000](http://localhost:3000) を再読み込みします。投稿一覧が空に戻っていれば、メモリ保存の弱点を画面でも確認できています。

### docker-compose.yml を作成する

プロジェクト直下に `docker-compose.yml` を作成します。

```yaml:docker-compose.yml
services:
  postgres:
    image: postgres:17-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: hono
      POSTGRES_PASSWORD: hono
      POSTGRES_DB: hono_board
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hono -d hono_board"]
      interval: 5s
      timeout: 3s
      retries: 10

volumes:
  postgres-data:
```

`volumes` は、PostgreSQL のデータをコンテナの外側に残すための設定です。コンテナを止めても、DB の中身は `postgres-data` に残ります。

### PostgreSQL を起動する

```bash
docker compose up -d
```

> **Tips:** `docker compose up -d` は、`docker-compose.yml` に書いたサービスをバックグラウンドで起動します。ここでは PostgreSQL コンテナを起動し、API サーバーから接続できる DB を用意します。

`postgres` コンテナが `Started` または `Running` になれば成功です。

### DB 接続ファイルを作成する

`src/db.ts` を作成します。

```ts:src/db.ts
import { drizzle } from "drizzle-orm/node-postgres";
import pg from "pg";

const connectionString =
  process.env.DATABASE_URL ??
  "postgres://hono:hono@localhost:5432/hono_board";

const pool = new pg.Pool({
  connectionString
});

export const db = drizzle(pool);

export const closeDb = () => pool.end();
```

> **Tips:** Drizzle は、TypeScript から SQL を組み立てて DB を操作するためのライブラリです。SQL 文字列を手で連結する代わりに、テーブル定義と関数を使って安全に読み書きできます。

### Drizzle 設定ファイルを作成する

プロジェクト直下に `drizzle.config.ts` を作成します。

```ts:drizzle.config.ts
import { defineConfig } from "drizzle-kit";

export default defineConfig({
  schema: "./src/post.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: {
    url:
      process.env.DATABASE_URL ??
      "postgres://hono:hono@localhost:5432/hono_board"
  }
});
```

`schema` は、Drizzle がテーブル定義を探しに行くファイルです。今回は `posts` テーブルを `src/post.ts` に書くので、このパスを指定します。

### post.ts を DB 版に変更する

`src/post.ts` を次のように変更します。

```diff ts:src/post.ts
+import { desc } from "drizzle-orm";
+import { pgTable, serial, text, timestamp, varchar } from "drizzle-orm/pg-core";
import { Hono } from "hono";
+import { db } from "./db.js";

export interface PostOutput {
  id: number;
  content: string;
  authorUid: string;
  authorName: string;
  authorPhotoUrl: string | null;
  createdAt: string;
}

export interface CreatePostInput {
  content: string;
  authorUid: string;
  authorName: string;
  authorPhotoUrl?: string;
}

+export const posts = pgTable("posts", {
+  id: serial("id").primaryKey(),
+  content: text("content").notNull(),
+  authorUid: varchar("author_uid", { length: 128 }).notNull(),
+  authorName: varchar("author_name", { length: 128 }).notNull(),
+  authorPhotoUrl: text("author_photo_url"),
+  createdAt: timestamp("created_at", { withTimezone: true })
+    .defaultNow()
+    .notNull()
+});
+
-const posts: PostOutput[] = [];
-let nextId = 1;
+const toPostOutput = (post: typeof posts.$inferSelect): PostOutput => ({
+  id: post.id,
+  content: post.content,
+  authorUid: post.authorUid,
+  authorName: post.authorName,
+  authorPhotoUrl: post.authorPhotoUrl,
+  createdAt: post.createdAt.toISOString()
+});

 export const listPosts = async (): Promise<PostOutput[]> => {
-  return posts;
+  const rows = await db
+    .select()
+    .from(posts)
+    .orderBy(desc(posts.createdAt), desc(posts.id));
+
+  return rows.map(toPostOutput);
 };

 export const createPost = async (
   input: CreatePostInput
 ): Promise<PostOutput> => {
-  const post = {
-    id: nextId,
-    content: input.content,
-    authorUid: input.authorUid,
-    authorName: input.authorName,
-    authorPhotoUrl: input.authorPhotoUrl ?? null,
-    createdAt: new Date().toISOString()
-  };
-
-  nextId += 1;
-  posts.unshift(post);
-  return post;
+  const rows = await db
+    .insert(posts)
+    .values({
+      content: input.content,
+      authorUid: input.authorUid,
+      authorName: input.authorName,
+      authorPhotoUrl: input.authorPhotoUrl
+    })
+    .returning();
+
+  return toPostOutput(rows[0]);
 };

 export const postRoutes = new Hono()
  .get("/", async (c) => {
    const rows = await listPosts();
    return c.json({ posts: rows });
  })
  .post("/", async (c) => {
    const body = (await c.req.json().catch(() => null)) as {
      content?: unknown;
    } | null;

    if (typeof body?.content !== "string" || body.content.trim().length === 0) {
      return c.json({ error: "投稿内容を入力してください。" }, 400);
    }

    const post = await createPost({
      content: body.content.trim(),
      authorUid: "temporary-user",
      authorName: "仮ユーザー",
      authorPhotoUrl: undefined
    });

    return c.json({ post }, 201);
  });
```

> **Tips:** `db.select().from(posts).orderBy(desc(posts.createdAt), desc(posts.id))` は、DB の `posts` テーブルから行を取得し、作成日時が新しい順、同じ時刻なら ID が大きい順に並べます。

### DB にテーブルを作る

```bash
npx drizzle-kit push
```

> **Tips:** `npx` は、プロジェクトに入っているコマンドを一時的に実行するためのコマンドです。ここでは `package.json` に新しい script を追加せず、`drizzle-kit` を直接実行しています。

> **Troubleshooting:** `/Users/.../honojs-backend-app/drizzle.config.json file does not exist` のようなエラーが出た場合は、`drizzle.config.ts` がプロジェクト直下にあるか確認してください。
> `src/drizzle.config.ts` のように `src` フォルダの中に作っている場合は、`honojs-backend-app/drizzle.config.ts` に移動します。

エラーで止まらなければ成功です。Drizzle が `posts` テーブルを PostgreSQL に作成します。

### DB 保存を確認する

サーバーを起動し直します。

```bash
npm run dev
```

別のターミナルで投稿します。

```bash
curl -X POST http://localhost:3000/api/posts \
  -H "Content-Type: application/json" \
  -d '{"content":"DBに保存される投稿です"}'
```

サーバーを `Ctrl + C` で止め、もう一度起動します。

```bash
npm run dev
```

投稿一覧を取得します。

```bash
curl http://localhost:3000/api/posts
```

再起動しても投稿が残っていれば成功です。

### ブラウザで確認する

ブラウザで [http://localhost:3000](http://localhost:3000) を再読み込みします。`DBに保存される投稿です` が投稿一覧に残っていれば成功です。

さらに投稿フォームから `ブラウザからDBへ保存します` と投稿し、サーバーを再起動してからブラウザを再読み込みします。投稿が残っていれば、React SPA から作った投稿も PostgreSQL に保存されています。

### 現時点のコードベース

この時点のディレクトリ構成は次のようになります。

```text
.
├── .gitignore
├── README.md
├── docker-compose.yml
├── drizzle.config.ts
├── index.html
├── package-lock.json
├── package.json
├── src
│   ├── client.tsx
│   ├── db.ts
│   ├── index.ts
│   └── post.ts
├── style.css
├── tailwind.config.ts
├── tsconfig.json
└── vite.config.ts
```

<button>
  [この時点のコードを見る: step-drizzle-postgres](https://github.com/gdg-jp/honojs-backend-template/tree/step-drizzle-postgres)
</button>

## Zod でリクエストを検証する

Duration: 0:10:00

このステップでは、`POST /api/posts` に届く JSON を Zod で検証します。いまの手書きチェックを、再利用しやすく読みやすい schema に置き換えます。

> **Tips:** Zod は、外から来た値が期待した形かどうかを実行時に確認するライブラリです。TypeScript の型は開発中の助けですが、HTTP で届いた JSON が本当に正しいかは実行時に確認する必要があります。

### post.ts に Zod schema を追加する

`src/post.ts` を次のように変更します。

```diff ts:src/post.ts
import { desc } from "drizzle-orm";
import { pgTable, serial, text, timestamp, varchar } from "drizzle-orm/pg-core";
import { Hono } from "hono";
import { db } from "./db.js";
+import { z } from "zod";

export const posts = pgTable("posts", {
  id: serial("id").primaryKey(),
  content: text("content").notNull(),
  authorUid: varchar("author_uid", { length: 128 }).notNull(),
  authorName: varchar("author_name", { length: 128 }).notNull(),
  authorPhotoUrl: text("author_photo_url"),
  createdAt: timestamp("created_at", { withTimezone: true })
    .defaultNow()
    .notNull()
});

export interface PostOutput {
  id: number;
  content: string;
  authorUid: string;
  authorName: string;
  authorPhotoUrl: string | null;
  createdAt: string;
}

export interface CreatePostInput {
  content: string;
  authorUid: string;
  authorName: string;
  authorPhotoUrl?: string;
}

+export const createPostSchema = z.object({
+  content: z
+    .string()
+    .trim()
+    .min(1, "投稿内容を入力してください。")
+    .max(280, "投稿は280文字以内です。")
+});

const toPostOutput = (post: typeof posts.$inferSelect): PostOutput => ({
  id: post.id,
  content: post.content,
  authorUid: post.authorUid,
  authorName: post.authorName,
  authorPhotoUrl: post.authorPhotoUrl,
  createdAt: post.createdAt.toISOString()
});

export const listPosts = async (): Promise<PostOutput[]> => {
  const rows = await db
    .select()
    .from(posts)
    .orderBy(desc(posts.createdAt), desc(posts.id));

  return rows.map(toPostOutput);
};

export const createPost = async (
  input: CreatePostInput
): Promise<PostOutput> => {
  const rows = await db
    .insert(posts)
    .values({
      content: input.content,
      authorUid: input.authorUid,
      authorName: input.authorName,
      authorPhotoUrl: input.authorPhotoUrl
    })
    .returning();

  return toPostOutput(rows[0]);
};

export const postRoutes = new Hono()
  .get("/", async (c) => {
    const rows = await listPosts();
    return c.json({ posts: rows });
  })
  .post("/", async (c) => {
-    const body = (await c.req.json().catch(() => null)) as {
-      content?: unknown;
-    } | null;
-
-    if (typeof body?.content !== "string" || body.content.trim().length === 0) {
-      return c.json({ error: "投稿内容を入力してください。" }, 400);
-    }
+    const body = await c.req.json().catch(() => null);
+    const parsed = createPostSchema.safeParse(body);
+
+    if (!parsed.success) {
+      return c.json(
+        { error: parsed.error.issues[0]?.message ?? "Invalid request body." },
+        400
+      );
+    }

    const post = await createPost({
-      content: body.content.trim(),
+      content: parsed.data.content,
      authorUid: "temporary-user",
      authorName: "仮ユーザー",
      authorPhotoUrl: undefined
    });

    return c.json({ post }, 201);
  });
```

`safeParse` は、成功したら `parsed.success === true` と検証済みデータを返し、失敗したら `parsed.success === false` とエラー情報を返します。例外で落とすのではなく、API として `400 Bad Request` を返しやすくなります。

### 空文字を送って確認する

サーバーを起動し直します。

```bash
npm run dev
```

別のターミナルで、空文字を投稿してみます。

```bash
curl -X POST http://localhost:3000/api/posts \
  -H "Content-Type: application/json" \
  -d '{"content":""}'
```

`"投稿内容を入力してください。"` というエラーが返れば成功です。

### ブラウザで確認する

ブラウザで [http://localhost:3000](http://localhost:3000) を開き、投稿フォームに 280 文字を超える文章を入力します。残り文字数がマイナス表示になり、**投稿** ボタンが押せなくなれば成功です。

画面側でも入力ミスを防いでいますが、API 側の Zod validation も必要です。ブラウザの制御は利用者に見えるコードなので、悪意のある人は回避できます。そのため、サーバー側でも `curl` のような直接リクエストを検証します。

### 現時点のコードベース

この時点のディレクトリ構成は次のようになります。

```text
.
├── .gitignore
├── README.md
├── docker-compose.yml
├── drizzle.config.ts
├── index.html
├── package-lock.json
├── package.json
├── src
│   ├── client.tsx
│   ├── db.ts
│   ├── index.ts
│   └── post.ts
├── style.css
├── tailwind.config.ts
├── tsconfig.json
└── vite.config.ts
```

<button>
  [この時点のコードを見る: step-zod-validation](https://github.com/gdg-jp/honojs-backend-template/tree/step-zod-validation)
</button>

## Firebase Bearer 認可を実装する

Duration: 0:15:00

このステップでは、投稿作成 API をログイン済みユーザーだけが使えるようにします。`GET /api/posts` はログインなしでも見られますが、`POST /api/posts` は Firebase ID トークンを必須にします。

### serviceAccount.json を配置する

Discord の `#260625-honojs-backend` に講師が投稿した Firebase Admin SDK の JSON をコピーし、プロジェクト直下に `serviceAccount.json` という名前で保存します。

> **Warning:** `serviceAccount.json` は秘密鍵です。GitHub、Discord の別チャンネル、SNS などに貼らないでください。

### Firebase middleware を作成する

`src/firebase.ts` を作成します。

```ts:src/firebase.ts
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { cert, getApps, initializeApp } from "firebase-admin/app";
import { getAuth } from "firebase-admin/auth";
import type { MiddlewareHandler } from "hono";
import { createMiddleware } from "hono/factory";

export interface AuthUser {
  uid: string;
  name: string;
  picture?: string;
}

export interface FirebaseVariables {
  user: AuthUser;
}

const firebaseServiceAccountPath = resolve(
  process.cwd(),
  process.env.FIREBASE_SERVICE_ACCOUNT_PATH ?? "serviceAccount.json"
);

const getFirebaseApp = () => {
  if (getApps().length > 0) {
    return getApps()[0];
  }

  if (!existsSync(firebaseServiceAccountPath)) {
    throw new Error(
      `Firebase Admin SDK credentials were not found. Place serviceAccount.json at ${firebaseServiceAccountPath}.`
    );
  }

  return initializeApp({
    credential: cert(firebaseServiceAccountPath)
  });
};

export const verifyIdToken = async (idToken: string): Promise<AuthUser> => {
  const decoded = await getAuth(getFirebaseApp()).verifyIdToken(idToken);

  return {
    uid: decoded.uid,
    name:
      typeof decoded.name === "string" && decoded.name.length > 0
        ? decoded.name
        : "匿名ユーザー",
    picture: typeof decoded.picture === "string" ? decoded.picture : undefined
  };
};

export const requireFirebaseAuth: MiddlewareHandler<{
  Variables: FirebaseVariables;
}> = createMiddleware(async (c, next) => {
  const authorization = c.req.header("authorization");
  const match = authorization?.match(/^Bearer\s+(.+)$/i);

  if (!match) {
    return c.json({ error: "Bearer token is required." }, 401);
  }

  try {
    const user = await verifyIdToken(match[1]);
    c.set("user", user);
    await next();
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "Firebase authentication failed.";
    return c.json({ error: message }, 401);
  }
});
```

Firebase Admin SDK は、サーバー側だけで使うライブラリです。`verifyIdToken` で ID トークンを検証し、信用できる `uid` や表示名を取り出します。

### post.ts の POST だけを保護する

`src/post.ts` を次のように変更します。

```diff ts:src/post.ts
import { desc } from "drizzle-orm";
import { pgTable, serial, text, timestamp, varchar } from "drizzle-orm/pg-core";
import { Hono } from "hono";
import { z } from "zod";
import { db } from "./db.js";
+import { type FirebaseVariables, requireFirebaseAuth } from "./firebase.js";

@@

-export const postRoutes = new Hono()
+export const postRoutes = new Hono<{ Variables: FirebaseVariables }>()
  .get("/", async (c) => {
    const rows = await listPosts();
    return c.json({ posts: rows });
  })
-  .post("/", async (c) => {
+  .post("/", requireFirebaseAuth, async (c) => {
    const body = await c.req.json().catch(() => null);
    const parsed = createPostSchema.safeParse(body);

    if (!parsed.success) {
      return c.json(
        { error: parsed.error.issues[0]?.message ?? "Invalid request body." },
        400
      );
    }

+    const user = c.get("user");
     const post = await createPost({
      content: parsed.data.content,
-      authorUid: "temporary-user",
-      authorName: "仮ユーザー",
-      authorPhotoUrl: undefined
+      authorUid: user.uid,
+      authorName: user.name,
+      authorPhotoUrl: user.picture
    });

    return c.json({ post }, 201);
  });
```

`requireFirebaseAuth` は、POST の本処理に入る前に実行されます。トークンがなければ `401` で止まり、トークンが正しければ `c.set("user", user)` によって後続の処理でログインユーザーを使えます。

### トークンなしの投稿が拒否されることを確認する

サーバーを起動し直します。

```bash
npm run dev
```

別のターミナルで、トークンなしの投稿を試します。

```bash
curl -X POST http://localhost:3000/api/posts \
  -H "Content-Type: application/json" \
  -d '{"content":"ログインなしの投稿"}'
```

`"Bearer token is required."` が返れば成功です。投稿作成 API をログイン必須にできました。

### ブラウザで確認する

ブラウザで [http://localhost:3000](http://localhost:3000) を開きます。Google でログインし、投稿フォームから `Firebase認可後の投稿です` と投稿します。

投稿一覧に表示される投稿者名やアイコンが、自分の Google アカウントの表示名・アイコンになっていれば成功です。React SPA は Firebase Web SDK で ID トークンを取得し、`Authorization: Bearer ...` ヘッダーとして API に送っています。Hono 側は Firebase Admin SDK の `verifyIdToken` でそのトークンを検証しています。

### 現時点のコードベース

この時点のディレクトリ構成は次のようになります。

```text
.
├── .gitignore
├── README.md
├── docker-compose.yml
├── drizzle.config.ts
├── index.html
├── package-lock.json
├── package.json
├── src
│   ├── client.tsx
│   ├── db.ts
│   ├── firebase.ts
│   ├── index.ts
│   └── post.ts
├── style.css
├── tailwind.config.ts
├── tsconfig.json
└── vite.config.ts
```

<button>
  [この時点のコードを見る: step-firebase-auth](https://github.com/gdg-jp/honojs-backend-template/tree/step-firebase-auth)
</button>

## おめでとうございます！

Duration: 0:00:00

このコードラボでは、Hono.js、PostgreSQL、Drizzle、Zod、Firebase Auth を使って、掲示板 API サーバーをゼロから作りました。

### 学んだこと

- Hono.js で Web API の入口を作る方法
- HTTP リクエストとレスポンスを確認する方法
- メモリ保存と DB 保存の違いを体験する方法
- Drizzle で PostgreSQL のテーブルを定義して読み書きする方法
- Zod で API リクエストを検証する方法
- Firebase Admin SDK で ID トークンを検証する方法

### 完成コード

完成したコードは次のリポジトリにあります。

<button>
  [完成版リポジトリを開く](https://github.com/gdg-jp/honojs-backend-example)
</button>

詰まったときは、各ステップ末尾の checkpoint tag と自分のコードを見比べてください。

### 片付け

PostgreSQL コンテナを止める場合は、ターミナルで次を実行します。

```bash
docker compose down
```

今日作った `serviceAccount.json` は秘密鍵です。不要になったら削除してください。

## Extra: Cloud Run + Cloud SQL にデプロイする

Duration: 0:00:00

この Extra では、本編で作った Hono + React + PostgreSQL アプリを Google Cloud Run と Cloud SQL for PostgreSQL にデプロイします。本編では全員共通の Firebase project を使いましたが、このステップでは自分で作成した Google Cloud project と Firebase project を使います。

Cloud Run は HTTP リクエストが来たときだけコンテナを起動できる実行環境です。Cloud SQL は Google Cloud が管理する PostgreSQL です。この構成にすると、Hono サーバーは Cloud Run で動き、投稿データは Cloud SQL に保存されます。

> **Warning:** このステップでは課金が発生する Google Cloud リソースを作成します。最後の「クリーンアップ」まで実行し、Cloud Run、Cloud SQL、Artifact Registry などの有料リソースを削除してください。

### このステップで使う名前を決める

このステップでは、次の名前を使います。`PROJECT_ID` だけは世界中で一意にする必要があります。`your-name-hono-2026` のように、自分の名前や日付を入れてください。

```bash
export PROJECT_ID="your-project-id"
export REGION="asia-northeast2"
export SERVICE_NAME="honojs-backend"
export INSTANCE_NAME="hono-postgres"
export DB_NAME="hono_board"
export DB_USER="hono"
export DB_PASSWORD="change-this-password"
export SERVICE_ACCOUNT_NAME="hono-cloud-run"
```

**期待される出力:**

```text
出力がなければ成功です。
```

以降のコマンドは、この変数を使って実行します。新しいターミナルを開いた場合は、もう一度このブロックを実行してください。

> **Tips:** `DB_PASSWORD` はそのまま使わず、自分だけが知っている長い文字列に変更してください。記号を含める場合、シェルで特別な意味を持つ文字は避けると詰まりにくいです。

### gcloud CLI にログインする

Google Cloud の操作には `gcloud` CLI を使います。まだ入っていない場合は、公式ドキュメントから Google Cloud CLI をインストールします。

<button>
  [Google Cloud CLI のインストール手順を開く](https://cloud.google.com/sdk/docs/install)
</button>

インストール後、ターミナルでログインします。

```bash
gcloud auth login
```

ブラウザが開いたら、自分の Google アカウントでログインします。ログインできたら、アカウントを確認します。

```bash
gcloud auth list
```

**期待される出力:**

```text
Credentialed Accounts
ACTIVE  ACCOUNT
*       your-email@example.com
```

`ACTIVE` に `*` が付いているアカウントが、以降の Google Cloud 操作に使われます。

### Google Cloud project を作成する

この Extra 用の Google Cloud project を作成します。本編の Firebase project とは別に、自分の project を使います。

```bash
gcloud projects create "$PROJECT_ID" \
  --name="Hono Backend Workshop"
```

**期待される出力:**

```text
Create in progress for [https://cloudresourcemanager.googleapis.com/v1/projects/your-project-id].
Waiting for [operations/...] to finish...done.
```

作成した project を `gcloud` のデフォルトに設定します。

```bash
gcloud config set project "$PROJECT_ID"
```

**期待される出力:**

```text
Updated property [core/project].
```

設定できているか確認します。

```bash
gcloud config list project
```

**期待される出力:**

```text
[core]
project = your-project-id
```

### 課金アカウントを設定する

Cloud Run、Cloud SQL、Cloud Build、Artifact Registry を使うには、Google Cloud project に課金アカウントを紐づける必要があります。

まず、利用できる課金アカウントを確認します。

```bash
gcloud billing accounts list
```

**期待される出力:**

```text
ACCOUNT_ID            NAME                OPEN  MASTER_ACCOUNT_ID
XXXXXX-XXXXXX-XXXXXX  My Billing Account  True
```

`ACCOUNT_ID` を変数に入れます。

```bash
export BILLING_ACCOUNT_ID="XXXXXX-XXXXXX-XXXXXX"
```

Google Cloud project に課金アカウントを紐づけます。

```bash
gcloud billing projects link "$PROJECT_ID" \
  --billing-account="$BILLING_ACCOUNT_ID"
```

**期待される出力:**

```text
billingAccountName: billingAccounts/XXXXXX-XXXXXX-XXXXXX
billingEnabled: true
name: projects/your-project-id/billingInfo
projectId: your-project-id
```

> **Warning:** 課金アカウントを紐づけると、この project で作った有料リソースに料金が発生します。このステップの最後に削除コマンドを実行してください。

### この構成の費用を確認する

今回の Cloud Run は `--min-instances=0` にするため、アクセスがない間は Cloud Run の実行インスタンス料金がかかりません。小さなワークショップ利用であれば、Cloud Run のリクエスト、CPU、メモリは無料枠に収まることが多いです。ただし、`gcloud run deploy --source .` では Cloud Build と Artifact Registry も使うため、保存されたコンテナイメージが増えると Artifact Registry の保存料金が発生することがあります。

Cloud SQL は、アクセスがなくてもインスタンスが起動している間は課金されます。今回の最低性能構成では、主な費用は次のとおりです。

| リソース | 設定 | 目安 |
| --- | --- | --- |
| Cloud Run | 0.08 vCPU、128 MiB、最小インスタンス 0 | アイドル時は実行インスタンス料金なし |
| Cloud SQL instance | `db-f1-micro` | `$0.0105/hour`、約 `$0.252/day` |
| Cloud SQL SSD storage | 10 GiB | `$0.000232877/GiB-hour`、約 `$0.056/day` |
| 合計 | Cloud SQL が中心 | 約 `$0.31/day` |

この金額は税、為替、リージョン、無料枠、将来の価格変更で変わります。正確な金額は Google Cloud の請求画面と Pricing Calculator で確認してください。

参考:

- [Cloud Run pricing](https://cloud.google.com/run/pricing)
- [Cloud Run CPU limits](https://docs.cloud.google.com/run/docs/configuring/services/cpu)
- [Cloud SQL pricing](https://cloud.google.com/sql/pricing)
- [Cloud SQL from Cloud Run](https://docs.cloud.google.com/sql/docs/postgres/connect-run)
- [Firebase Admin SDK setup](https://firebase.google.com/docs/admin/setup)
- [Firebase Auth IAM roles](https://docs.cloud.google.com/iam/docs/roles-permissions/firebaseauth)

### 必要な API を有効化する

Cloud Run、Cloud SQL、Cloud Build、Artifact Registry、Firebase を使うために API を有効化します。

```bash
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  firebase.googleapis.com \
  identitytoolkit.googleapis.com \
  iam.googleapis.com \
  serviceusage.googleapis.com \
  cloudresourcemanager.googleapis.com
```

**期待される出力:**

```text
Operation "operations/..." finished successfully.
```

エラーが出なければ成功です。API の有効化には数十秒かかることがあります。

### Firebase project を作成する

Firebase Console を開き、作成した Google Cloud project に Firebase を追加します。

<button>
  [Firebase Console を開く](https://console.firebase.google.com/)
</button>

次の順に進めます。

1. **プロジェクトを追加** を押します。
2. 画面下部の **Google Cloud プロジェクトに Firebase を追加** を選びます。
3. `PROJECT_ID` に設定した project を選びます。
4. Google Analytics は、このコードラボでは無効でかまいません。
5. **Firebase を追加** を押します。

Firebase project が開けたら成功です。Firebase project と Google Cloud project は同じ project ID を共有します。

### Firebase Authentication を有効化する

Firebase Console で Google ログインを有効にします。

1. 左メニューの **Authentication** を開きます。
2. **始める** を押します。
3. **Sign-in method** タブを開きます。
4. **Google** を選びます。
5. **有効にする** をオンにします。
6. サポートメールに自分のメールアドレスを選びます。
7. **保存** を押します。

Google provider が `有効` と表示されれば成功です。

> **補足:** 本編では講師が用意した Firebase project を使いました。この Extra では、自分の Cloud Run URL からログインできるように、自分の Firebase project 側で Google ログインを有効化します。

### Firebase Web アプリを追加する

Firebase Console の project overview に戻り、Web アプリを追加します。

1. `</>` アイコンを押します。
2. アプリのニックネームに `honojs-backend-web` と入力します。
3. Firebase Hosting は有効にしません。
4. **アプリを登録** を押します。
5. 表示された `firebaseConfig` をコピーします。

`src/client.tsx` の `firebaseConfig` を、自分の Firebase project の値に置き換えます。

```diff ts:src/client.tsx
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "your-project-id.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project-id.firebasestorage.app",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
};
```

この設定は、ブラウザ側の Firebase Web SDK がどの Firebase project に接続するかを決めます。秘密鍵ではないためブラウザに含まれても問題ありませんが、自分の project の値を正しく入れる必要があります。

### Firebase Admin SDK の秘密鍵を作成する

ローカル開発では、Firebase Admin SDK が ID トークンを検証するために `serviceAccount.json` を使います。Firebase Console で秘密鍵を作成します。

1. Firebase Console の歯車アイコンから **プロジェクトの設定** を開きます。
2. **サービス アカウント** タブを開きます。
3. **新しい秘密鍵の生成** を押します。
4. 確認画面で **キーを生成** を押します。
5. ダウンロードした JSON を、プロジェクト直下に `serviceAccount.json` という名前で置きます。

> **Warning:** `serviceAccount.json` は秘密鍵です。GitHub、Discord、SNS、スクリーンショットに載せないでください。本編の `.gitignore` では `serviceAccount.json` を除外していますが、`git status` でコミット対象になっていないことを必ず確認してください。

ローカルで Firebase 認証がまだ動くか確認します。

```bash
npm run dev
```

ブラウザで [http://localhost:3000](http://localhost:3000) を開き、Google ログインして投稿します。投稿者名が表示されれば成功です。

### Cloud Run 用に build script を変更する

Cloud Run の source deploy では、Google Cloud 側で `npm run build` が実行され、そのあと `npm start` でサーバーが起動します。React SPA と Hono サーバーの両方をビルドするように、`build` script を変更します。

```bash
npm pkg set scripts.build="npx vite build && tsc"
```

**期待される出力:**

```text
出力がなければ成功です。
```

変更後、ローカルでビルドできるか確認します。

```bash
npm run build
```

**期待される出力:**

```text
✓ built in ...
```

`dist` フォルダが作成され、TypeScript のエラーが出なければ成功です。

### Firebase Admin SDK を Cloud Run の認証情報に対応させる

Cloud Run 上では、`serviceAccount.json` を置かず、Cloud Run のサービスアカウントを使って Firebase Admin SDK を初期化します。ローカルでは `serviceAccount.json`、Cloud Run では Application Default Credentials を使うように変更します。

`src/firebase.ts` を以下の内容で上書きします。

```ts:src/firebase.ts
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import {
  applicationDefault,
  cert,
  getApps,
  initializeApp
} from "firebase-admin/app";
import { getAuth } from "firebase-admin/auth";
import type { MiddlewareHandler } from "hono";
import { createMiddleware } from "hono/factory";

export interface AuthUser {
  uid: string;
  name: string;
  picture?: string;
}

export interface FirebaseVariables {
  user: AuthUser;
}

const firebaseServiceAccountPath = resolve(
  process.cwd(),
  process.env.FIREBASE_SERVICE_ACCOUNT_PATH ?? "serviceAccount.json"
);

const getFirebaseApp = () => {
  if (getApps().length > 0) {
    return getApps()[0];
  }

  if (existsSync(firebaseServiceAccountPath)) {
    return initializeApp({
      credential: cert(firebaseServiceAccountPath)
    });
  }

  return initializeApp({
    credential: applicationDefault()
  });
};

export const verifyIdToken = async (idToken: string): Promise<AuthUser> => {
  const decoded = await getAuth(getFirebaseApp()).verifyIdToken(idToken);

  return {
    uid: decoded.uid,
    name:
      typeof decoded.name === "string" && decoded.name.length > 0
        ? decoded.name
        : "匿名ユーザー",
    picture: typeof decoded.picture === "string" ? decoded.picture : undefined
  };
};

export const requireFirebaseAuth: MiddlewareHandler<{
  Variables: FirebaseVariables;
}> = createMiddleware(async (c, next) => {
  const authorization = c.req.header("authorization");
  const match = authorization?.match(/^Bearer\s+(.+)$/i);

  if (!match) {
    return c.json({ error: "Bearer token is required." }, 401);
  }

  try {
    const user = await verifyIdToken(match[1]);
    c.set("user", user);
    await next();
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "Firebase authentication failed.";
    return c.json({ error: message }, 401);
  }
});
```

`applicationDefault()` は、Cloud Run の実行環境に割り当てたサービスアカウントを使うための設定です。これにより、Cloud Run に秘密鍵ファイルをアップロードせずに Firebase Admin SDK を使えます。

### Cloud SQL 接続に対応させる

ローカルでは `DATABASE_URL` で Docker の PostgreSQL に接続し、Cloud Run では Cloud SQL の Unix socket に接続します。`INSTANCE_CONNECTION_NAME` がある場合だけ Cloud SQL 接続に切り替えるようにします。

`src/db.ts` を以下の内容で上書きします。

```ts:src/db.ts
import { drizzle } from "drizzle-orm/node-postgres";
import pg from "pg";

const cloudSqlConnectionName = process.env.INSTANCE_CONNECTION_NAME;

const connectionConfig = cloudSqlConnectionName
  ? {
      user: process.env.DB_USER ?? "hono",
      password: process.env.DB_PASSWORD ?? "",
      database: process.env.DB_NAME ?? "hono_board",
      host: `/cloudsql/${cloudSqlConnectionName}`
    }
  : {
      connectionString:
        process.env.DATABASE_URL ??
        "postgres://hono:hono@localhost:5432/hono_board"
    };

const pool = new pg.Pool(connectionConfig);

export const db = drizzle(pool);

export const closeDb = () => pool.end();
```

Cloud Run と Cloud SQL を接続すると、`/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME` という Unix socket が使えるようになります。アプリはその socket を通して PostgreSQL に接続します。

変更後、もう一度ビルドします。

```bash
npm run build
```

TypeScript のエラーが出なければ成功です。

### Cloud Run 用サービスアカウントを作成する

Cloud Run の実行時に使う専用サービスアカウントを作ります。

```bash
gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
  --display-name="Hono Cloud Run runtime"
```

**期待される出力:**

```text
Created service account [hono-cloud-run].
```

サービスアカウントのメールアドレスを変数に入れます。

```bash
export SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
```

Cloud SQL に接続できるように、Cloud SQL Client ロールを付与します。

```bash
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/cloudsql.client"
```

**期待される出力:**

```text
Updated IAM policy for project [your-project-id].
```

Firebase Admin SDK が Firebase Auth を使えるように、Firebase Authentication Admin ロールを付与します。

```bash
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/firebaseauth.admin"
```

**期待される出力:**

```text
Updated IAM policy for project [your-project-id].
```

> **補足:** このコードでは ID トークンの検証が中心ですが、Cloud Run のサービスアカウントで Firebase Admin SDK を動かせるように IAM を明示します。より権限を絞る設計は、本番運用時に改めて検討します。

### Cloud SQL PostgreSQL を作成する

Cloud SQL for PostgreSQL のインスタンスを作成します。今回は費用を抑えるため、共有 CPU の `db-f1-micro`、10 GiB SSD、バックアップ無効、ストレージ自動増加無効にします。

```bash
gcloud sql instances create "$INSTANCE_NAME" \
  --database-version=POSTGRES_17 \
  --tier=db-f1-micro \
  --region="$REGION" \
  --availability-type=zonal \
  --storage-type=SSD \
  --storage-size=10 \
  --no-storage-auto-increase \
  --no-backup
```

**期待される出力:**

```text
Creating Cloud SQL instance for POSTGRES_17...done.
Created [https://sqladmin.googleapis.com/sql/v1beta4/projects/your-project-id/instances/hono-postgres].
```

作成には数分かかります。完了したら、アプリ用のデータベースを作成します。

```bash
gcloud sql databases create "$DB_NAME" \
  --instance="$INSTANCE_NAME"
```

**期待される出力:**

```text
Created database [hono_board].
```

アプリ用ユーザーを作成します。

```bash
gcloud sql users create "$DB_USER" \
  --instance="$INSTANCE_NAME" \
  --password="$DB_PASSWORD"
```

**期待される出力:**

```text
Created user [hono].
```

Cloud SQL の接続名を取得します。

```bash
export INSTANCE_CONNECTION_NAME="$(gcloud sql instances describe "$INSTANCE_NAME" --format='value(connectionName)')"
echo "$INSTANCE_CONNECTION_NAME"
```

**期待される出力:**

```text
your-project-id:asia-northeast2:hono-postgres
```

この接続名を Cloud Run の環境変数と Cloud SQL 接続設定で使います。

### Drizzle の migration SQL を作成する

Cloud SQL に本番用テーブルを作ります。ここでは `drizzle-kit push` で直接 DB に反映するのではなく、migration SQL を作成し、Cloud SQL Studio で手動実行します。

```bash
npx drizzle-kit generate
```

**期待される出力:**

```text
[✓] Your SQL migration file ➜ drizzle/0000_....sql
```

作成された SQL ファイルを確認します。

```bash
ls drizzle
```

**期待される出力:**

```text
0000_....sql
meta
```

`drizzle/0000_....sql` を VS Code で開きます。`CREATE TABLE "posts"` を含む SQL が表示されれば成功です。

> **Troubleshooting:** `No schema changes, nothing to migrate` と表示された場合は、すでに `drizzle` フォルダに migration がある可能性があります。その場合は既存の `drizzle/*.sql` を使って次に進みます。

### Cloud SQL Studio で migration SQL を実行する

Google Cloud Console で Cloud SQL Studio を開きます。

<button>
  [Cloud SQL instances を開く](https://console.cloud.google.com/sql/instances)
</button>

次の順に進めます。

1. `hono-postgres` インスタンスを開きます。
2. 左メニューの **Cloud SQL Studio** を開きます。
3. Database に `hono_board` を選びます。
4. User に `hono` を入力します。
5. Password に `DB_PASSWORD` に設定した値を入力します。
6. **Authenticate** を押します。
7. SQL エディタに `drizzle/0000_....sql` の内容を貼り付けます。
8. **Run** を押します。

実行後、`posts` テーブルが作成されれば成功です。

確認用に、Cloud SQL Studio で次の SQL を実行します。

```sql
select table_name
from information_schema.tables
where table_schema = 'public';
```

**期待される出力:**

```text
posts
```

### Cloud Run にデプロイする

Cloud Run に source deploy します。Cloud Build がソースコードからコンテナイメージを作り、Cloud Run に配置します。

```bash
gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region="$REGION" \
  --service-account="$SERVICE_ACCOUNT_EMAIL" \
  --add-cloudsql-instances="$INSTANCE_CONNECTION_NAME" \
  --set-env-vars="INSTANCE_CONNECTION_NAME=${INSTANCE_CONNECTION_NAME},DB_NAME=${DB_NAME},DB_USER=${DB_USER},DB_PASSWORD=${DB_PASSWORD}" \
  --cpu=0.08 \
  --memory=128Mi \
  --concurrency=1 \
  --execution-environment=gen1 \
  --min-instances=0 \
  --allow-unauthenticated
```

**期待される出力:**

```text
Deploying from source requires an Artifact Registry Docker repository to store built containers.
Do you want to continue (Y/n)?
```

`Y` を入力して Enter を押します。デプロイが終わると、次のように URL が表示されます。

```text
Service [honojs-backend] revision [...] has been deployed and is serving 100 percent of traffic.
Service URL: https://honojs-backend-....a.run.app
```

URL を変数に入れます。

```bash
export SERVICE_URL="$(gcloud run services describe "$SERVICE_NAME" \
  --region="$REGION" \
  --format='value(status.url)')"
echo "$SERVICE_URL"
```

**期待される出力:**

```text
https://honojs-backend-....a.run.app
```

### Firebase Authentication の承認済みドメインを追加する

Cloud Run の URL で Google ログインできるように、Firebase Authentication に承認済みドメインを追加します。

1. Firebase Console で **Authentication** を開きます。
2. **Settings** タブを開きます。
3. **Authorized domains** を開きます。
4. **Add domain** を押します。
5. Cloud Run URL のホスト名だけを入力します。

たとえば `SERVICE_URL` が次の場合:

```text
https://honojs-backend-abc123-uc.a.run.app
```

追加するドメインは次です。

```text
honojs-backend-abc123-uc.a.run.app
```

`https://` や末尾の `/` は入れません。保存できたら、Cloud Run 上のアプリで Firebase ログインを使えるようになります。

### デプロイしたアプリを確認する

まず API の health check を確認します。

```bash
curl "$SERVICE_URL/api/health"
```

**期待される出力:**

```json
{"ok":true}
```

次に投稿一覧 API を確認します。

```bash
curl "$SERVICE_URL/api/posts"
```

**期待される出力:**

```json
{"posts":[]}
```

ブラウザで `SERVICE_URL` を開きます。Google ログインし、投稿フォームから `Cloud Run から投稿しています` と投稿します。投稿一覧に表示されれば、Cloud Run から Cloud SQL に保存できています。

> **Troubleshooting:** `Firebase authentication failed.` が出る場合は、Firebase Web app の `firebaseConfig` が自分の project の値か、Cloud Run のサービスアカウントに `roles/firebaseauth.admin` が付いているか、Firebase Authentication の承認済みドメインに Cloud Run のホスト名を追加したかを確認してください。

DB に保存されたことを Cloud SQL Studio でも確認できます。

```sql
select id, content, author_name, created_at
from posts
order by created_at desc;
```

**期待される出力:**

```text
Cloud Run から投稿しています
```

### クリーンアップ

課金され続けないように、この Extra で作成した有料リソースを削除します。Cloud SQL は起動しているだけで課金されるため、必ず削除してください。

まず Cloud Run service を削除します。

```bash
gcloud run services delete "$SERVICE_NAME" \
  --region="$REGION" \
  --quiet
```

**期待される出力:**

```text
Deleted service [honojs-backend].
```

Cloud SQL instance を削除します。中のデータベースと投稿データも削除されます。

```bash
gcloud sql instances delete "$INSTANCE_NAME" \
  --quiet
```

**期待される出力:**

```text
Deleted [hono-postgres].
```

Artifact Registry に作られた Cloud Run source deploy 用リポジトリを確認します。

```bash
gcloud artifacts repositories list \
  --location="$REGION"
```

**期待される出力:**

```text
REPOSITORY  FORMAT  MODE                 DESCRIPTION
cloud-run-source-deploy  DOCKER  STANDARD_REPOSITORY
```

リポジトリがある場合は削除します。

```bash
gcloud artifacts repositories delete cloud-run-source-deploy \
  --location="$REGION" \
  --quiet
```

**期待される出力:**

```text
Deleted repository [cloud-run-source-deploy].
```

Cloud Run 用サービスアカウントを削除します。

```bash
gcloud iam service-accounts delete "$SERVICE_ACCOUNT_EMAIL" \
  --quiet
```

**期待される出力:**

```text
Deleted service account [hono-cloud-run@your-project-id.iam.gserviceaccount.com].
```

最後に、project ごと削除する場合は次を実行します。Firebase project も同じ Google Cloud project に紐づいているため、一緒に削除されます。

> **Warning:** `gcloud projects delete` は project 内のリソースをまとめて削除する強い操作です。この Extra 専用に作った project であることを確認してから実行してください。既存の project を使った場合は、project 全体ではなく Cloud Run、Cloud SQL、Artifact Registry など、このステップで作ったリソースだけを削除します。

```bash
gcloud projects delete "$PROJECT_ID" \
  --quiet
```

**期待される出力:**

```text
Deleted [https://cloudresourcemanager.googleapis.com/v1/projects/your-project-id].
```

ローカルの秘密鍵も不要になったら削除します。

```bash
rm -f serviceAccount.json
```

**期待される出力:**

```text
出力がなければ成功です。
```

## Extra: API をテストする

Duration: 0:30:00

この Extra では、API の Unit test、Integration test、E2E test を追加します。Vitest、Hono の `testClient()`、Testcontainers PostgreSQL、Drizzle ORM、`drizzle-kit migrate` を組み合わせ、テストごとに DB を空にしてから検証します。

### ソフトウェアテストを考える

実装に入る前に、次の問題を考えてください。

> **問い:** 3つの整数 `a`, `b`, `c` を受け取り、それらが三角形の3辺として成立するか、成立するなら正三角形・二等辺三角形・不等辺三角形のどれかを判定するプログラムがあります。以下のプログラムをテストするために十分なテストケースを考えてください。

これは、ソフトウェアテストの古典的な練習問題である Myers の三角形問題です。単に `3, 3, 3` や `3, 4, 5` だけを試すと、明らかな成功ケースしか確認できません。

たとえば、次のような観点があります。

- 正三角形
- 二等辺三角形
- 不等辺三角形
- 三角形不成立
- 0、負数、小数、文字列のような不正入力
- `a + b = c` のような境界
- 入力順序を入れ替えた場合
- 非常に大きい数

Myers の問題では、22個程度のテストケースで主要な観点を網羅できるとかなり高い水準です。それより大きく増える場合は、同じ意味のテストを重複していないか見直します。テストは多ければ多いほどよいのではなく、欠陥を見つけやすい観点を過不足なく置くことが大切です。

テストする目的は、主に次の3つです。

- 欠陥を防ぐ: バグだらけの製品をリリースしないため
- ユーザーの期待を満たしているか確認する: 要件を満たすかどうかを確かめるため
- 変更による破壊を検知する: コード変更で以前の動作が壊れたことに気づくため

### テストの種類を整理する

Unit test は、関数や小さなモジュールを単体で検証します。今回なら、Zod schema が空文字や長すぎる投稿を拒否することを確認します。

Integration test は、複数の部品を組み合わせて検証します。今回なら、Hono API、Drizzle、PostgreSQL をつないで、DB に入れた投稿を API から取得できることを確認します。

E2E test は、利用者に近い入口からシステム全体の振る舞いを検証します。今回なら、Hono の request boundary を通して `GET /api/health` や `POST /api/posts` の認可エラーまで確認します。ブラウザ操作まで含める場合は Playwright などを追加しますが、この Extra では API E2E に絞ります。

ほかにも、Mutation test、Property-based test、Alloy のような形式手法・モデル検査など、さまざまなテストや検証の方法があります。

ホワイトボックステストは、内部構造を知ったうえで分岐や関数をテストします。ブラックボックステストは、内部実装ではなく入力と出力、つまり振る舞いをテストします。今回の Unit test はややホワイトボックス寄り、API の Integration / E2E test はブラックボックス寄りです。

ソフトウェアテストの七原則も押さえておきます。

1. テストは欠陥があることは示せるが、欠陥がないことは示せない
2. 全数テストは不可能
3. 早期テストで時間とコストを削減できる
4. 欠陥は偏在する
5. 同じテストだけでは新しい欠陥を見つけにくくなる
6. テストは条件次第で変わる
7. バグゼロでもユーザーの役に立たなければ意味がない

テストケースを考えるときは、同値分割法と境界値分析がよく使われます。同値分割法は「同じ扱いになる入力」をグループ化し、代表値を選ぶ技法です。境界値分析は、`0` と `1`、`280` と `281` のように、条件が切り替わる境界の前後を重点的に試す技法です。

### テストライブラリを追加する

Vitest と Testcontainers を追加します。Hono の `testClient()` は `hono/testing` から import できるため、追加インストールは不要です。

```bash
npm install -D vitest testcontainers @testcontainers/postgresql
```

**期待される出力:**

```text
added ... packages
```

> **補足:** `@hono/vitest-helper` を使う構成もありますが、この Extra では Hono 本体に含まれる `hono/testing` の `testClient()` を使います。

### npm scripts を追加する

`package.json` の `scripts` にテスト用コマンドを追加します。

```diff json:package.json
   "scripts": {
     "dev": "tsx watch src/index.ts",
     "build": "npx vite build && tsc",
-    "start": "node dist/index.js"
+    "start": "node dist/index.js",
+    "test:unit": "vitest run test/**/*.unit.test.ts",
+    "test:integration": "vitest run test/**/*.integration.test.ts",
+    "test:e2e": "vitest run test/**/*.e2e.test.ts",
+    "test:all": "npm run test:unit && npm run test:integration && npm run test:e2e"
   },
```

`test:unit` は速い検証、`test:integration` は DB まで含む検証、`test:e2e` は API の入口から見る検証です。`test:all` は3種類を順番に実行します。

### Hono app をテストしやすく分離する

今の `src/index.ts` は、app の定義と `serve()` によるサーバー起動が同じファイルにあります。テストで import しただけでサーバーが起動しないように、app の定義を `src/app.ts` に分けます。

`src/app.ts` を作成します。

```ts:src/app.ts
import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { serveStatic } from "@hono/node-server/serve-static";
import { Hono } from "hono";
import { logger } from "hono/logger";
import { postRoutes } from "./post.js";

const publicDir = join(process.cwd(), "dist", "public");
const indexHtml = join(publicDir, "index.html");

export const app = new Hono()
  .use(logger())
  .get("/api/health", (c) => c.json({ ok: true }))
  .route("/api/posts", postRoutes)
  .use(
    "/*",
    serveStatic({
      root: "./dist/public"
    })
  )
  .get("*", async (c) => {
    if (c.req.path.startsWith("/api/")) {
      return c.json({ error: "API route is not implemented yet." }, 404);
    }

    if (!existsSync(indexHtml)) {
      return c.text(
        "React SPA is not built yet. Run `npx vite build` first.",
        404
      );
    }

    return c.html(await readFile(indexHtml, "utf8"));
  });

export type AppType = typeof app;
```

`testClient()` の型推論を効かせるため、`new Hono()` から `.get()`、`.route()` をつなげて app を作っています。

`src/index.ts` は、サーバー起動だけを担当するファイルにします。

```ts:src/index.ts
import { serve } from "@hono/node-server";
import { app } from "./app.js";

const port = Number(process.env.PORT ?? 3000);

serve(
  {
    fetch: app.fetch,
    port
  },
  (info) => {
    console.log(`Server is running on http://localhost:${info.port}`);
  }
);
```

テストでは `src/app.ts` を import します。ローカル開発や Cloud Run では、これまでどおり `src/index.ts` からサーバーを起動します。

### migration SQL を用意する

Testcontainers で起動した PostgreSQL にも、本番と同じテーブルを作る必要があります。Drizzle の migration SQL がまだない場合は作成します。

```bash
npx drizzle-kit generate
```

**期待される出力:**

```text
[✓] Your SQL migration file ➜ drizzle/0000_....sql
```

すでに migration がある場合は、`No schema changes, nothing to migrate` と表示されることがあります。その場合は、既存の `drizzle/*.sql` を使います。

### テスト用 DB ヘルパーを作成する

`test` フォルダを作成し、Testcontainers PostgreSQL を起動するヘルパーを作ります。

```bash
mkdir -p test
```

**期待される出力:**

```text
出力がなければ成功です。
```

`test/test-db.ts` を作成します。

```ts:test/test-db.ts
import { execFileSync } from "node:child_process";
import { PostgreSqlContainer } from "@testcontainers/postgresql";
import type { StartedPostgreSqlContainer } from "@testcontainers/postgresql";
import pg from "pg";

let container: StartedPostgreSqlContainer | undefined;
let pool: pg.Pool | undefined;

export const setupTestDatabase = async () => {
  if (container && pool) {
    return;
  }

  container = await new PostgreSqlContainer("postgres:17-alpine")
    .withDatabase("hono_board")
    .withUsername("hono")
    .withPassword("hono")
    .start();

  process.env.DATABASE_URL = container.getConnectionUri();

  execFileSync("npx", ["drizzle-kit", "migrate"], {
    stdio: "inherit",
    env: {
      ...process.env,
      DATABASE_URL: process.env.DATABASE_URL
    }
  });

  pool = new pg.Pool({
    connectionString: process.env.DATABASE_URL
  });
};

export const resetTestDatabase = async () => {
  if (!pool) {
    throw new Error("Test database is not started.");
  }

  await pool.query("TRUNCATE TABLE posts RESTART IDENTITY CASCADE");
};

export const stopTestDatabase = async () => {
  await import("../src/db.js")
    .then(({ closeDb }) => closeDb())
    .catch(() => undefined);

  await pool?.end();
  await container?.stop();

  pool = undefined;
  container = undefined;
};
```

`setupTestDatabase()` は PostgreSQL コンテナを起動し、`DATABASE_URL` をそのコンテナに向け、`drizzle-kit migrate` でテーブルを作ります。`resetTestDatabase()` は各テスト前に `TRUNCATE TABLE posts RESTART IDENTITY CASCADE` を実行し、投稿データと ID 採番を初期化します。

> **Troubleshooting:** Testcontainers は Docker を使います。`Could not find a working container runtime strategy` のようなエラーが出た場合は、Docker Desktop が起動しているか確認してください。

### Unit test を追加する

Unit test では、DB や HTTP を使わず、Zod schema だけを検証します。

`test/post.unit.test.ts` を作成します。

```ts:test/post.unit.test.ts
import { describe, expect, it } from "vitest";
import { createPostSchema } from "../src/post.js";

describe("createPostSchema", () => {
  it("投稿内容の前後の空白を取り除く", () => {
    const result = createPostSchema.parse({ content: "  hello  " });

    expect(result.content).toBe("hello");
  });

  it("空文字を拒否する", () => {
    const result = createPostSchema.safeParse({ content: "" });

    expect(result.success).toBe(false);
  });

  it("281文字の投稿を拒否する", () => {
    const result = createPostSchema.safeParse({
      content: "a".repeat(281)
    });

    expect(result.success).toBe(false);
  });
});
```

空文字と281文字は境界値分析の例です。`0文字`、`1文字`、`280文字`、`281文字` のように、条件が切り替わる前後を狙うと、少ないテストで欠陥を見つけやすくなります。

Unit test を実行します。

```bash
npm run test:unit
```

**期待される出力:**

```text
✓ test/post.unit.test.ts
```

### Integration test を追加する

Integration test では、Testcontainers の PostgreSQL、Drizzle ORM、Hono app を組み合わせます。Hono の `testClient()` を使うと、テストコードから型安全に API を呼び出せます。

`test/posts.integration.test.ts` を作成します。

```ts:test/posts.integration.test.ts
import { testClient } from "hono/testing";
import { afterAll, beforeAll, beforeEach, describe, expect, it } from "vitest";
import type { AppType } from "../src/app.js";
import {
  resetTestDatabase,
  setupTestDatabase,
  stopTestDatabase
} from "./test-db.js";

let app: AppType;

beforeAll(async () => {
  await setupTestDatabase();
  app = (await import("../src/app.js")).app;
}, 60_000);

beforeEach(async () => {
  await resetTestDatabase();
});

afterAll(async () => {
  await stopTestDatabase();
});

describe("GET /api/posts", () => {
  it("DB に保存された投稿を新しい順で返す", async () => {
    const { createPost } = await import("../src/post.js");

    await createPost({
      content: "Integration test から作った投稿です",
      authorUid: "test-user",
      authorName: "Test User"
    });

    const client = testClient(app);
    const res = await client.api.posts.$get();
    const body = await res.json();

    expect(res.status).toBe(200);
    expect(body.posts).toHaveLength(1);
    expect(body.posts[0]).toMatchObject({
      id: 1,
      content: "Integration test から作った投稿です",
      authorUid: "test-user",
      authorName: "Test User"
    });
  });
});
```

`setupTestDatabase()` のあとに `src/app.ts` を dynamic import しています。これは、`src/db.ts` が import される前に `DATABASE_URL` を Testcontainers の PostgreSQL に向けるためです。

Integration test を実行します。

```bash
npm run test:integration
```

**期待される出力:**

```text
✓ test/posts.integration.test.ts
```

### API E2E test を追加する

E2E test では、API の入口から見た振る舞いを確認します。ここでは実ブラウザではなく、Hono の request boundary を `testClient()` で叩きます。

`test/api.e2e.test.ts` を作成します。

```ts:test/api.e2e.test.ts
import { testClient } from "hono/testing";
import { afterAll, beforeAll, beforeEach, describe, expect, it } from "vitest";
import type { AppType } from "../src/app.js";
import {
  resetTestDatabase,
  setupTestDatabase,
  stopTestDatabase
} from "./test-db.js";

let app: AppType;

beforeAll(async () => {
  await setupTestDatabase();
  app = (await import("../src/app.js")).app;
}, 60_000);

beforeEach(async () => {
  await resetTestDatabase();
});

afterAll(async () => {
  await stopTestDatabase();
});

describe("API E2E", () => {
  it("health check が成功する", async () => {
    const client = testClient(app);
    const res = await client.api.health.$get();

    expect(res.status).toBe(200);
    expect(await res.json()).toEqual({ ok: true });
  });

  it("ログインなしの投稿作成を 401 で拒否する", async () => {
    const client = testClient(app);
    const res = await client.api.posts.$post({
      json: {
        content: "ログインなしの投稿"
      }
    });
    const body = await res.json();

    expect(res.status).toBe(401);
    expect(body).toEqual({ error: "Bearer token is required." });
  });
});
```

Firebase ID トークンを本物の Google ログインから取得して検証するテストは、CI で安定させるために別設計が必要です。ここでは、まず「認可なしのリクエストが拒否される」という重要な振る舞いを固定します。

E2E test を実行します。

```bash
npm run test:e2e
```

**期待される出力:**

```text
✓ test/api.e2e.test.ts
```

### すべてのテストを実行する

最後に、3種類のテストをまとめて実行します。

```bash
npm run test:all
```

**期待される出力:**

```text
✓ test/post.unit.test.ts
✓ test/posts.integration.test.ts
✓ test/api.e2e.test.ts
```

これで、Zod schema の Unit test、PostgreSQL まで含む Integration test、API の入口から確認する E2E test がそろいました。今後、投稿削除や投稿編集を追加したら、成功ケースだけでなく、`401`、`403`、`404`、validation error、境界値も追加していきます。

### 現時点のコードベース

この時点のディレクトリ構成は次のようになります。

```text
.
├── .gitignore
├── README.md
├── docker-compose.yml
├── drizzle
│   ├── 0000_....sql
│   └── meta
├── drizzle.config.ts
├── index.html
├── package-lock.json
├── package.json
├── src
│   ├── app.ts
│   ├── client.tsx
│   ├── db.ts
│   ├── firebase.ts
│   ├── index.ts
│   └── post.ts
├── style.css
├── tailwind.config.ts
├── test
│   ├── api.e2e.test.ts
│   ├── post.unit.test.ts
│   ├── posts.integration.test.ts
│   └── test-db.ts
├── tsconfig.json
└── vite.config.ts
```


## Extra: 投稿を削除する

Duration: 0:00:00

ここからは早く終わった人向けの拡張課題です。

### ゴール

自分が作った投稿だけ削除できる API を追加します。

- `DELETE /api/posts/:id` を追加する
- Firebase Bearer 認可を必須にする
- DB の `authorUid` とログイン中ユーザーの `uid` が一致したときだけ削除する
- 一致しない場合は `403` を返す

> **Hint:** `drizzle-orm` の `eq` と `and` を調べると実装しやすいです。

## Extra: 投稿を編集する

Duration: 0:00:00

### ゴール

自分が作った投稿だけ編集できる API を追加します。

- `PATCH /api/posts/:id` を追加する
- request body は `{ content }` にする
- 作成時と同じ Zod validation を使う
- 自分の投稿ではない場合は `403` を返す

編集後に投稿一覧を再取得すると、画面でも変更が確認できます。

## Extra: 複数スレッドにする

Duration: 0:00:00

### ゴール

単一スレッドだった掲示板を、複数スレッド対応にします。

- `threads` テーブルを追加する
- `posts` に `threadId` を追加する
- `GET /api/threads/:threadId/posts` を追加する
- `POST /api/threads/:threadId/posts` を追加する

まずはスレッドの作成 UI までは作らず、DB に手動でスレッドを1件追加して動作確認すると進めやすいです。
