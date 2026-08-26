"use client";

import { useActionState } from "react";

import { Field, FormError, SubmitButton } from "@/components/form";
import { registerAction, type FormState } from "@/lib/auth-actions";

const initialState: FormState = { error: null };

export function RegisterForm() {
  // useActionState wires the form to a Server Action and hands back whatever it
  // returned — here, an error message to show. The action itself still runs
  // entirely on the server.
  const [state, formAction] = useActionState(registerAction, initialState);

  return (
    <form action={formAction} className="flex flex-col gap-5">
      <FormError message={state.error} />

      <Field
        label="Email"
        name="email"
        type="email"
        autoComplete="email"
        hint="We send the confirmation link here."
      />
      <Field
        label="Username"
        name="username"
        autoComplete="username"
        minLength={3}
        hint="3–32 characters. This is what other drivers see."
      />
      <Field
        label="Password"
        name="password"
        type="password"
        autoComplete="new-password"
        minLength={8}
        hint="At least 8 characters."
      />

      <div className="mt-1">
        <SubmitButton>Create account</SubmitButton>
      </div>
    </form>
  );
}
