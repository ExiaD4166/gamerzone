import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { LoginForm } from "./login-form";
import { AuthCard, AuthCardLink } from "@/components/auth-card";
import { getCurrentUser } from "@/lib/session";

export const metadata: Metadata = {
  title: "Sign in",
};

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ reset?: string }>;
}) {
  if (await getCurrentUser()) redirect("/profile");

  const { reset } = await searchParams;

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
      {reset ? (
        <p
          role="status"
          className="mb-6 rounded-lg border border-[#2f4a35] bg-[#16211a] px-4 py-3 text-[14px] leading-relaxed text-[#8fd0a3]"
        >
          Your password has been changed. Sign in with the new one.
        </p>
      ) : null}

      <LoginForm />
    </AuthCard>
  );
}
