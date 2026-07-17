import { DEFAULT_PROJECT_ID } from "@/lib/projectContext";
import { getActiveProjectId } from "@/lib/projectPrefs";
import {
  proposalClient,
  type ProposalApiRecord,
  type ProposalCreateBody,
} from "@/lib/proposalClient";

export type ProposalStatus = "pending" | "approved" | "rejected";

export type WritingProposal = {
  id: string;
  actionId: string;
  actionLabel: string;
  chapterId: string;
  selectionText: string | null;
  selectionAnchor: string | null;
  preview: string;
  status: ProposalStatus;
  createdAt: string;
};

const ACTION_LABELS: Record<string, string> = {
  rewrite: "Riscrivi",
  verify: "Verifica",
  expand: "Espandi",
  "find-sources": "Trova fonti",
};

const cache: WritingProposal[] = [];
let refreshPromise: Promise<WritingProposal[]> | null = null;

function nextOptimisticId(): string {
  return `prop-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function apiStatusToLocal(status: ProposalApiRecord["status"]): ProposalStatus {
  if (status === "accepted") return "approved";
  return status;
}

function readMetadata(record: ProposalApiRecord): Record<string, unknown> {
  const raw = (record as ProposalApiRecord & { metadata?: Record<string, unknown> }).metadata;
  return raw && typeof raw === "object" ? raw : {};
}

export function mapApiProposal(record: ProposalApiRecord): WritingProposal {
  const metadata = readMetadata(record);
  const actionLabel =
    typeof metadata.action_label === "string"
      ? metadata.action_label
      : ACTION_LABELS[record.action] ?? record.action;

  return {
    id: record.id,
    actionId: record.action,
    actionLabel,
    chapterId: record.chapter_id,
    selectionText:
      typeof metadata.selection_text === "string"
        ? metadata.selection_text
        : record.original || null,
    selectionAnchor:
      typeof metadata.selection_anchor === "string" ? metadata.selection_anchor : null,
    preview: record.proposed,
    status: apiStatusToLocal(record.status),
    createdAt: record.created_at,
  };
}

export function mapWritingProposalToCreate(
  input: Omit<WritingProposal, "id" | "status" | "createdAt">,
  projectId: string = typeof window !== "undefined" ? getActiveProjectId() : DEFAULT_PROJECT_ID
): ProposalCreateBody {
  return {
    project_id: projectId,
    chapter_id: input.chapterId,
    original: input.selectionText?.trim() || input.preview.trim(),
    proposed: input.preview.trim(),
    action: input.actionId,
    metadata: {
      action_label: input.actionLabel,
      selection_text: input.selectionText,
      selection_anchor: input.selectionAnchor,
    },
  };
}

function replaceCache(items: WritingProposal[]): void {
  cache.length = 0;
  cache.push(...items);
}

function upsertCache(proposal: WritingProposal): void {
  const index = cache.findIndex((p) => p.id === proposal.id);
  if (index >= 0) cache[index] = proposal;
  else cache.push(proposal);
}

function removeFromCache(id: string): void {
  const index = cache.findIndex((p) => p.id === id);
  if (index >= 0) cache.splice(index, 1);
}

/** Load pending proposals from API into the local cache. */
export async function refreshProposalsFromApi(
  params: { projectId?: string; chapterId?: string } = {}
): Promise<WritingProposal[]> {
  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    const { items } = await proposalClient.list({
      project_id: params.projectId ?? (typeof window !== "undefined" ? getActiveProjectId() : DEFAULT_PROJECT_ID),
      chapter_id: params.chapterId,
    });
    const mapped = items.map(mapApiProposal).filter((p) => p.status === "pending");
    replaceCache(mapped);
    return mapped;
  })();

  try {
    return await refreshPromise;
  } finally {
    refreshPromise = null;
  }
}

export function getPendingProposals(): WritingProposal[] {
  return cache.filter((p) => p.status === "pending");
}

export function getPendingProposalCount(): number {
  return getPendingProposals().length;
}

export function addProposal(
  input: Omit<WritingProposal, "id" | "status" | "createdAt">
): WritingProposal {
  const optimistic: WritingProposal = {
    ...input,
    id: nextOptimisticId(),
    status: "pending",
    createdAt: new Date().toISOString(),
  };
  cache.push(optimistic);

  void proposalClient
    .create(mapWritingProposalToCreate(input, getActiveProjectId()))
    .then((record) => {
      removeFromCache(optimistic.id);
      upsertCache(mapApiProposal(record));
    })
    .catch(() => {
      removeFromCache(optimistic.id);
    });

  return optimistic;
}

/** Test helper — clears local proposal cache */
export function _resetProposalQueueForTests(): void {
  cache.length = 0;
  refreshPromise = null;
}

/** Test helper — seed cache without API */
export function _seedProposalQueueForTests(proposals: WritingProposal[]): void {
  replaceCache(proposals);
}

/** Alias for sessionState integration */
export function listPendingProposals(): WritingProposal[] {
  return getPendingProposals();
}

export function clearPendingProposals(): void {
  for (const p of cache) {
    if (p.status === "pending") p.status = "rejected";
  }
  cache.length = 0;
}

export function getPendingProposalsForChapter(chapterId: string): WritingProposal[] {
  return cache.filter((p) => p.status === "pending" && p.chapterId === chapterId);
}

export function getProposalById(id: string): WritingProposal | undefined {
  return cache.find((p) => p.id === id);
}

export async function approveProposal(id: string): Promise<WritingProposal | undefined> {
  const proposal = cache.find((p) => p.id === id);
  if (!proposal || proposal.status !== "pending") return proposal;

  await proposalClient.accept(id);
  proposal.status = "approved";
  return proposal;
}

export async function rejectProposal(
  id: string,
  reason?: string
): Promise<WritingProposal | undefined> {
  const proposal = cache.find((p) => p.id === id);
  if (!proposal || proposal.status !== "pending") return proposal;

  await proposalClient.reject(id, reason ? { reason } : {});
  proposal.status = "rejected";
  return proposal;
}

/** Chapters with at least one pending proposal. */
export function listChaptersWithPendingProposals(): string[] {
  const ids = new Set<string>();
  for (const p of cache) {
    if (p.status === "pending") ids.add(p.chapterId);
  }
  return [...ids];
}
