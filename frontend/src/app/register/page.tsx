import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { RegisterForm } from "./register-form";
import { AuthCard, AuthCardLink } from "@/components/auth-card";
import { getCurrentUser } from "@/lib/session";

export const metadata: Metadata = {
  title: "Create an account",
  description: "Join the GamerZone convoy community.",
};

export default async function RegisterPage() {
  if (await getCurrentUser()) redirect("/profile");

  return (
    <AuthCard
      title="Create your account"
      intro="Register to reach the mod packs and join our convoys. We'll email you a link to confirm your address."
      footer={
        <>
          Already a member? <AuthCardLink href="/login">Sign in</AuthCardLink>
        </>
      }
    >
      <RegisterForm />
    </AuthCard>
  );
}
