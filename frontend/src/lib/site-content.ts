/**
 * All the community's copy in one place. Rules, links and wording change far more
 * often than layout, and appear on several pages.
 */

export const site = {
  name: "GamerZone",
  tagline: "Bangladeshi bus & truck sim community",
  description:
    "We share bus and map mods for the roads we actually know — Bangladeshi liveries, local buses, and maps worth driving. Everything here is tested by the community.",
} as const;

/** TODO: replace with the real invite and page URLs. */
export const socialLinks = {
  discord: "https://discord.gg/REPLACE-ME",
  facebook: "https://facebook.com/REPLACE-ME",
} as const;

export const communityRules: readonly string[] = [
  "Drive Realistically and Safely.",
  "Use indicators precisely.",
  "Respect Your Fellow Drivers.",
  "Follow Admin Instructions.",
  "Do Not Misuse and Reupload The Mod Files.",
];

/** Icons are drawn in the component; this keeps the copy free of markup. */
export type OfferingIcon = "convoy" | "mods" | "community" | "events";

export const about = {
  foundedYear: 2024,
  story: [
    "Founded in 2024, GamerZone started as an exclusive, private driving community where a select group of dedicated casual bus drivers came together to share a passion for the open road. Back then, our focus was on tight-knit gameplay and testing custom setups behind closed doors.",
    "Now, the wait is over. With optimized game updates, highly stable mod packs, and a refreshed administrative team, we are opening our doors to the public and expanding our network to drivers of all skill levels.",
  ],
  offerings: [
    {
      icon: "convoy",
      title: "Regular convoy drives",
      body: "Jump into scheduled multiplayer group drives where teamwork, realistic road discipline, and clean navigation take center stage.",
    },
    {
      icon: "mods",
      title: "Tested & stable mods",
      body: "Skip the troubleshooting. Gain direct access to our curated collection of map extensions, realistic vehicle physics, and custom skins.",
    },
    {
      icon: "community",
      title: "Active & friendly community",
      body: "Whether you need tips on perfecting your indicator timing or just want to chill in voice chat during a long haul, you'll find a welcoming crowd ready to roll.",
    },
    {
      icon: "events",
      title: "Organized server events",
      body: "Participate in structured convoy trips, route challenges, and community showcases hosted by our moderation team.",
    },
  ] satisfies readonly { icon: OfferingIcon; title: string; body: string }[],
  closing:
    "If you love clean driving, active multiplayer sessions, and sharing the thrill of the highway, there's a seat saved for you.",
} as const;

/** The pages in the main navigation, in order. */
export const navLinks: readonly { href: string; label: string }[] = [
  { href: "/", label: "Home" },
  { href: "/about", label: "About" },
  { href: "/downloads", label: "Downloads" },
  { href: "/profile", label: "Profile" },
];
