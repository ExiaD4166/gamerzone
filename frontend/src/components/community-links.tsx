import { socialLinks } from "@/lib/site-content";

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

/**
 * The two ways into the community, used wherever we invite someone in.
 *
 * Both open in a new tab: they leave the site entirely, and rel="noreferrer
 * noopener" stops the opened page from being able to reach back into ours.
 */
export function CommunityLinks({ discordLabel = "Join our Discord" }: { discordLabel?: string }) {
  return (
    <div className="flex flex-wrap gap-3">
      <a
        href={socialLinks.discord}
        target="_blank"
        rel="noreferrer noopener"
        className="inline-flex items-center gap-2.5 rounded-lg bg-accent px-5 py-3 text-[15px] font-semibold text-accent-ink transition-colors hover:bg-accent-hover"
      >
        <DiscordIcon />
        {discordLabel}
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
  );
}
