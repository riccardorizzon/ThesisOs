/**
 * ADR-0048 — optional shared beta token for public cohort.
 * Empty env → no header (local DX unchanged).
 */
export function apiAuthHeaders(init?: HeadersInit): Headers {
  const headers = new Headers(init);
  const token =
    process.env.BETA_ACCESS_TOKEN?.trim() ||
    process.env.NEXT_PUBLIC_BETA_ACCESS_TOKEN?.trim() ||
    "";
  if (token) {
    headers.set("X-Beta-Token", token);
  }
  return headers;
}
