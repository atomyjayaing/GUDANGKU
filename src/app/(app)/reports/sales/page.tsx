import Link from "next/link";
import { prisma } from "@/lib/prisma";
import { Button, Card, PageHeader, Badge, Input } from "@/components/ui";
import { Table, THead, TR, TH, TD } from "@/components/table";
import {
  formatRupiah,
  formatDate,
  SALES_CHANNELS,
  PAYMENT_METHODS,
  CHANNEL_LABEL,
  PAYMENT_LABEL,
  type SalesChannel,
  type PaymentMethod,
} from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function SalesReportPage({
  searchParams,
}: {
  searchParams: Promise<{
    from?: string;
    to?: string;
    channel?: string;
    payment?: string;
  }>;
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
    ...(sp.payment ? { paymentMethod: sp.payment } : {}),
  };

  const sales = await prisma.sale.findMany({
    where,
    orderBy: { date: "desc" },
  });

  const totals = sales.reduce(
    (a, s) => ({
      total: a.total + s.grandTotal,
      cost: a.cost + s.totalCost,
      profit: a.profit + s.grossProfit,
    }),
    { total: 0, cost: 0, profit: 0 }
  );

  const exportQuery = new URLSearchParams(
    Object.entries(sp).filter(([, v]) => !!v) as [string, string][]
  ).toString();

  return (
    <>
      <PageHeader
        title="Laporan Penjualan"
        description="Daftar transaksi penjualan + filter periode/channel"
        action={
          <a
            href={`/api/reports/sales${exportQuery ? `?${exportQuery}` : ""}`}
          >
            <Button variant="secondary">⬇ Export CSV</Button>
          </a>
        }
      />

      <Card className="p-4 mb-4">
        <form method="get" className="grid grid-cols-2 md:grid-cols-5 gap-2 items-end">
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
          <div>
            <label className="block text-xs text-slate-500 mb-1">Pembayaran</label>
            <select
              name="payment"
              defaultValue={sp.payment || ""}
              className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
            >
              <option value="">Semua</option>
              {PAYMENT_METHODS.map((p) => (
                <option key={p} value={p}>
                  {PAYMENT_LABEL[p]}
                </option>
              ))}
            </select>
          </div>
          <div className="flex gap-2">
            <Button type="submit" variant="secondary">
              Terapkan
            </Button>
            <Link href="/reports/sales">
              <Button type="button" variant="ghost">
                Reset
              </Button>
            </Link>
          </div>
        </form>
      </Card>

      <div className="grid grid-cols-3 gap-3 mb-4">
        <Card className="p-4">
          <div className="text-xs uppercase text-slate-500">Total Omset</div>
          <div className="text-lg font-bold">{formatRupiah(totals.total)}</div>
        </Card>
        <Card className="p-4">
          <div className="text-xs uppercase text-slate-500">Total Modal</div>
          <div className="text-lg font-bold">{formatRupiah(totals.cost)}</div>
        </Card>
        <Card className="p-4">
          <div className="text-xs uppercase text-slate-500">Total Laba</div>
          <div
            className={
              "text-lg font-bold " +
              (totals.profit < 0 ? "text-red-600" : "text-emerald-700")
            }
          >
            {formatRupiah(totals.profit)}
          </div>
        </Card>
      </div>

      <Card>
        {sales.length === 0 ? (
          <div className="p-10 text-center text-sm text-slate-400">
            Tidak ada transaksi pada filter ini.
          </div>
        ) : (
          <Table>
            <THead>
              <TR>
                <TH>Tanggal</TH>
                <TH>Invoice</TH>
                <TH>Channel</TH>
                <TH>Customer</TH>
                <TH className="text-right">Total</TH>
                <TH className="text-right">Modal</TH>
                <TH className="text-right">Laba</TH>
                <TH>Bayar</TH>
              </TR>
            </THead>
            <tbody>
              {sales.map((s) => (
                <TR key={s.id}>
                  <TD>{formatDate(s.date)}</TD>
                  <TD>
                    <Link href={`/sales/${s.id}`} className="font-mono hover:underline">
                      {s.invoiceNo}
                    </Link>
                  </TD>
                  <TD>
                    <Badge variant="muted">
                      {CHANNEL_LABEL[s.channel as SalesChannel] ?? s.channel}
                    </Badge>
                  </TD>
                  <TD>{s.customerName || "-"}</TD>
                  <TD className="text-right">{formatRupiah(s.grandTotal)}</TD>
                  <TD className="text-right text-slate-500">
                    {formatRupiah(s.totalCost)}
                  </TD>
                  <TD
                    className={
                      "text-right font-medium " +
                      (s.grossProfit < 0 ? "text-red-600" : "text-emerald-700")
                    }
                  >
                    {formatRupiah(s.grossProfit)}
                  </TD>
                  <TD>
                    <Badge variant="muted">
                      {PAYMENT_LABEL[s.paymentMethod as PaymentMethod] ?? s.paymentMethod}
                    </Badge>
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
