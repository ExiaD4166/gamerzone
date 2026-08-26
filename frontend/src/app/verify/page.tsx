import type { Metadata } from "next";

import { AuthCard, AuthCardLink } from "@/components/auth-card";
import { api } from "@/lib/api";

export const metadata: Metadata = {
  title: "Confirm your email",
};

function SuccessMark() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-7 w-7"
      aria-hidden
    >
      <circle cx="12" cy="12" r="9" />
      <path d="m8.5 12.5 2.5 2.5 4.5-5" />
    </svg>
  );
}

function ProblemMark() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-7 w-7"
      aria-hidden
    >
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7.5v5M12 16h.01" />
    </svg>
  );
}

/**
 * Where the confirmation link lands. The work happens on the server while the page
 * renders, so the visitor sees a result rather than a spinner.
 */
export default async function VerifyPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>;
}) {
  const { token } = await searchParams;

  if (!token) {
    return (
      <AuthCard
        title="Something's missing"
        intro="That link didn't include a confirmation code. Try opening it again from your email, or request a new one."
        footer={
          <AuthCardLink href="/register/check-email">Send another link</AuthCardLink>
        }
      >
        <span className="inline-flex h-14 w-14 items-center justify-center rounded-full bg-surface text-ink-3">
          <ProblemMark />
        </span>
      </AuthCard>
    );
  }

  const result = await api<{ message: string }>(
    `/api/v1/auth/verify?token=${encodeURIComponent(token)}`,
  );

  if (!result.ok) {
    return (
      <AuthCard
        title="This link didn't work"
        intro={result.error.detail}
        footer={<AuthCardLink href="/register/check-email">Send another link</AuthCardLink>}
      >
        <span className="inline-flex h-14 w-14 items-center justify-center rounded-full bg-surface text-ink-3">
          <ProblemMark />
        </span>
      </AuthCard>
    );
  }

  return (
    <AuthCard
      title="Email confirmed"
      intro="Your account is ready. Sign in and the downloads are yours."
    >
      <span className="mb-8 inline-flex h-14 w-14 items-center justify-center rounded-full bg-surface text-accent">
        <SuccessMark />
      </span>
      <div>
        <AuthCardLink href="/login">
          <span className="inline-block rounded-lg bg-accent px-5 py-3 text-[15px] font-semibold text-accent-ink transition-colors hover:bg-accent-hover">
            Sign in
          </span>
        </AuthCardLink>
      </div>
    </AuthCard>
  );
}
