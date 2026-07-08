import { redirect } from "next/navigation";

/** @deprecated ADR-0036 — use /sources */
export default function LibraryRedirect() {
  redirect("/sources");
}
