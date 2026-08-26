import type { Metadata } from "next";
import Link from "next/link";

import { PageHero } from "@/components/page-hero";

export const metadata: Metadata = {
  title: "Downloads",
  description: "Mod packs and map extensions for GamerZone members.",
};

function LockIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-6 w-6"
      aria-hidden
    >
      <rect x="4" y="10" width="16" height="10" rx="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3" />
    </svg>
  );
}

/**
 * The members-only download page.
 *
 * For now this is only the locked state: the frontend has no way to sign in
 * yet, so every visitor is treated as signed out. Once sessions exist this page
 * fetches the real list for a verified member and keeps this panel as the
 * fallback for everyone else.
 *
 * The gate here is presentational. The links are never sent to a browser that
 * hasn't earned them because the API itself refuses — hiding them in the UI is
 * a courtesy, not the security boundary.
 */
export default function DownloadsPage() {
  return (
    <>
      <PageHero
        image="/images/hero-downloads.jpg"
        imageAlt="A GamerZone bus on a night highway in Euro Truck Simulator 2"
        kicker="Members only"
        title="Downloads"
        priority
      />

      <div className="mx-auto max-w-6xl px-6 pt-8 sm:px-8">
        <div className="mx-auto max-w-xl rounded-xl border border-line bg-surface px-6 py-12 text-center sm:px-10">
          <span className="mx-auto mb-5 inline-flex h-14 w-14 items-center justify-center rounded-full bg-surface-2 text-accent">
            <LockIcon />
          </span>

          <h2 className="font-display text-2xl font-semibold tracking-tight text-balance">
            Sign in to reach the downloads
          </h2>
          <p className="mx-auto mt-3 max-w-[46ch] text-[16px] leading-relaxed text-ink-2 text-pretty">
            Our mod packs and map extensions are shared with community members. Create an
            account, confirm your email, and the full list opens up.
          </p>

          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link
              href="/register"
              className="rounded-lg bg-accent px-5 py-3 text-[15px] font-semibold text-accent-ink transition-colors hover:bg-accent-hover"
            >
              Create an account
            </Link>
            <Link
              href="/login"
              className="rounded-lg border border-line px-5 py-3 text-[15px] font-medium transition-colors hover:border-ink-4"
            >
              I already have one
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}
