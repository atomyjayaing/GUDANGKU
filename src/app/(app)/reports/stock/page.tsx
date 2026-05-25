import { prisma } from "@/lib/prisma";
import { Button, Card, PageHeader, Badge } from "@/components/ui";
import { Table, THead, TR, TH, TD } from "@/components/table";
import { formatRupiah } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function StockReportPage() {
  const products = await prisma.product.findMany({
    orderBy: { name: "asc" },
    include: { defaultSupplier: { select: { name: true } } },
  });

  const totalUnits = products.reduce((s, p) => s + p.stock, 0);
  const totalValue = products.reduce((s, p) => s + p.stock * p.costPrice, 0);

  return (
    <>
      <PageHeader
        title="Laporan Stok Tersisa"
        description={`${products.length} produk • ${totalUnits} unit • Nilai: ${formatRupiah(totalValue)}`}
        action={
          <a href="/api/reports/stock">
            <Button variant="secondary">⬇ Export CSV</Button>
          </a>
        }
      />

      <Card>
        <Table>
          <THead>
            <TR>
              <TH>SKU</TH>
              <TH>Nama</TH>
              <TH>Kategori</TH>
              <TH>Brand</TH>
              <TH>Supplier Default</TH>
              <TH className="text-right">Stok</TH>
              <TH className="text-right">Modal/Unit</TH>
              <TH className="text-right">Nilai Stok</TH>
              <TH>Status</TH>
            </TR>
          </THead>
          <tbody>
            {products.map((p) => (
              <TR key={p.id}>
                <TD className="font-mono text-xs">{p.sku}</TD>
                <TD>{p.name}</TD>
                <TD className="text-slate-600">{p.category || "-"}</TD>
                <TD className="text-slate-600">{p.brand || "-"}</TD>
                <TD className="text-slate-600">{p.defaultSupplier?.name || "-"}</TD>
                <TD className="text-right">
                  <Badge
                    variant={
                      p.stock === 0 ? "danger" : p.stock <= 2 ? "warning" : "muted"
                    }
                  >
                    {p.stock}
                  </Badge>
                </TD>
                <TD className="text-right">{formatRupiah(p.costPrice)}</TD>
                <TD className="text-right font-medium">
                  {formatRupiah(p.stock * p.costPrice)}
                </TD>
                <TD>
                  <Badge variant={p.status === "ACTIVE" ? "success" : "muted"}>
                    {p.status === "ACTIVE" ? "Aktif" : "Nonaktif"}
                  </Badge>
                </TD>
              </TR>
            ))}
          </tbody>
        </Table>
      </Card>
    </>
  );
}
