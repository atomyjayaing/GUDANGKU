"use server";

import { z } from "zod";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { writeAudit } from "@/lib/audit";
import { getCurrentUser } from "@/lib/session";

const ProductSchema = z.object({
  sku: z.string().trim().min(1, "SKU wajib diisi").max(64),
  name: z.string().trim().min(1, "Nama produk wajib diisi"),
  category: z.string().trim().optional().nullable(),
  brand: z.string().trim().optional().nullable(),
  model: z.string().trim().optional().nullable(),
  defaultSupplierId: z.string().optional().nullable(),
  costPrice: z.number().int().min(0, "Harga modal tidak boleh negatif"),
  sellPrice: z.number().int().min(0, "Harga jual tidak boleh negatif"),
  status: z.enum(["ACTIVE", "INACTIVE"]),
  notes: z.string().trim().optional().nullable(),
});

export type ActionState = { error?: string | null };

function parseProduct(formData: FormData) {
  const num = (v: FormDataEntryValue | null) =>
    parseInt(String(v ?? "0").replace(/[^\d-]/g, ""), 10) || 0;
  return ProductSchema.safeParse({
    sku: formData.get("sku")?.toString() ?? "",
    name: formData.get("name")?.toString() ?? "",
    category: formData.get("category")?.toString() || null,
    brand: formData.get("brand")?.toString() || null,
    model: formData.get("model")?.toString() || null,
    defaultSupplierId: formData.get("defaultSupplierId")?.toString() || null,
    costPrice: num(formData.get("costPrice")),
    sellPrice: num(formData.get("sellPrice")),
    status: (formData.get("status")?.toString() as "ACTIVE" | "INACTIVE") || "ACTIVE",
    notes: formData.get("notes")?.toString() || null,
  });
}

export async function createProduct(
  _prev: ActionState,
  formData: FormData
): Promise<ActionState> {
  const parsed = parseProduct(formData);
  if (!parsed.success) {
    return { error: parsed.error.issues[0]?.message ?? "Data tidak valid" };
  }
  const exists = await prisma.product.findUnique({ where: { sku: parsed.data.sku } });
  if (exists) return { error: `SKU "${parsed.data.sku}" sudah dipakai produk lain.` };

  const product = await prisma.product.create({
    data: { ...parsed.data, stock: 0 },
  });
  const user = await getCurrentUser();
  await writeAudit({
    userId: user?.id ?? null,
    action: "CREATE",
    entityType: "Product",
    entityId: product.id,
    description: `Tambah produk "${product.name}" (${product.sku})`,
  });
  revalidatePath("/products");
  redirect(`/products/${product.id}`);
}

export async function updateProduct(
  id: string,
  _prev: ActionState,
  formData: FormData
): Promise<ActionState> {
  const parsed = parseProduct(formData);
  if (!parsed.success) {
    return { error: parsed.error.issues[0]?.message ?? "Data tidak valid" };
  }
  const conflict = await prisma.product.findFirst({
    where: { sku: parsed.data.sku, NOT: { id } },
  });
  if (conflict) return { error: `SKU "${parsed.data.sku}" sudah dipakai produk lain.` };

  await prisma.product.update({ where: { id }, data: parsed.data });
  const user = await getCurrentUser();
  await writeAudit({
    userId: user?.id ?? null,
    action: "UPDATE",
    entityType: "Product",
    entityId: id,
    description: `Edit produk "${parsed.data.name}"`,
  });
  revalidatePath("/products");
  revalidatePath(`/products/${id}`);
  redirect(`/products/${id}`);
}

export async function setProductStatus(id: string, status: "ACTIVE" | "INACTIVE") {
  const product = await prisma.product.update({
    where: { id },
    data: { status },
  });
  const user = await getCurrentUser();
  await writeAudit({
    userId: user?.id ?? null,
    action: status === "ACTIVE" ? "ACTIVATE" : "DEACTIVATE",
    entityType: "Product",
    entityId: id,
    description: `${status === "ACTIVE" ? "Aktifkan" : "Nonaktifkan"} produk "${product.name}"`,
  });
  revalidatePath("/products");
  revalidatePath(`/products/${id}`);
}

export async function deleteProduct(id: string) {
  const used =
    (await prisma.stockEntry.count({ where: { productId: id } })) +
    (await prisma.saleItem.count({ where: { productId: id } }));
  if (used > 0) {
    throw new Error(
      "Produk sudah punya transaksi. Gunakan tombol 'Nonaktifkan' alih-alih hapus permanen."
    );
  }
  const product = await prisma.product.findUnique({ where: { id } });
  await prisma.product.delete({ where: { id } });
  const user = await getCurrentUser();
  await writeAudit({
    userId: user?.id ?? null,
    action: "DELETE",
    entityType: "Product",
    entityId: id,
    description: `Hapus produk "${product?.name ?? id}"`,
  });
  revalidatePath("/products");
  redirect("/products");
}
