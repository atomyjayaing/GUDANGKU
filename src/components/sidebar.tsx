"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { signOut } from "next-auth/react";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: "📊" },
  { href: "/sales", label: "Penjualan", icon: "🧾" },
  { href: "/stock-entries", label: "Stok Masuk", icon: "📥" },
  { href: "/products", label: "Produk", icon: "📦" },
  { href: "/suppliers", label: "Supplier", icon: "🏭" },
  { href: "/supplier-payments", label: "Bayar Supplier", icon: "💸" },
];

const REPORTS = [
  { href: "/reports/sales", label: "Laporan Penjualan" },
  { href: "/reports/stock", label: "Laporan Stok" },
  { href: "/reports/profit", label: "Laporan Laba Kasar" },
  { href: "/reports/supplier-debt", label: "Hutang Supplier" },
];

export function Sidebar({ userName }: { userName?: string | null }) {
  const pathname = usePathname();
  const isActive = (href: string) =>
    pathname === href || pathname.startsWith(href + "/");

  return (
    <aside className="w-64 shrink-0 bg-white border-r border-slate-200 flex flex-col">
      <div className="px-5 py-4 border-b border-slate-200">
        <div className="text-lg font-bold tracking-tight">SJE POS</div>
        <div className="text-xs text-slate-500">Toko Elektronik</div>
      </div>

      <nav className="flex-1 overflow-y-auto py-3">
        <ul className="space-y-0.5 px-2">
          {NAV.map((item) => (
            <li key={item.href}>
              <Link
                href={item.href}
                className={cn(
                  "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium",
                  isActive(item.href)
                    ? "bg-slate-900 text-white"
                    : "text-slate-700 hover:bg-slate-100"
                )}
              >
                <span className="text-base">{item.icon}</span>
                {item.label}
              </Link>
            </li>
          ))}
        </ul>

        <div className="px-5 pt-5 pb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
          Laporan
        </div>
        <ul className="space-y-0.5 px-2">
          {REPORTS.map((item) => (
            <li key={item.href}>
              <Link
                href={item.href}
                className={cn(
                  "flex items-center gap-2 rounded-md px-3 py-2 text-sm",
                  isActive(item.href)
                    ? "bg-slate-900 text-white"
                    : "text-slate-700 hover:bg-slate-100"
                )}
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>

        <div className="px-5 pt-5 pb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
          Sistem
        </div>
        <ul className="space-y-0.5 px-2">
          <li>
            <Link
              href="/audit-logs"
              className={cn(
                "flex items-center gap-2 rounded-md px-3 py-2 text-sm",
                isActive("/audit-logs")
                  ? "bg-slate-900 text-white"
                  : "text-slate-700 hover:bg-slate-100"
              )}
            >
              Audit Log
            </Link>
          </li>
        </ul>
      </nav>

      <div className="border-t border-slate-200 p-4">
        <div className="text-xs text-slate-500 mb-1">Login sebagai</div>
        <div className="text-sm font-medium truncate">{userName || "Owner"}</div>
        <button
          onClick={() => signOut({ callbackUrl: "/login" })}
          className="mt-3 w-full text-xs text-slate-600 hover:text-slate-900 border border-slate-200 hover:border-slate-400 rounded-md py-1.5"
        >
          Keluar
        </button>
      </div>
    </aside>
  );
}
