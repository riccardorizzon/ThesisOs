"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { AppShell } from "@/components/AppShell";
import { hasCompletedWelcome } from "@/lib/workspacePrefs";

type ShellRouterProps = {
  children: React.ReactNode;
};

export function ShellRouter({ children }: ShellRouterProps) {
  const pathname = usePathname();
  const router = useRouter();
  const isWelcome = pathname === "/welcome";

  useEffect(() => {
    if (isWelcome) return;
    if (!hasCompletedWelcome()) {
      router.replace("/welcome");
    }
  }, [isWelcome, router]);

  if (isWelcome) {
    return <>{children}</>;
  }

  return <AppShell>{children}</AppShell>;
}
