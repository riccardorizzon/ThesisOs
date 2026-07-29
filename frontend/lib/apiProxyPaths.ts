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
  "proposals",
  "export",
] as const;

/**
 * Exact API paths (not prefixes) — avoids clobbering UI routes like /writing/[chapterId].
 * SSE routes (`writing/actions`, `chat`) are handled by App Router Route Handlers
 * (`app/api/.../route.ts`) that stream via `proxySsePost` — do not rely on rewrites for those.
 */
export const API_PROXY_EXACT_PATHS = ["writing/actions"] as const;

/** Paths with dedicated SSE Route Handlers (must not depend on Next rewrite buffering). */
export const SSE_ROUTE_HANDLER_PATHS = ["writing/actions", "chat"] as const;
