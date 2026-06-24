import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { serve } from "@hono/node-server";
import { serveStatic } from "@hono/node-server/serve-static";
import { Hono } from "hono";
import { logger } from "hono/logger";
import { env } from "./env.js";
import { postRoutes } from "./post.js";

const publicDir = join(process.cwd(), "dist", "public");
const indexHtml = join(publicDir, "index.html");

export const app = new Hono();

app.use(logger());

app.get("/api/health", (c) =>
  c.json({
    ok: true,
    firebaseServiceAccount: env.hasFirebaseServiceAccount ? "found" : "missing"
  })
);

app.route("/api/posts", postRoutes);

app.use(
  "/*",
  serveStatic({
    root: "./dist/public"
  })
);

app.get("*", async (c) => {
  if (!existsSync(indexHtml)) {
    return c.text(
      "React SPA is not built yet. Run `npm run build` first.",
      404
    );
  }

  return c.html(await readFile(indexHtml, "utf8"));
});

serve(
  {
    fetch: app.fetch,
    port: env.PORT
  },
  (info) => {
    console.log(`Server is running on http://localhost:${info.port}`);
  }
);
