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
