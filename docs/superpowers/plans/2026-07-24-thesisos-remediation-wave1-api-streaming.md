# ThesisOS Remediation Wave 1 — API and Streaming Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove browser API/UI route collisions and make every streaming failure visible, cancellable, and testable.

**Architecture:** Browser requests use the dedicated `/api` namespace. Next.js and nginx strip that prefix before forwarding to FastAPI, while direct backend paths remain compatible. A shared SSE response guard validates status, content type, frame completion, and cancellation for chat and writing actions.

**Tech Stack:** Next.js 15, React 19, TypeScript, Vitest, nginx, Playwright, FastAPI SSE.

## Global Constraints

- Product Plane only; do not modify Engineering Runtime or governance.
- Preserve direct FastAPI routes.
- No raw parsing or transport errors in user-visible copy.
- No production code before its regression test fails.
- Do not create git commits unless the user explicitly requests them.

---

### Task 1: Dedicated browser API namespace

**Files:**
- Modify: `frontend/lib/apiBase.ts`
- Modify: `frontend/lib/apiBase.test.ts`
- Modify: `frontend/next.config.ts`
- Modify: `frontend/lib/apiProxyPaths.test.ts`
- Modify: `infra/dev-vm/nginx-beta-public.conf`
- Create: `tests/e2e/api-boundary.spec.ts`

**Interfaces:**
- Produces: `resolveApiBase(true) === "/api"`.
- Produces: Next rewrite `/api/<path>` → backend `/<path>`.
- Preserves: SSR `resolveApiBase(false)` behavior.

- [ ] **Step 1: Write failing unit tests for the browser base and rewrite contract**

Add assertions:

```ts
expect(resolveApiBase(true)).toBe("/api");
expect(resolveApiBase(false)).toBe("http://backend:8000");
```

Export a pure `buildApiRewrites(upstream: string)` helper from `next.config.ts` (or a focused `frontend/lib/apiRewrites.ts`) and assert:

```ts
expect(buildApiRewrites("http://backend:8000")).toContainEqual({
  source: "/api/chat",
  destination: "http://backend:8000/chat",
});
expect(buildApiRewrites("http://backend:8000")).toContainEqual({
  source: "/api/documents/:path*",
  destination: "http://backend:8000/documents/:path*",
});
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
cd frontend
npm test -- lib/apiBase.test.ts lib/apiProxyPaths.test.ts
```

Expected: FAIL because the browser base is currently empty and rewrites omit `/api`.

- [ ] **Step 3: Implement `/api` browser base and prefix-stripping rewrites**

Use:

```ts
export function resolveApiBase(isBrowser: boolean): string {
  if (isBrowser) return "/api";
  return (
    process.env.INTERNAL_API_BASE_URL ??
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    "http://localhost:8000"
  );
}
```

Generate exact and prefix rewrites with `/api` only on the source side.

- [ ] **Step 4: Add nginx `/api/` ingress**

Add a `location ^~ /api/` block before the direct API regex:

```nginx
location ^~ /api/ {
    rewrite ^/api/(.*)$ /$1 break;
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 300s;
}
```

Retain the existing direct backend-path location for backwards compatibility.

- [ ] **Step 5: Add Playwright route-collision regression**

Assert:

```ts
expect((await request.get("/chat", { maxRedirects: 0 })).status()).toBe(307);
expect((await request.get("/api/documents?project_id=thesis-agent")).headers()["content-type"])
  .toContain("application/json");
```

For chat, post a deliberately invalid body to `/api/chat` and require FastAPI JSON 422 rather than redirect/405. Do not spend an LLM call in this boundary test.

- [ ] **Step 6: Run unit and E2E boundary tests GREEN**

Run:

```bash
cd frontend && npm test -- lib/apiBase.test.ts lib/apiProxyPaths.test.ts
cd ../tests/e2e && npx playwright test api-boundary.spec.ts
```

Expected: PASS; no 307 beneath `/api`.

### Task 2: Shared defensive SSE transport

**Files:**
- Create: `frontend/lib/sseClient.ts`
- Create: `frontend/lib/sseClient.test.ts`
- Modify: `frontend/lib/api.ts`
- Modify: `frontend/lib/aiActions.ts`

**Interfaces:**
- Produces:

```ts
export type SseFrame = { event: string; data: unknown };
export async function consumeSse(
  response: Response,
  onFrame: (frame: SseFrame) => void,
): Promise<void>;
export async function requireSseResponse(
  response: Response,
  labels: Record<number, string>,
): Promise<Response>;
```

- [ ] **Step 1: Write failing transport tests**

Cover:

```ts
it("rejects a 405 HTML response before parsing");
it("rejects a 200 response without text/event-stream");
it("parses CRLF and LF frames");
it("rejects a stream ending without done or error");
it("does not convert AbortError into a transport error");
```

Use real `Response` and `ReadableStream` objects. The 405 assertion must expect the stable Italian message, not HTML.

- [ ] **Step 2: Run test and verify RED**

Run:

```bash
cd frontend && npm test -- lib/sseClient.test.ts
```

Expected: FAIL because `sseClient.ts` does not exist.

- [ ] **Step 3: Implement minimal transport**

`requireSseResponse`:

