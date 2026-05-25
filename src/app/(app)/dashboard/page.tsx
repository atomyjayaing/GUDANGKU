import Link from "next/link";
import { prisma } from "@/lib/prisma";
import { Card, PageHeader, Badge } from "@/components/ui";
import { formatRupiah, formatDateTime, CHANNEL_LABEL, type SalesChannel } from "@/lib/utils";

export const dynamic = "force-dynamic";

async function getDashboardData() {
  const now = new Date();
  const startOfDay = new Date(now);
  startOfDay.setHours(0, 0, 0, 0);
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);

  const [salesToday, salesMonth, products, suppliersDebt, recentSales, topProducts] =
    await Promise.all([
      prisma.sale.aggregate({
        _sum: { grandTotal: true, grossProfit: true },
        where: { date: { gte: startOfDay } },
      }),
      prisma.sale.aggregate({
        _sum: { grandTotal: true, grossProfit: true },
        where: { date: { gte: startOfMonth } },
      }),
      prisma.product.findMany({
        where: { status: "ACTIVE" },
        select: { id: true, sku: true, name: true, stock: true, costPrice: true },
      }),
      prisma.$queryRaw<Array<{ supplierId: string; totalCost: number; totalPaid: number }>>`
        SELECT
          s.id AS supplierId,
          COALESCE((SELECT SUM(totalCostItem) FROM SaleItem WHERE supplierId = s.id), 0) AS totalCost,
          COALESCE((SELECT SUM(amount) FROM SupplierPayment WHERE supplierId = s.id), 0) AS totalPaid
        FROM Supplier s
      `,
      prisma.sale.findMany({
        orderBy: { date: "desc" },
        take: 5,
        select: {
          id: true,
          invoiceNo: true,
          date: true,
          channel: true,
          customerName: true,
          grandTotal: true,
        },
      }),
      prisma.saleItem.groupBy({
        by: ["productId", "productNameSnapshot"],
        _sum: { qty: true, subtotalItem: true },
        orderBy: { _sum: { qty: "desc" } },
        take: 5,
      }),
    ]);

  const totalStock = products.reduce((sum, p) => sum + p.stock, 0);
  const totalStockValue = products.reduce((sum, p) => sum + p.stock * p.costPrice, 0);
  const lowStock = products
    .filter((p) => p.stock <= 2)
    .slice(0, 5);
  const totalDebt = suppliersDebt.reduce(
    (sum, r) => sum + Math.max(0, Number(r.totalCost) - Number(r.totalPaid)),
    0
  );

  return {
    revenueToday: salesToday._sum.grandTotal ?? 0,
    profitToday: salesToday._sum.grossProfit ?? 0,
    revenueMonth: salesMonth._sum.grandTotal ?? 0,
    profitMonth: salesMonth._sum.grossProfit ?? 0,
    totalStock,
    totalStockValue,
    totalDebt,
    lowStock,
    recentSales,
    topProducts,
  };
}

function Kpi({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint?: string;
}) {
  return (
    <Card className="p-5">
      <div className="text-xs font-medium text-slate-500 uppercase tracking-wide">
        {label}
      </div>
      <div className="text-2xl font-bold mt-2">{value}</div>
      {hint && <div className="text-xs text-slate-400 mt-1">{hint}</div>}
    </Card>
  );
}

export default async function DashboardPage() {
  const d = await getDashboardData();

  return (
    <>
      <PageHeader
        title="Dashboard"
        description="Ringkasan operasional toko hari ini & bulan ini"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Kpi label="Omset Hari Ini" value={formatRupiah(d.revenueToday)} />
        <Kpi label="Laba Kasar Hari Ini" value={formatRupiah(d.profitToday)} />
        <Kpi label="Omset Bulan Ini" value={formatRupiah(d.revenueMonth)} />
        <Kpi label="Laba Kasar Bulan Ini" value={formatRupiah(d.profitMonth)} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Kpi label="Total Stok" value={`${d.totalStock} unit`} />
        <Kpi label="Nilai Stok (modal)" value={formatRupiah(d.totalStockValue)} />
        <Kpi
          label="Hutang ke Supplier"
          value={formatRupiah(d.totalDebt)}
          hint="Total modal terjual − total pembayaran"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="p-5 lg:col-span-2">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold">Penjualan Terbaru</h2>
            <Link
              href="/sales"
              className="text-xs text-slate-500 hover:text-slate-900"
            >
              Lihat semua →
            </Link>
          </div>
          {d.recentSales.length === 0 ? (
            <p className="text-sm text-slate-400 py-4">Belum ada transaksi.</p>
          ) : (
            <table className="w-full text-sm">
              <thead className="text-left text-xs text-slate-500 uppercase">
                <tr>
                  <th className="py-2">Invoice</th>
                  <th>Tanggal</th>
                  <th>Channel</th>
                  <th className="text-right">Total</th>
                </tr>
              </thead>
              <tbody>
                {d.recentSales.map((s) => (
                  <tr key={s.id} className="border-t border-slate-100">
                    <td className="py-2">
                      <Link
                        href={`/sales/${s.id}`}
                        className="font-mono text-slate-900 hover:underline"
                      >
                        {s.invoiceNo}
                      </Link>
                    </td>
                    <td className="text-slate-600">{formatDateTime(s.date)}</td>
                    <td>
                      <Badge variant="muted">
                        {CHANNEL_LABEL[s.channel as SalesChannel] ?? s.channel}
                      </Badge>
                    </td>
                    <td className="text-right font-medium">
                      {formatRupiah(s.grandTotal)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Card>

        <Card className="p-5">
          <h2 className="font-semibold mb-3">Stok Rendah</h2>
          {d.lowStock.length === 0 ? (
            <p className="text-sm text-slate-400 py-4">
              Semua produk aman (stok &gt; 2).
            </p>
          ) : (
            <ul className="space-y-2">
              {d.lowStock.map((p) => (
                <li
                  key={p.id}
                  className="flex items-center justify-between text-sm"
                >
                  <Link
                    href={`/products/${p.id}`}
                    className="hover:underline truncate pr-2"
                  >
                    {p.name}
                  </Link>
                  <Badge variant={p.stock === 0 ? "danger" : "warning"}>
                    {p.stock} unit
                  </Badge>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <Card className="p-5 mt-4">
        <h2 className="font-semibold mb-3">Produk Paling Laku</h2>
        {d.topProducts.length === 0 ? (
          <p className="text-sm text-slate-400 py-4">Belum ada penjualan.</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="text-left text-xs text-slate-500 uppercase">
              <tr>
                <th className="py-2">Produk</th>
                <th className="text-right">Qty Terjual</th>
                <th className="text-right">Total Omset</th>
              </tr>
            </thead>
            <tbody>
              {d.topProducts.map((p) => (
                <tr key={p.productId} className="border-t border-slate-100">
                  <td className="py-2">{p.productNameSnapshot}</td>
                  <td className="text-right">{p._sum.qty ?? 0} unit</td>
                  <td className="text-right font-medium">
                    {formatRupiah(p._sum.subtotalItem ?? 0)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </>
  );
}
