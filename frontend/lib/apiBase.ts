/**
 * API base URL — browser uses same-origin paths (nginx or Next rewrites);
 * SSR in Docker uses the internal service URL.
 */
export function resolveApiBase(isBrowser: boolean): string {
  if (isBrowser) {
    return "";
  }
  return (
    process.env.INTERNAL_API_BASE_URL ??
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    "http://localhost:8000"
  );
}

export function apiBaseUrl(): string {
  return resolveApiBase(typeof window !== "undefined");
}
