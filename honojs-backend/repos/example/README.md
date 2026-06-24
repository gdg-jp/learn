# Hono.js で掲示板バックエンド API サーバーを作ろう

90分 codelab 用の完成版サンプルです。Hono が `/api/*` とビルド済み React SPA の両方を配信します。

## Stack

- Hono + TypeScript
- PostgreSQL + Drizzle
- Zod
- Firebase Admin SDK / Firebase Web Auth
- React SPA + HeroUI + Tailwind
- Biome

## Setup

```bash
npm install
cp .env.example .env
docker compose up -d
npm run db:push
```

Firebase Admin SDK の秘密鍵 JSON は `serviceAccount.json` としてこのディレクトリに置きます。別の場所に置く場合は `.env` の `FIREBASE_SERVICE_ACCOUNT_PATH` を変更してください。

`serviceAccount.json` は `.gitignore` 済みです。コミットしないでください。

フロントエンドの Firebase Web 設定は `src/client.tsx` の `firebaseConfig` を自分の Firebase プロジェクト値に置き換えます。プレースホルダーのままでもビルドは通りますが、ログインは実プロジェクト設定が必要です。

## Development

```bash
npm run build
npm start
```

起動後:

- SPA: <http://localhost:3000>
- health check: <http://localhost:3000/api/health>
- posts API: <http://localhost:3000/api/posts>

Vite の開発サーバーで画面だけを素早く確認する場合:

```bash
npm run build:server
npm run dev
```

別ターミナルで必要に応じて:

```bash
npx vite
```

## API

### `GET /api/posts`

認証不要です。投稿を新しい順で返します。空の DB では `posts: []` になります。

```json
{
  "posts": []
}
```

### `POST /api/posts`

Firebase ID トークンの Bearer 認証が必要です。本文は `{ "content": "..." }` だけを送ります。

```bash
curl -X POST http://localhost:3000/api/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <Firebase ID token>" \
  -d '{"content":"こんにちは Hono!"}'
```

`authorUid`, `authorName`, `authorPhotoUrl` は Firebase トークンからサーバー側で決めます。

## Verification

```bash
npm run lint
npm run build
```

DB スキーマ更新:

```bash
npm run db:push
```
