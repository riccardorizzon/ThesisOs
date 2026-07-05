import {
  LIBRARY_SOURCES,
  getSourceById,
  type LibrarySource,
  type SourceStatus,
} from "@/lib/libraryStub";

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type CorpusSource = LibrarySource & {
  body: string;
  year?: string;
  exclusionReason?: string;
};

export const LINKED_SOURCES_CHANGED = "thesisos:linked-sources-changed";

const RECENT_KEY = "thesisos:recent-sources";
const LINKED_KEY = "thesisos:chapter-linked-sources";
const MAX_RECENT = 10;

const SOURCE_BODIES: Record<
  string,
  { body: string; exclusionReason?: string }
> = {
  "benjamin-opera-arte": {
    body:
      "L'opera d'arte nell'epoca della sua riproducibilità tecnica perde la sua presenza unica nel tempo e nello spazio. Questa presenza unica del suo esistere nel luogo in cui si trova è ciò che si chiama aura dell'opera d'arte.",
  },
  "barthes-mythologies": {
    body:
      "Il mito è un sistema di comunicazione, un messaggio. Il mito borghese naturalizza il significato ideologico, presentandolo come naturale e eterno.",
    exclusionReason:
      "Esclusa da CORPUS-02/03 — Mythologies non appartiene al corpus attivo della tesi.",
  },
  "albers-interaction-color": {
    body:
      "In visual perception a color is almost never seen as it really is — as it physically is. This fact makes color the most relative medium in art.",
  },
  "csikszentmihalyi-flow": {
    body:
      "Flow is the state in which people are so involved in an activity that nothing else seems to matter; the experience itself is so enjoyable that people will do it even at great cost.",
  },
  "hollander-sex-suits": {
    body:
      "Clothes make visible the invisible social and psychological forces that shape the self. Fashion is not mere ornament but a sign system embedded in culture.",
  },
};

function parseYear(meta?: string): string | undefined {
  const match = meta?.match(/\b(19|20)\d{2}\b/);
  return match?.[0];
}

function toCorpusSource(source: LibrarySource): CorpusSource {
  const extra = SOURCE_BODIES[source.id];
  return {
    ...source,
    body: extra?.body ?? "Estratto non disponibile — contenuto completo in PX-3.",
    year: parseYear(source.meta),
    exclusionReason: extra?.exclusionReason,
  };
}

function readJson<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function writeJson(key: string, value: unknown): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(key, JSON.stringify(value));
}

function dispatchLinkedChanged(): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent(LINKED_SOURCES_CHANGED));
}

type LinkedMap = Record<string, string[]>;

function readLinkedMap(): LinkedMap {
  return readJson<LinkedMap>(LINKED_KEY, {});
}

function writeLinkedMap(map: LinkedMap): void {
  writeJson(LINKED_KEY, map);
  dispatchLinkedChanged();
}

export const corpusClient = {
  list(): CorpusSource[] {
    return LIBRARY_SOURCES.map(toCorpusSource);
  },

  getById(id: string): CorpusSource | undefined {
    const source = getSourceById(id);
    return source ? toCorpusSource(source) : undefined;
  },

  /** Search corpus — excluded sources omitted unless includeExcluded (IR-4). */
  search(query: string, options?: { includeExcluded?: boolean }): CorpusSource[] {
    const q = query.trim().toLowerCase();
    let results = this.list();
    if (!options?.includeExcluded) {
      results = results.filter((s) => s.status !== "esclusa");
    }
    if (!q) return results;
    return results.filter((s) => {
      const haystack = [s.title, s.subtitle, s.meta, s.year]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return haystack.includes(q);
    });
  },

  async searchRemote(query: string, limit = 12): Promise<CorpusSource[]> {
    const q = query.trim();
    if (!q) return [];
    try {
      const r = await fetch(`${BASE}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q, limit }),
        cache: "no-store",
      });
      if (!r.ok) return this.search(q);
      const data = (await r.json()) as {
        results?: Array<{ document_title?: string; content?: string }>;
      };
      const titles = new Set(
        (data.results ?? [])
          .map((item) => item.document_title?.toLowerCase())
          .filter(Boolean)
      );
      if (titles.size === 0) return this.search(q);
      return this.search(q).filter((s) =>
        titles.has(s.title.toLowerCase()) ||
        titles.has(s.subtitle?.toLowerCase() ?? "")
      );
    } catch {
      return this.search(q);
    }
  },

  getRecent(limit = MAX_RECENT): CorpusSource[] {
    const ids = readJson<string[]>(RECENT_KEY, []);
    return ids
      .slice(0, limit)
      .map((id) => this.getById(id))
      .filter((s): s is CorpusSource => s != null);
  },

  recordRecent(sourceId: string): void {
    const ids = readJson<string[]>(RECENT_KEY, []);
    const next = [sourceId, ...ids.filter((id) => id !== sourceId)].slice(
      0,
      MAX_RECENT
    );
    writeJson(RECENT_KEY, next);
  },

  getLinkedToChapter(chapterId: string): CorpusSource[] {
    const map = readLinkedMap();
    return (map[chapterId] ?? [])
      .map((id) => this.getById(id))
      .filter((s): s is CorpusSource => s != null);
  },

  getLinkedCount(chapterId: string): number {
    const map = readLinkedMap();
    return map[chapterId]?.length ?? 0;
  },

  linkToChapter(chapterId: string, sourceId: string): void {
    const map = readLinkedMap();
    const current = map[chapterId] ?? [];
    if (current.includes(sourceId)) return;
    map[chapterId] = [...current, sourceId];
    writeLinkedMap(map);
    this.recordRecent(sourceId);
  },

  unlinkFromChapter(chapterId: string, sourceId: string): void {
    const map = readLinkedMap();
    map[chapterId] = (map[chapterId] ?? []).filter((id) => id !== sourceId);
    writeLinkedMap(map);
  },

  isLinkedToChapter(chapterId: string, sourceId: string): boolean {
    const map = readLinkedMap();
    return (map[chapterId] ?? []).includes(sourceId);
  },
};
