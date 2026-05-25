import Link from "next/link";
import { notFound } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { Button, Card, PageHeader, Badge } from "@/components/ui";
import { Table, THead, TR, TH, TD } from "@/components/table";
import { formatRupiah, formatDate, CHANNEL_LABEL, type SalesChannel } from "@/lib/utils";
import { DeleteSupplierButton } from "./delete-button";

export const dynamic = "force-dynamic";

async function getSupplierDetail(id: string) {
  const supplier = await prisma.supplier.findUnique({ where: { id } });
  if (!supplier) return null;

  const [stockEntries, soldItems, payments, stockOnHand] = await Promise.all([
    prisma.stockEntry.findMany({
      where: { supplierId: id },
      orderBy: { date: "desc" },
      take: 20,
      include: { product: { select: { name: true, sku: true } } },
    }),
    prisma.saleItem.findMany({
      where: { supplierId: id },
      orderBy: { createdAt: "desc" },
      take: 20,
      include: {
        sale: { select: { invoiceNo: true, date: true, channel: true } },
      },
    }),
    prisma.supplierPayment.findMany({
      where: { supplierId: id },
      orderBy: { date: "desc" },
      take: 20,
    }),
    prisma.product.aggregate({
      where: { defaultSupplierId: id, status: "ACTIVE" },
      _sum: { stock: true },
    }),
  ]);

  const totalIn = await prisma.stockEntry.aggregate({
    where: { supplierId: id },
    _sum: { totalCost: true },
  });
  const totalSoldCost = await prisma.saleItem.aggregate({
    where: { supplierId: id },
    _sum: { totalCostItem: true },
  });
  const totalPaid = await prisma.supplierPayment.aggregate({
    where: { supplierId: id },
    _sum: { amount: true },
  });

  const totalInValue = totalIn._sum.totalCost ?? 0;
  const totalSoldCostValue = totalSoldCost._sum.totalCostItem ?? 0;
  const totalPaidValue = totalPaid._sum.amount ?? 0;
  const debt = Math.max(0, totalSoldCostValue - totalPaidValue);

  return {
    supplier,
    stockEntries,
    soldItems,
    payments,
    stockOnHand: stockOnHand._sum.stock ?? 0,
    totalInValue,
    totalSoldCostValue,
    totalPaidValue,
    debt,
  };
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <Card className="p-4">
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className="text-lg font-bold mt-1">{value}</div>
    </Card>
  );
}

export default async function SupplierDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const data = await getSupplierDetail(id);
  if (!data) notFound();
  const { supplier, stockEntries, soldItems, payments } = data;

  return (
    <>
      <PageHeader
        title={supplier.name}
        description={supplier.phone || undefined}
        action={
          <div className="flex gap-2">
            <Link href={`/suppliers/${supplier.id}/edit`}>
              <Button variant="secondary">Edit</Button>
            </Link>
            <Link href="/supplier-payments/new">
              <Button>+ Catat Pembayaran</Button>
            </Link>
          </div>
        }
      />

      {supplier.address && (
        <p className="text-sm text-slate-600 mb-4">{supplier.address}</p>
      )}
      {supplier.notes && (
        <p className="text-sm text-slate-500 italic mb-6">"{supplier.notes}"</p>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <Stat label="Stok Tersisa" value={`${data.stockOnHand} unit`} />
        <Stat
          label="Total Nilai Stok Masuk"
          value={formatRupiah(data.totalInValue)}
        />
        <Stat
          label="Total Modal Terjual"
          value={formatRupiah(data.totalSoldCostValue)}
        />
        <Stat label="Total Dibayar" value={formatRupiah(data.totalPaidValue)} />
      </div>

      <Card className="p-5 mb-6 bg-amber-50 border-amber-200">
        <div className="text-sm text-amber-800">Sisa Kewajiban / Hutang</div>
        <div className="text-3xl font-bold text-amber-900 mt-1">
          {formatRupiah(data.debt)}
        </div>
        <div className="text-xs text-amber-700 mt-1">
          = Total Modal Terjual − Total Dibayar
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <div className="p-4 border-b border-slate-200">
            <h3 className="font-semibold">Riwayat Stok Masuk</h3>
          </div>
          {stockEntries.length === 0 ? (
            <div className="p-6 text-sm text-slate-400">Belum ada stok masuk.</div>
          ) : (
            <Table>
              <THead>
                <TR>
                  <TH>Tanggal</TH>
                  <TH>Produk</TH>
                  <TH className="text-right">Qty</TH>
                  <TH className="text-right">Total</TH>
                </TR>
              </THead>
              <tbody>
                {stockEntries.map((e) => (
                  <TR key={e.id}>
                    <TD>{formatDate(e.date)}</TD>
                    <TD>{e.product.name}</TD>
                    <TD className="text-right">{e.qty}</TD>
                    <TD className="text-right">{formatRupiah(e.totalCost)}</TD>
                  </TR>
                ))}
              </tbody>
            </Table>
          )}
        </Card>

        <Card>
          <div className="p-4 border-b border-slate-200">
            <h3 className="font-semibold">Riwayat Barang Terjual</h3>
          </div>
          {soldItems.length === 0 ? (
            <div className="p-6 text-sm text-slate-400">
              Belum ada barang terjual.
            </div>
          ) : (
            <Table>
              <THead>
                <TR>
                  <TH>Invoice</TH>
                  <TH>Produk</TH>
                  <TH className="text-right">Qty</TH>
                  <TH className="text-right">Modal</TH>
                </TR>
              </THead>
              <tbody>
                {soldItems.map((it) => (
                  <TR key={it.id}>
                    <TD className="font-mono text-xs">{it.sale.invoiceNo}</TD>
                    <TD>{it.productNameSnapshot}</TD>
                    <TD className="text-right">{it.qty}</TD>
                    <TD className="text-right">
                      {formatRupiah(it.totalCostItem)}
                    </TD>
                  </TR>
                ))}
              </tbody>
            </Table>
          )}
        </Card>

        <Card className="lg:col-span-2">
          <div className="p-4 border-b border-slate-200">
            <h3 className="font-semibold">Riwayat Pembayaran</h3>
          </div>
          {payments.length === 0 ? (
            <div className="p-6 text-sm text-slate-400">
              Belum ada pembayaran.
            </div>
          ) : (
            <Table>
              <THead>
                <TR>
                  <TH>Tanggal</TH>
                  <TH>Metode</TH>
                  <TH>Catatan</TH>
                  <TH className="text-right">Jumlah</TH>
                </TR>
              </THead>
              <tbody>
                {payments.map((p) => (
                  <TR key={p.id}>
                    <TD>{formatDate(p.date)}</TD>
                    <TD>
                      <Badge variant="muted">{p.paymentMethod}</Badge>
                    </TD>
                    <TD className="text-slate-600">{p.notes || "-"}</TD>
                    <TD className="text-right font-medium">
                      {formatRupiah(p.amount)}
                    </TD>
                  </TR>
                ))}
              </tbody>
            </Table>
          )}
        </Card>
      </div>

      <div className="mt-8">
        <DeleteSupplierButton id={supplier.id} name={supplier.name} />
      </div>
    </>
  );
}
