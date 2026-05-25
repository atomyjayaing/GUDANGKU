import { NextRequest } from "next/server";
import { prisma } from "@/lib/prisma";
import { toCSV, csvResponse } from "@/lib/csv";
import { getCurrentUser } from "@/lib/session";

export async function GET(req: NextRequest) {
  const user = await getCurrentUser();
  if (!user) return new Response("Unauthorized", { status: 401 });

  const sp = req.nextUrl.searchParams;
  const from = sp.get("from") ? new Date(sp.get("from")!) : null;
  const to = sp.get("to") ? new Date(sp.get("to") + "T23:59:59") : null;
  const channel = sp.get("channel") || undefined;

  const sales = await prisma.sale.findMany({
    where: {
      ...(from || to
        ? {
            date: {
              ...(from ? { gte: from } : {}),
              ...(to ? { lte: to } : {}),
            },
          }
        : {}),
      ...(channel ? { channel } : {}),
    },
    orderBy: { date: "asc" },
  });

  // Per hari
  const byDay = new Map<
    string,
    { total: number; cost: number; profit: number; count: number }
  >();
  for (const s of sales) {
    const k = s.date.toISOString().slice(0, 10);
    const cur = byDay.get(k) ?? { total: 0, cost: 0, profit: 0, count: 0 };
    cur.total += s.grandTotal;
    cur.cost += s.totalCost;
    cur.profit += s.grossProfit;
    cur.count += 1;
    byDay.set(k, cur);
  }

  const rows = Array.from(byDay.entries()).map(([day, v]) => [
    day,
    v.count,
    v.total,
    v.cost,
    v.profit,
    v.total > 0 ? ((v.profit / v.total) * 100).toFixed(2) + "%" : "0%",
  ]);

  const csv = toCSV(
    [
      "Tanggal",
      "Jumlah Transaksi",
      "Total Omset",
      "Total Modal",
      "Laba Kasar",
      "Margin",
    ],
    rows
  );
  return csvResponse(`laporan-laba-${Date.now()}.csv`, csv);
}
