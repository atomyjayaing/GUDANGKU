import Link from "next/link";
import { prisma } from "@/lib/prisma";
import { Card, PageHeader, Badge, Button } from "@/components/ui";
import { Table, THead, TR, TH, TD } from "@/components/table";
import { formatDateTime } from "@/lib/utils";

export const dynamic = "force-dynamic";

const ACTION_VARIANT: Record<string, "default" | "success" | "warning" | "danger" | "muted"> = {
  CREATE: "success",
  UPDATE: "default",
  DELETE: "danger",
  DEACTIVATE: "warning",
  ACTIVATE: "success",
  SALE: "success",
  PAYMENT: "default",
  STOCK_IN: "default",
  LOGIN: "muted",
};

const ENTITY_PATH: Record<string, (id: string) => string> = {
  Product: (id) => `/products/${id}`,
  Supplier: (id) => `/suppliers/${id}`,
  Sale: (id) => `/sales/${id}`,
};

export default async function AuditLogsPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string; entity?: string }>;
}) {
  const sp = await searchParams;
  const page = Math.max(1, parseInt(sp.page || "1", 10) || 1);
  const pageSize = 50;

  const where = sp.entity ? { entityType: sp.entity } : {};

  const [logs, total] = await Promise.all([
    prisma.auditLog.findMany({
      where,
      orderBy: { createdAt: "desc" },
      take: pageSize,
      skip: (page - 1) * pageSize,
      include: { user: { select: { name: true, email: true } } },
    }),
    prisma.auditLog.count({ where }),
  ]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <>
      <PageHeader
        title="Audit Log"
        description={`${total} aktivitas tercatat • Halaman ${page}/${totalPages}`}
      />

      <Card className="p-4 mb-4">
        <form method="get" className="flex flex-wrap gap-2 items-end">
          <div>
            <label className="block text-xs text-slate-500 mb-1">Filter Entitas</label>
            <select
              name="entity"
              defaultValue={sp.entity || ""}
              className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
            >
              <option value="">Semua</option>
              <option value="Product">Produk</option>
              <option value="Supplier">Supplier</option>
              <option value="StockEntry">Stok Masuk</option>
              <option value="Sale">Penjualan</option>
              <option value="SupplierPayment">Pembayaran Supplier</option>
            </select>
          </div>
          <Button type="submit" variant="secondary">
            Terapkan
          </Button>
          <Link href="/audit-logs">
            <Button type="button" variant="ghost">
              Reset
            </Button>
          </Link>
        </form>
      </Card>

      <Card>
        {logs.length === 0 ? (
          <div className="p-10 text-center text-sm text-slate-400">
            Belum ada aktivitas tercatat.
          </div>
        ) : (
          <Table>
            <THead>
              <TR>
                <TH>Waktu</TH>
                <TH>Aksi</TH>
                <TH>Entitas</TH>
                <TH>Deskripsi</TH>
                <TH>User</TH>
              </TR>
            </THead>
            <tbody>
              {logs.map((l) => {
                const pathFn = ENTITY_PATH[l.entityType];
                const path = pathFn && l.entityId ? pathFn(l.entityId) : null;
                return (
                  <TR key={l.id}>
                    <TD className="text-slate-600 whitespace-nowrap">
                      {formatDateTime(l.createdAt)}
                    </TD>
                    <TD>
                      <Badge variant={ACTION_VARIANT[l.action] || "default"}>
                        {l.action}
                      </Badge>
                    </TD>
                    <TD>
                      <Badge variant="muted">{l.entityType}</Badge>
                    </TD>
                    <TD>
                      {path ? (
                        <Link href={path} className="hover:underline">
                          {l.description}
                        </Link>
                      ) : (
                        l.description
                      )}
                    </TD>
                    <TD className="text-slate-600 text-xs">
                      {l.user?.name || l.user?.email || "-"}
                    </TD>
                  </TR>
                );
              })}
            </tbody>
          </Table>
        )}
      </Card>

      {totalPages > 1 && (
        <div className="flex justify-center gap-2 mt-4">
          {page > 1 && (
            <Link
              href={`/audit-logs?page=${page - 1}${sp.entity ? `&entity=${sp.entity}` : ""}`}
            >
              <Button variant="secondary" size="sm">
                ← Sebelumnya
              </Button>
            </Link>
          )}
          <span className="text-sm text-slate-500 self-center">
            Halaman {page} dari {totalPages}
          </span>
          {page < totalPages && (
            <Link
              href={`/audit-logs?page=${page + 1}${sp.entity ? `&entity=${sp.entity}` : ""}`}
            >
              <Button variant="secondary" size="sm">
                Selanjutnya →
              </Button>
            </Link>
          )}
        </div>
      )}
    </>
  );
}
