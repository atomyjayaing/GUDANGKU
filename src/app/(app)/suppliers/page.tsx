import Link from "next/link";
import { prisma } from "@/lib/prisma";
import { Button, Card, PageHeader, EmptyState } from "@/components/ui";
import { Table, THead, TR, TH, TD } from "@/components/table";
import { formatRupiah } from "@/lib/utils";

export const dynamic = "force-dynamic";

async function getSuppliersWithStats() {
  const suppliers = await prisma.supplier.findMany({
    orderBy: { name: "asc" },
  });
  const stats = await prisma.$queryRaw<
    Array<{ supplierId: string; totalCost: number; totalPaid: number }>
  >`
    SELECT
      s.id AS supplierId,
      COALESCE((SELECT SUM(totalCostItem) FROM SaleItem WHERE supplierId = s.id), 0) AS totalCost,
      COALESCE((SELECT SUM(amount) FROM SupplierPayment WHERE supplierId = s.id), 0) AS totalPaid
    FROM Supplier s
  `;
  const statMap = new Map(stats.map((r) => [r.supplierId, r]));
  return suppliers.map((s) => {
    const st = statMap.get(s.id);
    const totalCost = Number(st?.totalCost ?? 0);
    const totalPaid = Number(st?.totalPaid ?? 0);
    return { ...s, totalCost, totalPaid, debt: Math.max(0, totalCost - totalPaid) };
  });
}

export default async function SuppliersPage() {
  const suppliers = await getSuppliersWithStats();
  return (
    <>
      <PageHeader
        title="Supplier / Agen"
        description={`${suppliers.length} supplier terdaftar`}
        action={
          <Link href="/suppliers/new">
            <Button>+ Tambah Supplier</Button>
          </Link>
        }
      />

      <Card>
        {suppliers.length === 0 ? (
          <EmptyState
            title="Belum ada supplier"
            description="Mulai dengan menambah supplier/agen pertama Anda."
            action={
              <Link href="/suppliers/new">
                <Button>+ Tambah Supplier</Button>
              </Link>
            }
          />
        ) : (
          <Table>
            <THead>
              <TR>
                <TH>Nama Supplier</TH>
                <TH>HP</TH>
                <TH className="text-right">Total Modal Terjual</TH>
                <TH className="text-right">Total Dibayar</TH>
                <TH className="text-right">Sisa Hutang</TH>
              </TR>
            </THead>
            <tbody>
              {suppliers.map((s) => (
                <TR key={s.id}>
                  <TD>
                    <Link
                      href={`/suppliers/${s.id}`}
                      className="font-medium text-slate-900 hover:underline"
                    >
                      {s.name}
                    </Link>
                  </TD>
                  <TD className="text-slate-600">{s.phone || "-"}</TD>
                  <TD className="text-right">{formatRupiah(s.totalCost)}</TD>
                  <TD className="text-right">{formatRupiah(s.totalPaid)}</TD>
                  <TD className="text-right font-semibold">
                    {formatRupiah(s.debt)}
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
