"use client";

import { deleteDownloadItemAction } from "@/lib/admin-actions";

/**
 * Client-side only so it can ask before deleting. The confirmation is a courtesy
 * against a misclick; the form is what actually performs the delete.
 */
export function DeleteButton({ id, title }: { id: number; title: string }) {
  return (
    <form
      action={deleteDownloadItemAction}
      onSubmit={(event) => {
        if (!window.confirm(`Delete "${title}"? This cannot be undone.`)) {
          event.preventDefault();
        }
      }}
    >
      <input type="hidden" name="id" value={id} />
      <button
        type="submit"
        className="rounded-md border border-line px-3 py-1.5 text-[13px] text-ink-3 transition-colors hover:border-[#5a2b22] hover:text-[#f0a89a]"
      >
        Delete
      </button>
    </form>
  );
}
