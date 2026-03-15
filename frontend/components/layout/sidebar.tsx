"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  FolderOpen,
  Zap,
  CreditCard,
  Settings,
  ChevronRight,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/projects", label: "Projects", icon: FolderOpen },
  { href: "/credits", label: "Credits", icon: CreditCard },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-full w-60 bg-surface border-r border-border flex flex-col z-40">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-accent-gradient flex items-center justify-center text-bg font-bold text-sm flex-shrink-0">
            J
          </div>
          <div>
            <div className="text-sm font-bold text-text-primary leading-none">OpenClaw Jimmy</div>
            <div className="text-xs text-text-muted mt-0.5">AI Product Studio</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || (href !== "/" && pathname.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150",
                active
                  ? "bg-tag-bg text-accent"
                  : "text-text-secondary hover:text-text-primary hover:bg-surface-raised"
              )}
            >
              <Icon size={16} strokeWidth={active ? 2.5 : 1.8} />
              {label}
              {active && <ChevronRight size={12} className="ml-auto opacity-60" />}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-border">
        <div className="flex items-center gap-2 px-2">
          <div className="w-2 h-2 rounded-full bg-accent animate-pulse-slow" />
          <span className="text-xs text-text-muted">Backend connected</span>
        </div>
      </div>
    </aside>
  );
}
