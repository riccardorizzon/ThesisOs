import { redirect } from "next/navigation";

/** @deprecated ADR-0036 — outline is the Writing left panel */
export default function OutlineRedirect() {
  redirect("/writing");
}
