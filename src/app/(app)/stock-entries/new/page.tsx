import Link from "next/link";
import { prisma } from "@/lib/prisma";
import { Card, PageHeader, Button, EmptyState } from "@/components/ui";
import { StockEntryForm } from "../stock-entry-form";
import { createStockEntry } from "../actions";

export default async function NewStockEntryPage() {
  const [suppliers, products] = await Promise.all([
    prisma.supplier.findMany({
      orderBy: { name: "asc" },
      select: { id: true, name: true },
    }),
    prisma.product.findMany({
      where: { status: "ACTIVE" },
      orderBy: { name: "asc" },
      select: { id: true, name: true, sku: true, costPrice: true, defaultSupplierId: true },
    }),
  ]);

  return (
    <>
      <PageHeader title="Catat Stok Masuk" />

      {suppliers.length === 0 || products.length === 0 ? (
        <Card>
          <EmptyState
            title="Data master belum lengkap"
            description={
              suppliers.length === 0
                ? "Tambah minimal 1 supplier terlebih dulu."
                : "Tambah minimal 1 produk terlebih dulu."
            }
            action={
              <Link href={suppliers.length === 0 ? "/suppliers/new" : "/products/new"}>
                <Button>
                  {suppliers.length === 0 ? "+ Tambah Supplier" : "+ Tambah Produk"}
                </Button>
              </Link>
            }
          />
        </Card>
      ) : (
        <Card className="p-6">
          <StockEntryForm
            action={createStockEntry}
            suppliers={suppliers}
            products={products}
          />
        </Card>
      )}
    </>
  );
}
