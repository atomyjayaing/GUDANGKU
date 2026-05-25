"use client";

import { useActionState } from "react";
import { useFormStatus } from "react-dom";
import Link from "next/link";
import { Button, Input, Label, Textarea } from "@/components/ui";
import type { ActionState } from "./actions";

type Initial = {
  name: string;
  phone: string | null;
  address: string | null;
  notes: string | null;
};

export function SupplierForm({
  action,
  initial,
  submitLabel = "Simpan",
}: {
  action: (prev: ActionState, fd: FormData) => Promise<ActionState>;
  initial?: Partial<Initial>;
  submitLabel?: string;
}) {
  const [state, formAction] = useActionState<ActionState, FormData>(action, {});
  return (
    <form action={formAction} className="space-y-4 max-w-xl">
      <div>
        <Label required>Nama Supplier</Label>
        <Input name="name" defaultValue={initial?.name ?? ""} required />
      </div>
      <div>
        <Label>Nomor HP</Label>
        <Input name="phone" defaultValue={initial?.phone ?? ""} />
      </div>
      <div>
        <Label>Alamat</Label>
        <Textarea name="address" rows={2} defaultValue={initial?.address ?? ""} />
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
        <Link href="/suppliers">
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
