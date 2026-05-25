import Link from "next/link";
import { prisma } from "@/lib/prisma";
import {
  Button,
  Card,
  PageHeader,
  EmptyState,
  Badge,
  Input,
} from "@/components/ui";
import { Table, THead, TR, TH, TD } from "@/components/table";
import {
  formatRupiah,
  formatDateTime,
  CHANNEL_LABEL,
  PAYMENT_LABEL,
  SALES_CHANNELS,
  PAYMENT_METHODS,
  type SalesChannel,
  type PaymentMethod,
} from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function SalesPage({
  searchParams,
}: {
  searchParams: Promise<{
    from?: string;
    to?: string;
    channel?: string;
    payment?: string;
    q?: string;
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
    ...(sp.q
      ? {
          OR: [
            { invoiceNo: { contains: sp.q } },
            { customerName: { contains: sp.q } },
          ],
        }
      : {}),
  };

  const sales = await prisma.sale.findMany({
    where,
    orderBy: { date: "desc" },
    take: 300,
    select: {
      id: true,
      invoiceNo: true,
      date: true,
      channel: true,
      customerName: true,
      paymentMethod: true,
      grandTotal: true,
      grossProfit: true,
    },
  });

  const totals = sales.reduce(
    (a, s) => ({
      total: a.total + s.grandTotal,
      profit: a.profit + s.grossProfit,
    }),
    { total: 0, profit: 0 }
  );

  return (
    <>
      <PageHeader
        title="Penjualan"
        description={`${sales.length} transaksi • Total: ${formatRupiah(totals.total)} • Laba: ${formatRupiah(totals.profit)}`}
        action={
          <Link href="/sales/new">
            <Button>+ Penjualan Baru</Button>
          </Link>
        }
      />

      <Card className="p-4 mb-4">
        <form method="get" className="grid grid-cols-2 md:grid-cols-6 gap-2">
          <div className="col-span-1">
            <label className="block text-xs text-slate-500 mb-1">Dari</label>
            <Input type="date" name="from" defaultValue={sp.from || ""} />
          </div>
          <div className="col-span-1">
            <label className="block text-xs text-slate-500 mb-1">Sampai</label>
            <Input type="date" name="to" defaultValue={sp.to || ""} />
          </div>
          <div className="col-span-1">
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
          <div className="col-span-1">
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
          <div className="col-span-2">
            <label className="block text-xs text-slate-500 mb-1">Cari</label>
            <Input
              name="q"
              placeholder="Invoice / nama customer"
              defaultValue={sp.q || ""}
            />
          </div>
          <div className="col-span-2 md:col-span-6 flex gap-2 pt-1">
            <Button type="submit" variant="secondary">
              Terapkan Filter
            </Button>
            <Link href="/sales">
              <Button type="button" variant="ghost">
                Reset
              </Button>
            </Link>
          </div>
        </form>
      </Card>

      <Card>
        {sales.length === 0 ? (
          <EmptyState
            title="Belum ada penjualan"
            description="Catat penjualan pertama Anda."
            action={
              <Link href="/sales/new">
                <Button>+ Penjualan Baru</Button>
              </Link>
            }
          />
        ) : (
          <Table>
            <THead>
              <TR>
                <TH>Tanggal</TH>
                <TH>Invoice</TH>
                <TH>Customer</TH>
                <TH>Channel</TH>
                <TH>Pembayaran</TH>
                <TH className="text-right">Total</TH>
                <TH className="text-right">Laba</TH>
              </TR>
            </THead>
            <tbody>
              {sales.map((s) => (
                <TR key={s.id}>
                  <TD className="text-slate-600">{formatDateTime(s.date)}</TD>
                  <TD>
                    <Link
                      href={`/sales/${s.id}`}
                      className="font-mono text-slate-900 hover:underline"
                    >
                      {s.invoiceNo}
                    </Link>
                  </TD>
                  <TD>{s.customerName || "-"}</TD>
                  <TD>
                    <Badge variant="muted">
                      {CHANNEL_LABEL[s.channel as SalesChannel] ?? s.channel}
                    </Badge>
                  </TD>
                  <TD>
                    <Badge variant="muted">
                      {PAYMENT_LABEL[s.paymentMethod as PaymentMethod] ?? s.paymentMethod}
                    </Badge>
                  </TD>
                  <TD className="text-right font-medium">
                    {formatRupiah(s.grandTotal)}
                  </TD>
                  <TD
                    className={
                      "text-right " +
                      (s.grossProfit < 0 ? "text-red-600" : "text-emerald-700")
                    }
                  >
                    {formatRupiah(s.grossProfit)}
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
