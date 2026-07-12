export type WorkspaceMode = "personal" | "demo";

const MODE_KEY = "thesisos:workspace-mode";
const WELCOME_KEY = "thesisos:welcome-complete";
const MODE_COOKIE = "thesisos-workspace-mode";
const WELCOME_COOKIE = "thesisos-welcome-complete";

export type ChapterListScope = "all" | "owned" | "demo";

export function chapterScopeForMode(mode: WorkspaceMode): ChapterListScope {
  return mode === "demo" ? "demo" : "owned";
}

export function getWorkspaceMode(): WorkspaceMode {
  if (typeof window === "undefined") return "personal";
  return localStorage.getItem(MODE_KEY) === "demo" ? "demo" : "personal";
}

export function setWorkspaceMode(mode: WorkspaceMode): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(MODE_KEY, mode);
  document.cookie = `${MODE_COOKIE}=${mode}; path=/; max-age=31536000; samesite=lax`;
}

export function hasCompletedWelcome(): boolean {
  if (typeof window === "undefined") return true;
  return localStorage.getItem(WELCOME_KEY) === "1";
}

export function markWelcomeComplete(): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(WELCOME_KEY, "1");
  document.cookie = `${WELCOME_COOKIE}=1; path=/; max-age=31536000; samesite=lax`;
}

export function readWorkspaceModeCookie(cookieHeader: string | null): WorkspaceMode {
  if (!cookieHeader) return "personal";
  const match = cookieHeader.match(/(?:^|;\s*)thesisos-workspace-mode=(personal|demo)/);
  return match?.[1] === "demo" ? "demo" : "personal";
}

export function readWelcomeCompleteCookie(cookieHeader: string | null): boolean {
  if (!cookieHeader) return false;
  return /(?:^|;\s*)thesisos-welcome-complete=1/.test(cookieHeader);
}
