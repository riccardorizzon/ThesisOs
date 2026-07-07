import { Crimson_Pro, Atkinson_Hyperlegible } from "next/font/google";
import "./globals.css";
import type { Metadata, Viewport } from "next";
import { AppShell } from "@/components/AppShell";

const crimsonPro = Crimson_Pro({
  subsets: ["latin"],
  variable: "--font-heading",
  display: "swap",
});

const atkinson = Atkinson_Hyperlegible({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-body",
  display: "swap",
});

export const metadata: Metadata = {
  title: "ThesisOS",
  description: "Research Operating System",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="it" className={`${crimsonPro.variable} ${atkinson.variable}`}>
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
