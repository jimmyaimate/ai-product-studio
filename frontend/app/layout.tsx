import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";

export const metadata: Metadata = {
  title: "AI Product Studio — OpenClaw Jimmy",
  description: "Multi-agent AI product studio",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-bg text-text-primary">
        <Sidebar />
        <div className="ml-60 min-h-screen flex flex-col">
          <Topbar />
          <main className="flex-1 p-6 animate-fade-in">{children}</main>
        </div>
      </body>
    </html>
  );
}
