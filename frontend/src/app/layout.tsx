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
  themeColor: "#3B82F6",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        suppressHydrationWarning
      >
        {children}
      </body>
    </html>
  );
}
