"use client";

import { useActionState, useEffect, useState } from "react";
import { useFormStatus } from "react-dom";
import Link from "next/link";
import { Button, Input, Label, Select, Textarea } from "@/components/ui";
import { formatRupiah, toInputDate, SUPPLIER_PAYMENT_METHODS } from "@/lib/utils";
import type { ActionState } from "../actions";
import { createSupplierPayment } from "../actions";

type SupplierWithDebt = {
  id: string;
  name: string;
  debt: number;
};

export function PaymentForm({
  suppliers,
  defaultSupplierId,
}: {
  suppliers: SupplierWithDebt[];
  defaultSupplierId?: string;
}) {
  const [state, formAction] = useActionState<ActionState, FormData>(
    createSupplierPayment,
    {}
  );
  const [supplierId, setSupplierId] = useState(
    defaultSupplierId || suppliers[0]?.id || ""
  );
  const [amount, setAmount] = useState(0);
  const [confirmOverpay, setConfirmOverpay] = useState(false);

  const selected = suppliers.find((s) => s.id === supplierId);
  const debt = selected?.debt ?? 0;
  const isOverpay = amount > debt;

  // Reset konfirmasi ketika ganti supplier / amount turun
  useEffect(() => {
    setConfirmOverpay(false);
  }, [supplierId]);

  return (
    <form action={formAction} className="space-y-4 max-w-xl">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label required>Tanggal</Label>
          <Input
            name="date"
            type="date"
            defaultValue={toInputDate(new Date())}
            required
          />
        </div>
        <div>
          <Label required>Metode Pembayaran</Label>
          <Select name="paymentMethod" defaultValue="TRANSFER" required>
            {SUPPLIER_PAYMENT_METHODS.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </Select>
        </div>
        <div className="md:col-span-2">
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
                {s.name} (Sisa hutang: {formatRupiah(s.debt)})
              </option>
            ))}
          </Select>
        </div>
        <div className="md:col-span-2">
          <Label required>Jumlah Pembayaran (Rp)</Label>
          <Input
            name="amount"
            type="number"
            min={1}
            step={1}
            value={amount}
            onChange={(e) => setAmount(parseInt(e.target.value || "0", 10) || 0)}
            required
          />
          {selected && (
            <div className="text-xs text-slate-500 mt-1">
              Sisa hutang: <b>{formatRupiah(debt)}</b>
              {amount > 0 && (
                <>
                  {" • Sisa setelah bayar: "}
                  <b>{formatRupiah(Math.max(0, debt - amount))}</b>
                </>
              )}
            </div>
          )}
        </div>
        <div className="md:col-span-2">
          <Label>Catatan</Label>
          <Textarea name="notes" rows={2} />
        </div>
      </div>

      {isOverpay && amount > 0 && (
        <div className="border border-amber-300 bg-amber-50 rounded-md p-3 text-sm">
          <div className="font-medium text-amber-800">
            ⚠ Pembayaran melebihi sisa hutang
          </div>
          <div className="text-amber-700 mt-1">
            Selisih lebih: {formatRupiah(amount - debt)}
          </div>
          <label className="flex items-center gap-2 mt-2 text-amber-800">
            <input
              type="checkbox"
              name="confirmOverpay"
              value="1"
              checked={confirmOverpay}
              onChange={(e) => setConfirmOverpay(e.target.checked)}
            />
            Ya, saya tetap ingin menyimpan pembayaran ini.
          </label>
        </div>
      )}

      {state.warning && (
        <div className="text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2">
          {state.warning}
        </div>
      )}
      {state.error && (
        <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
          {state.error}
        </div>
      )}

      <div className="flex gap-2 pt-2">
        <SubmitButton disabled={isOverpay && !confirmOverpay} />
        <Link href="/supplier-payments">
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
      {pending ? "Menyimpan..." : "Simpan Pembayaran"}
    </Button>
  );
}
