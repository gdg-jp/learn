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
</style>

<!-- _class: title -->
<!-- _paginate: false -->

# Flutter で<br>ミニ SNS アプリを作ろう

GDG on Campus University of Osaka
2026.05.21 / 120 分ハンズオン

---

<!-- _class: lead -->

# 今日のゴール

テンプレートから始めて
**投稿フィードが動く Flutter Web アプリ**を完成させましょう!

---

## Discord に参加してください

![bg right:50% fit](../img/discord-invitation.png)

質問、詰まったところ、進捗共有は Discord で受け付けます

- 招待リンク: `https://discord.gg/pMTKHQRg`
- チャンネル: `#260521-flutter-workshop`
- 途中で止まったら、画面やエラー文をそのまま貼ってください!

---

## 今日作るもの

![bg right:60% fit](../img/final-app-screenshot.png)

縦スクロールで投稿を眺めるミニ SNS フィードです

- Firestore の `posts` を新着順に表示します
- 投稿ごとに画像、ユーザー名、本文、いいね数を出します
- いいねボタンで Firestore と画面の状態を更新します
- Pull to Refresh で投稿リストを再取得します

---

## 今日の流れ

| Step | 内容                                  | 目安  |
| ---- | ------------------------------------- | ----- |
| 1    | セットアップと起動確認                | 15 分 |
| 2    | Flutter の画面構造をつかむ            | 10 分 |
| 3    | Riverpod と Firestore の流れをつかむ  | 15 分 |
| 4    | `FeedPage` で状態を出し分ける         | 10 分 |
| 5    | `postsProvider` を Firestore につなぐ | 15 分 |
| 6    | 投稿一覧を `ListView` で表示する      | 15 分 |
| 7    | `PostCard` を段階的に作る             | 30 分 |
| 8    | 動作確認と共有                        | 10 分 |

---

## 今日のスコープ

<div class="container">

<div class="col">

### やること

- Flutter Web を Chrome で動かします
- Riverpod で Provider を読みます
- Firestore の stream を表示します
- 画像の上に本文とボタンを重ねます

</div>

<div class="col">

### やらないこと

- Firebase プロジェクトの新規作成
- 認証、投稿作成、投稿削除
- iOS / Android のネイティブビルド
- アーキテクチャ設計やテスト設計

</div>

</div>

---

## 触るファイルは 3 つ

![bg right:60% fit](../img/app-architecture.svg)

本編ではテンプレートの TODO を順に埋めます

| ファイル                            | 役割                      |
| ----------------------------------- | ------------------------- |
| `lib/feed_page.dart`                | 投稿一覧の状態とリスト UI |
| `lib/providers/post_providers.dart` | Firestore といいね操作    |
| `lib/widgets/post_card.dart`        | 投稿 1 件分のカード UI    |

---

<!-- _class: section yellow -->

# 01. セットアップ

## Flutter Web を Chrome で起動します

---

## 必要なもの

| ツール             | 確認方法            | 今日の用途                 |
| ------------------ | ------------------- | -------------------------- |
| Git                | `git --version`     | テンプレートを取得します   |
| Google Chrome      | `flutter devices`   | Flutter Web の実行先です   |
| Visual Studio Code | Flutter 拡張機能    | SDK とコード編集に使います |
| Flutter SDK        | `flutter --version` | アプリをビルドします       |

Android Studio、Android SDK、Xcode、エミュレータは今日は使いません

---

## OS ごとのセットアップ

<div class="container">

<div class="col">

### Windows

```powershell
winget install --id Git.Git -e
winget install --id Google.Chrome -e
winget install --id Microsoft.VisualStudioCode -e
```

VS Code の Flutter 拡張機能から SDK を入れます

</div>

<div class="col">

### macOS

```bash
xcode-select --install
brew install --cask google-chrome visual-studio-code
```

VS Code の Flutter 拡張機能から SDK を入れます

</div>

</div>

---

<!-- _class: invert -->

## 起動確認

```bash
git --version
flutter --version
flutter doctor -v
flutter devices

git clone https://github.com/gdsc-osaka/flutter-workshop.git
cd flutter-workshop
flutter pub get
flutter run -d chrome
```

