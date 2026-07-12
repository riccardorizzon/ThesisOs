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
