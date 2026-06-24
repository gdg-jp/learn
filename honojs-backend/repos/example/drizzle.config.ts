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
