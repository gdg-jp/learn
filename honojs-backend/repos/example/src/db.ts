import { drizzle } from "drizzle-orm/node-postgres";
import pg from "pg";
import { env } from "./env.js";

const pool = new pg.Pool({
  connectionString: env.DATABASE_URL
});

export const db = drizzle(pool);

export const closeDb = () => pool.end();
