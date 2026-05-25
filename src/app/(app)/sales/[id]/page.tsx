import Link from "next/link";
import { notFound } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { Card, PageHeader, Badge, Button } from "@/components/ui";
import { Table, THead, TR, TH, TD } from "@/components/table";
import {
  formatRupiah,
  formatDateTime,
  CHANNEL_LABEL,
  PAYMENT_LABEL,
  type SalesChannel,
  type PaymentMethod,
} from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function SaleDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const sale = await prisma.sale.findUnique({
    where: { id },
    include: {
      items: {
        include: {
          supplier: { select: { id: true, name: true } },
          product: { select: { id: true } },
        },
      },
    },
  });
  if (!sale) notFound();

  return (
    <>
      <PageHeader
        title={`Invoice ${sale.invoiceNo}`}
        description={formatDateTime(sale.date)}
        action={
          <Link href="/sales">
            <Button variant="secondary">← Kembali</Button>
          </Link>
        }
      />

      <Card className="p-6 mb-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-xs uppercase text-slate-500">Channel</div>
            <Badge variant="muted">
              {CHANNEL_LABEL[sale.channel as SalesChannel] ?? sale.channel}
            </Badge>
          </div>
          <div>
            <div className="text-xs uppercase text-slate-500">Pembayaran</div>
            <Badge variant="muted">
              {PAYMENT_LABEL[sale.paymentMethod as PaymentMethod] ?? sale.paymentMethod}
            </Badge>
          </div>
          <div>
            <div className="text-xs uppercase text-slate-500">Status</div>
            <Badge variant="success">{sale.paymentStatus}</Badge>
          </div>
          <div>
            <div className="text-xs uppercase text-slate-500">Customer</div>
            <div>{sale.customerName || "-"}</div>
            <div className="text-xs text-slate-500">{sale.customerPhone || ""}</div>
          </div>
        </div>
        {sale.notes && (
          <p className="text-sm text-slate-500 italic mt-4 pt-4 border-t border-slate-100">
            "{sale.notes}"
          </p>
        )}
      </Card>

      <Card className="mb-4">
        <div className="p-4 border-b border-slate-200">
          <h3 className="font-semibold">Item</h3>
        </div>
        <Table>
          <THead>
            <TR>
              <TH>Produk</TH>
              <TH>Supplier</TH>
              <TH className="text-right">Qty</TH>
              <TH className="text-right">Harga Jual</TH>
              <TH className="text-right">Diskon</TH>
              <TH className="text-right">Modal</TH>
              <TH className="text-right">Subtotal</TH>
              <TH className="text-right">Laba</TH>
            </TR>
          </THead>
          <tbody>
            {sale.items.map((it) => (
              <TR key={it.id}>
                <TD>
                  <Link
                    href={`/products/${it.product.id}`}
                    className="font-medium hover:underline"
                  >
                    {it.productNameSnapshot}
                  </Link>
                  <div className="text-xs text-slate-500 font-mono">
                    {it.skuSnapshot}
                  </div>
                </TD>
                <TD>
                  <Link
                    href={`/suppliers/${it.supplier.id}`}
                    className="hover:underline"
                  >
                    {it.supplier.name}
                  </Link>
                </TD>
                <TD className="text-right">{it.qty}</TD>
                <TD className="text-right">{formatRupiah(it.sellPriceActual)}</TD>
                <TD className="text-right">
                  {it.discountItem > 0 ? `− ${formatRupiah(it.discountItem)}` : "-"}
                </TD>
                <TD className="text-right text-slate-500">
                  {formatRupiah(it.costPriceSnapshot)} × {it.qty}
                </TD>
                <TD className="text-right font-medium">
                  {formatRupiah(it.subtotalItem)}
                </TD>
                <TD
                  className={
                    "text-right " +
                    (it.grossProfitItem < 0 ? "text-red-600" : "text-emerald-700")
                  }
                >
                  {formatRupiah(it.grossProfitItem)}
                </TD>
              </TR>
            ))}
          </tbody>
        </Table>
      </Card>

      <Card className="p-6 max-w-sm ml-auto">
        <div className="space-y-2 text-sm">
          <Row label="Subtotal" value={formatRupiah(sale.subtotal)} />
          {sale.discountTotal > 0 && (
            <Row
              label="Diskon Total"
              value={`− ${formatRupiah(sale.discountTotal)}`}
            />
          )}
          <Row label="Total Modal" value={formatRupiah(sale.totalCost)} muted />
          <div className="border-t border-slate-200 my-2"></div>
          <Row label="Grand Total" value={formatRupiah(sale.grandTotal)} bold />
          <Row
            label="Laba Kasar"
            value={formatRupiah(sale.grossProfit)}
            profit={sale.grossProfit}
          />
        </div>
      </Card>
    </>
  );
}

function Row({
  label,
  value,
  bold,
  muted,
  profit,
}: {
  label: string;
  value: string;
  bold?: boolean;
  muted?: boolean;
  profit?: number;
}) {
  return (
    <div className="flex justify-between">
      <span className={muted ? "text-slate-500" : ""}>{label}</span>
      <span
        className={
          (bold ? "text-lg font-bold " : "") +
          (profit !== undefined
            ? profit < 0
              ? "text-red-600 font-semibold"
              : "text-emerald-700 font-semibold"
            : "")
        }
      >
        {value}
      </span>
    </div>
  );
}
