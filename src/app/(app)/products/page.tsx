import Link from "next/link";
import { prisma } from "@/lib/prisma";
import { Button, Card, PageHeader, EmptyState, Badge, Input } from "@/components/ui";
import { Table, THead, TR, TH, TD } from "@/components/table";
import { formatRupiah } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function ProductsPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; status?: string }>;
}) {
  const sp = await searchParams;
  const q = sp.q?.trim() || "";
  const status = sp.status === "INACTIVE" ? "INACTIVE" : sp.status === "ALL" ? null : "ACTIVE";

  const where: Parameters<typeof prisma.product.findMany>[0] extends infer P
    ? P extends { where?: infer W }
      ? W
      : never
    : never = {
    ...(status ? { status } : {}),
    ...(q
      ? {
          OR: [
            { name: { contains: q } },
            { sku: { contains: q } },
            { brand: { contains: q } },
            { category: { contains: q } },
          ],
        }
      : {}),
  };

  const products = await prisma.product.findMany({
    where,
    orderBy: { name: "asc" },
    include: { defaultSupplier: { select: { name: true } } },
    take: 500,
  });

  return (
    <>
      <PageHeader
        title="Produk"
        description={`${products.length} produk ditampilkan`}
        action={
          <Link href="/products/new">
            <Button>+ Tambah Produk</Button>
          </Link>
        }
      />

      <Card className="p-4 mb-4">
        <form className="flex flex-col sm:flex-row gap-2" method="get">
          <Input
            name="q"
            placeholder="Cari nama, SKU, brand, kategori..."
            defaultValue={q}
            className="sm:max-w-sm"
          />
          <select
            name="status"
            defaultValue={sp.status || "ACTIVE"}
            className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
          >
            <option value="ACTIVE">Hanya Aktif</option>
            <option value="INACTIVE">Hanya Nonaktif</option>
            <option value="ALL">Semua</option>
          </select>
          <Button type="submit" variant="secondary">
            Cari
          </Button>
        </form>
      </Card>

      <Card>
        {products.length === 0 ? (
          <EmptyState
            title="Tidak ada produk"
            description={q ? `Tidak ada hasil untuk "${q}"` : "Tambahkan produk pertama Anda."}
            action={
              <Link href="/products/new">
                <Button>+ Tambah Produk</Button>
              </Link>
            }
          />
        ) : (
          <Table>
            <THead>
              <TR>
                <TH>SKU</TH>
                <TH>Nama Produk</TH>
                <TH>Kategori</TH>
                <TH>Supplier Default</TH>
                <TH className="text-right">Modal</TH>
                <TH className="text-right">Jual</TH>
                <TH className="text-right">Stok</TH>
                <TH>Status</TH>
              </TR>
            </THead>
            <tbody>
              {products.map((p) => (
                <TR key={p.id}>
                  <TD className="font-mono text-xs">{p.sku}</TD>
                  <TD>
                    <Link
                      href={`/products/${p.id}`}
                      className="font-medium text-slate-900 hover:underline"
                    >
                      {p.name}
                    </Link>
                    {p.brand && (
                      <div className="text-xs text-slate-500">{p.brand} {p.model || ""}</div>
                    )}
                  </TD>
                  <TD className="text-slate-600">{p.category || "-"}</TD>
                  <TD className="text-slate-600">{p.defaultSupplier?.name || "-"}</TD>
                  <TD className="text-right">{formatRupiah(p.costPrice)}</TD>
                  <TD className="text-right">{formatRupiah(p.sellPrice)}</TD>
                  <TD className="text-right">
                    <Badge
                      variant={
                        p.stock === 0 ? "danger" : p.stock <= 2 ? "warning" : "muted"
                      }
                    >
                      {p.stock}
                    </Badge>
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
        )}
      </Card>
    </>
  );
}
