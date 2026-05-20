summary: Flutter でミニ SNS アプリを作ろう！120 分ハンズオン
id: flutter-workshop
categories: Flutter, Dart, Web
environments: Web
status: Draft
author: GDG on Campus University of Osaka

# Flutter でミニ SNS アプリを作ろう

## Codelab の概要
Duration: 0:05:00

このハンズオンでは、テンプレートから出発して**投稿フィードを表示するミニ SNS アプリ**を完成させます。
Flutter / Dart を触ったことがなくても大丈夫です！

**今日のゴール**

- Flutter の最小限の文法を知る
- Riverpod で状態を管理する
- Firestore から投稿をリアルタイム取得する
- ミニ SNS の投稿フィードを完成させる

**今日の流れ (120 分)**

| # | 内容 | 時間 |
|---|------|------|
| 1 | Codelab の概要・デモ | 5 分 |
| 2 | 事前準備 | 10 分 |
| 3 | Flutter 基礎 | 20 分 |
| 4 | Riverpod 基礎 | 15 分 |
| 5 | ハンズオン① FeedPage | 20 分 |
| 6 | ハンズオン② postsProvider | 20 分 |
| 7 | ハンズオン③ PostCard | 20 分 |
| 8 | 共有 | 10 分 |

**今日やらないこと**

- iOS / Android エミュレータの利用
- 認証・投稿の作成・削除
- Firebase 設定の変更

**完成イメージ**

縦スクロールで投稿を眺めるフィードアプリです。

- 投稿が縦にずらっと並ぶ (TikTok / Reels 風)
- 各投稿に**画像・ユーザー名・テキスト**が表示される
- ❤️ ボタンでその場でいいね！できる
- 引っ張って更新 (Pull to Refresh) もできる

完成版のコード: `gdsc-osaka/flutter-workshop-example`

**アーキテクチャ概観**

今日はこの 3 ファイルに手を入れます。

```
FeedPage (ConsumerWidget)
  lib/feed_page.dart
    ↓ ref.watch
postsProvider (StreamProvider)
  lib/providers/post_providers.dart
    ↓ StreamProvider
PostCard (ConsumerWidget)
  lib/widgets/post_card.dart
```

## 事前準備 (Windows)
Duration: 0:20:00

ハンズオン当日までに、以下のツールをインストールしておいてください。  
今日は **Flutter Web を Chrome で動かす** ため、Android Studio / Android SDK / Xcode は不要です。

> **Note:** すでにインストール済みのものは、確認コマンドだけ実行してください。

### 1. Git

Git は、リポジトリを取得するために使います。

#### 方法 A: インストーラーで入れる

