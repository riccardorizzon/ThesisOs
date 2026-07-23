import { apiBaseUrl } from "@/lib/apiBase";

export type CompanionResume = {
  focus_chapter: string;
  focus_section: string;
  focus_section_title: string;
  focus_status: string;
  backlog: string[];
  next_action: string;
  session_notes: string[];
  key_decisions: string[];
  section_text: string | null;
  last_session_summary: string | null;
  work_artifact: string | null;
};

export type CompanionResumePacket = {
  schema_version: string;
  project_id: string;
  title: string;
  author: string;
  institution: string;
  migration_run: string | null;
  progress_summary: string;
  continue_prompt: string;
  focus_chapter_id: string | null;
  resume: CompanionResume;
};

export async function getCompanionResume(
  projectId: string,
): Promise<CompanionResumePacket> {
  const response = await fetch(
    `${apiBaseUrl()}/projects/${encodeURIComponent(projectId)}/companion/resume`,
    { cache: "no-store" },
  );
  if (!response.ok) {
    throw new Error(`companion resume ${response.status}`);
  }
  return response.json();
}
