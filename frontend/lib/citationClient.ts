import { apiBaseUrl } from "@/lib/apiBase";
import type { CitationIssue } from "@/lib/citationValidation";

export type CitationValidationResponse = {
  issues: CitationIssue[];
  blocking: boolean;
};

export async function validateProjectCitations(
  projectId: string,
  text: string
): Promise<CitationValidationResponse> {
  const response = await fetch(`${apiBaseUrl()}/citations/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ project_id: projectId, text }),
  });
  const contentType = response.headers.get("content-type") ?? "";
  if (
    !response.ok ||
    !contentType.toLowerCase().includes("application/json")
  ) {
    throw new Error("Verifica citazioni non disponibile. Riprova.");
  }
  try {
    return (await response.json()) as CitationValidationResponse;
  } catch {
    throw new Error("Verifica citazioni non disponibile. Riprova.");
  }
}
