import { Card, PageHeader } from "@/components/ui";
import { SupplierForm } from "../supplier-form";
import { createSupplier } from "../actions";

export default function NewSupplierPage() {
  return (
    <>
      <PageHeader title="Tambah Supplier" />
      <Card className="p-6">
        <SupplierForm action={createSupplier} submitLabel="Simpan Supplier" />
      </Card>
    </>
  );
}