`Chrome - develop for the web` にチェックが付き、Chrome で
`TODO: 投稿一覧を表示する` が見えれば準備 OK!

---

<!-- _class: section -->

# 02. Flutter の画面構造

## Widget ツリーだけ押さえます

---

## Flutter は Widget で画面を作ります

![bg right:60% fit](../img/widget-tree.svg)

Flutter では画面の部品を Widget と呼びます

- 文字は `Text`
- 画像は `Image`
- 縦並びは `Column`
- スクロールリストは `ListView`
- 画面の土台は `Scaffold`

親 Widget が `child` や `children` で子 Widget を持ちます

---

## Web 開発の知識と対応させる

| Web                    | Flutter                        |
| ---------------------- | ------------------------------ |
| DOM ツリー             | Widget ツリー                  |
| `<div>` / `<button>`   | `Container` / `ElevatedButton` |
| CSS の色、余白、角丸   | Widget のプロパティ            |
| React の component     | Widget                         |
| React の state / hooks | `StatefulWidget` / Riverpod    |
| Vite の HMR            | Hot reload                     |

カンマを付けておくと Dart formatter が読みやすく整えてくれます

---

<!-- _class: invert -->

## アプリの入口

```dart
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  runApp(const ProviderScope(child: MiniInstagramApp()));
}
```

- `Firebase.initializeApp()` で Firebase を初期化します
- `ProviderScope` で Riverpod をアプリ全体から使えるようにします
- `MaterialApp` の `home` は `FeedPage` です

---

## Hot reload / Hot restart

`flutter run -d chrome` で起動している間は、ターミナルから操作できます

| キー | 使う場面                                    |
| ---- | ------------------------------------------- |
| `r`  | 表示だけを変えたとき                        |
| `R`  | Firebase 初期化や Provider の形を変えたとき |
| `q`  | アプリを終了するとき                        |

画面が更新されないときは `R` で Hot restart してください!

---

<!-- _class: section green -->

# 03. Riverpod と Firestore

## データの流れを先に見ます

---

## アプリ全体の構成

![bg right:60% fit](../img/app-architecture.svg)

Flutter の UI、Riverpod の Provider、Firebase のサービスをつなぎます

- `FeedPage` は投稿リストの状態を読みます
- `PostCard` は投稿 1 件分といいね状態を読みます
- `postsProvider` は Firestore の stream を返します
- `postActionsProvider` は Firestore の更新処理を持ちます

---

## なぜ Riverpod を使う?

![bg right:60% fit](../img/state-flow.svg)

`StatefulWidget` だけだと、状態は Widget の中に閉じます

- 離れた Widget で同じ状態を使いづらいです
- 親から子へ値を渡し続ける必要が出ます
- Riverpod なら状態や取得処理を Widget の外に置けます
- Widget は `ref.watch()` で必要な Provider だけ読みます

---

<!-- _class: invert -->

## 今回使う Provider

```dart
final firestoreProvider = Provider<FirebaseFirestore>((ref) {
  return FirebaseFirestore.instance;
});

final postsProvider = StreamProvider<List<Post>>((ref) {
  // TODO: Firestore の stream に置き換えます
  return const Stream<List<Post>>.empty();
});

final likedPostIdsProvider = NotifierProvider<LikedPostIds, Set<String>>(
  LikedPostIds.new,
);
```

`postsProvider` を Firestore に接続するのが今日の中心です

---

## `ref.watch` と `ref.read`

| やりたいこと           | 使う API              | 例                                               |
| ---------------------- | --------------------- | ------------------------------------------------ |
| 画面に表示する値を読む | `ref.watch(provider)` | `final posts = ref.watch(postsProvider);`        |
| ボタン押下で処理を呼ぶ | `ref.read(provider)`  | `ref.read(postActionsProvider).toggleLike(...);` |

表示は `watch`、操作は `read` と覚えてください!

---

## `AsyncValue` は 3 状態

```dart
final posts = ref.watch(postsProvider);

return posts.when(
  loading: () => const CircularProgressIndicator(),
  error: (error, stackTrace) => Text('エラー: $error'),
  data: (items) => Text('投稿数: ${items.length}'),
);
```

