import Link from "next/link";

import { navLinks, site, socialLinks } from "@/lib/site-content";

export function SiteFooter() {
  return (
    <footer className="mt-24 border-t border-line-soft">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-10 text-sm text-ink-3 sm:flex-row sm:items-center sm:justify-between sm:px-8">
        <p>
          © {new Date().getFullYear()} {site.name}. Mods belong to their original creators.
        </p>

        <ul className="flex flex-wrap items-center gap-5">
          {navLinks.slice(1).map((link) => (
            <li key={link.href}>
              <Link href={link.href} className="transition-colors hover:text-ink-2">
                {link.label}
              </Link>
            </li>
          ))}
          <li>
            <a
              href={socialLinks.discord}
              target="_blank"
              rel="noreferrer noopener"
              className="transition-colors hover:text-ink-2"
            >
              Discord
            </a>
          </li>
          <li>
            <a
              href={socialLinks.facebook}
              target="_blank"
              rel="noreferrer noopener"
              className="transition-colors hover:text-ink-2"
            >
              Facebook
            </a>
          </li>
        </ul>
      </div>
    </footer>
  );
}
