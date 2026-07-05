"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/cn";

export type OfflineBannerProps = {
  className?: string;
};

/**
 * Fixed top banner when navigator.onLine is false (spec §19).
 * Layer: Business (Product Plane)
 */
export function OfflineBanner({ className }: OfflineBannerProps) {
  const [offline, setOffline] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    const update = () => {
      setOffline(!navigator.onLine);
      if (navigator.onLine) setDismissed(false);
    };
    update();
    window.addEventListener("online", update);
    window.addEventListener("offline", update);
    return () => {
      window.removeEventListener("online", update);
      window.removeEventListener("offline", update);
    };
  }, []);

  if (!offline || dismissed) return null;

  return (
    <div
      role="status"
      className={cn(
        "fixed inset-x-0 top-0 z-[55] flex items-center justify-center gap-3",
        "border-b border-warning/30 bg-warning/10 px-4 py-2 text-sm text-ink",
        className
      )}
      data-testid="offline-banner"
    >
      <span>Sei offline — modifiche salvate localmente</span>
      <button
        type="button"
        onClick={() => setDismissed(true)}
        className="rounded-md px-2 py-0.5 text-xs font-medium text-ink-muted transition-colors duration-200 hover:bg-surface-muted hover:text-ink"
        aria-label="Chiudi avviso offline"
      >
        Chiudi
      </button>
    </div>
  );
}