`StreamProvider<List<Post>>` を `watch` すると、Widget 側には
`AsyncValue<List<Post>>` が届きます

---

<!-- _class: section red -->

# 04. FeedPage

## 投稿一覧の状態を分けます

---

<!-- _class: lead -->

# Step 1 のゴール

`postsProvider` の結果を
`data` / `error` / `loading` に分けましょう!

---

<!-- _class: invert -->

## 現在の `FeedPage`

```dart
class FeedPage extends ConsumerWidget {
  const FeedPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // TODO
    ref.watch(postsProvider);

    return const Scaffold(
      body: Center(
        child: Text('TODO: 投稿一覧を表示する'),
      ),
    );
  }
}
```

Provider を読んでいますが、まだ画面では使っていません

---

<!-- _class: invert -->

## `posts.when` の形を作る

```dart
@override
Widget build(BuildContext context, WidgetRef ref) {
  final posts = ref.watch(postsProvider);

  return Scaffold(
    body: posts.when(
      data: (items) {
        return Center(child: Text('投稿数: ${items.length}'));
      },
      error: (error, stackTrace) {
        return Center(child: Text('エラー: $error'));
      },
      loading: () {
        return const Center(child: Text('投稿を読み込んでいます...'));
      },
    ),
  );
}
```

---

## まず確認する表示

この時点では `postsProvider` がまだ Firestore に接続されていません

```text
投稿を読み込んでいます...
```

この表示が見えれば、`AsyncValue.when()` の骨組みは OK です

次のステップで `postsProvider` が投稿データを返すようにします

---

<!-- _class: section -->

# 05. Firestore から取得

## `postsProvider` を stream にします

---

<!-- _class: lead -->

# Step 2 のゴール

Firestore の `posts` を購読して
**新着順の投稿リスト**を受け取りましょう!

---

## Riverpod と Firestore の流れ

![bg right:60% fit](../img/riverpod-firestore-flow.svg)

`postsProvider` は Firestore の変更を stream として返します

1. Firestore の `posts` コレクションを選びます
2. `createdAt` の降順で並べます
3. `snapshots()` でリアルタイム更新を受け取ります
4. `Post.fromDocument` で `List<Post>` に変換します

---

<!-- _class: invert -->

## `postsProvider` を実装する

```dart
final postsProvider = StreamProvider<List<Post>>((ref) {
  final firestore = ref.watch(firestoreProvider);

  return firestore
      .collection('posts')
      .orderBy('createdAt', descending: true)
      .snapshots()
      .map((snapshot) {
        return snapshot.docs.map(Post.fromDocument).toList();
      });
});
```

Firestore のデータが変わると、`FeedPage` が自動で再描画されます

---

## `Post` モデルのフィールド

| フィールド  | 型         | 内容                      |
| ----------- | ---------- | ------------------------- |
| `id`        | `String`   | Firestore ドキュメント ID |
| `imageUrl`  | `String`   | 投稿画像の URL            |
| `authorUrl` | `String`   | 投稿者アイコンの URL      |
| `authorId`  | `String`   | 投稿者 ID                 |
| `text`      | `String`   | 投稿本文                  |
| `likes`     | `int`      | いいね数                  |
| `createdAt` | `DateTime` | 投稿日時                  |

`Post.fromDocument()` が Firestore のドキュメントを変換します

---

## 投稿数が見えれば接続成功

Hot restart して画面を確認します

```text
投稿数: 3
```

Firestore に `posts` データがある場合は件数が表示されます

まだリスト UI は作っていないので、次は `FeedPage` の `data` を
`ListView.builder` に変えます

---

<!-- _class: section yellow -->

# 06. 投稿一覧を表示

## `FeedPage` をリスト UI にします

---

<!-- _class: lead -->

# Step 3 のゴール

投稿データを 1 件ずつ `PostCard` に渡して
縦スクロールで表示しましょう!

---

<!-- _class: invert -->

## `data` の UI をリストにする

