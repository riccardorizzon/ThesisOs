import { apiAuthHeaders } from "@/lib/apiAuth";
import { apiBaseUrl } from "@/lib/apiBase";
import { getActiveProjectId } from "@/lib/projectPrefs";
import { DEFAULT_PROJECT_ID } from "@/lib/projectContext";

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
  return DEFAULT_PROJECT_ID;
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
    { cache: "no-store", headers: apiAuthHeaders() }
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
    headers: apiAuthHeaders({ "Content-Type": "application/json" }),
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
    headers: apiAuthHeaders(),
  });
  if (!res.ok) await parseError(res, "Load messages failed");
  const body = (await res.json()) as ConversationMessagesResponse;
  return body.items;
}

export async function renameConversation(
  conversationId: string,
  title: string,
  projectId?: string
): Promise<ConversationSummary> {
  const pid = resolveProjectId(projectId);
  const query = new URLSearchParams({ project_id: pid });
  const res = await fetch(
    `${apiBaseUrl()}/conversations/${encodeURIComponent(conversationId)}?${query}`,
    {
      method: "PATCH",
      headers: apiAuthHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({ title }),
    }
  );
  if (!res.ok) await parseError(res, "Rename conversation failed");
  return res.json() as Promise<ConversationSummary>;
}

export async function deleteConversation(
  conversationId: string,
  projectId?: string
): Promise<void> {
  const pid = resolveProjectId(projectId);
  const query = new URLSearchParams({ project_id: pid });
  const res = await fetch(
    `${apiBaseUrl()}/conversations/${encodeURIComponent(conversationId)}?${query}`,
    { method: "DELETE", headers: apiAuthHeaders() }
  );
  if (!res.ok) await parseError(res, "Delete conversation failed");
}
