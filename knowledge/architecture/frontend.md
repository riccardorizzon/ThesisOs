# Frontend Architecture

> Sources: `frontend/**`, M0 plan Task 7, M1 spec §4.2 + plan Tasks 13–16, `plans/builder/STATE.yaml` (P-F).

## Stack

- **Next.js 15** (App Router) + **React 19**.
- **Tailwind CSS** for styling.
- **Zustand** for client state (`lib/store.ts`).
- **TypeScript** (TS only lives in the frontend — ADR-0005).
- API base from `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`).

## Layout (`frontend/`)

```text
app/
  layout.tsx · page.tsx (redirects to /chat) · globals.css
  chat/page.tsx        ← LIVE (M1): streaming chat screen
  library/  memory/  outline/  workspace/  settings/   ← placeholder routes (frozen layout)
components/
  MessageBubble.tsx · InputBox.tsx · ConversationList.tsx   (M1 chat UI)
lib/
  api.ts    ← getHealth() + postChatStream() (SSE client)
  store.ts  ← useChatStore (messages/streaming/error) + useUIStore (activeRoute)
```

(There is also a `components.json` and design tooling pulled in via
`scripts/download-ui-libraries.sh` / `references/` — design-system references, not
runtime code.)

## Chat data flow (M1)

> Source: M1 plan Tasks 13–16.

1. `chat/page.tsx` `send(text)`: optimistically push a `user` message and an empty
   `assistant` message, set `streaming`.
2. `postChatStream({ message, conversation_id? }, onEvent, signal)`:
   `fetch('/chat')` then parse the `ReadableStream` into SSE frames
   (`event:` / `data:` lines, frames split on blank line). `409` → emits an error
   event; non-200/no-body → throws.
3. `onEvent`: `token` → `appendToLastAssistant(delta)`; `done` →
   `setConversationId(...)`; `error` → `setError(...)`; `ping` is ignored.
4. An `AbortController` cancels the stream on unmount/disconnect (M7 review fix in
   STATE).

## State (`lib/store.ts`)

- `useChatStore`: `conversationId`, `messages: ChatMessage[]`, `streaming`,
  `error`, and actions `setConversationId`, `addMessage`, `appendToLastAssistant`,
  `setStreaming`, `setError`.
- `useUIStore`: `activeRoute` (preserved from M0).

## SSE contract consumed (must match backend)

`event: token {text}` · `event: ping {}` · `event: done {conversation_id,
message_id, usage}` · `event: error {code, message}`. See `contracts/api-contracts.md`.

## Conventions / constraints
- Non-chat routes stay **empty placeholders** until their milestone (freezes the
  layout; ADR-0001). `library`→M3, `memory`→M2, `outline`→M8, `workspace`→M6.
- Single conversation in the M1 UI; `ConversationList` is a placeholder.
- Italian-facing copy in M1 components (e.g. "Scrivi un messaggio…", "Invia") —
  the product targets an Italian thesis.

## Known frontend gaps (carried from gates)
- `NEXT_PUBLIC_API_BASE_URL` is **build-time inlined** but
  `docker/frontend.Dockerfile` does not yet declare it as an `ARG`, so prod
  frontend→backend wiring is an M1 follow-up (`docs/m0-runbook.md` §4b).
- End-to-end UI↔backend streaming was verified via `next build` + local smoke;
  full Cloud Run UI wiring is pending with the M1 cloud promotion.
