import Link from "next/link";

/** A narrow centred card. No photo header — nothing should compete with the form. */
export function AuthCard({
  title,
  intro,
  children,
  footer,
}: {
  title: string;
  intro?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}) {
  return (
    <div className="mx-auto flex max-w-md flex-col px-6 py-16 sm:py-24">
      <h1 className="font-display text-3xl font-bold tracking-tight text-balance">{title}</h1>
      {intro ? (
        <p className="mt-3 text-[15px] leading-relaxed text-ink-2 text-pretty">{intro}</p>
      ) : null}

      <div className="mt-8">{children}</div>

      {footer ? <div className="mt-8 text-[14px] text-ink-3">{footer}</div> : null}
    </div>
  );
}

export function AuthCardLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link href={href} className="text-accent transition-colors hover:text-accent-hover">
      {children}
    </Link>
  );
}
