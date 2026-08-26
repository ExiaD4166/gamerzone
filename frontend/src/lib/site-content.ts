/**
 * Everything about the community that isn't code lives here.
 *
 * Rules, links and copy change far more often than layout does, and they appear
 * on several pages. Keeping them in one file means editing a rule is a one-line
 * change in one place rather than a hunt through components.
 */

export const site = {
  name: "GamerZone",
  tagline: "Bangladeshi bus & truck sim community",
  description:
    "We build and share bus and truck mods for the roads we actually know — Bangladeshi liveries, local buses, and maps worth driving. Everything here is made and tested by the community.",
} as const;

/** TODO: replace with the real invite and page URLs. */
export const socialLinks = {
  discord: "https://discord.gg/REPLACE-ME",
  facebook: "https://facebook.com/REPLACE-ME",
} as const;

export const communityRules: readonly string[] = [
  "Credit the original creator on every re-upload.",
  "No paid or leaked mods.",
  "Keep discussion in Bangla or English.",
  "Report broken links instead of reposting them.",
];

/** The pages in the main navigation, in order. */
export const navLinks: readonly { href: string; label: string }[] = [
  { href: "/", label: "Home" },
  { href: "/about", label: "About" },
  { href: "/downloads", label: "Downloads" },
  { href: "/profile", label: "Profile" },
];
