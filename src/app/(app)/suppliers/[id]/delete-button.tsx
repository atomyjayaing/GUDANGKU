"use client";

import { useState, useTransition } from "react";
import { Button } from "@/components/ui";
import { deleteSupplier } from "../actions";

export function DeleteSupplierButton({ id, name }: { id: string; name: string }) {
  const [error, setError] = useState<string | null>(null);
  const [pending, start] = useTransition();

  return (
    <div>
      <Button
        type="button"
        variant="danger"
        size="sm"
        disabled={pending}
        onClick={() => {
          if (!confirm(`Hapus supplier "${name}"? Tindakan ini tidak bisa dibatalkan.`))
            return;
          setError(null);
          start(async () => {
            try {
              await deleteSupplier(id);
            } catch (e) {
              setError(e instanceof Error ? e.message : "Gagal menghapus");
            }
          });
        }}
      >
        {pending ? "Menghapus..." : "Hapus Supplier"}
      </Button>
      {error && (
        <p className="text-sm text-red-600 mt-2">{error}</p>
      )}
    </div>
  );
}
