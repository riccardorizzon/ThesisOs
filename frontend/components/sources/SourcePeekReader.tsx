"use client";

import { useEffect, useRef } from "react";
import { SourceReader } from "@/components/sources/SourceReader";
import type { CorpusSource } from "@/lib/corpusClient";

export type SourcePeekReaderProps = {
  source: CorpusSource;
  resultIds?: string[];
  chapterId?: string;
  onNavigate?: (sourceId: string) => void;
  onCite?: (source: CorpusSource, quote?: string) => void;
  onDismiss: () => void;
  /** Element to restore focus after dismiss (IR-8). */
  focusReturnRef?: React.RefObject<HTMLElement | null>;
  className?: string;
};

/**
 * Compact peek reader for RightRail Fonte tab — Integration B slot.
 * Esc dismisses; focus returns to editor (IR-8).
 */
export function SourcePeekReader({
  source,
  resultIds,
  chapterId,
  onNavigate,
  onCite,
  onDismiss,
  focusReturnRef,
  className,
}: SourcePeekReaderProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    containerRef.current?.focus();
  }, [source.id]);

  const handleDismiss = () => {
    onDismiss();
    requestAnimationFrame(() => {
      focusReturnRef?.current?.focus();
    });
  };

  return (
    <div
      ref={containerRef}
      tabIndex={-1}
      className={className}
      data-testid="source-peek-reader"
      aria-label="Lettore fonte compatto"
    >
      <SourceReader
        source={source}
        variant="peek"
        resultIds={resultIds}
        chapterId={chapterId}
        onNavigate={onNavigate}
        onCite={onCite}
        onDismiss={handleDismiss}
      />
    </div>
  );
}
