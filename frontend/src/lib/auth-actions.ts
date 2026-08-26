"use server";

import { redirect } from "next/navigation";

import { api, type User } from "@/lib/api";
import { clearSession, createSession, getSessionToken } from "@/lib/session";

/**
 * Server Actions for signing up, in and out.
 *
 * "use server" means none of this is ever sent to the browser. The API address,
 * the cookie handling and the token stay on the server; the browser only posts a
 * form and receives the result.
 */

/** What a form returns to the page so it can show an error. */
export type FormState = { error: string | null };

export async function registerAction(
  _previous: FormState,
  formData: FormData,
): Promise<FormState> {
  const email = String(formData.get("email") ?? "").trim();
  const username = String(formData.get("username") ?? "").trim();
  const password = String(formData.get("password") ?? "");

  if (!email || !username || !password) {
    return { error: "Please fill in every field." };
  }

  const result = await api<User>("/api/v1/auth/signup", {
    method: "POST",
    json: { email, username, password },
  });

  if (!result.ok) {
    return { error: result.error.detail };
  }

  // Redirect throws internally to unwind the request, so it must sit outside any
  // try/catch and after every check that could fail.
  redirect(`/register/check-email?email=${encodeURIComponent(email)}`);
}

export async function loginAction(_previous: FormState, formData: FormData): Promise<FormState> {
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");

  if (!email || !password) {
    return { error: "Please enter your email and password." };
  }

  // The OAuth2 password flow expects form-encoded fields named username and
  // password. We put the email in "username" because that is what we sign in with.
  const result = await api<{ access_token: string }>("/api/v1/auth/login", {
    method: "POST",
    form: { username: email, password },
  });

  if (!result.ok) {
    return { error: result.error.detail };
  }

  await createSession(result.data.access_token);
  redirect("/profile");
}

export async function logoutAction(): Promise<never> {
  const token = await getSessionToken();

  if (token) {
    // Tell the API to blacklist this token, so a copy of it cannot be replayed.
    // If that call fails the cookie still goes: leaving the visitor signed in
    // because cleanup failed would be the worse outcome.
    await api("/api/v1/auth/logout", { method: "POST", token });
  }

  await clearSession();
  redirect("/");
}

/**
 * Some forms need three states, not two: nothing submitted yet, done, and
 * failed. A plain `error: null` cannot tell "no problem" apart from "not asked
 * yet", which would show a success message before the user had done anything.
 */
export type ResendState = { status: "idle" | "sent"; error: string | null };

export async function resendVerificationAction(
  _previous: ResendState,
  formData: FormData,
): Promise<ResendState> {
  const email = String(formData.get("email") ?? "").trim();
  if (!email) {
    return { status: "idle", error: "Please enter your email address." };
  }

  await api(`/api/v1/auth/resend-verification?email=${encodeURIComponent(email)}`, {
    method: "POST",
  });

  // Always reports the same thing. The API deliberately answers identically for
  // addresses that exist and ones that don't, and repeating that here keeps the
  // frontend from leaking what the API is careful not to.
  return { status: "sent", error: null };
}

export async function forgotPasswordAction(
  _previous: ResendState,
  formData: FormData,
): Promise<ResendState> {
  const email = String(formData.get("email") ?? "").trim();
  if (!email) {
    return { status: "idle", error: "Please enter your email address." };
  }

  await api("/api/v1/auth/forgot-password", { method: "POST", json: { email } });

  // Same reasoning as resend: one answer for every address, so this cannot be
  // used to find out who has an account.
  return { status: "sent", error: null };
}

export async function resetPasswordAction(
  _previous: FormState,
  formData: FormData,
): Promise<FormState> {
  const token = String(formData.get("token") ?? "");
  const password = String(formData.get("password") ?? "");
  const confirmation = String(formData.get("password_confirmation") ?? "");

  if (!token) {
    return { error: "This reset link is missing its code. Please request a new one." };
  }
  if (!password) {
    return { error: "Please choose a new password." };
  }
  // Checked here rather than by the API, which never sees the second field —
  // it exists purely to catch a typo before the password is committed.
  if (password !== confirmation) {
    return { error: "Those two passwords don't match." };
  }

  const result = await api("/api/v1/auth/reset-password", {
    method: "POST",
    json: { token, new_password: password },
  });

  if (!result.ok) {
    return { error: result.error.detail };
  }

  // Changing the password invalidates every token issued before it, including
  // one this browser may still be holding. Dropping the cookie keeps the UI
  // honest — otherwise the header would claim the visitor is signed in while
  // every request quietly failed.
  await clearSession();
  redirect("/login?reset=1");
}
