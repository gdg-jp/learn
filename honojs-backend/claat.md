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

Duration: 0:25:00

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

## バックエンドの説明

Duration: 0:15:00

このステップでは、実装に入る前にバックエンドの役割を整理します。覚える言葉は多く見えますが、すべては「ブラウザから来たリクエストを受け取り、安全にデータを読み書きして、レスポンスを返す」という流れに集約できます。

![掲示板アプリのリクエストの流れ](img/backend-request-flow.png)

### なぜバックエンドが必要か

![バックエンドが守る信頼境界](img/backend-trust-boundary.png)

フロントエンドは、利用者のブラウザで動きます。画面を表示し、ボタンや入力欄の操作を受け取り、API を呼び出します。一方で、ブラウザに届いたコードは利用者から見えるため、DB 接続情報や Firebase Admin SDK の秘密鍵を置けません。

バックエンドは、サーバー側の信頼できる場所で動きます。このコードラボでは Hono API がバックエンドです。

| 場所           | 担当すること       | このコードラボでの例                        |
| -------------- | ------------------ | ------------------------------------------- |
| フロントエンド | 画面と操作         | Google ログイン画面、投稿フォーム、投稿一覧 |
| バックエンド   | ルールとデータ     | 投稿内容の検証、認可、DB 保存               |
| 外部サービス   | 認証などの専門機能 | Firebase Auth                               |
| DB             | アプリの記憶       | PostgreSQL の `posts` テーブル              |

### API はフロントエンドとバックエンドの約束

![HTTPリクエストの解剖図](img/api-request-anatomy.png)

API は、フロントエンドとバックエンドの間の約束です。約束には、URL、HTTP メソッド、ヘッダー、リクエスト body、レスポンスの形が含まれます。

このコードラボで作る API は2つです。

| HTTP メソッド | URL          | 役割                 |
| ------------- | ------------ | -------------------- |
| `GET`         | `/api/posts` | 投稿一覧を取得する   |
| `POST`        | `/api/posts` | 新しい投稿を作成する |

`POST /api/posts` では、フロントエンドから投稿本文だけを送ります。バックエンドは、投稿者の `uid`、名前、アイコン URL を Firebase ID トークンから取り出します。投稿者名をフロントエンドから受け取らないことで、他人の名前を名乗る投稿を防ぎます。

### DB はアプリの記憶

![投稿がpostsテーブルの1行になる流れ](img/db-post-record.png)

DB は、アプリのデータを保存し、あとから検索できるようにする場所です。このコードラボでは PostgreSQL を使い、掲示板の投稿を `posts` テーブルに保存します。

| カラム             | 役割                     |
| ------------------ | ------------------------ |
| `id`               | 投稿を一意に識別する番号 |
| `content`          | 投稿本文                 |
| `author_uid`       | Firebase のユーザー ID   |
| `author_name`      | 投稿者名                 |
| `author_photo_url` | 投稿者アイコン           |
| `created_at`       | 作成日時                 |

DB は単なる保存場所ではありません。複数人が同時にアクセスしても壊れにくくし、必要なデータを検索しやすくし、`not null` のようなルールでデータの形も守ります。

### バリデーションは外から来た値の門番

![Zodによる検証パイプライン](img/zod-validation-gate.png)

API に届く JSON は、常に正しいとは限りません。空文字、長すぎる文字列、JSON ではない値、想定外の object が届くことがあります。

このコードラボでは Zod を使って、投稿作成のリクエストを検証します。

`unknown input` → `Zod validation` → `typed data` → `DB`

Zod の役割は、外から来た信用できない値を、アプリの内側で安心して扱える値に変換することです。

### 認証と認可は分けて考える

![認証と認可の2段階ゲート](img/auth-authz-gates.png)

認証は「あなたは誰か」を確認することです。認可は「あなたはその操作をしてよいか」を確認することです。

| API               | 認可                       |
| ----------------- | -------------------------- |
| `GET /api/posts`  | 誰でも取得できる           |
| `POST /api/posts` | ログイン済みだけ作成できる |

フロントエンドは Firebase ID トークンを `Authorization: Bearer ...` ヘッダーに入れて送ります。バックエンドは Firebase Admin SDK の `verifyIdToken` で検証します。

ログイン済みであっても、何でもできるわけではありません。たとえば拡張課題の投稿削除では、「ログイン済み」だけでなく「その投稿を作った本人か」も確認する必要があります。

### 今日使う言葉

| 言葉             | 意味                                                 |
| ---------------- | ---------------------------------------------------- |
| リクエスト       | ブラウザから API へ送る要求                          |
| レスポンス       | API からブラウザへ返す結果                           |
| エンドポイント   | `GET /api/posts` のような API の呼び出し口           |
| HTTP メソッド    | `GET`、`POST` など、何をしたいかを表す動詞           |
| JSON             | フロントエンドとバックエンドでやり取りするデータ形式 |
| ステータスコード | `200`、`201`、`400`、`401` など、結果を表す番号      |
| テーブル         | DB のデータの入れ物                                  |
| レコード         | テーブルに保存された1件分のデータ                    |
| スキーマ         | データの形やルール                                   |
| バリデーション   | 入力が期待した形か確認すること                       |

