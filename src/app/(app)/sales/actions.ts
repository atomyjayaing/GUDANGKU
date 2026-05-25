"use server";

import { z } from "zod";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { writeAudit } from "@/lib/audit";
import { getCurrentUser } from "@/lib/session";
import { generateInvoiceNo, SALES_CHANNELS, PAYMENT_METHODS } from "@/lib/utils";

const SaleItemSchema = z.object({
  productId: z.string().min(1),
  qty: z.number().int().positive("Qty harus > 0"),
  sellPriceActual: z.number().int().min(0, "Harga jual tidak boleh negatif"),
  discountItem: z.number().int().min(0),
});

const SaleSchema = z.object({
  date: z.string().min(1, "Tanggal wajib diisi"),
  channel: z.enum(SALES_CHANNELS),
  customerName: z.string().trim().optional().nullable(),
  customerPhone: z.string().trim().optional().nullable(),
  paymentMethod: z.enum(PAYMENT_METHODS),
  discountTotal: z.number().int().min(0),
  notes: z.string().trim().optional().nullable(),
  items: z.array(SaleItemSchema).min(1, "Minimal 1 item penjualan"),
});

export type ActionState = { error?: string | null; warning?: string | null };

export async function createSale(
  _prev: ActionState,
  formData: FormData
): Promise<ActionState> {
  // Parse items dari JSON di hidden input
  let itemsParsed: unknown;
  try {
    itemsParsed = JSON.parse(formData.get("itemsJson")?.toString() || "[]");
  } catch {
    return { error: "Format items tidak valid" };
  }

  const num = (v: FormDataEntryValue | null) =>
    parseInt(String(v ?? "0").replace(/[^\d-]/g, ""), 10) || 0;

  const parsed = SaleSchema.safeParse({
    date: formData.get("date")?.toString() ?? "",
    channel: formData.get("channel")?.toString() ?? "",
    customerName: formData.get("customerName")?.toString() || null,
    customerPhone: formData.get("customerPhone")?.toString() || null,
    paymentMethod: formData.get("paymentMethod")?.toString() ?? "",
    discountTotal: num(formData.get("discountTotal")),
    notes: formData.get("notes")?.toString() || null,
    items: itemsParsed,
  });

  if (!parsed.success) {
    return { error: parsed.error.issues[0]?.message ?? "Data tidak valid" };
  }

  const data = parsed.data;

  // Ambil semua produk yang terlibat sekaligus
  const productIds = data.items.map((i) => i.productId);
  const products = await prisma.product.findMany({
    where: { id: { in: productIds } },
  });
  const productMap = new Map(products.map((p) => [p.id, p]));

  // Validasi stok cukup + produk aktif
  for (const it of data.items) {
    const p = productMap.get(it.productId);
    if (!p) return { error: `Produk tidak ditemukan: ${it.productId}` };
    if (p.status !== "ACTIVE") return { error: `Produk "${p.name}" sudah nonaktif.` };
    if (p.stock < it.qty) {
      return {
        error: `Stok "${p.name}" tidak cukup. Tersedia: ${p.stock}, diminta: ${it.qty}`,
      };
    }
    if (!p.defaultSupplierId) {
      return {
        error: `Produk "${p.name}" belum punya supplier default. Edit produk dulu.`,
      };
    }
  }

  // Hitung total
  let subtotal = 0;
  let totalCost = 0;
  const itemRows: Array<{
    productId: string;
    supplierId: string;
    productNameSnapshot: string;
    skuSnapshot: string;
    qty: number;
    costPriceSnapshot: number;
    sellPriceActual: number;
    discountItem: number;
    subtotalItem: number;
    totalCostItem: number;
    grossProfitItem: number;
  }> = [];
  let belowCost = false;

  for (const it of data.items) {
    const p = productMap.get(it.productId)!;
    const subtotalItem = it.sellPriceActual * it.qty - it.discountItem;
    const totalCostItem = p.costPrice * it.qty;
    const grossProfitItem = subtotalItem - totalCostItem;
    if (it.sellPriceActual < p.costPrice) belowCost = true;
    subtotal += subtotalItem;
    totalCost += totalCostItem;
    itemRows.push({
      productId: p.id,
      supplierId: p.defaultSupplierId!,
      productNameSnapshot: p.name,
      skuSnapshot: p.sku,
      qty: it.qty,
      costPriceSnapshot: p.costPrice,
      sellPriceActual: it.sellPriceActual,
      discountItem: it.discountItem,
      subtotalItem,
      totalCostItem,
      grossProfitItem,
    });
  }

  const grandTotal = Math.max(0, subtotal - data.discountTotal);
  const grossProfit = grandTotal - totalCost;

  // Generate invoice number unik (loop kecil kalau bentrok)
  let invoiceNo = generateInvoiceNo(new Date(data.date));
  for (let i = 0; i < 5; i++) {
    const existing = await prisma.sale.findUnique({ where: { invoiceNo } });
    if (!existing) break;
    invoiceNo = generateInvoiceNo(new Date(data.date));
  }

  const sale = await prisma.$transaction(async (tx) => {
    const created = await tx.sale.create({
      data: {
        invoiceNo,
        date: new Date(data.date),
        channel: data.channel,
        customerName: data.customerName,
        customerPhone: data.customerPhone,
        paymentMethod: data.paymentMethod,
        paymentStatus: "PAID",
        subtotal,
        discountTotal: data.discountTotal,
        grandTotal,
        totalCost,
        grossProfit,
        notes: data.notes,
        items: { create: itemRows },
      },
    });
    // Kurangi stok per item
    for (const it of data.items) {
      await tx.product.update({
        where: { id: it.productId },
        data: { stock: { decrement: it.qty } },
      });
    }
    return created;
  });

  const user = await getCurrentUser();
  await writeAudit({
    userId: user?.id ?? null,
    action: "SALE",
    entityType: "Sale",
    entityId: sale.id,
    description: `Penjualan ${invoiceNo} (${data.channel}) total ${grandTotal}${belowCost ? " [⚠ ada item di bawah modal]" : ""}`,
    metadata: { grandTotal, totalCost, grossProfit, items: itemRows.length, belowCost },
  });

  revalidatePath("/sales");
  revalidatePath("/products");
  revalidatePath("/dashboard");
  revalidatePath("/suppliers");
  redirect(`/sales/${sale.id}`);
}
