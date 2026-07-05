import Link from "next/link";
import { cn } from "@/lib/cn";

export type ModuleStubProps = {
  title: string;
  description: string;
  milestone: string;
  children?: React.ReactNode;
  className?: string;
};

/**
 * PX-1 placeholder for modules not yet implemented.
 * Layer: Business (Product Plane)
 */
export function ModuleStub({
  title,
  description,
  milestone,
  children,
  className,
}: ModuleStubProps) {
  return (
    <div className={cn("mx-auto max-w-content", className)}>
      <header className="mb-6">
        <p className="text-xs font-medium uppercase tracking-wide text-ink-subtle">
          {milestone}
        </p>
        <h1 className="mt-1 text-2xl font-semibold text-ink">{title}</h1>
        <p className="mt-2 max-w-prose text-sm leading-relaxed text-ink-muted">
          {description}
        </p>
      </header>
      <div className="rounded-lg border border-dashed border-border bg-surface-muted p-6">
        {children ?? (
          <p className="text-sm text-ink-muted">
            Modulo in arrivo.{" "}
            <Link
              href="/"
              className="font-medium text-accent underline-offset-2 hover:underline cursor-pointer"
            >
              Torna alla Home
            </Link>
          </p>
        )}
      </div>
    </div>
  );
}
