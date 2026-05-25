import { notFound } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { Card, PageHeader } from "@/components/ui";
import { SupplierForm } from "../../supplier-form";
import { updateSupplier, type ActionState } from "../../actions";

export default async function EditSupplierPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const supplier = await prisma.supplier.findUnique({ where: { id } });
  if (!supplier) notFound();

  const action = async (prev: ActionState, fd: FormData) =>
    updateSupplier(id, prev, fd);

  return (
    <>
      <PageHeader title={`Edit Supplier: ${supplier.name}`} />
      <Card className="p-6">
        <SupplierForm action={action} initial={supplier} submitLabel="Update" />
      </Card>
    </>
  );
}
