"use client";

import { useActionState } from "react";

import Link from "next/link";

import { Field, FormError, SubmitButton } from "@/components/form";
import { loginAction, type FormState } from "@/lib/auth-actions";

const initialState: FormState = { error: null };

export function LoginForm() {
  const [state, formAction] = useActionState(loginAction, initialState);

  return (
    <form action={formAction} className="flex flex-col gap-5">
      <FormError message={state.error} />

      <Field label="Email" name="email" type="email" autoComplete="email" />
      <Field label="Password" name="password" type="password" autoComplete="current-password" />

      <div className="mt-1 flex flex-wrap items-center gap-5">
        <SubmitButton>Sign in</SubmitButton>
        <Link
          href="/forgot-password"
          className="text-[14px] text-ink-3 transition-colors hover:text-ink-2"
        >
          Forgot your password?
        </Link>
      </div>
    </form>
  );
}
