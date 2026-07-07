"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { loadCanvasSavedViews, recentCanvasSavedViews } from "@/lib/canvasSavedViews";

/**
 * Hub "Riprendi" section with saved canvas views (PX5-EWO-010).
 */
export function ResearchResumeSection() {
  const [views, setViews] = useState<ReturnType<typeof recentCanvasSavedViews>>([]);

  useEffect(() => {
    setViews(recentCanvasSavedViews(loadCanvasSavedViews(), 3));
  }, []);

  if (views.length === 0) {
    return (
      <p className="mt-1 text-sm text-ink-muted">
        Nessuna vista salvata — apri la{" "}
        <Link
          href="/research/canvas"
          className="font-medium text-accent hover:underline cursor-pointer"
        >
          mappa concettuale
        </Link>{" "}
        e usa <span className="font-medium">Salva vista</span>.
      </p>
    );
  }

  return (
    <ul className="mt-2 space-y-2" data-testid="research-resume-views">
      {views.map((view) => (
        <li key={view.id}>
          <Link
            href={`/research/canvas?view=${encodeURIComponent(view.id)}`}
            className="text-sm font-medium text-accent hover:underline cursor-pointer"
          >
            Riprendi mappa — {view.name}
          </Link>
        </li>
      ))}
    </ul>
  );
}
