import { redirect } from "next/navigation";

/** @deprecated ADR-0036 — use /ai */
export default function ChatRedirect() {
  redirect("/ai");
}