```ts
if (!response.ok) {
  throw new SseHttpError(response.status, labels[response.status] ?? "Servizio non disponibile. Riprova.");
}
const contentType = response.headers.get("content-type") ?? "";
if (!contentType.toLowerCase().includes("text/event-stream")) {
  throw new SseProtocolError("Risposta del servizio non valida. Riprova.");
}
return response;
```

`consumeSse` tracks terminal frames:

```ts
let terminal = false;
// parse frames; terminal = true for done/error
if (!terminal) throw new SseProtocolError("Risposta interrotta. Riprova.");
```

- [ ] **Step 4: Refactor chat and writing action clients**

Both clients must:

1. fetch;
2. call `requireSseResponse`;
3. call `consumeSse`;
4. map typed events;
5. preserve `AbortError`.

Known chat labels:

```ts
{
  409: "È già in corso una risposta in questa conversazione.",
  422: "Il messaggio non è valido o è troppo lungo.",
  503: "L’assistente non è configurato.",
}
```

- [ ] **Step 5: Run focused tests GREEN**

Run:

```bash
cd frontend
npm test -- lib/sseClient.test.ts lib/aiActions.test.ts
```

Expected: PASS.

### Task 3: Chat error, progress, and cancellation UX

**Files:**
- Modify: `frontend/components/AiChatView.tsx`
- Modify: `frontend/components/InputBox.tsx`
- Modify: `frontend/components/AiChatView.test.tsx`
- Create: `frontend/components/InputBox.test.tsx`

**Interfaces:**
- `InputBox` receives optional `streaming` and `onCancel`.
- `AiChatView` removes an empty optimistic assistant bubble on failure.

- [ ] **Step 1: Write failing component tests**

Add tests that:

- a transport rejection renders “Servizio non disponibile. Riprova.”;
- the empty assistant bubble is removed after rejection;
- streaming renders “Generazione in corso” and an “Interrompi” button;
- clicking “Interrompi” calls `AbortController.abort()`;
- the input enforces `maxLength={32000}` and shows a character-limit message.

- [ ] **Step 2: Run test and verify RED**

Run:

```bash
cd frontend && npm test -- components/AiChatView.test.tsx components/InputBox.test.tsx
```

Expected: FAIL on missing cancellation/error behavior.

- [ ] **Step 3: Implement minimal UX**

Expose:

```tsx
{streaming ? (
  <button type="button" onClick={() => abortRef.current?.abort()}>
    Interrompi
  </button>
) : null}
```

On failure:

```ts
setMessages((current) => {
  const last = current.at(-1);
  return last?.role === "assistant" && !last.content ? current.slice(0, -1) : current;
});
```

Keep cancellation non-error and preserve the user message.

- [ ] **Step 4: Run component tests GREEN**

Run the command from Step 2. Expected: PASS.

### Task 4: Document/memory status and product-safe errors

**Files:**
- Modify: `frontend/lib/documentClient.ts`
- Modify: `frontend/lib/documentClient.test.ts`
- Modify: `frontend/lib/memoryClient.ts`
- Modify: `frontend/lib/memoryClient.test.ts`
- Modify: `frontend/components/writing/DocumentIndexStatusBanner.tsx`
- Modify: `frontend/components/writing/DocumentIndexStatusBanner.test.tsx`

**Interfaces:**
- `DocumentStatus` includes historical `parsed` and canonical `indexed`.
- Client parse failures become typed product errors.

- [ ] **Step 1: Write failing tests**

Assert:

- HTML returned with status 200 becomes `DocumentApiError(code="invalid_response")`;
- `indexed` renders “Indicizzato” and is terminal;
- no banner contains `Unexpected token`, `DOCTYPE`, or parser exception text;
- memory client uses the `/api/memory` browser base through `apiBaseUrl`.

- [ ] **Step 2: Run focused tests RED**

```bash
cd frontend
npm test -- lib/documentClient.test.ts lib/memoryClient.test.ts components/writing/DocumentIndexStatusBanner.test.tsx
```

- [ ] **Step 3: Implement typed response parsing**

Before JSON parsing, require an `application/json` content type. Map any mismatch to:

```ts
new DocumentApiError(
  response.status,
  "invalid_response",
  "Impossibile leggere lo stato del documento. Riprova.",
);
```

Do the equivalent for memory.

- [ ] **Step 4: Run focused tests GREEN**

Run the command from Step 2. Expected: PASS.

### Task 5: Wave 1 integration gate

**Files:**
- Modify only if a regression is found in the files above.

- [ ] **Step 1: Run frontend quality gates**

```bash
cd frontend
npm test
npx tsc --noEmit
npm run build
```

- [ ] **Step 2: Rebuild local frontend and backend**

```bash
docker compose up --build -d
curl --fail localhost:8000/health
curl --fail localhost:3000/api/health
```

- [ ] **Step 3: Run browser smoke**

```bash
cd tests/e2e
npx playwright test api-boundary.spec.ts px1-ui-smoke.spec.ts
```

Require:

- chat POST reaches `/api/chat`;
- no POST `/ai`;
- Writing has no JSON parse banner;
- document and memory responses are JSON;
- cancellation produces no uncaught console error.

- [ ] **Step 4: Inspect repository state**

```bash
git diff --check
git status --short
```

Do not commit. Proceed to Wave 2 only when all Wave 1 evidence is green.
