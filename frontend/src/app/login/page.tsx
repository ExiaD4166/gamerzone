import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { LoginForm } from "./login-form";
import { AuthCard, AuthCardLink } from "@/components/auth-card";
import { getCurrentUser } from "@/lib/session";

export const metadata: Metadata = {
  title: "Sign in",
};

export default async function LoginPage() {
  if (await getCurrentUser()) redirect("/profile");

  return (
    <AuthCard
      title="Sign in"
      intro="Welcome back. Sign in to reach the downloads."
      footer={
        <>
          New here? <AuthCardLink href="/register">Create an account</AuthCardLink>
        </>
      }
    >
      <LoginForm />
    </AuthCard>
  );
}
