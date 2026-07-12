/** API path prefixes proxied to the backend (keep in sync with nginx-beta-public.conf). */
export const API_PROXY_PREFIXES = [
  "health",
  "ready",
  "metrics",
  "upload",
  "search",
  "chat",
  "citations",
  "conformance",
  "jobs",
  "projects",
  "documents",
  "memory",
  "chapters",
  "conversations",
  "export",
] as const;

/** Exact API paths (not prefixes) — avoids clobbering UI routes like /writing/[chapterId]. */
export const API_PROXY_EXACT_PATHS = ["writing/actions"] as const;
