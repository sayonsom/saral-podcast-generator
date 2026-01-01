import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Energy Debates - Podcast Script Generator",
  description: "Convert energy blogs into debate-style podcast scripts",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans bg-neutral-50 min-h-screen">{children}</body>
    </html>
  );
}
