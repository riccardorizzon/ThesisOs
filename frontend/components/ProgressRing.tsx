import { cn } from "@/lib/cn";

export type ProgressRingProps = {
  /** Progress 0–100 (deterministic — ADR-0040 INV-PS-1) */
  value: number;
  size?: number;
  strokeWidth?: number;
  label?: string;
  sublabel?: string;
  className?: string;
};

function clamp(value: number): number {
  return Math.min(100, Math.max(0, value));
}

/**
 * Circular progress indicator for Home — ADR-0040 progress_pct surface.
 * Layer: Business (Product Plane)
 */
export function ProgressRing({
  value,
  size = 120,
  strokeWidth = 8,
  label,
  sublabel,
  className,
}: ProgressRingProps) {
  const pct = clamp(value);
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (pct / 100) * circumference;
  const center = size / 2;

  return (
    <div
      className={cn("inline-flex flex-col items-center gap-2", className)}
      role="group"
      aria-label={label ?? "Progress"}
    >
      <div className="relative" style={{ width: size, height: size }}>
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          aria-hidden="true"
          className="-rotate-90"
        >
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="rgb(var(--color-border))"
            strokeWidth={strokeWidth}
          />
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="rgb(var(--color-accent-ring))"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-[stroke-dashoffset] duration-500 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="text-2xl font-semibold tabular-nums text-ink"
            aria-hidden="true"
          >
            {Math.round(pct)}%
          </span>
        </div>
        <span className="sr-only">{Math.round(pct)} percent complete</span>
      </div>
      {label != null && (
        <span className="text-sm font-medium text-ink">{label}</span>
      )}
      {sublabel != null && (
        <span className="text-xs text-ink-muted">{sublabel}</span>
      )}
    </div>
  );
}
