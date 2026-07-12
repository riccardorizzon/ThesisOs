import type { SourceListItem } from "@/lib/sourcesTypes";

const UPLOADED_SUMMARY_PREFIX = "Caricato ·";
const UUID_SLUG =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/** User-uploaded sources are deletable; seed catalog entries are not. */
export function isUserUploadedSource(source: SourceListItem): boolean {
  if (source.deletable) return true;
  if (source.document_id) return true;
  if (source.summary?.startsWith(UPLOADED_SUMMARY_PREFIX)) return true;
  return UUID_SLUG.test(source.slug);
}
