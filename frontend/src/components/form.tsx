"use client";

import { useFormStatus } from "react-dom";

/**
 * Small building blocks shared by the auth forms.
 *
 * These are Client Components because they react to the browser: the submit
 * button has to know whether the form is currently in flight. Everything else in
 * the auth pages stays on the server.
 */

export function Field({
  label,
  name,
  type = "text",
  autoComplete,
  required = true,
  minLength,
  hint,
  defaultValue,
}: {
  label: string;
  name: string;
  type?: string;
  autoComplete?: string;
  required?: boolean;
  minLength?: number;
  hint?: string;
  defaultValue?: string;
}) {
  const id = `field-${name}`;
  const hintId = hint ? `${id}-hint` : undefined;

  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={id} className="text-[14px] font-medium text-ink">
        {label}
      </label>
      <input
        id={id}
        name={name}
        type={type}
        autoComplete={autoComplete}
        required={required}
        minLength={minLength}
        defaultValue={defaultValue}
        aria-describedby={hintId}
        className="rounded-lg border border-line bg-ground px-4 py-3 text-[15px] text-ink placeholder:text-ink-4 transition-colors hover:border-ink-4 focus:border-accent"
      />
      {hint ? (
        <p id={hintId} className="text-[13px] text-ink-3">
          {hint}
        </p>
      ) : null}
    </div>
  );
}

export function SubmitButton({ children }: { children: React.ReactNode }) {
  // useFormStatus reads the state of the <form> this button sits inside, which
  // is why it has to be its own component rather than part of the form itself.
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
      className="rounded-lg bg-accent px-5 py-3 text-[15px] font-semibold text-accent-ink transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-60"
    >
      {pending ? "Working…" : children}
    </button>
  );
}

export function FormError({ message }: { message: string | null }) {
  if (!message) return null;

  return (
    // role="alert" makes a screen reader announce this the moment it appears,
    // rather than leaving it to be discovered.
    <p
      role="alert"
      className="rounded-lg border border-[#5a2b22] bg-[#221512] px-4 py-3 text-[14px] leading-relaxed text-[#f0a89a]"
    >
      {message}
    </p>
  );
}
