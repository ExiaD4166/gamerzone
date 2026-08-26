import type { Metadata } from "next";
import Link from "next/link";

import { PageHero } from "@/components/page-hero";
import { api, type DownloadItem } from "@/lib/api";
import { getCurrentUser, getSessionToken } from "@/lib/session";

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

function DownloadIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-[17px] w-[17px]"
      aria-hidden
    >
      <path d="M12 4v10m0 0 4-4m-4 4-4-4M5 19h14" />
    </svg>
  );
}

function Panel({
  title,
  body,
  children,
}: {
  title: string;
  body: string;
  children: React.ReactNode;
}) {
  return (
    <div className="mx-auto max-w-xl rounded-xl border border-line bg-surface px-6 py-12 text-center sm:px-10">
      <span className="mx-auto mb-5 inline-flex h-14 w-14 items-center justify-center rounded-full bg-surface-2 text-accent">
        <LockIcon />
      </span>
      <h2 className="font-display text-2xl font-semibold tracking-tight text-balance">{title}</h2>
      <p className="mx-auto mt-3 max-w-[46ch] text-[16px] leading-relaxed text-ink-2 text-pretty">
        {body}
      </p>
      <div className="mt-8 flex flex-wrap justify-center gap-3">{children}</div>
    </div>
  );
}

/**
 * The members-only download page.
 *
 * Three states: signed out, signed in but unconfirmed, and confirmed. The gate
 * here is presentational — the API refuses the request outright for the first
 * two, so the links never reach a browser that hasn't earned them. Hiding them
 * in the UI is a courtesy, not the security boundary.
 */
export default async function DownloadsPage() {
  const user = await getCurrentUser();

  if (!user) {
    return (
      <>
        <Hero />
        <div className="mx-auto max-w-6xl px-6 pt-8 sm:px-8">
          <Panel
            title="Sign in to reach the downloads"
            body="Our mod packs and map extensions are shared with community members. Create an account, confirm your email, and the full list opens up."
          >
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
          </Panel>
        </div>
      </>
    );
  }

  if (!user.is_verified) {
    return (
      <>
        <Hero />
        <div className="mx-auto max-w-6xl px-6 pt-8 sm:px-8">
          <Panel
            title="Confirm your email first"
            body="We sent a link when you registered. Following it unlocks the downloads — signing up alone doesn't prove the address is yours."
          >
            <Link
              href="/register/check-email"
              className="rounded-lg bg-accent px-5 py-3 text-[15px] font-semibold text-accent-ink transition-colors hover:bg-accent-hover"
            >
              Send another link
            </Link>
          </Panel>
        </div>
      </>
    );
  }

  const token = await getSessionToken();
  const result = await api<DownloadItem[]>("/api/v1/downloads/", { token });

  return (
    <>
      <Hero />
      <div className="mx-auto max-w-6xl px-6 pt-8 sm:px-8">
        {!result.ok ? (
          <p className="rounded-xl border border-line bg-surface px-6 py-8 text-center text-[15px] text-ink-2">
            {result.error.detail}
          </p>
        ) : result.data.length === 0 ? (
          <p className="rounded-xl border border-line bg-surface px-6 py-12 text-center text-[15px] text-ink-2">
            Nothing here yet — the team is preparing the next pack.
          </p>
        ) : (
          <ul className="grid gap-4 sm:grid-cols-2">
            {result.data.map((item) => (
              <li
                key={item.id}
                className="flex flex-col rounded-xl border border-line bg-surface p-6 transition-colors hover:border-ink-4"
              >
                <span className="mb-3 self-start rounded-full border border-line bg-surface-2 px-3 py-1 text-[12px] uppercase tracking-[0.1em] text-ink-3">
                  {item.category}
                </span>
                <h2 className="font-display text-[18px] font-semibold tracking-tight">
                  {item.title}
                </h2>
                {item.description ? (
                  <p className="mt-2 text-[15px] leading-relaxed text-ink-2 text-pretty">
                    {item.description}
                  </p>
                ) : null}
                <a
                  href={item.url}
                  target="_blank"
                  rel="noreferrer noopener"
                  className="mt-5 inline-flex items-center gap-2 self-start rounded-lg bg-accent px-4 py-2.5 text-[14.5px] font-semibold text-accent-ink transition-colors hover:bg-accent-hover"
                >
                  <DownloadIcon />
                  Download
                </a>
              </li>
            ))}
          </ul>
        )}
      </div>
    </>
  );
}

function Hero() {
  return (
    <PageHero
      image="/images/hero-downloads.jpg"
      imageAlt="A GamerZone bus on a night highway in Euro Truck Simulator 2"
      kicker="Members only"
      title="Downloads"
      priority
    />
  );
}
