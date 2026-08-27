import type { Metadata } from "next";

import { DownloadForm } from "../download-form";

export const metadata: Metadata = {
  title: "Add a download",
};

export default function NewDownloadPage() {
  return (
    <>
      <h2 className="mb-6 font-display text-xl font-semibold tracking-tight">Add a download</h2>
      <DownloadForm />
    </>
  );
}
