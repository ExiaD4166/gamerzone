"use client";

import { useActionState } from "react";

import { Field, FormError, SubmitButton } from "@/components/form";
import { resendVerificationAction, type ResendState } from "@/lib/auth-actions";

const initialState: ResendState = { status: "idle", error: null };

export function ResendForm({ defaultEmail }: { defaultEmail?: string }) {
  const [state, formAction, isPending] = useActionState(resendVerificationAction, initialState);

  return (
    <form action={formAction} className="flex flex-col gap-4">
      <FormError message={state.error} />

      <Field
        label="Email"
        name="email"
        type="email"
        autoComplete="email"
        defaultValue={defaultEmail}
      />

      <div className="flex flex-wrap items-center gap-4">
        <SubmitButton>Send another link</SubmitButton>
        {/* Deliberately non-committal, matching what the API withholds. */}
        {state.status === "sent" && !isPending ? (
          <p role="status" className="text-[14px] text-ink-3">
            If that address needs confirming, a new link is on its way.
          </p>
        ) : null}
      </div>
    </form>
  );
}
