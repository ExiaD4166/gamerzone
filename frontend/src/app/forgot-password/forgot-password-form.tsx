"use client";

import { useActionState } from "react";

import { Field, FormError, SubmitButton } from "@/components/form";
import { forgotPasswordAction, type ResendState } from "@/lib/auth-actions";

const initialState: ResendState = { status: "idle", error: null };

export function ForgotPasswordForm() {
  const [state, formAction, isPending] = useActionState(forgotPasswordAction, initialState);

  if (state.status === "sent" && !isPending) {
    return (
      // Deliberately vague: the API answers the same way whether or not that
      // address has an account, and saying "we found you" here would undo that.
      <p
        role="status"
        className="rounded-xl border border-line bg-surface px-5 py-6 text-[15px] leading-relaxed text-ink-2"
      >
        If that address has an account, a reset link is on its way. It works once and
        expires in an hour.
      </p>
    );
  }

  return (
    <form action={formAction} className="flex flex-col gap-5">
      <FormError message={state.error} />
      <Field label="Email" name="email" type="email" autoComplete="email" />
      <div className="mt-1">
        <SubmitButton>Send reset link</SubmitButton>
      </div>
    </form>
  );
}
