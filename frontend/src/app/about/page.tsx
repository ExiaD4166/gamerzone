import type { Metadata } from "next";

import { CommunityLinks } from "@/components/community-links";
import { OfferingIcon } from "@/components/offering-icon";
import { PageHero } from "@/components/page-hero";
import { about, communityRules, site } from "@/lib/site-content";

export const metadata: Metadata = {
  title: "About",
  description: about.story[0],
};

export default function AboutPage() {
  return (
    <>
      <PageHero
        image="/images/hero-about.jpg"
        imageAlt="A GamerZone convoy on the road in Euro Truck Simulator 2"
        kicker={`Driving together since ${about.foundedYear}`}
        title={`About ${site.name}`}
        priority
      />

      <div className="mx-auto max-w-6xl px-6 pt-8 sm:px-8">
        {/* Narrow measure so the story stays comfortable to read. */}
        <section className="max-w-[68ch]">
          {about.story.map((paragraph) => (
            <p
              key={paragraph.slice(0, 40)}
              className="mb-5 text-[17px] leading-relaxed text-ink-2 text-pretty last:mb-0"
            >
              {paragraph}
            </p>
          ))}
        </section>

        <section aria-labelledby="offer-heading" className="mt-16">
          <h2
            id="offer-heading"
            className="font-display text-2xl font-semibold tracking-tight sm:text-[28px]"
          >
            What we offer
          </h2>

          <ul className="mt-7 grid gap-4 sm:grid-cols-2">
            {about.offerings.map((offering) => (
              <li
                key={offering.title}
                className="rounded-xl border border-line bg-surface p-6 transition-colors hover:border-ink-4"
              >
                <span className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-lg bg-surface-2 text-accent">
                  <OfferingIcon name={offering.icon} />
                </span>
                <h3 className="mb-2 font-display text-[17px] font-semibold tracking-tight">
                  {offering.title}
                </h3>
                <p className="text-[15px] leading-relaxed text-ink-2 text-pretty">
                  {offering.body}
                </p>
              </li>
            ))}
          </ul>
        </section>

        {/* Given room here, unlike the sidebar treatment on the home page. */}
        <section aria-labelledby="rules-heading" className="mt-16">
          <h2
            id="rules-heading"
            className="font-display text-2xl font-semibold tracking-tight sm:text-[28px]"
          >
            Community rules
          </h2>
          <p className="mt-3 max-w-[62ch] text-[15px] leading-relaxed text-ink-3">
            These keep a convoy safe and enjoyable for everyone on the road.
          </p>

          <ol className="mt-7 grid gap-x-10 gap-y-5 sm:grid-cols-2">
            {communityRules.map((rule, index) => (
              <li key={rule} className="flex items-baseline gap-4">
                <span
                  className="font-display text-[15px] tabular-nums text-accent"
                  aria-hidden
                >
                  {String(index + 1).padStart(2, "0")}
                </span>
                <span className="text-[16px] leading-relaxed text-ink-2">{rule}</span>
              </li>
            ))}
          </ol>
        </section>

        <section className="mt-16 rounded-xl border border-line bg-surface px-6 py-10 sm:px-10">
          <p className="max-w-[54ch] font-display text-xl font-semibold leading-snug tracking-tight text-balance sm:text-2xl">
            {about.closing}
          </p>
          <p className="mt-3 max-w-[54ch] text-[16px] leading-relaxed text-ink-2">
            Join {site.name} today, download the mods, and let&apos;s hit the road together.
          </p>
          <div className="mt-7">
            <CommunityLinks />
          </div>
        </section>
      </div>
    </>
  );
}
