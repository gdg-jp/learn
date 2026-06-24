import { cert, getApps, initializeApp } from "firebase-admin/app";
import { getAuth } from "firebase-admin/auth";
import type { MiddlewareHandler } from "hono";
import { createMiddleware } from "hono/factory";
import { env } from "./env.js";

export interface AuthUser {
  uid: string;
  name: string;
  picture?: string;
}

export interface FirebaseVariables {
  user: AuthUser;
}

const getFirebaseApp = () => {
  if (getApps().length > 0) {
    return getApps()[0];
  }

  if (!env.hasFirebaseServiceAccount) {
    throw new Error(
      `Firebase Admin SDK credentials were not found. Place serviceAccount.json at ${env.firebaseServiceAccountPath} or set FIREBASE_SERVICE_ACCOUNT_PATH.`
    );
  }

  return initializeApp({
    credential: cert(env.firebaseServiceAccountPath)
  });
};

export const verifyIdToken = async (idToken: string): Promise<AuthUser> => {
  const decoded = await getAuth(getFirebaseApp()).verifyIdToken(idToken);

  return {
    uid: decoded.uid,
    name:
      typeof decoded.name === "string" && decoded.name.length > 0
        ? decoded.name
        : "匿名ユーザー",
    picture: typeof decoded.picture === "string" ? decoded.picture : undefined
  };
};

export const requireFirebaseAuth: MiddlewareHandler<{
  Variables: FirebaseVariables;
}> = createMiddleware(async (c, next) => {
  const authorization = c.req.header("authorization");
  const match = authorization?.match(/^Bearer\s+(.+)$/i);

  if (!match) {
    return c.json({ error: "Bearer token is required." }, 401);
  }

  try {
    const user = await verifyIdToken(match[1]);
    c.set("user", user);
    await next();
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "Firebase authentication failed.";
    return c.json({ error: message }, 401);
  }
});
