import Link from "next/link";
import { prisma } from "@/lib/prisma";
import { Button, Card, PageHeader, Input } from "@/components/ui";
import { Table, THead, TR, TH, TD } from "@/components/table";
import {
  formatRupiah,
  SALES_CHANNELS,
  CHANNEL_LABEL,
} from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function ProfitReportPage({
  searchParams,
}: {
  searchParams: Promise<{ from?: string; to?: string; channel?: string }>;
}) {
  const sp = await searchParams;
  const from = sp.from ? new Date(sp.from) : null;
  const to = sp.to ? new Date(sp.to + "T23:59:59") : null;

  const where = {
    ...(from || to
      ? {
          date: {
            ...(from ? { gte: from } : {}),
            ...(to ? { lte: to } : {}),
          },
        }
      : {}),
    ...(sp.channel ? { channel: sp.channel } : {}),
  };

  const sales = await prisma.sale.findMany({
    where,
    orderBy: { date: "asc" },
    select: { date: true, grandTotal: true, totalCost: true, grossProfit: true },
  });

  const totals = sales.reduce(
    (a, s) => ({
      total: a.total + s.grandTotal,
      cost: a.cost + s.totalCost,
      profit: a.profit + s.grossProfit,
    }),
    { total: 0, cost: 0, profit: 0 }
  );

  const margin = totals.total > 0 ? (totals.profit / totals.total) * 100 : 0;

  // Group per hari
  const byDay = new Map<string, { total: number; cost: number; profit: number; count: number }>();
  for (const s of sales) {
    const k = s.date.toISOString().slice(0, 10);
    const cur = byDay.get(k) ?? { total: 0, cost: 0, profit: 0, count: 0 };
    cur.total += s.grandTotal;
    cur.cost += s.totalCost;
    cur.profit += s.grossProfit;
    cur.count += 1;
    byDay.set(k, cur);
  }
  const dayRows = Array.from(byDay.entries()).sort((a, b) => (a[0] < b[0] ? 1 : -1));

  const exportQuery = new URLSearchParams(
    Object.entries(sp).filter(([, v]) => !!v) as [string, string][]
  ).toString();

  return (
    <>
      <PageHeader
        title="Laporan Laba Kasar"
        description="Total omset, modal, laba kasar berdasarkan periode"
        action={
          <a href={`/api/reports/profit${exportQuery ? `?${exportQuery}` : ""}`}>
            <Button variant="secondary">⬇ Export CSV</Button>
          </a>
        }
      />

      <Card className="p-4 mb-4">
        <form method="get" className="grid grid-cols-2 md:grid-cols-4 gap-2 items-end">
          <div>
            <label className="block text-xs text-slate-500 mb-1">Dari</label>
            <Input type="date" name="from" defaultValue={sp.from || ""} />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Sampai</label>
            <Input type="date" name="to" defaultValue={sp.to || ""} />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Channel</label>
            <select
              name="channel"
              defaultValue={sp.channel || ""}
              className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
            >
              <option value="">Semua</option>
              {SALES_CHANNELS.map((c) => (
                <option key={c} value={c}>
                  {CHANNEL_LABEL[c]}
                </option>
              ))}
            </select>
          </div>
          <div className="flex gap-2">
            <Button type="submit" variant="secondary">
              Terapkan
            </Button>
            <Link href="/reports/profit">
              <Button type="button" variant="ghost">
                Reset
              </Button>
            </Link>
          </div>
        </form>
      </Card>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <Card className="p-4">
          <div className="text-xs uppercase text-slate-500">Total Omset</div>
          <div className="text-lg font-bold">{formatRupiah(totals.total)}</div>
        </Card>
        <Card className="p-4">
          <div className="text-xs uppercase text-slate-500">Total Modal</div>
          <div className="text-lg font-bold">{formatRupiah(totals.cost)}</div>
        </Card>
        <Card className="p-4">
          <div className="text-xs uppercase text-slate-500">Laba Kasar</div>
          <div
            className={
              "text-lg font-bold " +
              (totals.profit < 0 ? "text-red-600" : "text-emerald-700")
            }
          >
            {formatRupiah(totals.profit)}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-xs uppercase text-slate-500">Margin</div>
          <div className="text-lg font-bold">{margin.toFixed(2)}%</div>
        </Card>
      </div>

      <Card>
        <div className="p-4 border-b border-slate-200">
          <h3 className="font-semibold">Rekap per Tanggal</h3>
        </div>
        {dayRows.length === 0 ? (
          <div className="p-10 text-center text-sm text-slate-400">
            Tidak ada transaksi pada filter ini.
          </div>
        ) : (
          <Table>
            <THead>
              <TR>
                <TH>Tanggal</TH>
                <TH className="text-right">Transaksi</TH>
                <TH className="text-right">Omset</TH>
                <TH className="text-right">Modal</TH>
                <TH className="text-right">Laba</TH>
                <TH className="text-right">Margin</TH>
              </TR>
            </THead>
            <tbody>
              {dayRows.map(([day, v]) => (
                <TR key={day}>
                  <TD>{day}</TD>
                  <TD className="text-right">{v.count}</TD>
                  <TD className="text-right">{formatRupiah(v.total)}</TD>
                  <TD className="text-right text-slate-500">
                    {formatRupiah(v.cost)}
                  </TD>
                  <TD
                    className={
                      "text-right font-medium " +
                      (v.profit < 0 ? "text-red-600" : "text-emerald-700")
                    }
                  >
                    {formatRupiah(v.profit)}
                  </TD>
                  <TD className="text-right">
                    {v.total > 0 ? ((v.profit / v.total) * 100).toFixed(2) : "0"}%
                  </TD>
                </TR>
              ))}
            </tbody>
          </Table>
        )}
      </Card>
    </>
  );
}
