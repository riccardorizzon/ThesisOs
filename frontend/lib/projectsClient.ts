import { apiBaseUrl } from "@/lib/apiBase";

export type ProjectEntry = {
  id: string;
  display_name: string;
  created_at: string;
  kind?: "demo" | "owned";
};

export async function listProjects(): Promise<ProjectEntry[]> {
  const res = await fetch(`${apiBaseUrl()}/projects`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Projects list failed: ${res.status}`);
  const data = (await res.json()) as { items: ProjectEntry[] };
  return data.items;
}

export async function createProject(displayName: string): Promise<ProjectEntry> {
  const res = await fetch(`${apiBaseUrl()}/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ display_name: displayName }),
  });
  if (!res.ok) throw new Error(`Project create failed: ${res.status}`);
  return res.json() as Promise<ProjectEntry>;
}

export async function renameProject(
  projectId: string,
  displayName: string
): Promise<ProjectEntry> {
  const res = await fetch(
    `${apiBaseUrl()}/projects/${encodeURIComponent(projectId)}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ display_name: displayName }),
    }
  );
  if (!res.ok) throw new Error(`Project rename failed: ${res.status}`);
  return res.json() as Promise<ProjectEntry>;
}

const PROJECT_DELETE_MESSAGES: Readonly<Record<string, string>> = {
  protected_project: "Questa tesi è protetta e non può essere eliminata.",
  project_confirmation_mismatch: "La conferma non corrisponde all’ID della tesi.",
  project_not_found: "La tesi non esiste più.",
};

export async function deleteProject(
  projectId: string,
  confirmationProjectId: string
): Promise<void> {
  const res = await fetch(
    `${apiBaseUrl()}/projects/${encodeURIComponent(projectId)}`,
    {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        confirmation_project_id: confirmationProjectId,
      }),
    }
  );
  if (res.ok) return;

  const body = (await res.json().catch(() => null)) as {
    code?: string;
  } | null;
  const code = body?.code ?? "project_delete_failed";
  throw new Error(
    PROJECT_DELETE_MESSAGES[code] ?? "Eliminazione non riuscita. Riprova."
  );
}
