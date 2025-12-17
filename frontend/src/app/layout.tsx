import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Генератор технических описаний | БСЛ-Лаб",
  description: "Автоматическая генерация технических описаний для таможенного оформления. Парсинг PDF-инвойсов и создание DOCX-отчетов.",
  keywords: ["технические описания", "таможня", "инвойс", "парсинг", "БСЛ-Лаб"],
  authors: [{ name: "БСЛ-Лаб" }],
  robots: "noindex, nofollow",  // Private app
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#ffffff",
};

import Sidebar from "./components/Sidebar";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground min-h-screen flex`}
        suppressHydrationWarning
      >
        <Sidebar />
        <main className="flex-1 ml-64 p-8 relative overflow-x-hidden bg-background">
          {children}
        </main>
      </body>
    </html>
  );
}
