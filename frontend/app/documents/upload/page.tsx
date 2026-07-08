import { redirect } from "next/navigation";

/** @deprecated ADR-0036 — use /sources/upload */
export default function DocumentUploadRedirect() {
  redirect("/sources/upload");
}
