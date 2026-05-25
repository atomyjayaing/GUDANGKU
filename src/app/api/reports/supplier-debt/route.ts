import { prisma } from "@/lib/prisma";
import { toCSV, csvResponse } from "@/lib/csv";
import { getCurrentUser } from "@/lib/session";

export async function GET() {
  const user = await getCurrentUser();
  if (!user) return new Response("Unauthorized", { status: 401 });

  const rows = await prisma.$queryRaw<
    Array<{
      name: string;
      totalCost: number;
      totalPaid: number;
    }>
  >`
    SELECT
      s.name AS name,
      COALESCE((SELECT SUM(totalCostItem) FROM SaleItem WHERE supplierId = s.id), 0) AS totalCost,
      COALESCE((SELECT SUM(amount) FROM SupplierPayment WHERE supplierId = s.id), 0) AS totalPaid
    FROM Supplier s
    ORDER BY s.name ASC
  `;

  const out = rows.map((r) => {
    const cost = Number(r.totalCost);
    const paid = Number(r.totalPaid);
    return [r.name, cost, paid, Math.max(0, cost - paid)];
  });

  const csv = toCSV(
    ["Supplier", "Total Modal Terjual", "Total Dibayar", "Sisa Hutang"],
    out
  );
  return csvResponse(`laporan-hutang-supplier-${Date.now()}.csv`, csv);
}
