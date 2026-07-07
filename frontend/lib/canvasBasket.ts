import type { CanvasNodeKind } from "@/lib/knowledgeTypes";

export const CANVAS_BASKET_STORAGE_KEY = "thesisos:canvas-basket";
export const CANVAS_BASKET_HANDOFF_KEY = "thesisos:canvas-basket-handoff";

export type CanvasBasketItem = {
  slug: string;
  title: string;
  kind: CanvasNodeKind;
};

function isBrowser(): boolean {
  return typeof window !== "undefined" && typeof sessionStorage !== "undefined";
}

export function loadCanvasBasket(): CanvasBasketItem[] {
  if (!isBrowser()) return [];
  try {
    const raw = sessionStorage.getItem(CANVAS_BASKET_STORAGE_KEY);
    if (raw == null) return [];
    const parsed = JSON.parse(raw) as CanvasBasketItem[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveCanvasBasket(items: readonly CanvasBasketItem[]): void {
  if (!isBrowser()) return;
  sessionStorage.setItem(CANVAS_BASKET_STORAGE_KEY, JSON.stringify(items));
}

export function addToCanvasBasket(
  current: readonly CanvasBasketItem[],
  incoming: readonly CanvasBasketItem[]
): CanvasBasketItem[] {
  const bySlug = new Map(current.map((item) => [item.slug, item]));
  for (const item of incoming) {
    bySlug.set(item.slug, item);
  }
  const next = [...bySlug.values()];
  saveCanvasBasket(next);
  return next;
}

export function removeFromCanvasBasket(
  current: readonly CanvasBasketItem[],
  slug: string
): CanvasBasketItem[] {
  const next = current.filter((item) => item.slug !== slug);
  saveCanvasBasket(next);
  return next;
}

export function clearCanvasBasket(): void {
  if (!isBrowser()) return;
  sessionStorage.removeItem(CANVAS_BASKET_STORAGE_KEY);
}

export function basketItemsFromSlugs(
  graph: { nodes: { slug: string; title: string; kind?: CanvasNodeKind }[] },
  slugs: readonly string[]
): CanvasBasketItem[] {
  const nodeBySlug = new Map(graph.nodes.map((node) => [node.slug, node]));
  return slugs
    .map((slug) => nodeBySlug.get(slug))
    .filter((node): node is NonNullable<typeof node> => node != null)
    .map((node) => ({
      slug: node.slug,
      title: node.title,
      kind: node.kind ?? "concept",
    }));
}

export function stageCanvasBasketHandoff(items: readonly CanvasBasketItem[]): void {
  if (!isBrowser()) return;
  sessionStorage.setItem(CANVAS_BASKET_HANDOFF_KEY, JSON.stringify(items));
}

export function peekCanvasBasketHandoff(): CanvasBasketItem[] | null {
  if (!isBrowser()) return null;
  try {
    const raw = sessionStorage.getItem(CANVAS_BASKET_HANDOFF_KEY);
    if (raw == null) return null;
    const parsed = JSON.parse(raw) as CanvasBasketItem[];
    return Array.isArray(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

export function consumeCanvasBasketHandoff(): CanvasBasketItem[] {
  const items = peekCanvasBasketHandoff() ?? [];
  if (isBrowser()) {
    sessionStorage.removeItem(CANVAS_BASKET_HANDOFF_KEY);
  }
  return items;
}
