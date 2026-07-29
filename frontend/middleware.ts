import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Inject shared beta token into same-origin /api/* rewrites (ADR-0048).
 * No-op when BETA_ACCESS_TOKEN unset.
 */
export function middleware(request: NextRequest) {
  const token = process.env.BETA_ACCESS_TOKEN?.trim();
  if (!token || !request.nextUrl.pathname.startsWith("/api/")) {
    return NextResponse.next();
  }
  const headers = new Headers(request.headers);
  headers.set("X-Beta-Token", token);
  return NextResponse.next({ request: { headers } });
}

export const config = {
  matcher: ["/api/:path*"],
};
