"use server";

import { redirect } from "next/navigation";

import { api, type User } from "@/lib/api";
import { clearSession, createSession, getSessionToken } from "@/lib/session";

/**
 * Server Actions for signing up, in and out. "use server" keeps the API address,
 * the cookie handling and the token off the browser entirely.
 */
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

  // redirect() throws to unwind the request, so it must sit outside any try/catch.
  redirect(`/register/check-email?email=${encodeURIComponent(email)}`);
}

export async function loginAction(_previous: FormState, formData: FormData): Promise<FormState> {
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");

  if (!email || !password) {
    return { error: "Please enter your email and password." };
  }

  // The OAuth2 password flow expects form fields named username and password; the
  // email goes in "username" because that is what we sign in with.
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
    // Blacklist it server-side so a copy cannot be replayed. If this fails the
    // cookie still goes - staying signed in because cleanup failed is worse.
    await api("/api/v1/auth/logout", { method: "POST", token });
  }

  await clearSession();
  redirect("/");
}

/** Three states, because `error: null` cannot tell "fine" from "not asked yet". */
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

  // One answer for every address, matching what the API is careful to withhold.
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

  // One answer for every address, so this cannot reveal who has an account.
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
  // The API never sees the second field; it only catches a typo before commit.
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

  // The API invalidates every token predating the change, so this cookie is already
  // dead; leaving it would show a signed-in header while every request failed.
  await clearSession();
  redirect("/login?reset=1");
}
