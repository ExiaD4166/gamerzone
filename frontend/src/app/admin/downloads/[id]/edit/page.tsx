import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { DownloadForm } from "../../download-form";
import { api, type DownloadItem } from "@/lib/api";
import { getSessionToken } from "@/lib/session";

export const metadata: Metadata = {
  title: "Edit download",
};

/**
 * The [id] folder makes this a dynamic route: /admin/downloads/5/edit gives
 * params.id === "5". Like FastAPI's /downloads/{item_id}.
 */
export default async function EditDownloadPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  const result = await api<DownloadItem>(`/api/v1/downloads/${id}`, {
    token: await getSessionToken(),
  });

  // Renders the standard 404 page rather than an error, which is what a stale
  // link to a deleted item should produce.
  if (!result.ok) notFound();

  return (
    <>
      <h2 className="mb-6 font-display text-xl font-semibold tracking-tight">Edit download</h2>
      <DownloadForm item={result.data} />
    </>
  );
}
