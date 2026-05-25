"use server";

import { z } from "zod";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { writeAudit } from "@/lib/audit";
import { getCurrentUser } from "@/lib/session";

const StockEntrySchema = z.object({
  date: z.string().min(1, "Tanggal wajib diisi"),
  supplierId: z.string().min(1, "Supplier wajib dipilih"),
  productId: z.string().min(1, "Produk wajib dipilih"),
  qty: z.number().int().positive("Jumlah harus lebih dari 0"),
  costPricePerUnit: z.number().int().min(0, "Harga modal tidak boleh negatif"),
  refNo: z.string().trim().optional().nullable(),
  notes: z.string().trim().optional().nullable(),
});

export type ActionState = { error?: string | null };

export async function createStockEntry(
  _prev: ActionState,
  formData: FormData
): Promise<ActionState> {
  const num = (v: FormDataEntryValue | null) =>
    parseInt(String(v ?? "0").replace(/[^\d-]/g, ""), 10) || 0;

  const parsed = StockEntrySchema.safeParse({
    date: formData.get("date")?.toString() ?? "",
    supplierId: formData.get("supplierId")?.toString() ?? "",
    productId: formData.get("productId")?.toString() ?? "",
    qty: num(formData.get("qty")),
    costPricePerUnit: num(formData.get("costPricePerUnit")),
    refNo: formData.get("refNo")?.toString() || null,
    notes: formData.get("notes")?.toString() || null,
  });

  if (!parsed.success) {
    return { error: parsed.error.issues[0]?.message ?? "Data tidak valid" };
  }

  const data = parsed.data;
  const totalCost = data.qty * data.costPricePerUnit;

  // Pastikan product & supplier exist
  const [product, supplier] = await Promise.all([
    prisma.product.findUnique({ where: { id: data.productId } }),
    prisma.supplier.findUnique({ where: { id: data.supplierId } }),
  ]);
  if (!product) return { error: "Produk tidak ditemukan." };
  if (!supplier) return { error: "Supplier tidak ditemukan." };

  // Transaksi: buat StockEntry + naikkan stok produk
  const entry = await prisma.$transaction(async (tx) => {
    const created = await tx.stockEntry.create({
      data: {
        date: new Date(data.date),
        supplierId: data.supplierId,
        productId: data.productId,
        qty: data.qty,
        costPricePerUnit: data.costPricePerUnit,
        totalCost,
        refNo: data.refNo,
        notes: data.notes,
      },
    });
    await tx.product.update({
      where: { id: data.productId },
      data: { stock: { increment: data.qty } },
    });
    return created;
  });

  const user = await getCurrentUser();
  await writeAudit({
    userId: user?.id ?? null,
    action: "STOCK_IN",
    entityType: "StockEntry",
    entityId: entry.id,
    description: `Stok masuk: ${data.qty}x ${product.name} dari ${supplier.name}`,
    metadata: { totalCost, productId: data.productId, supplierId: data.supplierId },
  });

  revalidatePath("/stock-entries");
  revalidatePath("/products");
  revalidatePath(`/products/${data.productId}`);
  revalidatePath(`/suppliers/${data.supplierId}`);
  revalidatePath("/dashboard");
  redirect("/stock-entries");
}