```dart
data: (items) {
  if (items.isEmpty) {
    return const _EmptyFeed();
  }

  return RefreshIndicator(
    onRefresh: () {
      return ref.refresh(postsProvider.future);
    },
    child: ListView.builder(
      padding: EdgeInsets.zero,
      itemCount: items.length,
      itemBuilder: (context, index) {
        return ProviderScope(
          overrides: [
            currentPostProvider.overrideWithValue(items[index]),
          ],
          child: const PostCard(),
        );
      },
    ),
  );
},
```

---

## ここで追加する UI 状態

| 状態       | 作るもの                                | 目的                                 |
| ---------- | --------------------------------------- | ------------------------------------ |
| 空         | `_EmptyFeed`                            | 投稿がない理由を画面で伝えます       |
| エラー     | `_ErrorView`                            | Firestore の読み込み失敗を表示します |
| 読み込み中 | `CircularProgressIndicator`             | 待っている状態を明確にします         |
| データあり | `RefreshIndicator` + `ListView.builder` | 投稿を縦に並べます                   |

真っ白な画面を避け、次に確認すべきことが分かる UI にします

---

## 期待される表示

`PostCard` はまだ未実装なので、各カードには TODO が出ます

```text
TODO: 投稿カードを作る
TODO: 投稿カードを作る
TODO: 投稿カードを作る
```

投稿の件数分だけ縦長のプレースホルダーが出れば成功です

---

<!-- _class: section green -->

# 07. PostCard を作る

## 画像、本文、いいねを段階的に重ねます

---

<!-- _class: lead -->

# Step 4 のゴール

`currentPostProvider` から投稿 1 件を読み
**縦長の投稿カード**を完成させましょう!

---

## 投稿カードの重なり

![bg right:50% fit](../img/post-card-layout.svg)

`Stack` で背景画像の上に UI を重ねます

- 一番下に `Image.network`
- 下側にグラデーション
- 左下に投稿本文
- 右下にいいねボタン
- 上に投稿者情報

---

<!-- _class: invert -->

## まずは画像だけ表示する

```dart
@override
Widget build(BuildContext context, WidgetRef ref) {
  final post = ref.watch(currentPostProvider);

  return AspectRatio(
    aspectRatio: 9 / 16,
    child: Image.network(
      post.imageUrl,
      fit: BoxFit.cover,
      loadingBuilder: (context, child, loadingProgress) {
        if (loadingProgress == null) {
          return child;
        }

        return const Center(child: CircularProgressIndicator());
      },
      errorBuilder: (context, error, stackTrace) {
        return const ColoredBox(
          color: Color(0xFF1D1D21),
          child: Center(child: Icon(Icons.broken_image_outlined, size: 48)),
        );
      },
    ),
  );
}
```

---

<!-- _class: invert -->

## `Stack` で本文を重ねる

```dart
return AspectRatio(
  aspectRatio: 9 / 16,
  child: Stack(
    fit: StackFit.expand,
    children: [
      Image.network(post.imageUrl, fit: BoxFit.cover),
      const DecoratedBox(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.transparent,
              Colors.transparent,
              Color(0xB0000000),
            ],
          ),
        ),
      ),
      Positioned(
        left: 16,
        right: 80,
        bottom: 28,
        child: Text(post.text, maxLines: 3),
      ),
    ],
  ),
);
```

---

## `Stack` と `Positioned` の役割

| Widget                        | 役割                                       |
| ----------------------------- | ------------------------------------------ |
| `AspectRatio(9 / 16)`         | 投稿カードを縦長に固定します               |
| `Stack(fit: StackFit.expand)` | 子 Widget を同じ領域に重ねます             |
| `DecoratedBox`                | 画像の下側を暗くして本文を読みやすくします |
| `Positioned`                  | 本文、ボタン、投稿者情報の位置を決めます   |

画像の上に文字を置くときは、読みやすさのために背景を少し暗くします

---

<!-- _class: invert -->

## いいね状態を読む

```dart
final post = ref.watch(currentPostProvider);
final likedPostIds = ref.watch(likedPostIdsProvider);
final isLiked = likedPostIds.contains(post.id);
```

いいね済みかどうかは、投稿 ID が集合に含まれるかで判断します