[Git for Windows](https://git-scm.com/download/win) から最新版のインストーラーをダウンロードして実行してください。  
インストール中の選択肢は、基本的にデフォルトのままで構いません。

#### 方法 B: winget で入れる

PowerShell を開いて、以下を実行します。

```powershell
winget install --id Git.Git -e --source winget
````

#### 確認

PowerShell またはコマンドプロンプトを開き直して、以下を実行します。

```bash
git --version
```

バージョン番号が表示されれば OK です。

### 2. Google Chrome

[Google Chrome](https://www.google.com/chrome/) からインストールしてください。
すでに入っている場合はスキップで OK です。

### 3. Visual Studio Code

[Visual Studio Code](https://code.visualstudio.com/) から Windows 版のインストーラーをダウンロードして実行してください。

通常は **User Installer** で問題ありません。
VS Code のセットアップでは、基本的にデフォルト設定のままで構いません。

> **Note:** VS Code のインストール後、ターミナルから `code .` を使いたい場合は PowerShell / コマンドプロンプトを開き直してください。

### 4. Flutter 拡張機能と Flutter SDK

Flutter SDK は、VS Code の Flutter 拡張機能からインストールします。

1. VS Code を開く
2. 左サイドバーの拡張機能アイコンを開く
3. `Flutter` を検索する
4. **Flutter** 拡張機能をインストールする

   * Dart 拡張機能も自動で入ります
5. `Ctrl + Shift + P` で Command Palette を開く
6. `Flutter: New Project` を選択する
7. Flutter SDK が見つからない場合は **Download SDK** を選択する
8. SDK の保存先を選ぶ

   * 例: `C:\src`
   * `Program Files` など、スペースを含むパスは避けてください
9. **Clone Flutter** をクリックする
10. 完了後、表示された場合は **Add SDK to PATH** をクリックする
11. VS Code と PowerShell / コマンドプロンプトを開き直す

### 5. Flutter の確認

PowerShell またはコマンドプロンプトで以下を実行します。

```bash
flutter --version
flutter doctor -v
```

`flutter --version` でバージョンが表示されれば SDK のインストールは完了です。

`flutter doctor -v` では、今日は **Chrome の項目に ✓ が付いていれば十分**です。
Android toolchain や Visual Studio、Android Studio などに ✗ が付いていても、今回のハンズオンでは無視して OK です。

> **Troubleshooting:** `flutter` コマンドが見つからない場合は、VS Code とターミナルをすべて閉じて開き直してください。それでも解決しない場合は、Flutter SDK の `bin` フォルダが PATH に追加されているか確認してください。

### 6. リポジトリをクローンして起動確認

PowerShell または VS Code のターミナルで以下を順に実行してください。

```bash
git clone https://github.com/gdsc-osaka/flutter-workshop.git
cd flutter-workshop
flutter pub get
flutter run -d chrome
```

Chrome が起動して「**TODO: 投稿一覧を表示する**」が表示されたら準備完了です。

最後に、VS Code で `flutter-workshop/` フォルダを開いておきましょう。

```bash
code .
```

> **Note:** `flutter pub get` は依存パッケージのダウンロードです。初回は少し時間がかかることがあります。

---

## 事前準備 (macOS)

Duration: 0:20:00

ハンズオン当日までに、以下のツールをインストールしておいてください。
今日は **Flutter Web を Chrome で動かす** ため、iOS シミュレータ / Android エミュレータは使いません。

> **Note:** すでにインストール済みのものは、確認コマンドだけ実行してください。

### 1. Git

macOS では、Git は Xcode Command Line Tools に含まれています。
ターミナルで以下を実行してください。

```bash
xcode-select --install
```

ダイアログが出たら「インストール」を押して完了を待ちます。
すでに入っている場合は「既にインストールされています」という内容のメッセージが出ますが、問題ありません。

#### 確認

```bash
git --version
```

バージョン番号が表示されれば OK です。

### 2. Google Chrome

[Google Chrome](https://www.google.com/chrome/) からインストールしてください。
すでに入っている場合はスキップで OK です。

### 3. Visual Studio Code

[Visual Studio Code](https://code.visualstudio.com/) から macOS 版をダウンロードしてください。

1. ダウンロードした `.dmg` を開く
2. `Visual Studio Code.app` を `Applications` フォルダにドラッグする
3. `Applications` フォルダから VS Code を起動する

ターミナルから `code .` で VS Code を開けるようにする場合は、以下も実行します。

1. VS Code を開く
2. `Cmd + Shift + P` で Command Palette を開く
3. `shell command` と入力する
4. **Shell Command: Install 'code' command in PATH** を選択する
5. ターミナルを開き直す

### 4. Flutter 拡張機能と Flutter SDK

Flutter SDK は、VS Code の Flutter 拡張機能からインストールします。

1. VS Code を開く
2. 左サイドバーの拡張機能アイコンを開く
3. `Flutter` を検索する
4. **Flutter** 拡張機能をインストールする

   * Dart 拡張機能も自動で入ります
5. `Cmd + Shift + P` で Command Palette を開く
6. `Flutter: New Project` を選択する
7. Flutter SDK が見つからない場合は **Download SDK** を選択する
8. SDK の保存先を選ぶ

   * 例: `~/development`
9. **Clone Flutter** をクリックする
10. 完了後、表示された場合は **Add SDK to PATH** をクリックする
11. VS Code とターミナルを開き直す

> **Note:** Homebrew で Flutter を入れる手順は環境差が出やすいため、このハンズオンでは VS Code から SDK を入れる方法に統一します。

### 5. Flutter の確認

ターミナルで以下を実行します。

```bash
flutter --version
flutter doctor -v
```

`flutter --version` でバージョンが表示されれば SDK のインストールは完了です。

`flutter doctor -v` では、今日は **Chrome の項目に ✓ が付いていれば十分**です。
Android toolchain や Xcode に ✗ が付いていても、今回のハンズオンでは無視して OK です。

> **Troubleshooting:** `flutter` コマンドが見つからない場合は、VS Code とターミナルをすべて閉じて開き直してください。それでも解決しない場合は、Flutter SDK の `bin` フォルダが PATH に追加されているか確認してください。

### 6. リポジトリをクローンして起動確認

ターミナルまたは VS Code のターミナルで以下を順に実行してください。

```bash
git clone https://github.com/gdsc-osaka/flutter-workshop.git
cd flutter-workshop
flutter pub get
flutter run -d chrome
```

Chrome が起動して「**TODO: 投稿一覧を表示する**」が表示されたら準備完了です。

最後に、VS Code で `flutter-workshop/` フォルダを開いておきましょう。

```bash
code .
```

> **Note:** `flutter pub get` は依存パッケージのダウンロードです。初回は少し時間がかかることがあります。

---

## Flutter 基礎
Duration: 0:20:00

### Flutter とは

Google が作っている**マルチプラットフォーム UI フレームワーク**です。

- 1 つのコードで **iOS / Android / Web / デスクトップ**に対応
- 言語は **Dart**
- 描画は Skia / Impeller で自前 (ネイティブ UI 部品は使わない)
- 今日は **Web ターゲット**だけ使います！

### Web 開発との対比

すでに知っている概念と紐付けると速いです。

| Web (HTML/CSS/JS) | Flutter |
|-------------------|---------|
| DOM ツリー | Widget ツリー |
| `<div>` / `<button>` などの要素 | `Container` / `ElevatedButton` 等の Widget |
| CSS のスタイル | Widget のプロパティ (色・余白・角丸など) |
| useState などのフック | StatefulWidget / Riverpod |
| Vite の HMR | ホットリロード |

### すべては Widget

Flutter では**画面のすべてが Widget** です。

- ボタンも文字も余白も Widget
- Widget が**入れ子になって 1 本のツリー**を作る
- ツリーのルートが `MaterialApp`
- 親 Widget が子 Widget を `child` / `children` で持つ

### Stateless と Stateful

**StatelessWidget**

- 状態を持たない
- 渡された値を表示するだけ
- ボタンやラベルなど
- React の純粋なコンポーネント相当

**StatefulWidget**

- 内部で状態を持つ
- 値が変わると**再描画**する
- カウンター / チェックボックスなど
- 今回は **Riverpod に任せる**

### main.dart の最小構造

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(...);
  runApp(const ProviderScope(child: MiniInstagramApp()));
}

class MiniInstagramApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return const MaterialApp(home: FeedPage());
  }
}
```

入り口は `main()` → `runApp()` → ルートの Widget の順です。

### Dart 文法 (JS との差分だけ)

| やりたいこと | JavaScript | Dart |
|-------------|-----------|------|
| 変数 (再代入あり) | `let x = 1;` | `var x = 1;` / `int x = 1;` |
| 変数 (再代入なし) | `const x = 1;` | `final x = 1;` |
| 関数 | `function add(a,b){…}` | `int add(int a, int b) {…}` |
| 文末 | `;` 省略 OK | `;` **必須** |
| null チェック | `x?.y` | `x?.y` (同じ！) |

### ホットリロードを使い倒しましょう

- ファイルを保存するだけで**約 1 秒**で画面が更新される
- 状態を保ったまま更新される (`r` キー)
- 状態をリセットしたいときは**ホットリスタート** (`R` キー)
- `flutter run -d chrome` で起動するとターミナルから操作できます

## Riverpod 基礎
Duration: 0:15:00

### なぜ状態管理が必要？

- StatefulWidget だけだと、状態が**その Widget の中**に閉じる
- 離れた Widget で同じ状態を見たいとき、**親から子へバケツリレー**になる
- Widget が増えると爆発的に書きづらくなる
- → **Riverpod** で「どこからでも触れる場所」に置きます

### Riverpod の三要素

今日覚えるのはこの 3 つだけです。

1. **Notifier**: 状態とロジックの入れ物
2. **NotifierProvider**: 状態を公開する窓口
3. **ref**: Widget から状態を読む手段 (`watch` / `read`)

### ① Notifier — 状態とロジック

```dart
class LikedPostIds extends Notifier<Set<String>> {
  @override
  Set<String> build() => <String>{};   // 初期値: 空のセット

  void setLiked(String postId, {required bool liked}) {
    if (liked) {
      state = <String>{...state, postId};
    } else {
      state = state.where((id) => id != postId).toSet();
    }
  }
}
```

- `Notifier<T>` の `T` が状態の型
- `build()` で初期値を返す
- `state = ...` と書き換えると**自動で再描画**される

### ② Provider — 公開する窓口

今日は **NotifierProvider** と **StreamProvider** を使います。

```dart
// いいね済み ID を管理する
final likedPostIdsProvider =
    NotifierProvider<LikedPostIds, Set<String>>(LikedPostIds.new);

// Firestore の変更をリアルタイムで受け取る
final postsProvider = StreamProvider<List<Post>>((ref) {
  // Firestore のストリームを返す (ハンズオン② で実装！)
  return const Stream<List<Post>>.empty();
});
```

- `StreamProvider` は**非同期のストリーム**を扱うプロバイダ
- `AsyncValue<T>` として Widget 側に届く

### ③ ref.watch と ref.read

| やりたいこと | 使うもの | 例 |
|-------------|---------|-----|
| **画面に表示**する値を取る | `ref.watch(p)` | `final posts = ref.watch(postsProvider);` |
| **ボタンを押して**操作する | `ref.read(p.notifier)` | `ref.read(likedPostIdsProvider.notifier).setLiked(…);` |
| 再描画される？ | watch → ○ / read → ✗ | — |

「**表示は watch、操作は read**」と覚えましょう！

### ConsumerWidget での使い方

```dart
class MyWidget extends ConsumerWidget {
  const MyWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final likedIds = ref.watch(likedPostIdsProvider); // 表示用
    return Text('いいね数: ${likedIds.length}');
  }
}
```

- `StatelessWidget` → `ConsumerWidget` に変えるだけ
- `build` に `WidgetRef ref` が加わる
- `ref.watch()` で値が変わると自動で再描画される

## ハンズオン① FeedPage
Duration: 0:20:00

### Step 1 のゴール

`postsProvider` から投稿リストを受け取り、**縦スクロールのリストとして表示**しましょう！

### 現在のコードを確認する

`lib/feed_page.dart` を開いてみましょう。

```dart
class FeedPage extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // TODO
    ref.watch(postsProvider);

    return const Scaffold(
      body: Center(child: Text('TODO: 投稿一覧を表示する')),
    );
  }
}
```

`postsProvider` を watch しているが、まだ UI に活かせていない状態です。

### `AsyncValue.when()` の使い方

`StreamProvider` が返す `AsyncValue<T>` は 3 状態を持ちます。

```dart
final posts = ref.watch(postsProvider);

return Scaffold(
  body: posts.when(
    data:    (items) => /* データがある場合の Widget */,
    error:   (e, st) => /* エラーが起きた場合の Widget */,
    loading: ()      => const CircularProgressIndicator(),
  ),
);
```

- **data**: Firestore からデータが届いた
- **error**: 読み込みに失敗した
- **loading**: まだデータが届いていない (ぐるぐる表示)

### ListView + ProviderScope のパターン

`data` コールバックの中で `ListView.builder` を返しましょう。

```dart
data: (items) => ListView.builder(
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
```

- `ProviderScope` で投稿データを **1 件ずつ PostCard に注入**する
- `currentPostProvider` は `post_card.dart` に定義済み

### 完成コード

`lib/feed_page.dart` を以下のように書き換えましょう。

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'providers/post_providers.dart';
import 'widgets/post_card.dart';

class FeedPage extends ConsumerWidget {
  const FeedPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final posts = ref.watch(postsProvider);

    return Scaffold(
      body: posts.when(
        data: (items) {
          if (items.isEmpty) {
            return const Center(
              child: Text('投稿がまだありません'),
            );
          }

          return RefreshIndicator(
            onRefresh: () async {
              ref.invalidate(postsProvider);
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
        error: (error, stackTrace) {
          return Center(child: Text('エラー: $error'));
        },
        loading: () {
          return const Center(child: CircularProgressIndicator());
        },
      ),
    );
  }
}
```

ファイルを保存すると、ホットリロードで画面が更新されます。まだ Firestore につながっていないので、ぐるぐる (loading 状態) が表示されるはずです。

## ハンズオン② postsProvider
Duration: 0:20:00

### Step 2 のゴール

`postsProvider` を Firestore に接続して、**リアルタイムで投稿を取得**しましょう！

### 現在のコードを確認する

`lib/providers/post_providers.dart` を開いてみましょう。

```dart
final postsProvider = StreamProvider<List<Post>>((ref) {
  // TODO
  return const Stream<List<Post>>.empty();
});
```

空のストリームを返しているため、Step 1 の `data` コールバックが空リストのままです。

### Post モデルのフィールド

`lib/models/post.dart` で定義されています。

| フィールド | 型 | 内容 |
|-----------|-----|------|
| `id` | `String` | Firestore ドキュメント ID |
| `imageUrl` | `String` | 投稿画像の URL |
| `authorId` | `String` | 投稿者のユーザー名 |
| `authorUrl` | `String` | 投稿者のアイコン URL |
| `text` | `String` | 投稿テキスト |
| `likes` | `int` | いいね数 |
| `createdAt` | `DateTime` | 投稿日時 |

`Post.fromDocument()` で Firestore ドキュメントから自動変換されます。

### Firestore からストリームを取得する

`firestoreProvider` は既に定義済みです。

```dart
final postsProvider = StreamProvider<List<Post>>((ref) {
  final firestore = ref.watch(firestoreProvider);

  return firestore
      .collection('posts')
      .orderBy('createdAt', descending: true)
      .snapshots()
      .map((snapshot) =>
          snapshot.docs.map(Post.fromDocument).toList());
});
```

- `.collection('posts')` で posts コレクションを指定
- `.orderBy('createdAt', descending: true)` で新着順にソート
- `.snapshots()` でリアルタイムストリームに変換
- `.map()` で `List<Post>` に変換

### 完成コード

`lib/providers/post_providers.dart` の `postsProvider` を書き換えましょう。

```dart
final postsProvider = StreamProvider<List<Post>>((ref) {
  final firestore = ref.watch(firestoreProvider);

  return firestore
      .collection('posts')
      .orderBy('createdAt', descending: true)
      .snapshots()
      .map((snapshot) =>
          snapshot.docs.map(Post.fromDocument).toList());
});
```

ファイルを保存するとホットリスタートが走り、Firestore から投稿データが届くはずです。投稿が表示されれば Step 2 完了です！

> **Note:** まだ投稿カードの UI が完成していないので、画面にはまだプレースホルダーが並んで表示されます。

## ハンズオン③ PostCard
Duration: 0:20:00

### Step 3 のゴール

`currentPostProvider` から投稿データを受け取り、**フルスクリーンのカード UI** を作りましょう！

### 現在のコードを確認する

`lib/widgets/post_card.dart` を開いてみましょう。

```dart
class PostCard extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // TODO
    ref.watch(currentPostProvider);

    return const AspectRatio(
      aspectRatio: 9 / 16,
      child: ColoredBox(
        color: Color(0xFF1D1D21),
        child: Center(child: Text('TODO: 投稿カードを作る')),
      ),
    );
  }
}
```

### Stack + Positioned で UI を重ねる

PostCard は複数の要素を**重ねて表示**します。

```dart
Stack(
  fit: StackFit.expand,
  children: [
    // ① 背景画像
    Image.network(post.imageUrl, ...),
    // ② グラデーションオーバーレイ
    const DecoratedBox(decoration: ...),
    // ③ ユーザー情報 (上)
    Positioned(top: 12, left: 12, ...),
    // ④ テキスト (下左)
    Positioned(bottom: 28, left: 16, ...),
    // ⑤ いいねボタン (下右)
    Positioned(right: 8, bottom: 20, ...),
  ],
)
```

- `Stack` で子を重ねる
- `Positioned` で位置を指定
- `AspectRatio(9/16)` で縦長に固定
- `StackFit.expand` で全体に広げる

### いいねボタンの実装

`likedPostIdsProvider` でいいね状態を管理します。

```dart
final post = ref.watch(currentPostProvider);
final likedPostIds = ref.watch(likedPostIdsProvider);
final isLiked = likedPostIds.contains(post.id);

IconButton.filledTonal(
  onPressed: () async {
    await ref
        .read(postActionsProvider)
        .toggleLike(post, isLiked: isLiked);
  },
  icon: Icon(
    isLiked ? Icons.favorite : Icons.favorite_border,
    color: isLiked ? Colors.pinkAccent : Colors.white,
  ),
),
```

表示は `watch`、操作は `read` のパターンです！

### 完成コード

`lib/widgets/post_card.dart` を以下のように書き換えましょう。

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/post.dart';
import '../providers/post_providers.dart';

final currentPostProvider = Provider<Post>((ref) {
  throw UnimplementedError('PostCard requires currentPostProvider override.');
});

class PostCard extends ConsumerWidget {
  const PostCard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final post = ref.watch(currentPostProvider);
    final likedPostIds = ref.watch(likedPostIdsProvider);
    final isLiked = likedPostIds.contains(post.id);

    return AspectRatio(
      aspectRatio: 9 / 16,
      child: Stack(
        fit: StackFit.expand,
        children: [
          // ① 背景画像
          Image.network(
            post.imageUrl,
            fit: BoxFit.cover,
            loadingBuilder: (context, child, loadingProgress) {
              if (loadingProgress == null) return child;
              return const Center(child: CircularProgressIndicator());
            },
            errorBuilder: (context, error, stackTrace) {
              return const ColoredBox(
                color: Color(0xFF1D1D21),
                child: Center(
                  child: Icon(Icons.broken_image_outlined, size: 48),
                ),
              );
            },
          ),
          // ② グラデーションオーバーレイ
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
          // ③ ユーザー情報 (上)
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
                    backgroundColor: Colors.white,
                    child: CircleAvatar(
                      radius: 15,
                      backgroundColor: const Color(0xFF2A2A2E),
                      backgroundImage: post.authorUrl.isEmpty
                          ? null
                          : NetworkImage(post.authorUrl),
                      child: post.authorUrl.isEmpty
                          ? const Icon(Icons.person, color: Colors.white, size: 18)
                          : null,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Text(
                    post.authorId,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w700,
                      shadows: [Shadow(color: Colors.black54, blurRadius: 8)],
                    ),
                  ),
                ],
              ),
            ),
          ),
          // ④ テキスト (下左)
          Positioned(
            left: 16,
            right: 80,
            bottom: 28,
            child: Text(
              post.text,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.w600,
                shadows: const [Shadow(color: Colors.black87, blurRadius: 8)],
              ),
            ),
          ),
          // ⑤ いいねボタン (下右)
          Positioned(
            right: 8,
            bottom: 20,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
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
                ),
                Text(
                  '${post.likes}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.w700,
                    shadows: [Shadow(color: Colors.black54, blurRadius: 8)],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
```

ファイルを保存すると、投稿カードが表示されるようになります。❤️ ボタンを押していいね！してみましょう。

## 共有・まとめ
Duration: 0:10:00

### 発表してみましょう！

時間が残ったら、隣の人や全体に共有してください。

- **どこまで実装できた？** — 完成したステップと現在の画面
- **どこで詰まった？** — 解決方法もセットで共有！
- **改善してみたいこと** — 追加したい機能やデザイン

### 今日のまとめ

- Flutter は **Widget ツリー**で画面を組みます
- Riverpod の **StreamProvider** で非同期データを扱えます
- **AsyncValue.when()** でデータ / エラー / 読み込み状態を切り替えます
- **ProviderScope** で親から子に値を注入できます

詰まったらすぐに **Discord `#260521-flutter-workshop`** で共有してください！

お疲れさまでした！楽しいアプリ作りを！
