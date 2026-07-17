"use client";

import { getActiveProjectId } from "@/lib/projectPrefs";
import { getWorkspaceMode } from "@/lib/workspacePrefs";

const DEMO_PROJECT_ID = "demo-thesis";

/** Visible banner when the active workspace is the demo project. */
export function DemoBanner() {
  const isDemo =
    getWorkspaceMode() === "demo" || getActiveProjectId() === DEMO_PROJECT_ID;
  if (!isDemo) return null;

  return (
    <div
      className="border-b border-amber-200 bg-amber-50 px-4 py-2 text-center text-xs font-medium text-amber-900"
      data-testid="demo-project-banner"
      role="status"
    >
      Modalità demo — stai esplorando <span className="font-mono">{DEMO_PROJECT_ID}</span>.
      I contenuti dimostrativi non fanno parte della tua tesi.
    </div>
  );
}
