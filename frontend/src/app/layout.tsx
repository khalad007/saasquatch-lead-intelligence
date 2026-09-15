import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "Lead Intelligence | SaaSquatch",
  description: "Deduplication, validation, and AI-powered lead scoring for B2B prospecting.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-bg text-text-primary">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}