import { redirect } from "next/navigation";

/** /admin has nothing of its own yet; downloads is the only thing to manage. */
export default function AdminIndexPage() {
  redirect("/admin/downloads");
}
