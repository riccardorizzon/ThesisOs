import { redirect } from "next/navigation";

/** @deprecated ADR-0036 — use /knowledge */
export default function MemoryNewRedirect() {
  redirect("/knowledge?view=notes");
}
