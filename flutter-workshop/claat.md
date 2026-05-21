summary: Flutter でミニ SNS アプリを作ろう！120 分ハンズオン
id: flutter-workshop
categories: Flutter, Dart, Web
environments: Web
status: Draft
author: GDG on Campus University of Osaka

# Flutter でミニ SNS アプリを作ろう

## はじめに
Duration: 0:05:00

このコードラボでは、Flutter と Riverpod を使って、Firestore から投稿をリアルタイム取得するミニ SNS フィードを作ります。スターターコードから始めて、3 つの Dart ファイルを編集しながら完成版に近づけます。

![完成イメージ](img/mini-sns-final.png)

### このコードラボで作るもの

縦スクロールで投稿を眺める Web 対応の Flutter アプリを作ります。

* Firestore の `posts` コレクションから投稿を新着順に表示する
* 投稿ごとに画像、ユーザー名、本文、いいね数を表示する
* いいねボタンを押すと画面の状態と Firestore の値を更新する
* Pull to Refresh で投稿リストを再取得する

完成版のコードは `flutter-workshop/example/`、スターターコードは `flutter-workshop/template/` にあります。

> **Tip:** まずは手順どおりに `template/` を編集し、詰まったときだけ `example/` と見比べてください。

### このコードラボで学ぶこと

* Flutter の Widget ツリーで画面を構築する方法
* `ConsumerWidget` と `WidgetRef` で Riverpod の値を読む方法
* `StreamProvider` で Firestore のリアルタイム更新を扱う方法
* `AsyncValue.when()` で loading / error / data を出し分ける方法
* `ProviderScope` の override でリストの 1 件分のデータを子 Widget に渡す方法
* `Stack` と `Positioned` で画像の上に UI を重ねる方法

### 必要なもの

* Windows または macOS の PC
* Google Chrome
* Visual Studio Code
* VS Code の Flutter 拡張機能
* Flutter SDK
* Git

このコードラボでは Flutter Web を Chrome で動かします。Android Studio、Android SDK、Xcode、iOS シミュレータ、Android エミュレータは使いません。

### 前提知識

* JavaScript、TypeScript、Java、Kotlin、Swift、C# など、いずれかのプログラミング言語の基本的な理解
* 関数、クラス、配列、非同期処理という言葉を見たことがある程度の理解

### このコードラボで扱わないこと

* Firebase プロジェクトの作成と初期設定
* 認証、投稿作成、投稿削除
* iOS / Android のネイティブビルド
* Riverpod のコード生成、テスト、アーキテクチャ設計

### 参考にした公開資料

構成は Google Codelabs の進め方に合わせています。たとえば、完成像を先に示す、スターターコードから始める、各ステップで目に見える成果を作る、という流れです。

