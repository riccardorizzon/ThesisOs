import "./globals.css";
import Link from "next/link";
import type { Metadata, Viewport } from "next";

export const metadata: Metadata = {
  title: "ThesisOS",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

const NAV_ROUTES: { href: string; label: string }[] = [
  { href: "/chat", label: "Chat" },
  { href: "/workspace", label: "Workspace" },
  { href: "/library", label: "Library" },
  { href: "/memory", label: "Memory" },
  { href: "/outline", label: "Outline" },
  { href: "/settings", label: "Settings" },
];

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="flex min-h-screen">
        <nav className="w-48 shrink-0 border-r border-gray-200 p-4">
          <div className="mb-4 text-lg font-semibold">ThesisOS</div>
          <ul className="space-y-1">
            {NAV_ROUTES.map((route) => (
              <li key={route.href}>
                <Link href={route.href} className="block rounded px-2 py-1 hover:bg-gray-100">
                  {route.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        <main className="flex-1 p-6">{children}</main>
      </body>
    </html>
  );
}
