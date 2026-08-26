"use client";

import { useActionState } from "react";

import { Field, FormError, SubmitButton } from "@/components/form";
import { resetPasswordAction, type FormState } from "@/lib/auth-actions";

const initialState: FormState = { error: null };

export function ResetPasswordForm({ token }: { token: string }) {
  const [state, formAction] = useActionState(resetPasswordAction, initialState);

  return (
    <form action={formAction} className="flex flex-col gap-5">
      <FormError message={state.error} />

      {/* The token travels from the URL into the submission. It is not secret
          from the person holding the link — they just followed it — but it does
          have to arrive alongside the new password. */}
      <input type="hidden" name="token" value={token} />

      <Field
        label="New password"
        name="password"
        type="password"
        autoComplete="new-password"
        minLength={8}
        hint="At least 8 characters."
      />
      <Field
        label="Confirm new password"
        name="password_confirmation"
        type="password"
        autoComplete="new-password"
        minLength={8}
      />

      <div className="mt-1">
        <SubmitButton>Set new password</SubmitButton>
      </div>
    </form>
  );
}