* [Your first Flutter app](https://codelabs.developers.google.com/codelabs/flutter-codelab-first)
* [Take your Flutter app from boring to beautiful](https://codelabs.developers.google.com/codelabs/flutter-boring-to-beautiful)
* [Get to know Firebase for Flutter](https://firebase.google.com/codelabs/firebase-get-to-know-flutter)
* [Flutter learning pathway](https://docs.flutter.dev/learn/pathway)
* [Install Flutter](https://docs.flutter.dev/install)
* [Approaches to state management](https://docs.flutter.dev/data-and-backend/state-mgmt/options)
* [Riverpod Providers](https://riverpod.dev/docs/concepts2/providers)

> **Note:** Flutter 公式ドキュメントは、特記がない限り Flutter 3.44.0 を反映し、ページ最終更新日は 2026-05-05 です。このコードラボは 2026-05-21 時点で確認した情報に基づいています。

## セットアップ
Duration: 0:20:00

このステップでは、Flutter Web を Chrome で起動できる状態を作ります。すでにインストール済みのツールは、確認コマンドだけ実行してください。

### Git をインストールする

Windows の場合は [Git for Windows](https://git-scm.com/download/win) をインストールします。`winget` を使う場合は PowerShell で次を実行します。

```powershell
winget install --id Git.Git -e --source winget
```

macOS の場合は、ターミナルで Xcode Command Line Tools をインストールします。

```bash
xcode-select --install
```

インストールできたか確認します。

```bash
git --version
```

**期待される出力:**

```text
git version 2.x.x
```

バージョン番号が表示されれば成功です。

### Chrome と VS Code をインストールする

[Google Chrome](https://www.google.com/chrome/) と [Visual Studio Code](https://code.visualstudio.com/) をインストールします。

macOS でターミナルから `code .` を使いたい場合は、VS Code を開いて `Cmd + Shift + P` を押し、`Shell Command: Install 'code' command in PATH` を実行します。

### Flutter SDK をインストールする

Flutter 公式のインストールページでは、VS Code などの Code OSS ベースのエディタからセットアップする Quick start が推奨されています。このコードラボでも VS Code の Flutter 拡張機能から SDK を入れます。

1. VS Code を開きます。
2. 左サイドバーの拡張機能を開きます。
3. `Flutter` を検索し、**Flutter** 拡張機能をインストールします。
4. `Ctrl + Shift + P` または `Cmd + Shift + P` で Command Palette を開きます。
5. `Flutter: New Project` を選択します。
6. Flutter SDK が見つからない場合は **Download SDK** を選択します。
7. SDK の保存先を選びます。

Windows の保存先例:

```text
C:\src
```

macOS の保存先例:

```text
~/development
```

> **Warning:** Windows では `Program Files` のようにスペースを含むパスを避けてください。SDK や一部のツールでパス解決の問題が起きることがあります。

インストール後、VS Code とターミナルを開き直します。

### Flutter を確認する

PowerShell、コマンドプロンプト、またはターミナルで次を実行します。

```bash
flutter --version
flutter doctor -v
```

**期待される出力:**

```text
Flutter 3.x.x • channel stable • ...
...
[✓] Chrome - develop for the web
```

このコードラボでは Chrome で動かすため、`Chrome - develop for the web` にチェックが付いていれば進められます。Android toolchain、Xcode、Android Studio にエラーが出ても、このハンズオンでは無視して構いません。

> **Troubleshooting:** `flutter` コマンドが見つからない場合は、VS Code とターミナルをすべて閉じて開き直してください。それでも解決しない場合は、Flutter SDK の `bin` フォルダが PATH に追加されているか確認します。

### スターターコードを起動する

任意の作業フォルダでリポジトリをクローンします。

```bash
git clone https://github.com/gdsc-osaka/flutter-workshop.git
cd flutter-workshop
flutter pub get
flutter run -d chrome
```

**期待される出力:**

```text
Launching lib/main.dart on Chrome in debug mode...
...
Flutter run key commands.
```

Chrome が開いて `TODO: 投稿一覧を表示する` と表示されたら準備完了です。

最後に VS Code でプロジェクトを開きます。

```bash
code .
```

## Flutter の画面構造をつかむ
Duration: 0:15:00

このステップでは、実装で使う Flutter / Dart の考え方だけを確認します。詳しい文法を全部覚える必要はありません。

### Flutter は Widget で画面を作る

Flutter は Google が開発しているマルチプラットフォーム UI フレームワークです。Flutter 公式の learning pathway でも、Dart と Flutter の基礎、Widget、状態管理、レイアウトを順に学ぶ構成になっています。

Flutter では、画面の部品を Widget と呼びます。

* 文字は `Text`
* 画像は `Image`
* 縦並びは `Column`
* スクロールリストは `ListView`
* 画面の土台は `Scaffold`

![Widget ツリー](img/widget-tree.png)

Widget は入れ子になって 1 本のツリーを作ります。親 Widget が `child` または `children` で子 Widget を持ちます。

### Web 開発の知識と対応させる

すでに Web 開発を知っている場合は、次の対応で考えると理解しやすくなります。

| Web | Flutter |
|-----|---------|
| DOM ツリー | Widget ツリー |
| `<div>` / `<button>` | `Container` / `ElevatedButton` |
| CSS の色、余白、角丸 | Widget のプロパティ |
| React の component | Widget |
| React の state / hooks | `StatefulWidget` / Riverpod |
| Vite の HMR | Hot reload |

Flutter のコードでは末尾のカンマをよく使います。Dart formatter が読みやすい形に整えてくれるため、複数行の Widget ではカンマを付けておくと便利です。

### アプリの入口を確認する

`lib/main.dart` と `lib/app.dart` はすでに用意されています。今回は編集しません。

`lib/main.dart` は次の流れでアプリを起動しています。

```dart
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  runApp(const ProviderScope(child: MiniInstagramApp()));
}
```

`Firebase.initializeApp()` で Firebase を初期化し、`ProviderScope` で Riverpod をアプリ全体から使えるようにしています。

### Hot reload で確認する

`flutter run -d chrome` で起動している間は、ファイル保存後にターミナルで `r` を押すと Hot reload、`R` を押すと Hot restart できます。

```text
r  Hot reload
R  Hot restart
q  Quit
```

表示だけを変えたときは Hot reload、Firebase 初期化や Provider の作りを変えたときは Hot restart を使います。

> **Note:** Flutter Web では開発環境や変更内容によって Hot reload の効き方に差があります。画面が更新されない場合は `R` で Hot restart してください。

## Riverpod のデータフローをつかむ
Duration: 0:15:00

このステップでは、今回使う Riverpod の部品を確認します。覚えるのは `ProviderScope`、`Provider`、`StreamProvider`、`NotifierProvider`、`ref.watch`、`ref.read` だけです。

### Riverpod を使う理由

`StatefulWidget` だけで状態を持つと、その状態は基本的に Widget の内側に閉じます。離れた Widget で同じ状態を使いたい場合、親から子へ値を渡し続ける必要があります。

![状態管理の課題](img/state-problem.png)

Riverpod では、状態やデータ取得処理を Widget の外に置きます。Widget は必要な Provider を `ref.watch()` で読み、値が変わると自動で再描画されます。

### 今回の Provider を確認する

今回のデータフローは次の形です。

```text
FeedPage
  ref.watch(postsProvider)
    ↓
postsProvider
  Firestore の posts コレクションを購読
    ↓
PostCard
  currentPostProvider で 1 件分の投稿を受け取る
  likedPostIdsProvider でいいね状態を読む
  postActionsProvider で Firestore を更新する
```

![Riverpod の流れ](img/riverpod-flow.png)

`lib/providers/post_providers.dart` には、すでに次の Provider が用意されています。

```dart
final firestoreProvider = Provider<FirebaseFirestore>((ref) {
  return FirebaseFirestore.instance;
});

final postsProvider = StreamProvider<List<Post>>((ref) {
  // TODO
  return const Stream<List<Post>>.empty();
});

final likedPostIdsProvider = NotifierProvider<LikedPostIds, Set<String>>(
  LikedPostIds.new,
);
```

`postsProvider` はこのあと Firestore の stream に置き換えます。`likedPostIdsProvider` は、いいね済み投稿 ID の集合を管理します。

### ref.watch と ref.read を使い分ける

Widget から Provider を使うときは、表示用と操作用で読み方を分けます。

| やりたいこと | 使う API | 例 |
|--------------|----------|----|
| 画面に表示する値を読む | `ref.watch(provider)` | `final posts = ref.watch(postsProvider);` |
| ボタン押下で処理を呼ぶ | `ref.read(provider)` | `ref.read(postActionsProvider).toggleLike(...);` |

表示は `watch`、操作は `read` と覚えてください。

### AsyncValue を扱う

`StreamProvider<List<Post>>` を `watch` すると、Widget 側には `AsyncValue<List<Post>>` が届きます。`AsyncValue.when()` を使うと、読み込み中、エラー、データありの UI を分けられます。

```dart
final posts = ref.watch(postsProvider);

return posts.when(
  loading: () => const CircularProgressIndicator(),
  error: (error, stackTrace) => Text('エラー: $error'),
  data: (items) => Text('投稿数: ${items.length}'),
);
```

この形を次のステップで `FeedPage` に組み込みます。

## 投稿一覧を表示する
Duration: 0:20:00

このステップでは、`postsProvider` から投稿リストを受け取り、縦スクロールのリストとして表示します。

### 現在の FeedPage を確認する

`lib/feed_page.dart` を開きます。

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

`postsProvider` を `watch` していますが、まだ画面には使っていません。

### 投稿リストを PostCard に渡す

`ListView.builder` で投稿の数だけ `PostCard` を作ります。1 件分の投稿は `ProviderScope` の `overrides` で `currentPostProvider` に渡します。

```dart
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) {
    return ProviderScope(
      overrides: [
        currentPostProvider.overrideWithValue(items[index]),
      ],
      child: const PostCard(),
    );
  },
)
```

この書き方にすると、`PostCard` は引数を増やさずに `currentPostProvider` から投稿データを読めます。

### FeedPage を実装する

`lib/feed_page.dart` を以下の内容で上書きします。

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
            return const _EmptyFeed();
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
          return _ErrorView(message: error.toString());
        },
        loading: () {
          return const Center(child: CircularProgressIndicator());
        },
      ),
    );
  }
}

class _EmptyFeed extends StatelessWidget {
  const _EmptyFeed();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Padding(
        padding: EdgeInsets.all(24),
        child: Text(
          '投稿がまだありません。Firestore に posts データを追加してください。',
          textAlign: TextAlign.center,
        ),
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.cloud_off_outlined,
              size: 40,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: 12),
            const Text(
              'Firestore から投稿を読み込めませんでした。',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              message,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}
```

このコードは `AsyncValue.when()` で 3 つの状態を分けています。`data` では投稿が空のときの表示、投稿があるときの `ListView`、Pull to Refresh の処理をまとめています。

### 画面を確認する

ファイルを保存し、必要に応じてターミナルで `R` を押します。

**期待される表示:**

* Firestore にまだ接続していない場合は、読み込み中のぐるぐるが表示される
* もし空配列が届いた場合は、`投稿がまだありません。Firestore に posts データを追加してください。` と表示される
* エラーが起きた場合は、エラーメッセージが表示される

次のステップで `postsProvider` を Firestore に接続します。

## Firestore から投稿を取得する
Duration: 0:20:00

このステップでは、`postsProvider` を Firestore に接続します。Firestore の `posts` コレクションを購読し、変更があれば画面へリアルタイムに反映します。

### 現在の postsProvider を確認する

`lib/providers/post_providers.dart` を開きます。

```dart
final postsProvider = StreamProvider<List<Post>>((ref) {
  // TODO
  return const Stream<List<Post>>.empty();
});
```

今は空の stream を返しているため、投稿データは届きません。

### Post モデルを確認する

`lib/models/post.dart` には、Firestore のドキュメントをアプリ用の `Post` に変換する処理が用意されています。

| フィールド | 型 | 内容 |
|------------|----|------|
| `id` | `String` | Firestore ドキュメント ID |
| `imageUrl` | `String` | 投稿画像の URL |
| `authorUrl` | `String` | 投稿者アイコンの URL |
| `authorId` | `String` | 投稿者のユーザー名 |
| `text` | `String` | 投稿本文 |
| `likes` | `int` | いいね数 |
| `createdAt` | `DateTime` | 投稿日時 |

`Post.fromDocument()` を使うと、Firestore の `DocumentSnapshot` を `Post` に変換できます。

### Firestore の stream を作る

Firestore から投稿を取得する処理は次の形です。

```dart
final firestore = ref.watch(firestoreProvider);

return firestore
    .collection('posts')
    .orderBy('createdAt', descending: true)
    .snapshots()
    .map((snapshot) {
      return snapshot.docs.map(Post.fromDocument).toList();
    });
```

`collection('posts')` でコレクションを選び、`orderBy('createdAt', descending: true)` で新着順に並べます。`snapshots()` は Firestore の変更を stream として返します。

### postsProvider を実装する

`lib/providers/post_providers.dart` の `postsProvider` だけを以下に置き換えます。

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

この Provider は `List<Post>` の stream を返します。Firestore のデータが増えたり、いいね数が変わったりすると、`FeedPage` が再描画されます。

### 投稿データを確認する

ファイルを保存し、ターミナルで `R` を押して Hot restart します。

**期待される表示:**

* Firestore に `posts` データがある場合は、縦長のプレースホルダーが投稿数分表示される
* `PostCard` はまだ未実装なので、各カードには `TODO: 投稿カードを作る` と表示される

> **Troubleshooting:** Firestore の権限エラーが表示される場合は、配布された Firebase 設定と Firestore ルールがハンズオン用のものになっているか確認してください。このコードラボでは Firebase プロジェクトの作成やルール変更は扱いません。

## 投稿カードを作る
Duration: 0:20:00

このステップでは、`PostCard` を完成させます。投稿画像を背景に表示し、その上にユーザー情報、本文、いいねボタンを重ねます。

### 現在の PostCard を確認する

`lib/widgets/post_card.dart` を開きます。

```dart
class PostCard extends ConsumerWidget {
  const PostCard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // TODO
    ref.watch(currentPostProvider);

    return const AspectRatio(
      aspectRatio: 9 / 16,
      child: ColoredBox(
        color: Color(0xFF1D1D21),
        child: Center(
          child: Text('TODO: 投稿カードを作る'),
        ),
      ),
    );
  }
}
```

`currentPostProvider` を `watch` していますが、まだ投稿データを表示していません。

### Stack で UI を重ねる

カードは `Stack` で作ります。背景画像を一番下に置き、その上にグラデーション、本文、いいねボタン、ユーザー情報を重ねます。

```dart
Stack(
  fit: StackFit.expand,
  children: [
    Image.network(post.imageUrl, fit: BoxFit.cover),
    const DecoratedBox(decoration: BoxDecoration(...)),
    Positioned(...),
  ],
)
```

`AspectRatio(aspectRatio: 9 / 16)` で縦長の投稿カードにします。

### いいね状態を読む

いいね済みかどうかは `likedPostIdsProvider` から読みます。

```dart
final post = ref.watch(currentPostProvider);
final likedPostIds = ref.watch(likedPostIdsProvider);
final isLiked = likedPostIds.contains(post.id);
```

ボタンを押したときは `postActionsProvider` を `read` して、Firestore の `likes` を更新します。

```dart
await ref
    .read(postActionsProvider)
    .toggleLike(post, isLiked: isLiked);
```

ここでも表示は `watch`、操作は `read` です。

### PostCard を実装する

`lib/widgets/post_card.dart` を以下の内容で上書きします。

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
          Image.network(
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
                child: Center(
                  child: Icon(Icons.broken_image_outlined, size: 48),
                ),
              );
            },
          ),
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
                          ? const Icon(
                              Icons.person,
                              color: Colors.white,
                              size: 18,
                            )
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
        ],
      ),
    );
  }
}
```

このコードは `Image.network` で投稿画像を表示し、画像読み込み中と失敗時の表示も用意しています。`IconButton.filledTonal` の `onPressed` では、いいね状態を反転し、Firestore の `likes` を増減します。

### いいねを確認する

ファイルを保存し、必要に応じて `R` を押して Hot restart します。

**期待される表示:**

* 投稿画像、ユーザー名、本文、いいね数が表示される
* いいねボタンを押すとハートの見た目が変わる
* Firestore の `likes` が更新され、しばらくすると画面にも反映される

> **Troubleshooting:** 画像が表示されない場合は、Firestore の `imageUrl` が空でないか、ブラウザから直接開ける URL かを確認してください。

## 仕上げと確認
Duration: 0:05:00

最後に、アプリ全体の動作を確認します。

### 実行状態を確認する

ターミナルで起動していない場合は、プロジェクトのルートで次を実行します。

```bash
flutter run -d chrome
```

**期待される表示:**

```text
Launching lib/main.dart on Chrome in debug mode...
Flutter run key commands.
```

Chrome で次の動作を確認します。

* 投稿が新着順に縦スクロールで表示される
* Pull to Refresh してもエラーにならない
* いいねボタンを押すとハート表示が切り替わる
* 画像 URL が壊れている投稿では、壊れた画像アイコンが表示される

### 余裕があれば改善する

時間が残ったら、次のどれかに挑戦してください。

* 投稿本文の文字サイズや影を調整する
* いいねボタンの位置や色を変える
* `createdAt` を使って投稿時間を表示する
* 空状態の画面をより親切にする

### まとめ

このコードラボでは、Flutter Web でミニ SNS フィードを作りました。

* Flutter は Widget ツリーで画面を構築する
* Riverpod は Widget の外に状態やデータ取得処理を置ける
* `StreamProvider` は Firestore のリアルタイム更新と相性が良い
* `AsyncValue.when()` を使うと loading / error / data の UI を整理できる
* `Stack` と `Positioned` で画像の上に UI を重ねられる

詰まったところ、改善したところ、気づいたことを Discord `#260521-flutter-workshop` に共有してください。

お疲れさまでした。
