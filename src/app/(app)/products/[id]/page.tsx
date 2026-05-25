import Link from "next/link";
import { notFound } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { Button, Card, PageHeader, Badge } from "@/components/ui";
import { Table, THead, TR, TH, TD } from "@/components/table";
import { formatRupiah, formatDate } from "@/lib/utils";
import { ProductActions } from "./product-actions";

export const dynamic = "force-dynamic";

export default async function ProductDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const product = await prisma.product.findUnique({
    where: { id },
    include: { defaultSupplier: true },
  });
  if (!product) notFound();

  const [stockEntries, saleItems, totals] = await Promise.all([
    prisma.stockEntry.findMany({
      where: { productId: id },
      orderBy: { date: "desc" },
      take: 20,
      include: { supplier: { select: { name: true } } },
    }),
    prisma.saleItem.findMany({
      where: { productId: id },
      orderBy: { createdAt: "desc" },
      take: 20,
      include: { sale: { select: { invoiceNo: true, date: true } } },
    }),
    prisma.saleItem.aggregate({
      where: { productId: id },
      _sum: { qty: true, subtotalItem: true, grossProfitItem: true },
    }),
  ]);

  return (
    <>
      <PageHeader
        title={product.name}
        description={`SKU: ${product.sku}`}
        action={
          <div className="flex gap-2">
            <Link href={`/products/${product.id}/edit`}>
              <Button variant="secondary">Edit</Button>
            </Link>
            <Link href="/stock-entries/new">
              <Button>+ Stok Masuk</Button>
            </Link>
          </div>
        }
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <Card className="p-4">
          <div className="text-xs uppercase text-slate-500">Stok Saat Ini</div>
          <div className="text-2xl font-bold mt-1">
            <Badge
              variant={
                product.stock === 0
                  ? "danger"
                  : product.stock <= 2
                  ? "warning"
                  : "success"
              }
            >
              {product.stock} unit
            </Badge>
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-xs uppercase text-slate-500">Harga Modal</div>
          <div className="text-lg font-bold mt-1">
            {formatRupiah(product.costPrice)}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-xs uppercase text-slate-500">Harga Jual</div>
          <div className="text-lg font-bold mt-1">
            {formatRupiah(product.sellPrice)}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-xs uppercase text-slate-500">Status</div>
          <div className="mt-2">
            <Badge variant={product.status === "ACTIVE" ? "success" : "muted"}>
              {product.status === "ACTIVE" ? "Aktif" : "Nonaktif"}
            </Badge>
          </div>
        </Card>
      </div>

      <Card className="p-5 mb-6">
        <h3 className="font-semibold mb-2">Info Produk</h3>
        <dl className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
          <div>
            <dt className="text-slate-500">Kategori</dt>
            <dd>{product.category || "-"}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Brand</dt>
            <dd>{product.brand || "-"}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Model</dt>
            <dd>{product.model || "-"}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Supplier Default</dt>
            <dd>{product.defaultSupplier?.name || "-"}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Total Qty Terjual</dt>
            <dd>{totals._sum.qty ?? 0} unit</dd>
          </div>
          <div>
            <dt className="text-slate-500">Total Laba Kasar</dt>
            <dd className="font-medium">
              {formatRupiah(totals._sum.grossProfitItem ?? 0)}
            </dd>
          </div>
        </dl>
        {product.notes && (
          <p className="text-sm text-slate-500 italic mt-3 pt-3 border-t border-slate-100">
            "{product.notes}"
          </p>
        )}
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
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
                  <TH>Supplier</TH>
                  <TH className="text-right">Qty</TH>
                  <TH className="text-right">Modal/Unit</TH>
                </TR>
              </THead>
              <tbody>
                {stockEntries.map((e) => (
                  <TR key={e.id}>
                    <TD>{formatDate(e.date)}</TD>
                    <TD>{e.supplier.name}</TD>
                    <TD className="text-right">{e.qty}</TD>
                    <TD className="text-right">
                      {formatRupiah(e.costPricePerUnit)}
                    </TD>
                  </TR>
                ))}
              </tbody>
            </Table>
          )}
        </Card>

        <Card>
          <div className="p-4 border-b border-slate-200">
            <h3 className="font-semibold">Riwayat Penjualan</h3>
          </div>
          {saleItems.length === 0 ? (
            <div className="p-6 text-sm text-slate-400">Belum ada penjualan.</div>
          ) : (
            <Table>
              <THead>
                <TR>
                  <TH>Invoice</TH>
                  <TH>Tanggal</TH>
                  <TH className="text-right">Qty</TH>
                  <TH className="text-right">Harga</TH>
                </TR>
              </THead>
              <tbody>
                {saleItems.map((it) => (
                  <TR key={it.id}>
                    <TD className="font-mono text-xs">{it.sale.invoiceNo}</TD>
                    <TD>{formatDate(it.sale.date)}</TD>
                    <TD className="text-right">{it.qty}</TD>
                    <TD className="text-right">
                      {formatRupiah(it.sellPriceActual)}
                    </TD>
                  </TR>
                ))}
              </tbody>
            </Table>
          )}
        </Card>
      </div>

      <ProductActions id={product.id} status={product.status} name={product.name} />
    </>
  );
}
