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

const queue: WritingProposal[] = [];

function nextId(): string {
  return `prop-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function getPendingProposals(): WritingProposal[] {
  return queue.filter((p) => p.status === "pending");
}

export function getPendingProposalCount(): number {
  return getPendingProposals().length;
}

export function addProposal(
  input: Omit<WritingProposal, "id" | "status" | "createdAt">
): WritingProposal {
  const proposal: WritingProposal = {
    ...input,
    id: nextId(),
    status: "pending",
    createdAt: new Date().toISOString(),
  };
  queue.push(proposal);
  return proposal;
}

/** Test helper — clears in-memory queue */
export function _resetProposalQueueForTests(): void {
  queue.length = 0;
}

/** Alias for sessionState integration */
export function listPendingProposals(): WritingProposal[] {
  return getPendingProposals();
}

export function clearPendingProposals(): void {
  for (const p of queue) {
    if (p.status === "pending") p.status = "rejected";
  }
  queue.length = 0;
}

export function getPendingProposalsForChapter(chapterId: string): WritingProposal[] {
  return queue.filter((p) => p.status === "pending" && p.chapterId === chapterId);
}

export function getProposalById(id: string): WritingProposal | undefined {
  return queue.find((p) => p.id === id);
}

export function approveProposal(id: string): WritingProposal | undefined {
  const proposal = queue.find((p) => p.id === id);
  if (proposal && proposal.status === "pending") {
    proposal.status = "approved";
  }
  return proposal;
}

export function rejectProposal(id: string): WritingProposal | undefined {
  const proposal = queue.find((p) => p.id === id);
  if (proposal && proposal.status === "pending") {
    proposal.status = "rejected";
  }
  return proposal;
}

/** Chapters with at least one pending proposal. */
export function listChaptersWithPendingProposals(): string[] {
  const ids = new Set<string>();
  for (const p of queue) {
    if (p.status === "pending") ids.add(p.chapterId);
  }
  return [...ids];
}
