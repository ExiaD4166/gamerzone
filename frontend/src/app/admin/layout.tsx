import Link from "next/link";
import { redirect } from "next/navigation";

import { getCurrentUser } from "@/lib/session";

/**
 * Wraps every /admin page with the one check they all need.
 *
 * A layout runs before the page inside it, so no admin page has to repeat this.
 * It is a convenience, not the security boundary — the API refuses these calls on
 * its own, so a non-admin reaching the URL directly still cannot change anything.
 */
export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const user = await getCurrentUser();

  if (!user) redirect("/login");
  if (!user.is_superuser) redirect("/downloads");

  return (
    <div className="mx-auto max-w-5xl px-6 py-12 sm:px-8 sm:py-16">
      <div className="mb-10 flex flex-wrap items-baseline justify-between gap-4 border-b border-line pb-6">
        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-[0.16em] text-accent">
            Administration
          </p>
          <h1 className="font-display text-3xl font-bold tracking-tight">Manage downloads</h1>
        </div>
        <Link
          href="/downloads"
          className="text-[14px] text-ink-3 transition-colors hover:text-ink-2"
        >
          View the public page →
        </Link>
      </div>

      {children}
    </div>
  );
}
