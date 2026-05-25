"use server";

import { z } from "zod";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { writeAudit } from "@/lib/audit";
import { getCurrentUser } from "@/lib/session";

const SupplierSchema = z.object({
  name: z.string().trim().min(1, "Nama supplier wajib diisi"),
  phone: z.string().trim().optional().nullable(),
  address: z.string().trim().optional().nullable(),
  notes: z.string().trim().optional().nullable(),
});

export type ActionState = { error?: string | null; ok?: boolean };

function parseSupplier(formData: FormData) {
  return SupplierSchema.safeParse({
    name: formData.get("name")?.toString() ?? "",
    phone: formData.get("phone")?.toString() || null,
    address: formData.get("address")?.toString() || null,
    notes: formData.get("notes")?.toString() || null,
  });
}

export async function createSupplier(
  _prev: ActionState,
  formData: FormData
): Promise<ActionState> {
  const parsed = parseSupplier(formData);
  if (!parsed.success) {
    return { error: parsed.error.issues[0]?.message ?? "Data tidak valid" };
  }
  const user = await getCurrentUser();
  const supplier = await prisma.supplier.create({ data: parsed.data });
  await writeAudit({
    userId: user?.id ?? null,
    action: "CREATE",
    entityType: "Supplier",
    entityId: supplier.id,
    description: `Tambah supplier "${supplier.name}"`,
  });
  revalidatePath("/suppliers");
  redirect(`/suppliers/${supplier.id}`);
}

export async function updateSupplier(
  id: string,
  _prev: ActionState,
  formData: FormData
): Promise<ActionState> {
  const parsed = parseSupplier(formData);
  if (!parsed.success) {
    return { error: parsed.error.issues[0]?.message ?? "Data tidak valid" };
  }
  await prisma.supplier.update({ where: { id }, data: parsed.data });
  const user = await getCurrentUser();
  await writeAudit({
    userId: user?.id ?? null,
    action: "UPDATE",
    entityType: "Supplier",
    entityId: id,
    description: `Edit supplier "${parsed.data.name}"`,
  });
  revalidatePath("/suppliers");
  revalidatePath(`/suppliers/${id}`);
  redirect(`/suppliers/${id}`);
}

export async function deleteSupplier(id: string) {
  const used =
    (await prisma.product.count({ where: { defaultSupplierId: id } })) +
    (await prisma.stockEntry.count({ where: { supplierId: id } })) +
    (await prisma.saleItem.count({ where: { supplierId: id } })) +
    (await prisma.supplierPayment.count({ where: { supplierId: id } }));
  if (used > 0) {
    throw new Error(
      "Supplier tidak bisa dihapus karena sudah punya data transaksi/produk."
    );
  }
  const supplier = await prisma.supplier.findUnique({ where: { id } });
  await prisma.supplier.delete({ where: { id } });
  const user = await getCurrentUser();
  await writeAudit({
    userId: user?.id ?? null,
    action: "DELETE",
    entityType: "Supplier",
    entityId: id,
    description: `Hapus supplier "${supplier?.name ?? id}"`,
  });
  revalidatePath("/suppliers");
  redirect("/suppliers");
}
