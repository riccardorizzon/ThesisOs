import { redirect } from "next/navigation";

/** @deprecated ADR-0036 — use /knowledge */
export default function MemoryRedirect() {
  redirect("/knowledge");
}
