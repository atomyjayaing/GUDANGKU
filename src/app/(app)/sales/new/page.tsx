import Link from "next/link";
import { prisma } from "@/lib/prisma";
import { Card, PageHeader, Button, EmptyState } from "@/components/ui";
import { SaleForm } from "./sale-form";

export const dynamic = "force-dynamic";

export default async function NewSalePage() {
  const products = await prisma.product.findMany({
    where: { status: "ACTIVE" },
    orderBy: { name: "asc" },
    select: {
      id: true,
      sku: true,
      name: true,
      costPrice: true,
      sellPrice: true,
      stock: true,
      defaultSupplierId: true,
    },
  });

  const inStock = products.filter((p) => p.stock > 0);

  return (
    <>
      <PageHeader title="Penjualan Baru" />
      {inStock.length === 0 ? (
        <Card>
          <EmptyState
            title="Tidak ada produk dengan stok tersedia"
            description="Catat stok masuk dari supplier terlebih dahulu."
            action={
              <Link href="/stock-entries/new">
                <Button>+ Catat Stok Masuk</Button>
              </Link>
            }
          />
        </Card>
      ) : (
        <SaleForm products={products} />
      )}
    </>
  );
}
