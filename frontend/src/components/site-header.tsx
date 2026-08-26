import Link from "next/link";

import { logoutAction } from "@/lib/auth-actions";
import { getCurrentUser } from "@/lib/session";
import { navLinks, site } from "@/lib/site-content";

function BusMark() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-6 w-6 text-accent"
      aria-hidden
    >
      <rect x="3" y="5" width="18" height="12" rx="2" />
      <path d="M3 11h18M7 17v2M17 17v2" />
    </svg>
  );
}

function NavItems({ className }: { className?: string }) {
  return (
    <ul className={className}>
      {navLinks.map((link) => (
        <li key={link.href}>
          <Link href={link.href} className="transition-colors hover:text-ink">
            {link.label}
          </Link>
        </li>
      ))}
    </ul>
  );
}

/**
 * The navigation bar. It is a solid strip of its own above the hero image, not
 * an overlay on top of it, so the links never have to compete with a photo.
 *
 * On phones the links move to a second row rather than hiding behind a hamburger:
 * four links cost less height than a menu button, and it keeps the header free of
 * client-side JavaScript.
 *
 * The session is read on the server, so the page never flashes "Sign in" at somebody
 * who is signed in.
 */
export async function SiteHeader() {
  const user = await getCurrentUser();

  return (
    <header className="border-b border-line bg-surface">
      <nav aria-label="Main" className="mx-auto max-w-6xl px-6 sm:px-8">
        <div className="flex h-16 items-center justify-between gap-4">
          <Link
            href="/"
            className="flex items-center gap-2.5 font-display text-[17px] font-bold tracking-tight"
          >
            <BusMark />
            {site.name}
          </Link>

          <div className="flex items-center gap-7">
            <NavItems className="hidden items-center gap-7 text-sm text-ink-2 sm:flex" />

            <div className="flex items-center gap-2.5">
              {user ? (
                <>
                  <Link
                    href="/profile"
                    className="hidden text-sm text-ink-2 transition-colors hover:text-ink sm:inline"
                  >
                    {user.username}
                  </Link>
                  {/* A form, not a link: it revokes the token, and a link could be
                      prefetched and fire by accident. */}
                  <form action={logoutAction}>
                    <button
                      type="submit"
                      className="rounded-md border border-line px-4 py-2 text-[13.5px] font-medium transition-colors hover:border-ink-4"
                    >
                      Sign out
                    </button>
                  </form>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="rounded-md border border-line px-4 py-2 text-[13.5px] font-medium transition-colors hover:border-ink-4"
                  >
                    Sign in
                  </Link>
                  <Link
                    href="/register"
                    className="rounded-md bg-accent px-4 py-2 text-[13.5px] font-semibold text-accent-ink transition-colors hover:bg-accent-hover"
                  >
                    Register
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>

        <NavItems className="-mx-6 flex items-center gap-6 overflow-x-auto border-t border-line-soft px-6 py-3 text-sm text-ink-2 sm:hidden" />
      </nav>
    </header>
  );
}
