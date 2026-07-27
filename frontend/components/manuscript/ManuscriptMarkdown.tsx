import type { ReactNode } from "react";
import { cn } from "@/lib/cn";
import { sectionIdFromHeading } from "@/components/writing/MarkdownEditor";

export type ManuscriptMarkdownProps = {
  content: string;
  className?: string;
};

type MarkdownBlock =
  | { type: "heading"; level: number; text: string }
  | { type: "paragraph"; text: string }
  | { type: "list"; items: string[] }
  | { type: "code"; lines: string[] };

const HEADING_CLASS: Record<number, string> = {
  1: "text-2xl font-semibold text-ink scroll-mt-4",
  2: "text-xl font-semibold text-ink scroll-mt-4",
  3: "text-lg font-semibold text-ink scroll-mt-4",
  4: "text-base font-semibold text-ink scroll-mt-4",
  5: "text-sm font-semibold text-ink scroll-mt-4",
  6: "text-sm font-medium text-ink-muted scroll-mt-4",
};

function parseMarkdownBlocks(content: string): MarkdownBlock[] {
  const lines = content.split("\n");
  const blocks: MarkdownBlock[] = [];
  let index = 0;
  let inCode = false;
  let codeLines: string[] = [];

  while (index < lines.length) {
    const line = lines[index]!;

    if (inCode) {
      if (line.trim().startsWith("```")) {
        blocks.push({ type: "code", lines: codeLines });
        codeLines = [];
        inCode = false;
      } else {
        codeLines.push(line);
      }
      index += 1;
      continue;
    }

    if (line.trim().startsWith("```")) {
      inCode = true;
      index += 1;
      continue;
    }

    if (line.trim() === "") {
      index += 1;
      continue;
    }

    const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);
    if (headingMatch) {
      blocks.push({
        type: "heading",
        level: headingMatch[1]!.length,
        text: headingMatch[2]!.trim(),
      });
      index += 1;
      continue;
    }

    const listMatch = line.match(/^[-*]\s+(.+)$/);
    if (listMatch) {
      const items: string[] = [];
      while (index < lines.length) {
        const itemMatch = lines[index]!.match(/^[-*]\s+(.+)$/);
        if (!itemMatch) break;
        items.push(itemMatch[1]!.trim());
        index += 1;
      }
      blocks.push({ type: "list", items });
      continue;
    }

    const paragraphLines: string[] = [];
    while (index < lines.length) {
      const paragraphLine = lines[index]!;
      if (paragraphLine.trim() === "") break;
      if (paragraphLine.trim().startsWith("```")) break;
      if (/^#{1,6}\s+/.test(paragraphLine)) break;
      if (/^[-*]\s+/.test(paragraphLine)) break;
      paragraphLines.push(paragraphLine);
      index += 1;
    }
    blocks.push({ type: "paragraph", text: paragraphLines.join(" ") });
  }

  if (inCode && codeLines.length > 0) {
    blocks.push({ type: "code", lines: codeLines });
  }

  return blocks;
}

function renderHeading(level: number, text: string, key: number): ReactNode {
  const id = sectionIdFromHeading(text);
  const className = HEADING_CLASS[level] ?? HEADING_CLASS[6];
  const children = text;

  switch (level) {
    case 1:
      return (
        <h1 key={key} id={id} className={className}>
          {children}
        </h1>
      );
    case 2:
      return (
        <h2 key={key} id={id} className={className}>
          {children}
        </h2>
      );
    case 3:
      return (
        <h3 key={key} id={id} className={className}>
          {children}
        </h3>
      );
    case 4:
      return (
        <h4 key={key} id={id} className={className}>
          {children}
        </h4>
      );
    case 5:
      return (
        <h5 key={key} id={id} className={className}>
          {children}
        </h5>
      );
    default:
      return (
        <h6 key={key} id={id} className={className}>
          {children}
        </h6>
      );
  }
}

function renderBlock(block: MarkdownBlock, key: number): ReactNode {
  switch (block.type) {
    case "heading":
      return renderHeading(block.level, block.text, key);
    case "paragraph":
      return (
        <p key={key} className="text-base leading-relaxed text-ink">
          {block.text}
        </p>
      );
    case "list":
      return (
        <ul key={key} className="list-disc space-y-1 pl-5 text-base text-ink">
          {block.items.map((item, itemIndex) => (
            <li key={itemIndex}>{item}</li>
          ))}
        </ul>
      );
    case "code":
      return (
        <pre
          key={key}
          className="overflow-x-auto rounded-md bg-surface-muted px-3 py-2 font-mono text-sm text-ink"
        >
          <code>{block.lines.join("\n")}</code>
        </pre>
      );
    default:
      return null;
  }
}

/** Read-only markdown view for Manoscritto — headings, paragraphs, lists, code fences. */
export function ManuscriptMarkdown({ content, className }: ManuscriptMarkdownProps) {
  const blocks = parseMarkdownBlocks(content);

  return (
    <div
      data-testid="manuscript-markdown"
      className={cn("space-y-4 text-ink", className)}
    >
      {blocks.map((block, index) => renderBlock(block, index))}
    </div>
  );
}
