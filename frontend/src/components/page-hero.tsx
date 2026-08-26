import Image from "next/image";

type PageHeroProps = {
  /** Path under /public. Omit for a gradient stand-in. */
  image?: string;
  imageAlt?: string;
  title: string;
  kicker?: string;
  /** Set on above-the-fold heroes, so they aren't lazy loaded. */
  priority?: boolean;
  /** A shorter band, for pages whose content matters more than their header. */
  compact?: boolean;
};

/**
 * The cinematic page header: a full-bleed screenshot dissolving into the page, with
 * the title inside the fade. It starts BELOW the navigation rather than behind it,
 * so the links stay readable whatever the photo is.
 */
export function PageHero({
  image,
  imageAlt = "",
  title,
  kicker,
  priority = false,
  compact = false,
}: PageHeroProps) {
  return (
    <section className="relative isolate">
      {/* Fixed ratio: identical crop everywhere, and the height is reserved before
          the image arrives. */}
      <div
        className={`relative w-full overflow-hidden ${
          compact
            ? "aspect-[21/6] max-h-[34vh] min-h-[180px]"
            : "aspect-[16/9] max-h-[62vh] min-h-[280px]"
        }`}
      >
        {image ? (
          <Image
            src={image}
            alt={imageAlt}
            fill
            priority={priority}
            sizes="100vw"
            className="object-cover"
          />
        ) : (
          // Stand-in when a page has no photo of its own.
          <div
            aria-hidden
            className="absolute inset-0 bg-[radial-gradient(ellipse_60%_70%_at_30%_20%,#3a332c,transparent_70%),radial-gradient(ellipse_50%_60%_at_85%_40%,#2e2723,transparent_70%),linear-gradient(180deg,#232020,#151312)]"
          />
        )}

        {/* A gentle overall darkening so white text stays readable, then a stronger
            fade blending the bottom edge into the page. */}
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
          <h1
            className={`font-display font-bold leading-[1.04] tracking-tight text-balance ${
              compact ? "text-3xl sm:text-4xl" : "text-4xl sm:text-5xl lg:text-6xl"
            }`}
          >
            {title}
          </h1>
        </div>
      </div>
    </section>
  );
}
