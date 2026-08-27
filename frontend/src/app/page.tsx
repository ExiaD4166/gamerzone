import type { Metadata } from "next";

import { CommunityLinks } from "@/components/community-links";
import { PageHero } from "@/components/page-hero";
import { WarmUp } from "@/components/warm-up";
import { communityRules, site } from "@/lib/site-content";

export const metadata: Metadata = {
  // Overrides the template so the home page doesn't read "GamerZone · GamerZone".
  title: `${site.name} — ${site.tagline}`,
};

export default function HomePage() {
  return (
    <>
      {/* Wakes the API while the visitor reads, so a sleeping free-tier service
          isn't waiting to be woken when they click Downloads or Sign in. */}
      <WarmUp />

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

          <div className="mt-7">
            <CommunityLinks />
          </div>
        </div>

        <section aria-labelledby="rules-heading">
          <h2
            id="rules-heading"
            className="mb-4 font-display text-[13px] font-semibold uppercase tracking-[0.11em] text-ink-3"
          >
            Community rules
          </h2>
          {/* Ordered because the numbers are shown, though they aren't a ranking. */}
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
