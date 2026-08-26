import type { Metadata } from "next";

import { PageHero } from "@/components/page-hero";
import { communityRules, site, socialLinks } from "@/lib/site-content";

export const metadata: Metadata = {
  // Overrides the template so the home page doesn't read "GamerZone · GamerZone".
  title: `${site.name} — ${site.tagline}`,
};

function DiscordIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      className="h-[17px] w-[17px]"
      aria-hidden
    >
      <path d="M8 12h.01M16 12h.01M7.5 18c-2-3-2-8 0-11 2-1 9-1 11 0 2 3 2 8 0 11-1 .8-3 1.2-3 1.2l-1-2M8.5 19.2S7 19 6 18" />
    </svg>
  );
}

function FacebookIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-[17px] w-[17px]"
      aria-hidden
    >
      <path d="M14 8h2.5V5H14c-2 0-3 1.3-3 3.2V11H9v3h2v7h3v-7h2.3l.7-3H14V8.6c0-.4.2-.6.6-.6z" />
    </svg>
  );
}

export default function HomePage() {
  return (
    <>
      <PageHero
        image="/images/hero-home.jpg"
        imageAlt="A Bangladeshi Unique Poribohon coach on a wet highway at dusk, from Euro Truck Simulator 2"
        kicker={site.tagline}
        title={`Welcome to ${site.name}`}
        priority
      />

      <div className="mx-auto grid max-w-6xl gap-12 px-6 pt-8 sm:px-8 lg:grid-cols-3 lg:gap-14">
        <div className="lg:col-span-2">
          <p className="max-w-[62ch] text-[17px] leading-relaxed text-ink-2 text-pretty">
            {site.description}
          </p>

          <div className="mt-7 flex flex-wrap gap-3">
            <a
              href={socialLinks.discord}
              target="_blank"
              rel="noreferrer noopener"
              className="inline-flex items-center gap-2.5 rounded-lg bg-accent px-5 py-3 text-[15px] font-semibold text-accent-ink transition-colors hover:bg-accent-hover"
            >
              <DiscordIcon />
              Join our Discord
            </a>
            <a
              href={socialLinks.facebook}
              target="_blank"
              rel="noreferrer noopener"
              className="inline-flex items-center gap-2.5 rounded-lg border border-line px-5 py-3 text-[15px] font-medium transition-colors hover:border-ink-4"
            >
              <FacebookIcon />
              Facebook page
            </a>
          </div>
        </div>

        <section aria-labelledby="rules-heading">
          <h2
            id="rules-heading"
            className="mb-4 font-display text-[13px] font-semibold uppercase tracking-[0.11em] text-ink-3"
          >
            Community rules
          </h2>
          {/* An ordered list because the numbers are shown and read out; they
              are just labels here, not a ranking. */}
          <ol className="flex flex-col gap-3">
            {communityRules.map((rule, index) => (
              <li key={rule} className="flex gap-3 text-[14.5px] leading-relaxed text-ink-2">
                <span className="tabular-nums text-ink-4" aria-hidden>
                  {String(index + 1).padStart(2, "0")}
                </span>
                {rule}
              </li>
            ))}
          </ol>
        </section>
      </div>
    </>
  );
}
