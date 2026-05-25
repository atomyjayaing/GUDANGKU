import Link from "next/link";
import { prisma } from "@/lib/prisma";
import { Button, Card, PageHeader, EmptyState } from "@/components/ui";
import { Table, THead, TR, TH, TD } from "@/components/table";
import { formatRupiah, formatDate } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function StockEntriesPage() {
  const entries = await prisma.stockEntry.findMany({
    orderBy: { date: "desc" },
    take: 200,
    include: {
      supplier: { select: { name: true, id: true } },
      product: { select: { name: true, sku: true, id: true } },
    },
  });

  const totalValue = entries.reduce((sum, e) => sum + e.totalCost, 0);

  return (
    <>
      <PageHeader
        title="Stok Masuk"
        description={`${entries.length} catatan • Total nilai: ${formatRupiah(totalValue)}`}
        action={
          <Link href="/stock-entries/new">
            <Button>+ Catat Stok Masuk</Button>
          </Link>
        }
      />

      <Card>
        {entries.length === 0 ? (
          <EmptyState
            title="Belum ada stok masuk"
            description="Catat penerimaan barang dari supplier untuk menambah stok produk."
            action={
              <Link href="/stock-entries/new">
                <Button>+ Catat Stok Masuk</Button>
              </Link>
            }
          />
        ) : (
          <Table>
            <THead>
              <TR>
                <TH>Tanggal</TH>
                <TH>Produk</TH>
                <TH>Supplier</TH>
                <TH className="text-right">Qty</TH>
                <TH className="text-right">Modal/Unit</TH>
                <TH className="text-right">Total</TH>
                <TH>Ref</TH>
              </TR>
            </THead>
            <tbody>
              {entries.map((e) => (
                <TR key={e.id}>
                  <TD>{formatDate(e.date)}</TD>
                  <TD>
                    <Link
                      href={`/products/${e.product.id}`}
                      className="font-medium hover:underline"
                    >
                      {e.product.name}
                    </Link>
                    <div className="text-xs text-slate-500 font-mono">
                      {e.product.sku}
                    </div>
                  </TD>
                  <TD>
                    <Link
                      href={`/suppliers/${e.supplier.id}`}
                      className="hover:underline"
                    >
                      {e.supplier.name}
                    </Link>
                  </TD>
                  <TD className="text-right">{e.qty}</TD>
                  <TD className="text-right">{formatRupiah(e.costPricePerUnit)}</TD>
                  <TD className="text-right font-medium">
                    {formatRupiah(e.totalCost)}
                  </TD>
                  <TD className="text-xs text-slate-500">{e.refNo || "-"}</TD>
                </TR>
              ))}
            </tbody>
          </Table>
        )}
      </Card>
    </>
  );
}
