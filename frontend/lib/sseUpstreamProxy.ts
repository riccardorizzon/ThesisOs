/**
 * Server-side SSE proxy — forward POST bodies to the backend and stream the
 * response without buffering (Next rewrites are unsafe for long event-streams).
 *
 * Prefer nginx ingress (`infra/docker/nginx.conf`) for production-like local use;
 * this Route Handler keeps `/api/writing/actions` and `/api/chat` usable on :3000.
 */

import { resolveApiBase } from "@/lib/apiBase";

function upstreamBase(): string {
  // Route Handlers are SSR — never use the browser `/api` base (AP-001).
  return resolveApiBase(false).replace(/\/$/, "");
}

function sseHeaders(upstreamType: string | null): Headers {
  const outHeaders = new Headers();
  outHeaders.set(
    "Content-Type",
    upstreamType ?? "text/event-stream; charset=utf-8"
  );
  outHeaders.set("Cache-Control", "no-cache, no-transform");
  outHeaders.set("Connection", "keep-alive");
  outHeaders.set("X-Accel-Buffering", "no");
  return outHeaders;
}

/** Re-pipe upstream bytes so Next does not collapse an empty passthrough body. */
function repipe(upstreamBody: ReadableStream<Uint8Array>): ReadableStream<Uint8Array> {
  const reader = upstreamBody.getReader();
  return new ReadableStream<Uint8Array>({
    async pull(controller) {
      const { done, value } = await reader.read();
      if (done) {
        controller.close();
        return;
      }
      if (value) controller.enqueue(value);
    },
    cancel(reason) {
      return reader.cancel(reason);
    },
  });
}

export async function proxySsePost(
  request: Request,
  backendPath: string
): Promise<Response> {
  const path = backendPath.replace(/^\//, "");
  const url = `${upstreamBase()}/${path}`;

  const headers = new Headers();
  const contentType = request.headers.get("Content-Type");
  if (contentType) headers.set("Content-Type", contentType);
  const beta =
    request.headers.get("X-Beta-Token")?.trim() ||
    process.env.BETA_ACCESS_TOKEN?.trim() ||
    "";
  if (beta) headers.set("X-Beta-Token", beta);

  const body = await request.text();
  let upstream: Response;
  try {
    upstream = await fetch(url, {
      method: "POST",
      headers,
      body,
      cache: "no-store",
    });
  } catch (err) {
    const message =
      err instanceof Error ? err.message : "upstream fetch failed";
    return Response.json(
      { code: "upstream_unavailable", message },
      { status: 502 }
    );
  }

  if (!upstream.body) {
    return Response.json(
      { code: "empty_upstream", message: "Upstream returned no body" },
      { status: 502 }
    );
  }

  return new Response(repipe(upstream.body), {
    status: upstream.status,
    statusText: upstream.statusText,
    headers: sseHeaders(upstream.headers.get("Content-Type")),
  });
}
