import Image from "next/image";

type PageHeroProps = {
  /** Path under /public, e.g. "/images/hero-home.jpg" */
  image: string;
  /** Describes the picture for screen readers and when the image fails to load. */
  imageAlt: string;
  title: string;
  /** Small line above the title. */
  kicker?: string;
  /**
   * Only the page that loads first should be priority — it stops Next.js lazy
   * loading an image that is visible immediately, which would otherwise show up
   * as a slow largest-contentful-paint.
   */
  priority?: boolean;
};

/**
 * The cinematic header used at the top of every page: a full-bleed screenshot
 * that dissolves into the page background, with the title sitting inside the
 * fade.
 *
 * It deliberately starts BELOW the navigation rather than running behind it, so
 * the links always sit on a solid bar and stay readable whatever the photo is.
 *
 * Each page passes its own image; nothing else has to change.
 */
export function PageHero({ image, imageAlt, title, kicker, priority = false }: PageHeroProps) {
  return (
    <section className="relative isolate">
      {/* Fixed aspect ratio so the crop is identical on every page and the
          browser reserves the right height before the image arrives. */}
      <div className="relative aspect-[16/9] max-h-[62vh] min-h-[280px] w-full overflow-hidden">
        <Image
          src={image}
          alt={imageAlt}
          fill
          priority={priority}
          sizes="100vw"
          className="object-cover"
        />

        {/* Two stacked gradients: a gentle darkening across the whole image so
            white text stays readable, then a stronger fade that blends the
            bottom edge into the page. aria-hidden because they are pure
            decoration. */}
        <div
          aria-hidden
          className="absolute inset-0 bg-gradient-to-b from-ground/20 via-transparent to-transparent"
        />
        <div
          aria-hidden
          className="absolute inset-x-0 bottom-0 h-3/5 bg-gradient-to-t from-ground via-ground/80 to-transparent"
        />
      </div>

      <div className="absolute inset-x-0 bottom-0">
        <div className="mx-auto max-w-6xl px-6 pb-8 sm:px-8 sm:pb-10">
          {kicker ? (
            <p className="mb-3 text-xs font-medium uppercase tracking-[0.16em] text-accent sm:text-[13px]">
              {kicker}
            </p>
          ) : null}
          <h1 className="font-display text-4xl font-bold leading-[1.04] tracking-tight text-balance sm:text-5xl lg:text-6xl">
            {title}
          </h1>
        </div>
      </div>
    </section>
  );
}
