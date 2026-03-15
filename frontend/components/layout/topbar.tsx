"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

const TITLES: Record<string, string> = {
  "/": "Dashboard",
  "/projects": "Projects",
  "/credits": "Credits",
};

export function Topbar() {
  const pathname = usePathname();
  const title =
    TITLES[pathname] ??
    (pathname.startsWith("/projects/") ? "Project Detail" : "AI Product Studio");

  return (
    <header className="h-14 border-b border-border bg-bg/80 backdrop-blur flex items-center justify-between px-6 sticky top-0 z-30">
      <h1 className="text-sm font-semibold text-text-primary">{title}</h1>
      <div className="flex items-center gap-3">
        <Link href="/projects/new">
          <Button size="sm">
            <Plus size={14} />
            New Project
          </Button>
        </Link>
      </div>
    </header>
  );
}
