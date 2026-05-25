import Link from "next/link";
import { prisma } from "@/lib/prisma";
import { Button, Card, PageHeader } from "@/components/ui";
import { Table, THead, TR, TH, TD } from "@/components/table";
import { formatRupiah } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function SupplierDebtReportPage() {
  const rows = await prisma.$queryRaw<
    Array<{
      id: string;
      name: string;
      totalCost: number;
      totalPaid: number;
    }>
  >`
    SELECT
      s.id AS id,
      s.name AS name,
      COALESCE((SELECT SUM(totalCostItem) FROM SaleItem WHERE supplierId = s.id), 0) AS totalCost,
      COALESCE((SELECT SUM(amount) FROM SupplierPayment WHERE supplierId = s.id), 0) AS totalPaid
    FROM Supplier s
    ORDER BY s.name ASC
  `;

  const data = rows.map((r) => {
    const cost = Number(r.totalCost);
    const paid = Number(r.totalPaid);
    return {
      id: r.id,
      name: r.name,
      totalCost: cost,
      totalPaid: paid,
      debt: Math.max(0, cost - paid),
    };
  });

  const totals = data.reduce(
    (a, r) => ({
      cost: a.cost + r.totalCost,
      paid: a.paid + r.totalPaid,
      debt: a.debt + r.debt,
    }),
    { cost: 0, paid: 0, debt: 0 }
  );

  return (
    <>
      <PageHeader
        title="Laporan Hutang Supplier"
        description="Sisa kewajiban per supplier (modal terjual − pembayaran)"
        action={
          <a href="/api/reports/supplier-debt">
            <Button variant="secondary">⬇ Export CSV</Button>
          </a>
        }
      />

      <div className="grid grid-cols-3 gap-3 mb-4">
        <Card className="p-4">
          <div className="text-xs uppercase text-slate-500">
            Total Modal Terjual
          </div>
          <div className="text-lg font-bold">{formatRupiah(totals.cost)}</div>
        </Card>
        <Card className="p-4">
          <div className="text-xs uppercase text-slate-500">Total Dibayar</div>
          <div className="text-lg font-bold">{formatRupiah(totals.paid)}</div>
        </Card>
        <Card className="p-4 bg-amber-50 border-amber-200">
          <div className="text-xs uppercase text-amber-700">
            Total Sisa Hutang
          </div>
          <div className="text-lg font-bold text-amber-900">
            {formatRupiah(totals.debt)}
          </div>
        </Card>
      </div>

      <Card>
        <Table>
          <THead>
            <TR>
              <TH>Supplier</TH>
              <TH className="text-right">Modal Terjual</TH>
              <TH className="text-right">Total Dibayar</TH>
              <TH className="text-right">Sisa Hutang</TH>
              <TH></TH>
            </TR>
          </THead>
          <tbody>
            {data.map((r) => (
              <TR key={r.id}>
                <TD>
                  <Link
                    href={`/suppliers/${r.id}`}
                    className="font-medium hover:underline"
                  >
                    {r.name}
                  </Link>
                </TD>
                <TD className="text-right">{formatRupiah(r.totalCost)}</TD>
                <TD className="text-right">{formatRupiah(r.totalPaid)}</TD>
                <TD className="text-right font-semibold">
                  {formatRupiah(r.debt)}
                </TD>
                <TD>
                  {r.debt > 0 && (
                    <Link
                      href={`/supplier-payments/new?supplierId=${r.id}`}
                      className="text-xs text-slate-700 hover:text-slate-900 underline"
                    >
                      Bayar →
                    </Link>
                  )}
                </TD>
              </TR>
            ))}
          </tbody>
        </Table>
      </Card>
    </>
  );
}
