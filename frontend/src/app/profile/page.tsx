import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { PageHero } from "@/components/page-hero";
import { logoutAction } from "@/lib/auth-actions";
import { getCurrentUser } from "@/lib/session";

export const metadata: Metadata = {
  title: "Profile",
};

function formatJoinDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function DetailRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1 border-b border-line-soft py-4 last:border-b-0 sm:flex-row sm:items-center sm:gap-6">
      <dt className="text-[13px] uppercase tracking-[0.11em] text-ink-3 sm:w-40 sm:shrink-0">
        {label}
      </dt>
      <dd className="text-[16px] text-ink">{children}</dd>
    </div>
  );
}

function Badge({ tone, children }: { tone: "good" | "warn" | "accent"; children: React.ReactNode }) {
  const tones = {
    good: "border-[#2f4a35] bg-[#16211a] text-[#8fd0a3]",
    warn: "border-[#5a4a22] bg-[#221d12] text-[#e5c07b]",
    accent: "border-[#5a4326] bg-[#221a12] text-accent",
  } as const;

  return (
    <span
      className={`inline-flex items-center rounded-full border px-3 py-1 text-[13px] font-medium ${tones[tone]}`}
    >
      {children}
    </span>
  );
}

export default async function ProfilePage() {
  const user = await getCurrentUser();

  // No session, or one the API no longer accepts — either way, sign in first.
  if (!user) redirect("/login");

  return (
    <>
      {/* No photograph here by choice: the page is about the account, and a
          screenshot behind it would only compete. The gradient keeps the same
          rhythm as the other pages. */}
      <PageHero kicker="Your account" title={user.username} compact />

      <div className="mx-auto max-w-3xl px-6 pt-8 sm:px-8">
        {!user.is_verified ? (
          <div className="mb-8 rounded-xl border border-[#5a4a22] bg-[#1c1811] px-5 py-4">
            <p className="text-[15px] leading-relaxed text-[#e5c07b]">
              Your email isn&apos;t confirmed yet, so the downloads stay locked.{" "}
              <Link href="/register/check-email" className="underline underline-offset-2">
                Send yourself another link
              </Link>
              .
            </p>
          </div>
        ) : null}

        <dl className="rounded-xl border border-line bg-surface px-6 py-2 sm:px-8">
          <DetailRow label="Username">{user.username}</DetailRow>
          <DetailRow label="Email">{user.email}</DetailRow>
          <DetailRow label="Status">
            <div className="flex flex-wrap gap-2">
              {user.is_verified ? (
                <Badge tone="good">Email confirmed</Badge>
              ) : (
                <Badge tone="warn">Email not confirmed</Badge>
              )}
              {user.is_superuser ? <Badge tone="accent">Administrator</Badge> : null}
            </div>
          </DetailRow>
          <DetailRow label="Member since">{formatJoinDate(user.created_at)}</DetailRow>
        </dl>

        <div className="mt-8 flex flex-wrap items-center gap-4">
          {/* A form rather than a link, because signing out changes something:
              it revokes the token on the server. A link would let a browser
              prefetch it and sign the user out by accident. */}
          <form action={logoutAction}>
            <button
              type="submit"
              className="rounded-lg border border-line px-5 py-3 text-[15px] font-medium transition-colors hover:border-ink-4"
            >
              Sign out
            </button>
          </form>

          {user.is_verified ? (
            <Link
              href="/downloads"
              className="text-[15px] text-accent transition-colors hover:text-accent-hover"
            >
              Go to downloads →
            </Link>
          ) : null}
        </div>
      </div>
    </>
  );
}
