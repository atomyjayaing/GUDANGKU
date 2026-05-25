import Link from "next/link";
import { prisma } from "@/lib/prisma";
import { Card, PageHeader, EmptyState, Button } from "@/components/ui";
import { PaymentForm } from "./payment-form";

export const dynamic = "force-dynamic";

async function getSuppliersWithDebt() {
  const suppliers = await prisma.supplier.findMany({ orderBy: { name: "asc" } });
  const stats = await prisma.$queryRaw<
    Array<{ supplierId: string; totalCost: number; totalPaid: number }>
  >`
    SELECT
      s.id AS supplierId,
      COALESCE((SELECT SUM(totalCostItem) FROM SaleItem WHERE supplierId = s.id), 0) AS totalCost,
      COALESCE((SELECT SUM(amount) FROM SupplierPayment WHERE supplierId = s.id), 0) AS totalPaid
    FROM Supplier s
  `;
  const m = new Map(stats.map((r) => [r.supplierId, r]));
  return suppliers.map((s) => {
    const st = m.get(s.id);
    const debt = Math.max(0, Number(st?.totalCost ?? 0) - Number(st?.totalPaid ?? 0));
    return { id: s.id, name: s.name, debt };
  });
}

export default async function NewSupplierPaymentPage({
  searchParams,
}: {
  searchParams: Promise<{ supplierId?: string }>;
}) {
  const sp = await searchParams;
  const suppliers = await getSuppliersWithDebt();

  return (
    <>
      <PageHeader title="Catat Pembayaran Supplier" />
      {suppliers.length === 0 ? (
        <Card>
          <EmptyState
            title="Belum ada supplier"
            description="Tambah supplier terlebih dahulu."
            action={
              <Link href="/suppliers/new">
                <Button>+ Tambah Supplier</Button>
              </Link>
            }
          />
        </Card>
      ) : (
        <Card className="p-6">
          <PaymentForm suppliers={suppliers} defaultSupplierId={sp.supplierId} />
        </Card>
      )}
    </>
  );
}