```dart
IconButton.filledTonal(
  tooltip: isLiked ? 'いいねを取り消す' : 'いいね',
  onPressed: () async {
    await ref
        .read(postActionsProvider)
        .toggleLike(post, isLiked: isLiked);
  },
  icon: Icon(
    isLiked ? Icons.favorite : Icons.favorite_border,
    color: isLiked ? Colors.pinkAccent : Colors.white,
  ),
)
```

操作を呼ぶ Provider は `ref.read()` です

---

## 投稿者情報を上に置く

```dart
Positioned(
  top: 12,
  left: 12,
  right: 12,
  child: SafeArea(
    bottom: false,
    child: Row(
      children: [
        CircleAvatar(
          radius: 17,
          backgroundImage:
              post.authorUrl.isEmpty ? null : NetworkImage(post.authorUrl),
        ),
        const SizedBox(width: 10),
        Text(
          post.authorId,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
      ],
    ),
  ),
)
```

`SafeArea` でステータスバーやノッチに近い位置でも隠れにくくします

---

## 完成チェック

Chrome で次の動作を確認します

- 投稿画像、ユーザー名、本文、いいね数が表示されます
- 長い本文は 3 行で省略されます
- いいねボタンを押すとハートの見た目が変わります
- Firestore の `likes` が更新され、画面にも反映されます
- 画像 URL が壊れている投稿では壊れた画像アイコンが出ます

ここまでできれば本編は完了です!

---

<!-- _class: section red -->

# 08. まとめ

## できたところを共有します

---

## 今日学んだこと

<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 24px;">
  <div style="padding: 20px; border-top: 4px solid var(--gdg-blue); background: var(--gdg-surface); border-radius: 8px;">
    <h3 style="margin: 0 0 8px;">Widget ツリー</h3>
    <p>画面を Widget の入れ子として組み立てました</p>
  </div>
  <div style="padding: 20px; border-top: 4px solid var(--gdg-green); background: var(--gdg-surface); border-radius: 8px;">
    <h3 style="margin: 0 0 8px;">Riverpod</h3>
    <p><code>ConsumerWidget</code> と <code>WidgetRef</code> で Provider を読みました</p>
  </div>
  <div style="padding: 20px; border-top: 4px solid var(--gdg-yellow); background: var(--gdg-surface); border-radius: 8px;">
    <h3 style="margin: 0 0 8px;">Firestore</h3>
    <p><code>StreamProvider</code> でリアルタイム更新を扱いました</p>
  </div>
  <div style="padding: 20px; border-top: 4px solid var(--gdg-red); background: var(--gdg-surface); border-radius: 8px;">
    <h3 style="margin: 0 0 8px;">Stack</h3>
    <p>画像の上に本文、ボタン、投稿者情報を重ねました</p>
  </div>
</div>

---

## 共有してみましょう

時間が残ったら、隣の人や Discord に共有してください!

| 観点       | 話すこと                                   |
| ---------- | ------------------------------------------ |
| 進捗       | どのステップまで実装できましたか           |
| 詰まった点 | どこで止まり、どう解決しましたか           |
| 改善案     | デザインや機能で次に足したいものは何ですか |

共有先: Discord `#260521-flutter-workshop`

---

## Extra で挑戦できること

本編が終わった人は、codelab の Extra に進めます

| Extra        | 追加する機能                           |
| ------------ | -------------------------------------- |
| ログイン機能 | Firebase Authentication の匿名ログイン |
| 投稿機能     | 画像 URL と本文から Firestore に投稿   |
| 投稿時刻     | `createdAt` から相対時間を表示         |

まずは短い改善として、本文の文字サイズ、ボタン位置、空状態の見た目を調整しても OK です

---

## 次に読むもの

- 完成版のコード: `https://github.com/gdsc-osaka/flutter-workshop-example`
- Flutter の学習パス: `https://docs.flutter.dev/learn/pathway`
- Flutter の状態管理: `https://docs.flutter.dev/data-and-backend/state-mgmt/options`
- Riverpod の Provider: `https://riverpod.dev/docs/concepts2/providers`

詰まったところや改善したところを `#260521-flutter-workshop` に残してください!

---

<!-- _class: lead -->

# Thank you!

質問は `#260521-flutter-workshop` で待っています!
