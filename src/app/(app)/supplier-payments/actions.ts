"use server";

import { z } from "zod";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { writeAudit } from "@/lib/audit";
import { getCurrentUser } from "@/lib/session";
import { SUPPLIER_PAYMENT_METHODS } from "@/lib/utils";

const PaymentSchema = z.object({
  date: z.string().min(1, "Tanggal wajib diisi"),
  supplierId: z.string().min(1, "Supplier wajib dipilih"),
  amount: z.number().int().positive("Jumlah harus lebih dari 0"),
  paymentMethod: z.enum(SUPPLIER_PAYMENT_METHODS),
  notes: z.string().trim().optional().nullable(),
  confirmOverpay: z.string().optional().nullable(),
});

export type ActionState = { error?: string | null; warning?: string | null };

export async function createSupplierPayment(
  _prev: ActionState,
  formData: FormData
): Promise<ActionState> {
  const num = (v: FormDataEntryValue | null) =>
    parseInt(String(v ?? "0").replace(/[^\d-]/g, ""), 10) || 0;

  const parsed = PaymentSchema.safeParse({
    date: formData.get("date")?.toString() ?? "",
    supplierId: formData.get("supplierId")?.toString() ?? "",
    amount: num(formData.get("amount")),
    paymentMethod: formData.get("paymentMethod")?.toString() ?? "",
    notes: formData.get("notes")?.toString() || null,
    confirmOverpay: formData.get("confirmOverpay")?.toString() || null,
  });

  if (!parsed.success) {
    return { error: parsed.error.issues[0]?.message ?? "Data tidak valid" };
  }
  const data = parsed.data;

  // Hitung sisa hutang
  const [supplier, sold, paid] = await Promise.all([
    prisma.supplier.findUnique({ where: { id: data.supplierId } }),
    prisma.saleItem.aggregate({
      where: { supplierId: data.supplierId },
      _sum: { totalCostItem: true },
    }),
    prisma.supplierPayment.aggregate({
      where: { supplierId: data.supplierId },
      _sum: { amount: true },
    }),
  ]);
  if (!supplier) return { error: "Supplier tidak ditemukan." };

  const totalSold = sold._sum.totalCostItem ?? 0;
  const totalPaid = paid._sum.amount ?? 0;
  const debt = Math.max(0, totalSold - totalPaid);

  if (data.amount > debt && !data.confirmOverpay) {
    return {
      warning: `Jumlah pembayaran (Rp ${data.amount.toLocaleString("id-ID")}) melebihi sisa hutang (Rp ${debt.toLocaleString("id-ID")}). Centang konfirmasi untuk tetap menyimpan.`,
    };
  }

  const payment = await prisma.supplierPayment.create({
    data: {
      date: new Date(data.date),
      supplierId: data.supplierId,
      amount: data.amount,
      paymentMethod: data.paymentMethod,
      notes: data.notes,
    },
  });

  const user = await getCurrentUser();
  await writeAudit({
    userId: user?.id ?? null,
    action: "PAYMENT",
    entityType: "SupplierPayment",
    entityId: payment.id,
    description: `Bayar supplier "${supplier.name}" sebesar ${data.amount}`,
    metadata: { supplierId: data.supplierId, debtBefore: debt, amount: data.amount },
  });

  revalidatePath("/supplier-payments");
  revalidatePath("/suppliers");
  revalidatePath(`/suppliers/${data.supplierId}`);
  revalidatePath("/dashboard");
  redirect(`/suppliers/${data.supplierId}`);
}
