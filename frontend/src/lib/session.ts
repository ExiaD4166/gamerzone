import "server-only";

import { cookies } from "next/headers";

import { api, type User } from "@/lib/api";

/**
 * The signed-in session.
 *
 * The token lives in an httpOnly cookie, so browser JavaScript cannot read it —
 * an XSS bug on this site would have nothing to steal. localStorage would hand it
 * over in one line. Only this server-side code unwraps it and forwards it.
 */

const COOKIE_NAME = "gz_session";

/** Matches the backend's ACCESS_TOKEN_EXPIRE_MINUTES, so the two expire together. */
const MAX_AGE_SECONDS = 30 * 60;

export async function createSession(token: string): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.set(COOKIE_NAME, token, {
    httpOnly: true,
    sameSite: "lax", // not sent on cross-site POSTs, which blocks basic CSRF
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: MAX_AGE_SECONDS,
  });
}

export async function getSessionToken(): Promise<string | undefined> {
  const cookieStore = await cookies();
  return cookieStore.get(COOKIE_NAME)?.value;
}

export async function clearSession(): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.delete(COOKIE_NAME);
}

/**
 * The signed-in user, or null.
 *
 * Asks the API every time rather than trusting the cookie: the token is a snapshot
 * up to thirty minutes old, and the account may since have been deactivated,
 * verified, or signed out elsewhere. A stale cookie just reads as signed out.
 */
export async function getCurrentUser(): Promise<User | null> {
  const token = await getSessionToken();
  if (!token) return null;

  const result = await api<User>("/api/v1/auth/me", { token });
  if (!result.ok) return null;

  return result.data;
}
