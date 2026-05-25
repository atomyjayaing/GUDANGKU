import { prisma } from "@/lib/prisma";
import { Card, PageHeader } from "@/components/ui";
import { ProductForm } from "../product-form";
import { createProduct } from "../actions";

export default async function NewProductPage() {
  const suppliers = await prisma.supplier.findMany({
    orderBy: { name: "asc" },
    select: { id: true, name: true },
  });
  return (
    <>
      <PageHeader title="Tambah Produk" />
      <Card className="p-6">
        <ProductForm
          action={createProduct}
          suppliers={suppliers}
          submitLabel="Simpan Produk"
        />
      </Card>
    </>
  );
}
