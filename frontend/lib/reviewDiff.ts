/**
 * Paragraph-level diff for Review workspace — PX2-EWO-007.
 * Layer: Business (Product Plane)
 */

export type ParagraphHunkStatus = "unchanged" | "modified" | "added" | "removed";

export type ParagraphHunk = {
  id: string;
  index: number;
  status: ParagraphHunkStatus;
  original: string | null;
  proposed: string | null;
};

export type ProposalContentInput = {
  selectionText: string | null;
  preview: string;
};

/** Split markdown-ish text into paragraph blocks (blank-line separated). */
export function splitParagraphs(text: string): string[] {
  if (!text.trim()) return [];
  return text
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter(Boolean);
}

/** Join paragraphs back into chapter content. */
export function joinParagraphs(paragraphs: string[]): string {
  return paragraphs.join("\n\n");
}

/**
 * Apply a writing proposal to original chapter content.
 * When selectionText matches, replaces that span; otherwise treats preview as full draft.
 */
export function applyProposalToContent(
  original: string,
  proposal: ProposalContentInput
): string {
  const trimmedPreview = proposal.preview.trim();
  if (!trimmedPreview) return original;

  const selection = proposal.selectionText?.trim();
  if (selection && original.includes(selection)) {
    return original.replace(selection, trimmedPreview);
  }

  return trimmedPreview;
}

function hunkId(index: number, status: ParagraphHunkStatus): string {
  return `hunk-${index}-${status}`;
}

/**
 * Compute paragraph-level hunks between original and proposed content.
 * Uses a simple LCS alignment on paragraph arrays.
 */
export function computeParagraphDiff(original: string, proposed: string): ParagraphHunk[] {
  const left = splitParagraphs(original);
  const right = splitParagraphs(proposed);
  const ops = alignParagraphs(left, right);
  const hunks: ParagraphHunk[] = [];
  let index = 0;

  for (const op of ops) {
    if (op.type === "equal") {
      hunks.push({
        id: hunkId(index, "unchanged"),
        index,
        status: "unchanged",
        original: op.left,
        proposed: op.right,
      });
    } else if (op.type === "replace") {
      hunks.push({
        id: hunkId(index, "modified"),
        index,
        status: "modified",
        original: op.left,
        proposed: op.right,
      });
    } else if (op.type === "delete") {
      hunks.push({
        id: hunkId(index, "removed"),
        index,
        status: "removed",
        original: op.left,
        proposed: null,
      });
    } else {
      hunks.push({
        id: hunkId(index, "added"),
        index,
        status: "added",
        original: null,
        proposed: op.right,
      });
    }
    index += 1;
  }

  return hunks;
}

type AlignOp =
  | { type: "equal"; left: string; right: string }
  | { type: "replace"; left: string; right: string }
  | { type: "delete"; left: string }
  | { type: "insert"; right: string };

function alignParagraphs(left: string[], right: string[]): AlignOp[] {
  const m = left.length;
  const n = right.length;
  const dp: number[][] = Array.from({ length: m + 1 }, () =>
    Array<number>(n + 1).fill(0)
  );

  for (let i = 1; i <= m; i += 1) {
    for (let j = 1; j <= n; j += 1) {
      if (left[i - 1] === right[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1] + 1;
      } else {
        dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
      }
    }
  }

  const raw: AlignOp[] = [];
  let i = m;
  let j = n;

  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && left[i - 1] === right[j - 1]) {
      raw.unshift({ type: "equal", left: left[i - 1], right: right[j - 1] });
      i -= 1;
      j -= 1;
    } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
      raw.unshift({ type: "insert", right: right[j - 1] });
      j -= 1;
    } else {
      raw.unshift({ type: "delete", left: left[i - 1] });
      i -= 1;
    }
  }

  const merged: AlignOp[] = [];
  for (let k = 0; k < raw.length; k += 1) {
    const cur = raw[k];
    const next = raw[k + 1];
    if (cur.type === "delete" && next?.type === "insert") {
      merged.push({ type: "replace", left: cur.left, right: next.right });
      k += 1;
    } else {
      merged.push(cur);
    }
  }

  return merged;
}

/** Hunks that the operator can accept individually. */
export function selectableHunks(hunks: ParagraphHunk[]): ParagraphHunk[] {
  return hunks.filter((h) => h.status !== "unchanged");
}

/**
 * Merge accepted hunks into final chapter content.
 * Accepted modified/added hunks take proposed text; rejected keep original.
 */
export function mergeAcceptedHunks(
  hunks: ParagraphHunk[],
  acceptedIds: ReadonlySet<string>
): string {
  const paragraphs: string[] = [];

  for (const hunk of hunks) {
    if (hunk.status === "unchanged") {
      paragraphs.push(hunk.original ?? hunk.proposed ?? "");
      continue;
    }

    const accepted = acceptedIds.has(hunk.id);
    if (accepted) {
      if (hunk.proposed) paragraphs.push(hunk.proposed);
    } else if (hunk.status !== "added" && hunk.original) {
      paragraphs.push(hunk.original);
    }
  }

  return joinParagraphs(paragraphs);
}

/** All change hunks selected — equivalent to full accept. */
export function allChangeHunkIds(hunks: ParagraphHunk[]): Set<string> {
  return new Set(selectableHunks(hunks).map((h) => h.id));
}
