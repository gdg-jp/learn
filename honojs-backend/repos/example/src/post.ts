import { desc } from "drizzle-orm";
import { pgTable, serial, text, timestamp, varchar } from "drizzle-orm/pg-core";
import { Hono } from "hono";
import { z } from "zod";
import { db } from "./db.js";
import { type FirebaseVariables, requireFirebaseAuth } from "./firebase.js";

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

export const createPostSchema = z.object({
  content: z
    .string()
    .trim()
    .min(1, "投稿内容を入力してください。")
    .max(280, "投稿は280文字以内です。")
});

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

export const postRoutes = new Hono<{ Variables: FirebaseVariables }>()
  .get("/", async (c) => {
    const rows = await listPosts();
    return c.json({ posts: rows });
  })
  .post("/", requireFirebaseAuth, async (c) => {
    const body = await c.req.json().catch(() => null);
    const parsed = createPostSchema.safeParse(body);

    if (!parsed.success) {
      return c.json(
        { error: parsed.error.issues[0]?.message ?? "Invalid request body." },
        400
      );
    }

    const user = c.get("user");
    const post = await createPost({
      content: parsed.data.content,
      authorUid: user.uid,
      authorName: user.name,
      authorPhotoUrl: user.picture
    });

    return c.json({ post }, 201);
  });
