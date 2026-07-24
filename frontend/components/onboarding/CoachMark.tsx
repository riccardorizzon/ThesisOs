"use client";

import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { cn } from "@/lib/cn";
import { useReducedMotion } from "@/hooks/useReducedMotion";

export const ONBOARDING_STORAGE_KEY = "thesisos-onboarding-m7";

export type OnboardingState = {
  dismissed: boolean;
  completedSteps: number[];
};

export type CoachMarkStep = {
  id: number;
  target: string;
  title: string;
  body: string;
  pathnameMatch: (pathname: string) => boolean;
};

export const PX2_COACH_STEPS: CoachMarkStep[] = [
  {
    id: 1,
    target: '[data-testid="continua-link"]',
    title: "Riprendi da dove hai lasciato",
    body: "Usa Continua per tornare subito al capitolo o alla sezione attiva.",
    pathnameMatch: (pathname) => pathname === "/",
  },
  {
    id: 2,
    target: '[data-testid="writing-workspace"]',
    title: "Tre pannelli di scrittura",
    body: "Outline a sinistra, editor al centro e pannello AI a destra lavorano insieme.",
    pathnameMatch: (pathname) =>
      pathname === "/writing" || pathname.startsWith("/writing/"),
  },
  {
    id: 3,
    target: '[data-testid="context-bar"]',
    title: "Contesto automatico",
    body: "L'AI vede questo contesto automaticamente mentre scrivi o revisioni.",
    pathnameMatch: (pathname) =>
      pathname.startsWith("/writing") ||
      pathname.startsWith("/sources") ||
      pathname.startsWith("/review"),
  },
  {
    id: 4,
    target: '[data-testid="sources-search-input"]',
    title: "Cerca nelle fonti",
    body: "Filtra la bibliografia per titolo, autore o tag — tutto dal database del progetto.",
    pathnameMatch: (pathname) => pathname === "/sources",
  },
  {
    id: 5,
    target: '[data-testid="home-import-cta"]',
    title: "Importa la prima fonte",
    body: "Carica PDF, EPUB, DOCX, Markdown o testo per indicizzarli e collegarli ai concetti della tesi.",
    pathnameMatch: (pathname) => pathname === "/",
  },
];

/** Full M7 onboarding sequence (PX-2 + M7.2 extensions). */
export const ALL_COACH_STEPS: CoachMarkStep[] = PX2_COACH_STEPS;

export function loadOnboardingState(): OnboardingState {
  if (typeof window === "undefined") {
    return { dismissed: false, completedSteps: [] };
  }
  try {
    const raw = localStorage.getItem(ONBOARDING_STORAGE_KEY);
    if (!raw) return { dismissed: false, completedSteps: [] };
    const parsed = JSON.parse(raw) as OnboardingState;
    return {
      dismissed: Boolean(parsed.dismissed),
      completedSteps: Array.isArray(parsed.completedSteps)
        ? parsed.completedSteps
        : [],
    };
  } catch {
    return { dismissed: false, completedSteps: [] };
  }
}

export function saveOnboardingState(state: OnboardingState): void {
  localStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify(state));
}

export type CoachMarkProps = {
  step: CoachMarkStep;
  onNext: () => void;
  onSkip: () => void;
  stepIndex: number;
  totalSteps: number;
};

/**
 * Single contextual coach mark — z-index 80 (PX2-EWO-008 §20).
 * Layer: Business (Product Plane)
 */
export function CoachMark({
  step,
  onNext,
  onSkip,
  stepIndex,
  totalSteps,
}: CoachMarkProps) {
  const reducedMotion = useReducedMotion();
  const [rect, setRect] = useState<DOMRect | null>(null);
  const popoverRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const update = () => {
      const el = document.querySelector(step.target);
      setRect(el?.getBoundingClientRect() ?? null);
    };
    update();
    window.addEventListener("resize", update);
    window.addEventListener("scroll", update, true);
    const observer = new MutationObserver(update);
    observer.observe(document.body, { childList: true, subtree: true });
    return () => {
      window.removeEventListener("resize", update);
      window.removeEventListener("scroll", update, true);
      observer.disconnect();
    };
  }, [step.target]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onSkip();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onSkip]);

  if (!rect) return null;

  const top = Math.min(rect.bottom + 8, window.innerHeight - 160);
  const left = Math.min(Math.max(rect.left, 8), window.innerWidth - 288);

  return (
    <>
      <div
        className="pointer-events-none fixed inset-0 z-[79] bg-ink/10"
        aria-hidden
        data-testid="coach-mark-backdrop"
      />
      <div
        ref={popoverRef}
        role="dialog"
        aria-labelledby={`coach-mark-title-${step.id}`}
        className={cn(
          "fixed z-[80] w-72 rounded-lg border border-border bg-surface p-4 shadow-md",
          !reducedMotion && "transition-opacity duration-100"
        )}
        style={{ top, left }}
        data-testid={`coach-mark-step-${step.id}`}
      >
        <p className="text-xs font-medium uppercase tracking-wide text-ink-subtle">
          Suggerimento {stepIndex + 1} di {totalSteps}
        </p>
        <h3
          id={`coach-mark-title-${step.id}`}
          className="mt-1 text-sm font-semibold text-ink"
        >
          {step.title}
        </h3>
        <p className="mt-1 text-sm leading-relaxed text-ink-muted">{step.body}</p>
        <div className="mt-4 flex items-center justify-between gap-2">
          <button
            type="button"
            onClick={onSkip}
            className="text-xs font-medium text-ink-subtle transition-colors duration-200 hover:text-ink"
            data-testid="coach-mark-skip"
          >
            Salta tutorial
          </button>
          <button
            type="button"
            onClick={onNext}
            className="rounded-md bg-accent px-3 py-1.5 text-xs font-medium text-ink-inverse transition-colors duration-200 hover:bg-accent-muted"
            data-testid="coach-mark-next"
          >
            {stepIndex + 1 >= totalSteps ? "Fine" : "Avanti"}
          </button>
        </div>
      </div>
    </>
  );
}

export type CoachMarkProviderProps = {
  pathname: string;
  steps?: CoachMarkStep[];
};

/**
 * Shows at most one coach mark per route visit (M7 onboarding, max 5 steps).
 * Layer: Business (Product Plane)
 */
export function CoachMarkProvider({
  pathname,
  steps = ALL_COACH_STEPS,
}: CoachMarkProviderProps) {
  const [state, setState] = useState<OnboardingState>({
    dismissed: false,
    completedSteps: [],
  });
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    setState(loadOnboardingState());
  }, []);

  const activeStep = steps.find(
    (step) =>
      !state.dismissed &&
      !state.completedSteps.includes(step.id) &&
      step.pathnameMatch(pathname)
  );

  const persist = useCallback((next: OnboardingState) => {
    setState(next);
    saveOnboardingState(next);
  }, []);

  const handleNext = useCallback(() => {
    if (!activeStep) return;
    const completedSteps = [...state.completedSteps, activeStep.id];
    const dismissed = completedSteps.length >= steps.length;
    persist({ dismissed, completedSteps });
  }, [activeStep, persist, state.completedSteps, steps.length]);

  const handleSkip = useCallback(() => {
    persist({ dismissed: true, completedSteps: state.completedSteps });
  }, [persist, state.completedSteps]);

  if (!mounted || !activeStep) return null;

  const completedCount = state.completedSteps.length;

  return (
    <CoachMark
      step={activeStep}
      onNext={handleNext}
      onSkip={handleSkip}
      stepIndex={completedCount}
      totalSteps={steps.length}
    />
  );
}
