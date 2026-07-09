import { apiBaseUrl } from "@/lib/apiBase";
import { getActiveProjectId } from "@/lib/projectPrefs";
const DEFAULT_PROJECT = "thesis-agent";

export type ConversationSummary = {
  id: string;
  project_id: string;
  title: string | null;
  created_at: string;
};

export type ConversationMessage = {
  id: string;
  role: string;
  content: string;
  created_at: string;
};

export type ConversationListResponse = {
  items: ConversationSummary[];
};

export type ConversationMessagesResponse = {
  items: ConversationMessage[];
};

function resolveProjectId(projectId?: string): string {
  if (projectId) return projectId;
  if (typeof window !== "undefined") return getActiveProjectId();
  return DEFAULT_PROJECT;
}

async function parseError(res: Response, action: string): Promise<never> {
  let detail = `${action}: ${res.status}`;
  try {
    const body = (await res.json()) as { message?: string; code?: string };
    if (body.message) detail = body.message;
  } catch {
    /* ignore */
  }
  throw new Error(detail);
}

export async function listConversations(
  projectId?: string
): Promise<ConversationSummary[]> {
  const pid = resolveProjectId(projectId);
  const res = await fetch(
    `${apiBaseUrl()}/conversations?${new URLSearchParams({ project_id: pid })}`,
    { cache: "no-store" }
  );
  if (!res.ok) await parseError(res, "Conversation list failed");
  const body = (await res.json()) as ConversationListResponse;
  return body.items;
}

export async function createConversation(
  options: { projectId?: string; title?: string } = {}
): Promise<ConversationSummary> {
  const pid = resolveProjectId(options.projectId);
  const res = await fetch(`${apiBaseUrl()}/conversations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ project_id: pid, title: options.title ?? null }),
  });
  if (!res.ok) await parseError(res, "Create conversation failed");
  return res.json() as Promise<ConversationSummary>;
}

export async function getConversationMessages(
  conversationId: string
): Promise<ConversationMessage[]> {
  const res = await fetch(`${apiBaseUrl()}/conversations/${conversationId}/messages`, {
    cache: "no-store",
  });
  if (!res.ok) await parseError(res, "Load messages failed");
  const body = (await res.json()) as ConversationMessagesResponse;
  return body.items;
}
