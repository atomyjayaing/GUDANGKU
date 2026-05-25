"use client";

import { useActionState } from "react";
import { useFormStatus } from "react-dom";
import Link from "next/link";
import { Button, Input, Label, Select, Textarea } from "@/components/ui";
import type { ActionState } from "./actions";

type Initial = {
  sku: string;
  name: string;
  category: string | null;
  brand: string | null;
  model: string | null;
  defaultSupplierId: string | null;
  costPrice: number;
  sellPrice: number;
  status: string;
  notes: string | null;
};

export function ProductForm({
  action,
  initial,
  suppliers,
  submitLabel = "Simpan",
  skuLocked = false,
}: {
  action: (prev: ActionState, fd: FormData) => Promise<ActionState>;
  initial?: Partial<Initial>;
  suppliers: { id: string; name: string }[];
  submitLabel?: string;
  skuLocked?: boolean;
}) {
  const [state, formAction] = useActionState<ActionState, FormData>(action, {});
  return (
    <form action={formAction} className="space-y-4 max-w-2xl">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label required>SKU</Label>
          <Input
            name="sku"
            defaultValue={initial?.sku ?? ""}
            required
            readOnly={skuLocked}
            className={skuLocked ? "bg-slate-50" : ""}
          />
        </div>
        <div>
          <Label required>Nama Produk</Label>
          <Input name="name" defaultValue={initial?.name ?? ""} required />
        </div>
        <div>
          <Label>Kategori</Label>
          <Input
            name="category"
            placeholder="TV, Kulkas, dll."
            defaultValue={initial?.category ?? ""}
          />
        </div>
        <div>
          <Label>Brand / Merek</Label>
          <Input name="brand" defaultValue={initial?.brand ?? ""} />
        </div>
        <div>
          <Label>Tipe / Model</Label>
          <Input name="model" defaultValue={initial?.model ?? ""} />
        </div>
        <div>
          <Label>Supplier Default</Label>
          <Select name="defaultSupplierId" defaultValue={initial?.defaultSupplierId ?? ""}>
            <option value="">— Tidak ditetapkan —</option>
            {suppliers.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </Select>
        </div>
        <div>
          <Label required>Harga Modal (Rp)</Label>
          <Input
            name="costPrice"
            type="number"
            min={0}
            step={1}
            defaultValue={initial?.costPrice ?? 0}
            required
          />
        </div>
        <div>
          <Label required>Harga Jual Default (Rp)</Label>
          <Input
            name="sellPrice"
            type="number"
            min={0}
            step={1}
            defaultValue={initial?.sellPrice ?? 0}
            required
          />
        </div>
        <div>
          <Label>Status</Label>
          <Select name="status" defaultValue={initial?.status ?? "ACTIVE"}>
            <option value="ACTIVE">Aktif</option>
            <option value="INACTIVE">Nonaktif</option>
          </Select>
        </div>
      </div>
      <div>
        <Label>Catatan</Label>
        <Textarea name="notes" rows={2} defaultValue={initial?.notes ?? ""} />
      </div>

      {state.error && (
        <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
          {state.error}
        </div>
      )}
      <div className="flex gap-2 pt-2">
        <SubmitButton label={submitLabel} />
        <Link href="/products">
          <Button type="button" variant="secondary">
            Batal
          </Button>
        </Link>
      </div>
    </form>
  );
}

function SubmitButton({ label }: { label: string }) {
  const { pending } = useFormStatus();
  return (
    <Button type="submit" disabled={pending}>
      {pending ? "Menyimpan..." : label}
    </Button>
  );
}
