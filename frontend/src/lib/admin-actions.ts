"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { api, type DownloadItem } from "@/lib/api";
import { getSessionToken } from "@/lib/session";

// A "use server" module may only export async functions — Next.js rewrites every
// export into a callable stub, so a constant exported from here reaches the client
// as an unusable reference. Shared values live in site-content.ts instead.

export type AdminFormState = { error: string | null };

function readForm(formData: FormData) {
  return {
    title: String(formData.get("title") ?? "").trim(),
    category: String(formData.get("category") ?? "").trim(),
    url: String(formData.get("url") ?? "").trim(),
    description: String(formData.get("description") ?? "").trim(),
  };
}

/** Anything the pages changed is cached; both views have to be dropped. */
function refreshDownloadViews() {
  revalidatePath("/downloads");
  revalidatePath("/admin/downloads");
}

export async function createDownloadItemAction(
  _previous: AdminFormState,
  formData: FormData,
): Promise<AdminFormState> {
  const fields = readForm(formData);

  if (!fields.title || !fields.category || !fields.url) {
    return { error: "Title, category and link are all required." };
  }

  const result = await api<DownloadItem>("/api/v1/downloads/", {
    method: "POST",
    token: await getSessionToken(),
    json: { ...fields, description: fields.description || null },
  });

  if (!result.ok) {
    return { error: result.error.detail };
  }

  refreshDownloadViews();
  redirect("/admin/downloads");
}

export async function updateDownloadItemAction(
  _previous: AdminFormState,
  formData: FormData,
): Promise<AdminFormState> {
  const id = String(formData.get("id") ?? "");
  const fields = readForm(formData);

  if (!id) {
    return { error: "Missing the item's id." };
  }
  if (!fields.title || !fields.category || !fields.url) {
    return { error: "Title, category and link are all required." };
  }

  const result = await api<DownloadItem>(`/api/v1/downloads/${id}`, {
    method: "PATCH",
    token: await getSessionToken(),
    json: { ...fields, description: fields.description || null },
  });

  if (!result.ok) {
    return { error: result.error.detail };
  }

  refreshDownloadViews();
  redirect("/admin/downloads");
}

export async function deleteDownloadItemAction(formData: FormData): Promise<void> {
  const id = String(formData.get("id") ?? "");
  if (!id) return;

  await api(`/api/v1/downloads/${id}`, { method: "DELETE", token: await getSessionToken() });

  refreshDownloadViews();
  redirect("/admin/downloads");
}
