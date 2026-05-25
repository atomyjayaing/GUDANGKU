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
  const payment = sp.get("payment") || undefined;

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
      ...(payment ? { paymentMethod: payment } : {}),
    },
    orderBy: { date: "asc" },
  });

  const rows = sales.map((s) => [
    s.date.toISOString().slice(0, 10),
    s.invoiceNo,
    s.channel,
    s.customerName ?? "",
    s.customerPhone ?? "",
    s.paymentMethod,
    s.grandTotal,
    s.totalCost,
    s.grossProfit,
  ]);

  const csv = toCSV(
    [
      "Tanggal",
      "Invoice",
      "Channel",
      "Customer",
      "HP",
      "Metode Bayar",
      "Total Penjualan",
      "Total Modal",
      "Laba Kasar",
    ],
    rows
  );
  return csvResponse(`laporan-penjualan-${Date.now()}.csv`, csv);
}
