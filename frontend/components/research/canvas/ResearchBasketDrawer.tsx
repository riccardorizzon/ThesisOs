"use client";

import Link from "next/link";

import type { CanvasBasketItem } from "@/lib/canvasBasket";
import { cn } from "@/lib/cn";

export type ResearchBasketDrawerProps = {
  open: boolean;
  items: readonly CanvasBasketItem[];
  onClose: () => void;
  onRemove: (slug: string) => void;
  onHandoff: () => void;
};

/**
 * Session-scoped canvas basket drawer (PX5-EWO-009).
 */
export function ResearchBasketDrawer({
  open,
  items,
  onClose,
  onRemove,
  onHandoff,
}: ResearchBasketDrawerProps) {
  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex justify-end bg-ink/20"
      data-testid="canvas-basket-drawer"
      role="dialog"
      aria-label="Basket canvas"
    >
      <button
        type="button"
        className="absolute inset-0 cursor-pointer"
        aria-label="Chiudi basket"
        onClick={onClose}
      />
      <aside className="relative flex h-full w-full max-w-md flex-col border-l border-border bg-surface shadow-lg">
        <header className="flex items-center justify-between border-b border-border px-4 py-3">
          <h2 className="text-sm font-semibold text-ink">Basket canvas</h2>
          <button
            type="button"
            className="text-sm text-ink-muted hover:text-ink cursor-pointer"
            onClick={onClose}
          >
            Chiudi
          </button>
        </header>

        <ul className="flex-1 overflow-y-auto px-4 py-3">
          {items.length === 0 ? (
            <li className="text-sm text-ink-muted">Nessun elemento nel basket.</li>
          ) : (
            items.map((item) => (
              <li
                key={item.slug}
                className="mb-2 flex items-center justify-between rounded-md border border-border px-3 py-2"
                data-testid={`basket-item-${item.slug}`}
              >
                <div>
                  <p className="text-sm font-medium text-ink">{item.title}</p>
                  <p className="text-xs text-ink-subtle">{item.kind}</p>
                </div>
                <button
                  type="button"
                  className="text-xs text-ink-muted hover:text-ink cursor-pointer"
                  onClick={() => onRemove(item.slug)}
                >
                  Rimuovi
                </button>
              </li>
            ))
          )}
        </ul>

        <footer className="flex flex-col gap-2 border-t border-border px-4 py-3">
          <button
            type="button"
            disabled={items.length === 0}
            className={cn(
              "rounded-md px-3 py-2 text-sm font-medium",
              items.length === 0
                ? "bg-accent/40 text-ink-subtle"
                : "bg-accent text-on-accent cursor-pointer"
            )}
            data-testid="basket-handoff-button"
            onClick={onHandoff}
          >
            Porta in Scrittura
          </button>
          <Link
            href="/research/guided"
            className="text-center text-xs text-accent hover:underline cursor-pointer"
          >
            Salva come trail (guidato)
          </Link>
        </footer>
      </aside>
    </div>
  );
}
