import type { Metadata } from "next";
import Link from "next/link";

import { DeleteButton } from "./delete-button";
import { api, type DownloadItem } from "@/lib/api";
import { getSessionToken } from "@/lib/session";

export const metadata: Metadata = {
  title: "Manage downloads",
};

export default async function AdminDownloadsPage() {
  const result = await api<DownloadItem[]>("/api/v1/downloads/", {
    token: await getSessionToken(),
  });

  return (
    <>
      <div className="mb-8 flex justify-end">
        <Link
          href="/admin/downloads/new"
          className="rounded-lg bg-accent px-5 py-3 text-[15px] font-semibold text-accent-ink transition-colors hover:bg-accent-hover"
        >
          Add a download
        </Link>
      </div>

      {!result.ok ? (
        <p className="rounded-xl border border-line bg-surface px-6 py-8 text-center text-[15px] text-ink-2">
          {result.error.detail}
        </p>
      ) : result.data.length === 0 ? (
        <p className="rounded-xl border border-line bg-surface px-6 py-12 text-center text-[15px] text-ink-2">
          No downloads yet. Add the first one.
        </p>
      ) : (
        <ul className="flex flex-col gap-3">
          {result.data.map((item) => (
            <li
              key={item.id}
              className="flex flex-wrap items-start justify-between gap-4 rounded-xl border border-line bg-surface p-5"
            >
              <div className="min-w-0 flex-1">
                <div className="mb-2 flex flex-wrap items-center gap-3">
                  <span className="rounded-full border border-line bg-surface-2 px-2.5 py-0.5 text-[11px] uppercase tracking-[0.1em] text-ink-3">
                    {item.category}
                  </span>
                  <h2 className="font-display text-[16px] font-semibold tracking-tight">
                    {item.title}
                  </h2>
                </div>
                {item.description ? (
                  <p className="mb-2 text-[14px] leading-relaxed text-ink-2">{item.description}</p>
                ) : null}
                {/* break-all so a long Drive URL wraps instead of stretching the row. */}
                <p className="break-all text-[13px] text-ink-4">{item.url}</p>
              </div>

              <div className="flex shrink-0 items-center gap-2">
                <Link
                  href={`/admin/downloads/${item.id}/edit`}
                  className="rounded-md border border-line px-3 py-1.5 text-[13px] text-ink-2 transition-colors hover:border-ink-4"
                >
                  Edit
                </Link>
                <DeleteButton id={item.id} title={item.title} />
              </div>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
