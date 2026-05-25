"use client";

import { useActionState, useState, useEffect } from "react";
import { useFormStatus } from "react-dom";
import Link from "next/link";
import { Button, Input, Label, Select, Textarea } from "@/components/ui";
import { formatRupiah, toInputDate } from "@/lib/utils";
import type { ActionState } from "./actions";

type ProductLite = {
  id: string;
  name: string;
  sku: string;
  costPrice: number;
  defaultSupplierId: string | null;
};

type SupplierLite = { id: string; name: string };

export function StockEntryForm({
  action,
  suppliers,
  products,
}: {
  action: (prev: ActionState, fd: FormData) => Promise<ActionState>;
  suppliers: SupplierLite[];
  products: ProductLite[];
}) {
  const [state, formAction] = useActionState<ActionState, FormData>(action, {});
  const [productId, setProductId] = useState(products[0]?.id ?? "");
  const [supplierId, setSupplierId] = useState("");
  const [qty, setQty] = useState(1);
  const [cost, setCost] = useState(products[0]?.costPrice ?? 0);

  // Saat produk diganti, default supplier & harga modal mengikuti produk
  useEffect(() => {
    const p = products.find((x) => x.id === productId);
    if (!p) return;
    setCost(p.costPrice);
    if (p.defaultSupplierId) setSupplierId(p.defaultSupplierId);
  }, [productId, products]);

  const total = qty * cost;

  return (
    <form action={formAction} className="space-y-4 max-w-2xl">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label required>Tanggal Masuk</Label>
          <Input
            name="date"
            type="date"
            defaultValue={toInputDate(new Date())}
            required
          />
        </div>
        <div>
          <Label required>Produk</Label>
          <Select
            name="productId"
            value={productId}
            onChange={(e) => setProductId(e.target.value)}
            required
          >
            <option value="">— Pilih produk —</option>
            {products.map((p) => (
              <option key={p.id} value={p.id}>
                [{p.sku}] {p.name}
              </option>
            ))}
          </Select>
        </div>
        <div>
          <Label required>Supplier</Label>
          <Select
            name="supplierId"
            value={supplierId}
            onChange={(e) => setSupplierId(e.target.value)}
            required
          >
            <option value="">— Pilih supplier —</option>
            {suppliers.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </Select>
        </div>
        <div>
          <Label>No. Referensi (opsional)</Label>
          <Input name="refNo" placeholder="No. surat jalan / faktur" />
        </div>
        <div>
          <Label required>Jumlah Masuk</Label>
          <Input
            name="qty"
            type="number"
            min={1}
            step={1}
            value={qty}
            onChange={(e) => setQty(parseInt(e.target.value || "0", 10) || 0)}
            required
          />
        </div>
        <div>
          <Label required>Harga Modal / Unit (Rp)</Label>
          <Input
            name="costPricePerUnit"
            type="number"
            min={0}
            step={1}
            value={cost}
            onChange={(e) => setCost(parseInt(e.target.value || "0", 10) || 0)}
            required
          />
        </div>
      </div>

      <div>
        <Label>Catatan</Label>
        <Textarea name="notes" rows={2} />
      </div>

      <div className="bg-slate-50 border border-slate-200 rounded-md px-4 py-3">
        <div className="text-sm text-slate-500">Total Nilai Stok Masuk</div>
        <div className="text-xl font-bold">{formatRupiah(total)}</div>
        <div className="text-xs text-slate-500 mt-1">
          {qty} unit × {formatRupiah(cost)}
        </div>
      </div>

      {state.error && (
        <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
          {state.error}
        </div>
      )}

      <p className="text-xs text-slate-500 bg-amber-50 border border-amber-200 rounded px-3 py-2">
        ℹ️ Karena sistem konsinyasi, hutang ke supplier <strong>tidak otomatis bertambah</strong> saat
        stok masuk. Hutang baru tercatat setelah barang berhasil dijual.
      </p>

      <div className="flex gap-2 pt-2">
        <SubmitButton />
        <Link href="/stock-entries">
          <Button type="button" variant="secondary">
            Batal
          </Button>
        </Link>
      </div>
    </form>
  );
}

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <Button type="submit" disabled={pending}>
      {pending ? "Menyimpan..." : "Simpan Stok Masuk"}
    </Button>
  );
}
