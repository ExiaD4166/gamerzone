import type { Metadata } from "next";

import { ForgotPasswordForm } from "./forgot-password-form";
import { AuthCard, AuthCardLink } from "@/components/auth-card";

export const metadata: Metadata = {
  title: "Reset your password",
};

export default function ForgotPasswordPage() {
  return (
    <AuthCard
      title="Reset your password"
      intro="Tell us the address on your account and we'll email you a link to set a new password."
      footer={
        <>
          Remembered it? <AuthCardLink href="/login">Sign in</AuthCardLink>
        </>
      }
    >
      <ForgotPasswordForm />
    </AuthCard>
  );
}