### 参考にした公開資料

この説明は、日本のソフトウェア企業が公開している研修資料の構成も参考にしています。

- [MIXI 新卒向け技術研修 2025](https://zenn.dev/mixi/articles/95e0d0477c1ed7)
- [リクルート エンジニアコース新人研修 2025](https://techblog.recruit.co.jp/article-5841/)
- [Cybozu エンジニア新人研修 2025](https://blog.cybozu.io/entry/2025/07/08/171543)
- [Cybozu Web API を使ってみよう](https://cybozu.dev/ja/tutorials/hello-js/web-api/)
- [CyberAgent セキュリティ研修 Technical Part 2024](https://speakerdeck.com/cyberagentdevelopers/security-training-technical-part2024)

## Hono プロジェクトを作成する

Duration: 0:10:00

ここから実装に入ります。まずは Hono の公式 starter から、新しい TypeScript プロジェクトを作成します。

> **Tips:** Hono は、Web API を作るための軽量な TypeScript フレームワークです。URL ごとに処理を書く「ルーティング」が中心で、今回のような小さな API サーバーを作り始めやすい道具です。

### 作業フォルダでプロジェクトを作成する

ターミナルまたは PowerShell で、作業用フォルダに移動してから次を実行します。

```bash
npm create hono@latest honojs-backend-app
```

> **Tips:** `npm create` は、指定した starter から新しいプロジェクトを作るコマンドです。ここでは Hono 公式 starter を使って、`honojs-backend-app` というフォルダに最小構成の Hono アプリを作ります。

途中で template を聞かれたら、`nodejs` を選びます。

```bash
cd honojs-backend-app
npm install
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

この時点では、Hono starter が作った最小構成だけがあります。

- `package.json`
- `tsconfig.json`
- `src/index.ts`

<button>
  [この時点のコードを見る: step-npm-create-hono](https://github.com/gdg-jp/honojs-backend-example/tree/step-npm-create-hono)
</button>

## 必要なライブラリを追加する

Duration: 0:08:00

このステップでは、後の手順で使うライブラリを先に追加します。package scripts は追加せず、Hono starter が最初から用意した `npm run dev`、`npm run build`、`npm start` を使います。DB 操作や React build には `npx` を使います。

### バックエンド用ライブラリを追加する

```bash
npm install @hono/node-server drizzle-orm pg zod firebase-admin
```

> **Tips:** `npm install` は、プロジェクトで使うライブラリを `node_modules` に入れ、`package.json` に記録するコマンドです。別の PC でも `npm install` すれば同じライブラリを復元できます。

### フロントエンド用ライブラリを追加する

```bash
npm install react react-dom firebase @heroui/react @heroui/theme @react-aria/ssr framer-motion lucide-react
```

### 開発用ライブラリを追加する

```bash
npm install -D vite @vitejs/plugin-react typescript tsx drizzle-kit @types/node @types/pg @types/react @types/react-dom tailwindcss @tailwindcss/vite
```

> **Tips:** `-D` は「開発中だけ使うライブラリ」を意味します。`drizzle-kit` は DB 定義を反映するための開発用コマンドなので、`dependencies` ではなく `devDependencies` に入れます。

### 現時点のコードベース

この時点では、ファイル構成はほぼ変わりません。代わりに `package.json` と `package-lock.json` にライブラリ情報が追加されています。

- `package.json`
- `package-lock.json`
- `tsconfig.json`
- `src/index.ts`

<button>
  [この時点のコードを見る: step-npm-install](https://github.com/gdg-jp/honojs-backend-example/tree/step-npm-install)
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
    port: 3000
  },
  (info) => {
    console.log(`Server is running on http://localhost:${info.port}`);
  }
);
```

`serveStatic` は、`dist/public` にある CSS や JavaScript を Hono から配信します。`app.get("*", ...)` は、React SPA の入口である `index.html` を返します。ただし `/api/` から始まる未実装の API は、HTML ではなく JSON の `404` を返すようにしておきます。

### ビルドして起動する

React SPA をビルドし、そのあと Hono サーバーをビルドします。この時点ではまだ投稿 API を作っていないため、ログイン後の投稿一覧にはエラーが表示されます。次のステップで `GET /api/posts` を作ると、画面から投稿一覧を確認できるようになります。

```bash
npx vite build
npm run build
npm start
```

ブラウザで [http://localhost:3000](http://localhost:3000) を開きます。Google ログイン画面が表示されれば成功です。

### 現時点のコードベース

この時点で、React SPA を同じ Hono サーバーから配信できるようになりました。次のステップから、API を追加するたびにブラウザで画面の変化を確認できます。

- `index.html`
- `package.json`
- `style.css`
- `tailwind.config.ts`
- `tsconfig.json`
- `vite.config.ts`
- `src/client.tsx`
- `src/index.ts`

<button>
  [この時点のコードを見る: step-react-spa](https://github.com/gdg-jp/honojs-backend-example/tree/step-react-spa)
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
    port: 3000
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

この時点で、最初の API が動きました。

- `index.html`
- `package.json`
- `style.css`
- `tailwind.config.ts`
- `tsconfig.json`
- `vite.config.ts`
- `src/client.tsx`
- `src/index.ts`
- `src/post.ts`

<button>
  [この時点のコードを見る: step-get-posts-memory](https://github.com/gdg-jp/honojs-backend-example/tree/step-get-posts-memory)
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
+      return c.json({ error: "投稿内容を入力してください。" }, 400);
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

この時点で、DB なしの小さな掲示板 API ができました。

- `index.html`
- `package.json`
- `style.css`
- `tailwind.config.ts`
- `tsconfig.json`
- `vite.config.ts`
- `src/client.tsx`
- `src/index.ts`
- `src/post.ts`

<button>
  [この時点のコードを見る: step-post-posts-memory](https://github.com/gdg-jp/honojs-backend-example/tree/step-post-posts-memory)
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

この時点で、投稿の保存先がメモリから PostgreSQL に変わりました。

- `docker-compose.yml`
- `drizzle.config.ts`
- `index.html`
- `package.json`
- `style.css`
- `tailwind.config.ts`
- `tsconfig.json`
- `vite.config.ts`
- `src/client.tsx`
- `src/index.ts`
- `src/db.ts`
- `src/post.ts`

<button>
  [この時点のコードを見る: step-drizzle-postgres](https://github.com/gdg-jp/honojs-backend-example/tree/step-drizzle-postgres)
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
+import { z } from "zod";
import { db } from "./db.js";

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

この時点で、外から来た JSON を Zod で検証できるようになりました。

- `docker-compose.yml`
- `drizzle.config.ts`
- `index.html`
- `package.json`
- `style.css`
- `tailwind.config.ts`
- `tsconfig.json`
- `vite.config.ts`
- `src/client.tsx`
- `src/index.ts`
- `src/db.ts`
- `src/post.ts`

<button>
  [この時点のコードを見る: step-zod-validation](https://github.com/gdg-jp/honojs-backend-example/tree/step-zod-validation)
</button>

## Firebase Bearer 認可を実装する

Duration: 0:15:00

このステップでは、投稿作成 API をログイン済みユーザーだけが使えるようにします。`GET /api/posts` はログインなしでも見られますが、`POST /api/posts` は Firebase ID トークンを必須にします。

### serviceAccount.json を配置する

Discord の `#260625-honojs-backend` に講師が投稿した Firebase Admin SDK の JSON をコピーし、プロジェクト直下に `serviceAccount.json` という名前で保存します。

> **Warning:** `serviceAccount.json` は秘密鍵です。GitHub、Discord の別チャンネル、SNS などに貼らないでください。

### .gitignore に秘密鍵を追加する

`.gitignore` に次の行を追加します。

```diff text:.gitignore
+serviceAccount.json
+.env
```

この設定により、秘密鍵や環境変数ファイルが Git に入る事故を防ぎます。

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

この時点で、API 側の認証認可まで完成しました。

- `.gitignore`
- `docker-compose.yml`
- `drizzle.config.ts`
- `index.html`
- `package.json`
- `style.css`
- `tailwind.config.ts`
- `tsconfig.json`
- `vite.config.ts`
- `src/client.tsx`
- `src/index.ts`
- `src/db.ts`
- `src/firebase.ts`
- `src/post.ts`

<button>
  [この時点のコードを見る: step-firebase-auth](https://github.com/gdg-jp/honojs-backend-example/tree/step-firebase-auth)
</button>

## Extra: 投稿を削除する

Duration: 0:05:00

ここからは早く終わった人向けの拡張課題です。

### ゴール

自分が作った投稿だけ削除できる API を追加します。

- `DELETE /api/posts/:id` を追加する
- Firebase Bearer 認可を必須にする
- DB の `authorUid` とログイン中ユーザーの `uid` が一致したときだけ削除する
- 一致しない場合は `403` を返す

> **Hint:** `drizzle-orm` の `eq` と `and` を調べると実装しやすいです。

## Extra: 投稿を編集する

Duration: 0:05:00

### ゴール

自分が作った投稿だけ編集できる API を追加します。

- `PATCH /api/posts/:id` を追加する
- request body は `{ content }` にする
- 作成時と同じ Zod validation を使う
- 自分の投稿ではない場合は `403` を返す

編集後に投稿一覧を再取得すると、画面でも変更が確認できます。

## Extra: 複数スレッドにする

Duration: 0:05:00

### ゴール

単一スレッドだった掲示板を、複数スレッド対応にします。

- `threads` テーブルを追加する
- `posts` に `threadId` を追加する
- `GET /api/threads/:threadId/posts` を追加する
- `POST /api/threads/:threadId/posts` を追加する

まずはスレッドの作成 UI までは作らず、DB に手動でスレッドを1件追加して動作確認すると進めやすいです。

## おめでとうございます！

Duration: 0:03:00

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
