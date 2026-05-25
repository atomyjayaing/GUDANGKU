"use client";

import { useActionState, useMemo, useState } from "react";
import { useFormStatus } from "react-dom";
import Link from "next/link";
import { Button, Card, Input, Label, Select, Textarea } from "@/components/ui";
import {
  formatRupiah,
  toInputDate,
  SALES_CHANNELS,
  PAYMENT_METHODS,
  CHANNEL_LABEL,
  PAYMENT_LABEL,
} from "@/lib/utils";
import type { ActionState } from "../actions";
import { createSale } from "../actions";

type ProductLite = {
  id: string;
  sku: string;
  name: string;
  costPrice: number;
  sellPrice: number;
  stock: number;
  defaultSupplierId: string | null;
};

type Line = {
  key: string;
  productId: string;
  qty: number;
  sellPriceActual: number;
  discountItem: number;
};

function newLine(): Line {
  return {
    key: Math.random().toString(36).slice(2),
    productId: "",
    qty: 1,
    sellPriceActual: 0,
    discountItem: 0,
  };
}

export function SaleForm({ products }: { products: ProductLite[] }) {
  const [state, formAction] = useActionState<ActionState, FormData>(createSale, {});
  const [lines, setLines] = useState<Line[]>([newLine()]);
  const [discountTotal, setDiscountTotal] = useState(0);

  const productMap = useMemo(
    () => new Map(products.map((p) => [p.id, p])),
    [products]
  );

  function updateLine(key: string, patch: Partial<Line>) {
    setLines((prev) =>
      prev.map((ln) => {
        if (ln.key !== key) return ln;
        const next = { ...ln, ...patch };
        // Saat produk diganti, isi default harga jual + reset qty
        if (patch.productId && patch.productId !== ln.productId) {
          const p = productMap.get(patch.productId);
          if (p) {
            next.sellPriceActual = p.sellPrice;
            if (next.qty < 1) next.qty = 1;
          }
        }
        return next;
      })
    );
  }

  function removeLine(key: string) {
    setLines((prev) => (prev.length === 1 ? prev : prev.filter((l) => l.key !== key)));
  }

  // Hitung totals
  const itemSummaries = lines.map((ln) => {
    const p = productMap.get(ln.productId);
    const subtotalItem = ln.sellPriceActual * ln.qty - ln.discountItem;
    const totalCostItem = (p?.costPrice ?? 0) * ln.qty;
    const profitItem = subtotalItem - totalCostItem;
    const stockIssue = p ? ln.qty > p.stock : false;
    const belowCost = p ? ln.sellPriceActual < p.costPrice : false;
    return { p, subtotalItem, totalCostItem, profitItem, stockIssue, belowCost };
  });

  const subtotal = itemSummaries.reduce((s, i) => s + i.subtotalItem, 0);
  const totalCost = itemSummaries.reduce((s, i) => s + i.totalCostItem, 0);
  const grandTotal = Math.max(0, subtotal - discountTotal);
  const grossProfit = grandTotal - totalCost;

  const hasStockIssue = itemSummaries.some((i) => i.stockIssue);
  const hasBelowCost = itemSummaries.some((i) => i.belowCost);
  const incomplete = lines.some((l) => !l.productId || l.qty <= 0);

  const itemsJson = JSON.stringify(
    lines
      .filter((l) => l.productId && l.qty > 0)
      .map((l) => ({
        productId: l.productId,
        qty: l.qty,
        sellPriceActual: l.sellPriceActual,
        discountItem: l.discountItem,
      }))
  );

  return (
    <form action={formAction} className="space-y-6">
      <input type="hidden" name="itemsJson" value={itemsJson} />

      <Card className="p-5">
        <h2 className="font-semibold mb-4">Info Transaksi</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <Label required>Tanggal</Label>
            <Input name="date" type="date" defaultValue={toInputDate(new Date())} required />
          </div>
          <div>
            <Label required>Channel</Label>
            <Select name="channel" defaultValue="OFFLINE" required>
              {SALES_CHANNELS.map((c) => (
                <option key={c} value={c}>
                  {CHANNEL_LABEL[c]}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <Label required>Metode Pembayaran</Label>
            <Select name="paymentMethod" defaultValue="CASH" required>
              {PAYMENT_METHODS.map((m) => (
                <option key={m} value={m}>
                  {PAYMENT_LABEL[m]}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <Label>Nama Customer</Label>
            <Input name="customerName" placeholder="Opsional" />
          </div>
          <div>
            <Label>HP Customer</Label>
            <Input name="customerPhone" placeholder="Opsional" />
          </div>
        </div>
      </Card>

      <Card className="p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold">Item Penjualan</h2>
          <Button
            type="button"
            variant="secondary"
            size="sm"
            onClick={() => setLines((p) => [...p, newLine()])}
          >
            + Tambah Item
          </Button>
        </div>

        <div className="space-y-3">
          {lines.map((ln, idx) => {
            const sum = itemSummaries[idx];
            const p = sum.p;
            return (
              <div
                key={ln.key}
                className="border border-slate-200 rounded-lg p-3 bg-slate-50/50"
              >
                <div className="grid grid-cols-12 gap-2 items-start">
                  <div className="col-span-12 md:col-span-5">
                    <Label>Produk</Label>
                    <Select
                      value={ln.productId}
                      onChange={(e) =>
                        updateLine(ln.key, { productId: e.target.value })
                      }
                    >
                      <option value="">— Pilih produk —</option>
                      {products.map((pr) => (
                        <option key={pr.id} value={pr.id}>
                          [{pr.sku}] {pr.name} (stok: {pr.stock})
                        </option>
                      ))}
                    </Select>
                    {p && (
                      <div className="text-xs text-slate-500 mt-1">
                        Modal: {formatRupiah(p.costPrice)} • Stok tersedia: {p.stock}
                      </div>
                    )}
                  </div>
                  <div className="col-span-4 md:col-span-2">
                    <Label>Qty</Label>
                    <Input
                      type="number"
                      min={1}
                      step={1}
                      value={ln.qty}
                      onChange={(e) =>
                        updateLine(ln.key, {
                          qty: parseInt(e.target.value || "0", 10) || 0,
                        })
                      }
                    />
                  </div>
                  <div className="col-span-4 md:col-span-2">
                    <Label>Harga Jual</Label>
                    <Input
                      type="number"
                      min={0}
                      step={1}
                      value={ln.sellPriceActual}
                      onChange={(e) =>
                        updateLine(ln.key, {
                          sellPriceActual: parseInt(e.target.value || "0", 10) || 0,
                        })
                      }
                    />
                  </div>
                  <div className="col-span-4 md:col-span-2">
                    <Label>Diskon Item</Label>
                    <Input
                      type="number"
                      min={0}
                      step={1}
                      value={ln.discountItem}
                      onChange={(e) =>
                        updateLine(ln.key, {
                          discountItem: parseInt(e.target.value || "0", 10) || 0,
                        })
                      }
                    />
                  </div>
                  <div className="col-span-12 md:col-span-1 flex md:justify-end md:items-end">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeLine(ln.key)}
                      disabled={lines.length === 1}
                      className="text-red-600"
                    >
                      Hapus
                    </Button>
                  </div>
                </div>

                <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs">
                  <span className="text-slate-600">
                    Subtotal: <b>{formatRupiah(sum.subtotalItem)}</b>
                  </span>
                  <span className="text-slate-600">
                    Modal: {formatRupiah(sum.totalCostItem)}
                  </span>
                  <span
                    className={
                      sum.profitItem < 0 ? "text-red-600 font-medium" : "text-emerald-600"
                    }
                  >
                    Laba: {formatRupiah(sum.profitItem)}
                  </span>
                  {sum.stockIssue && (
                    <span className="text-red-600 font-medium">
                      ⚠ Stok tidak cukup (tersedia {p?.stock ?? 0})
                    </span>
                  )}
                  {sum.belowCost && (
                    <span className="text-amber-600 font-medium">
                      ⚠ Harga jual di bawah modal
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      <Card className="p-5">
        <h2 className="font-semibold mb-4">Ringkasan</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label>Diskon Total Transaksi</Label>
            <Input
              name="discountTotal"
              type="number"
              min={0}
              step={1}
              value={discountTotal}
              onChange={(e) =>
                setDiscountTotal(parseInt(e.target.value || "0", 10) || 0)
              }
            />
          </div>
          <div className="md:col-span-2 bg-slate-900 text-white rounded-lg p-4 space-y-1">
            <div className="flex justify-between text-sm text-slate-300">
              <span>Subtotal</span>
              <span>{formatRupiah(subtotal)}</span>
            </div>
            <div className="flex justify-between text-sm text-slate-300">
              <span>Diskon Total</span>
              <span>− {formatRupiah(discountTotal)}</span>
            </div>
            <div className="flex justify-between text-sm text-slate-300">
              <span>Total Modal</span>
              <span>{formatRupiah(totalCost)}</span>
            </div>
            <div className="border-t border-slate-700 my-2"></div>
            <div className="flex justify-between text-lg font-bold">
              <span>Grand Total</span>
              <span>{formatRupiah(grandTotal)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Laba Kasar</span>
              <span
                className={grossProfit < 0 ? "text-red-300" : "text-emerald-300"}
              >
                {formatRupiah(grossProfit)}
              </span>
            </div>
          </div>
        </div>
        <div className="mt-4">
          <Label>Catatan</Label>
          <Textarea name="notes" rows={2} />
        </div>
      </Card>

      {hasBelowCost && (
        <div className="text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2">
          ⚠ Ada item dengan harga jual di bawah modal. Pastikan ini disengaja.
        </div>
      )}
      {state.error && (
        <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
          {state.error}
        </div>
      )}

      <div className="flex gap-2">
        <SubmitButton disabled={hasStockIssue || incomplete} />
        <Link href="/sales">
          <Button type="button" variant="secondary">
            Batal
          </Button>
        </Link>
      </div>
    </form>
  );
}

function SubmitButton({ disabled }: { disabled: boolean }) {
  const { pending } = useFormStatus();
  return (
    <Button type="submit" disabled={pending || disabled}>
      {pending ? "Menyimpan..." : "Simpan Penjualan"}
    </Button>
  );
}
