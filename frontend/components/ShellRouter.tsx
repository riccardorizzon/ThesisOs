"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import {
  getWorkspaceMode,
  hasCompletedWelcome,
  markWelcomeComplete,
  setWorkspaceMode,
} from "@/lib/workspacePrefs";
import {
  getActiveProjectId,
  setActiveProjectId,
} from "@/lib/projectPrefs";

const DEMO_PROJECT_ID = "demo-thesis";
const CHAT_PROJECT_ID = "thesis-agent";

type ShellRouterProps = {
  children: React.ReactNode;
};

export function ShellRouter({ children }: ShellRouterProps) {
  const pathname = usePathname();
  const router = useRouter();
  const isWelcome = pathname === "/welcome";
  const isChatFirst = pathname === "/" || pathname === "/ai";
  const [, rerenderWorkspace] = useState(0);

  useEffect(() => {
    if (isWelcome) return;
    if (isChatFirst) {
      const isDemo =
        getWorkspaceMode() === "demo" ||
        getActiveProjectId() === DEMO_PROJECT_ID;
      if (isDemo) {
        setActiveProjectId(CHAT_PROJECT_ID);
        setWorkspaceMode("personal");
        rerenderWorkspace((revision) => revision + 1);
      }
      if (!hasCompletedWelcome()) {
        markWelcomeComplete();
      }
      return;
    }
    if (!hasCompletedWelcome()) {
      router.replace("/welcome");
    }
  }, [isChatFirst, isWelcome, router]);

  if (isWelcome) {
    return <>{children}</>;
  }

  return <AppShell>{children}</AppShell>;
}
