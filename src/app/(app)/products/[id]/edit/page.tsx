import { notFound } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { Card, PageHeader } from "@/components/ui";
import { ProductForm } from "../../product-form";
import { updateProduct, type ActionState } from "../../actions";

export default async function EditProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const [product, suppliers] = await Promise.all([
    prisma.product.findUnique({ where: { id } }),
    prisma.supplier.findMany({
      orderBy: { name: "asc" },
      select: { id: true, name: true },
    }),
  ]);
  if (!product) notFound();

  const action = async (prev: ActionState, fd: FormData) =>
    updateProduct(id, prev, fd);

  return (
    <>
      <PageHeader title={`Edit Produk: ${product.name}`} />
      <Card className="p-6">
        <ProductForm
          action={action}
          initial={product}
          suppliers={suppliers}
          submitLabel="Update Produk"
        />
      </Card>
    </>
  );
}
