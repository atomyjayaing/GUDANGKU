import { prisma } from "@/lib/prisma";
import { toCSV, csvResponse } from "@/lib/csv";
import { getCurrentUser } from "@/lib/session";

export async function GET() {
  const user = await getCurrentUser();
  if (!user) return new Response("Unauthorized", { status: 401 });

  const products = await prisma.product.findMany({
    orderBy: { name: "asc" },
    include: { defaultSupplier: { select: { name: true } } },
  });

  const rows = products.map((p) => [
    p.sku,
    p.name,
    p.category ?? "",
    p.brand ?? "",
    p.stock,
    p.costPrice,
    p.stock * p.costPrice,
    p.defaultSupplier?.name ?? "",
    p.status,
  ]);

  const csv = toCSV(
    [
      "SKU",
      "Nama Produk",
      "Kategori",
      "Brand",
      "Stok",
      "Harga Modal",
      "Nilai Stok",
      "Supplier Default",
      "Status",
    ],
    rows
  );
  return csvResponse(`laporan-stok-${Date.now()}.csv`, csv);
}
