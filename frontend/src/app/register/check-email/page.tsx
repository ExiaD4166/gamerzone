import type { Metadata } from "next";

import { ResendForm } from "./resend-form";
import { AuthCard, AuthCardLink } from "@/components/auth-card";

export const metadata: Metadata = {
  title: "Confirm your email",
};

/**
 * Where registration lands. The account exists but cannot reach anything yet —
 * the confirmation link has to be followed first.
 */
export default async function CheckEmailPage({
  searchParams,
}: {
  // In Next 16 searchParams is a promise, in step with the other request-time APIs.
  searchParams: Promise<{ email?: string }>;
}) {
  const { email } = await searchParams;

  return (
    <AuthCard
      title="Check your email"
      intro={
        email
          ? `We sent a confirmation link to ${email}. Follow it and your account is ready.`
          : "We sent you a confirmation link. Follow it and your account is ready."
      }
      footer={
        <>
          Already confirmed? <AuthCardLink href="/login">Sign in</AuthCardLink>
        </>
      }
    >
      <div className="rounded-xl border border-line bg-surface p-6">
        <h2 className="font-display text-[15px] font-semibold">Didn&apos;t get it?</h2>
        <p className="mt-2 text-[14px] leading-relaxed text-ink-2">
          Check your spam folder first. If it still hasn&apos;t arrived, we can send another.
        </p>
        <div className="mt-5">
          <ResendForm defaultEmail={email} />
        </div>
      </div>
    </AuthCard>
  );
}
