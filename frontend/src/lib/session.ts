import "server-only";

import { cookies } from "next/headers";

import { api, type User } from "@/lib/api";

/**
 * The signed-in session.
 *
 * The access token lives in an httpOnly cookie, which means browser JavaScript
 * cannot read it at all — `document.cookie` simply does not show it. Even a
 * cross-site scripting bug on this site could not steal a token it has no way to
 * see. The alternative, localStorage, is readable by any script on the page.
 *
 * The browser holds the cookie and sends it back automatically; only this
 * server-side code ever unwraps it and forwards it to the API.
 */

const COOKIE_NAME = "gz_session";

/** Matches the backend's ACCESS_TOKEN_EXPIRE_MINUTES, so the two expire together. */
const MAX_AGE_SECONDS = 30 * 60;

export async function createSession(token: string): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.set(COOKIE_NAME, token, {
    httpOnly: true, // invisible to JavaScript
    sameSite: "lax", // not sent on cross-site POSTs, which blocks basic CSRF
    secure: process.env.NODE_ENV === "production", // HTTPS only once deployed
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
 * This asks the API every time rather than trusting the cookie on its own. The
 * token is a snapshot up to thirty minutes old: the account may since have been
 * deactivated, verified, or signed out on another device, and only the API
 * knows. A stale cookie is dropped so the visitor is simply treated as signed
 * out rather than being shown an error.
 */
export async function getCurrentUser(): Promise<User | null> {
  const token = await getSessionToken();
  if (!token) return null;

  const result = await api<User>("/api/v1/auth/me", { token });
  if (!result.ok) return null;

  return result.data;
}
