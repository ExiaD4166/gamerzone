import type { OfferingIcon as IconName } from "@/lib/site-content";

/** Drawn rather than emoji, so they scale cleanly and inherit the accent colour. */
export function OfferingIcon({ name }: { name: IconName }) {
  const shared = {
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.5,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    className: "h-[22px] w-[22px]",
    "aria-hidden": true,
  };

  switch (name) {
    case "convoy":
      // A route with two vehicles following it.
      return (
        <svg {...shared}>
          <path d="M4 20c0-4 3-5 6-5s6-1 6-5" />
          <rect x="2" y="16" width="5" height="4" rx="1" />
          <rect x="16" y="4" width="6" height="5" rx="1.5" />
          <path d="M16 7h6" />
        </svg>
      );
    case "mods":
      // Stacked layers: a pack of parts rather than a single file.
      return (
        <svg {...shared}>
          <path d="M12 3 3 7.5l9 4.5 9-4.5L12 3Z" />
          <path d="m3 12.5 9 4.5 9-4.5" />
          <path d="m3 17 9 4.5 9-4.5" />
        </svg>
      );
    case "community":
      // Two people, one slightly behind.
      return (
        <svg {...shared}>
          <circle cx="9" cy="8" r="3" />
          <path d="M3 20c0-3.3 2.7-5.5 6-5.5s6 2.2 6 5.5" />
          <path d="M16 5.5a3 3 0 0 1 0 5.8M18 20c0-2.6-1-4.4-2.5-5.4" />
        </svg>
      );
    case "events":
      // A calendar with a marked date.
      return (
        <svg {...shared}>
          <rect x="3" y="5" width="18" height="16" rx="2" />
          <path d="M3 10h18M8 3v4M16 3v4" />
          <path d="M8.5 14.5h3" />
        </svg>
      );
  }
}
