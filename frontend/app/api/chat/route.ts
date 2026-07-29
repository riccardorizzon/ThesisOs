import { proxySsePost } from "@/lib/sseUpstreamProxy";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** Stream /chat SSE; do not use Next rewrites (they buffer/close SSE). */
export async function POST(request: Request): Promise<Response> {
  return proxySsePost(request, "chat");
}
