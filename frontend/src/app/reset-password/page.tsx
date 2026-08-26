import type { Metadata } from "next";

import { ResetPasswordForm } from "./reset-password-form";
import { AuthCard, AuthCardLink } from "@/components/auth-card";

export const metadata: Metadata = {
  title: "Choose a new password",
};

/** Where the link in the reset email lands. */
export default async function ResetPasswordPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>;
}) {
  const { token } = await searchParams;

  if (!token) {
    return (
      <AuthCard
        title="Something's missing"
        intro="That link didn't include a reset code. Open it again from your email, or ask for a new one."
        footer={<AuthCardLink href="/forgot-password">Request a new link</AuthCardLink>}
      >
        <span />
      </AuthCard>
    );
  }

  return (
    <AuthCard
      title="Choose a new password"
      intro="This link works once. Setting a new password also signs you out everywhere else."
      footer={<AuthCardLink href="/login">Back to sign in</AuthCardLink>}
    >
      <ResetPasswordForm token={token} />
    </AuthCard>
  );
}
