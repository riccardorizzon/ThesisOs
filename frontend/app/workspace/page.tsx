import { redirect } from "next/navigation";

/** @deprecated ADR-0036 — use /writing */
export default function WorkspaceRedirect() {
  redirect("/writing");
}
