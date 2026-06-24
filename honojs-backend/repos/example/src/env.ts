import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { z } from "zod";

const envSchema = z.object({
  DATABASE_URL: z
    .string()
    .url()
    .default("postgres://hono:hono@localhost:5432/hono_board"),
  PORT: z.coerce.number().int().positive().default(3000),
  FIREBASE_SERVICE_ACCOUNT_PATH: z
    .string()
    .min(1)
    .default("serviceAccount.json")
});

const parsedEnv = envSchema.parse(process.env);

export const env = {
  ...parsedEnv,
  firebaseServiceAccountPath: resolve(
    process.cwd(),
    parsedEnv.FIREBASE_SERVICE_ACCOUNT_PATH
  ),
  hasFirebaseServiceAccount: existsSync(
    resolve(process.cwd(), parsedEnv.FIREBASE_SERVICE_ACCOUNT_PATH)
  )
};
