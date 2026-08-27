"use client";

import Link from "next/link";
import { useActionState } from "react";

import { Field, FormError, SubmitButton } from "@/components/form";
import {
  createDownloadItemAction,
  updateDownloadItemAction,
  type AdminFormState,
} from "@/lib/admin-actions";
import type { DownloadItem } from "@/lib/api";
import { downloadCategories } from "@/lib/site-content";

const initialState: AdminFormState = { error: null };

/**
 * One form for both adding and editing.
 *
 * Passing the existing item switches it to edit mode: the fields start filled and
 * the item's id rides along in a hidden input so the action knows what to update.
 */
export function DownloadForm({ item }: { item?: DownloadItem }) {
  const isEdit = item !== undefined;
  const [state, formAction] = useActionState(
    isEdit ? updateDownloadItemAction : createDownloadItemAction,
    initialState,
  );

  return (
    <form action={formAction} className="flex max-w-xl flex-col gap-5">
      <FormError message={state.error} />

      {isEdit ? <input type="hidden" name="id" value={item.id} /> : null}

      <Field label="Title" name="title" defaultValue={item?.title} />

      <div className="flex flex-col gap-2">
        <label htmlFor="field-category" className="text-[14px] font-medium text-ink">
          Category
        </label>
        <select
          id="field-category"
          name="category"
          defaultValue={item?.category ?? downloadCategories[0]}
          required
          className="rounded-lg border border-line bg-ground px-4 py-3 text-[15px] text-ink transition-colors hover:border-ink-4 focus:border-accent"
        >
          {downloadCategories.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
      </div>

      <Field
        label="Link"
        name="url"
        type="url"
        defaultValue={item?.url}
        hint="The Google Drive share link."
      />

      <div className="flex flex-col gap-2">
        <label htmlFor="field-description" className="text-[14px] font-medium text-ink">
          Description
        </label>
        <textarea
          id="field-description"
          name="description"
          rows={3}
          defaultValue={item?.description ?? ""}
          className="resize-y rounded-lg border border-line bg-ground px-4 py-3 text-[15px] text-ink placeholder:text-ink-4 transition-colors hover:border-ink-4 focus:border-accent"
        />
        <p className="text-[13px] text-ink-3">Optional. Shown under the title on the page.</p>
      </div>

      <div className="mt-1 flex flex-wrap items-center gap-5">
        <SubmitButton>{isEdit ? "Save changes" : "Add download"}</SubmitButton>
        <Link
          href="/admin/downloads"
          className="text-[14px] text-ink-3 transition-colors hover:text-ink-2"
        >
          Cancel
        </Link>
      </div>
    </form>
  );
}
