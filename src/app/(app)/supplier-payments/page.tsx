import Link from "next/link";
import { prisma } from "@/lib/prisma";
import {
  Button,
  Card,
  PageHeader,
  EmptyState,
  Badge,
} from "@/components/ui";
import { Table, THead, TR, TH, TD } from "@/components/table";
import { formatRupiah, formatDate } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function SupplierPaymentsPage() {
  const payments = await prisma.supplierPayment.findMany({
    orderBy: { date: "desc" },
    take: 300,
    include: { supplier: { select: { id: true, name: true } } },
  });
  const total = payments.reduce((s, p) => s + p.amount, 0);

  return (
    <>
      <PageHeader
        title="Pembayaran Supplier"
        description={`${payments.length} pembayaran • Total: ${formatRupiah(total)}`}
        action={
          <Link href="/supplier-payments/new">
            <Button>+ Catat Pembayaran</Button>
          </Link>
        }
      />

      <Card>
        {payments.length === 0 ? (
          <EmptyState
            title="Belum ada pembayaran"
            description="Catat pembayaran ke supplier untuk mengurangi hutang."
            action={
              <Link href="/supplier-payments/new">
                <Button>+ Catat Pembayaran</Button>
              </Link>
            }
          />
        ) : (
          <Table>
            <THead>
              <TR>
                <TH>Tanggal</TH>
                <TH>Supplier</TH>
                <TH>Metode</TH>
                <TH>Catatan</TH>
                <TH className="text-right">Jumlah</TH>
              </TR>
            </THead>
            <tbody>
              {payments.map((p) => (
                <TR key={p.id}>
                  <TD>{formatDate(p.date)}</TD>
                  <TD>
                    <Link
                      href={`/suppliers/${p.supplier.id}`}
                      className="font-medium hover:underline"
                    >
                      {p.supplier.name}
                    </Link>
                  </TD>
                  <TD>
                    <Badge variant="muted">{p.paymentMethod}</Badge>
                  </TD>
                  <TD className="text-slate-600">{p.notes || "-"}</TD>
                  <TD className="text-right font-medium">
                    {formatRupiah(p.amount)}
                  </TD>
                </TR>
              ))}
            </tbody>
          </Table>
        )}
      </Card>
    </>
  );
}
