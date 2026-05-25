"use client";

import { useState, useTransition } from "react";
import { Button } from "@/components/ui";
import { deleteProduct, setProductStatus } from "../actions";

export function ProductActions({
  id,
  status,
  name,
}: {
  id: string;
  status: string;
  name: string;
}) {
  const [error, setError] = useState<string | null>(null);
  const [pending, start] = useTransition();
  const isActive = status === "ACTIVE";

  return (
    <div className="border-t border-slate-200 pt-6 space-y-3">
      <h3 className="font-semibold text-sm text-slate-700">Aksi Lanjutan</h3>
      <div className="flex flex-wrap gap-2">
        <Button
          type="button"
          variant="secondary"
          size="sm"
          disabled={pending}
          onClick={() => {
            setError(null);
            start(async () => {
              try {
                await setProductStatus(id, isActive ? "INACTIVE" : "ACTIVE");
              } catch (e) {
                setError(e instanceof Error ? e.message : "Gagal mengubah status");
              }
            });
          }}
        >
          {isActive ? "Nonaktifkan Produk" : "Aktifkan Produk"}
        </Button>

        <Button
          type="button"
          variant="danger"
          size="sm"
          disabled={pending}
          onClick={() => {
            if (
              !confirm(
                `Hapus produk "${name}" permanen? Hanya bisa kalau belum ada transaksi.`
              )
            )
              return;
            setError(null);
            start(async () => {
              try {
                await deleteProduct(id);
              } catch (e) {
                setError(e instanceof Error ? e.message : "Gagal menghapus");
              }
            });
          }}
        >
          Hapus Permanen
        </Button>
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <p className="text-xs text-slate-500">
        Tip: produk yang sudah punya transaksi tidak bisa dihapus. Gunakan tombol
        "Nonaktifkan" agar produk tidak muncul di daftar penjualan baru.
      </p>
    </div>
  );
}
