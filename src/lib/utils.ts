export function cn(...classes: Array<string | undefined | false | null>) {
  return classes.filter(Boolean).join(" ");
}

const RUPIAH = new Intl.NumberFormat("id-ID", {
  style: "currency",
  currency: "IDR",
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

export function formatRupiah(value: number | bigint | null | undefined) {
  if (value === null || value === undefined) return "Rp 0";
  return RUPIAH.format(Number(value)).replace(/ /g, " ");
}

export function parseRupiah(input: string): number {
  const digits = input.replace(/[^\d-]/g, "");
  if (!digits || digits === "-") return 0;
  return parseInt(digits, 10);
}

const DATE_ID = new Intl.DateTimeFormat("id-ID", {
  day: "2-digit",
  month: "short",
  year: "numeric",
});

const DATETIME_ID = new Intl.DateTimeFormat("id-ID", {
  day: "2-digit",
  month: "short",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

export function formatDate(value: Date | string | null | undefined) {
  if (!value) return "-";
  const d = value instanceof Date ? value : new Date(value);
  return DATE_ID.format(d);
}

export function formatDateTime(value: Date | string | null | undefined) {
  if (!value) return "-";
  const d = value instanceof Date ? value : new Date(value);
  return DATETIME_ID.format(d);
}

export function toInputDate(value: Date | string | null | undefined) {
  if (!value) return "";
  const d = value instanceof Date ? value : new Date(value);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export function generateInvoiceNo(date = new Date()) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  const rand = Math.floor(1000 + Math.random() * 9000);
  return `INV-${y}${m}${d}-${rand}`;
}

export const SALES_CHANNELS = ["OFFLINE", "SHOPEE", "TOKOPEDIA", "TIKTOK"] as const;
export type SalesChannel = (typeof SALES_CHANNELS)[number];

export const PAYMENT_METHODS = [
  "CASH",
  "TRANSFER",
  "QRIS",
  "SHOPEE",
  "TOKOPEDIA",
  "TIKTOK",
  "OTHER",
] as const;
export type PaymentMethod = (typeof PAYMENT_METHODS)[number];

export const SUPPLIER_PAYMENT_METHODS = ["CASH", "TRANSFER", "QRIS", "OTHER"] as const;
export type SupplierPaymentMethod = (typeof SUPPLIER_PAYMENT_METHODS)[number];

export const PRODUCT_STATUSES = ["ACTIVE", "INACTIVE"] as const;
export type ProductStatus = (typeof PRODUCT_STATUSES)[number];

export const CHANNEL_LABEL: Record<SalesChannel, string> = {
  OFFLINE: "Offline",
  SHOPEE: "Shopee",
  TOKOPEDIA: "Tokopedia",
  TIKTOK: "TikTok",
};

export const PAYMENT_LABEL: Record<PaymentMethod, string> = {
  CASH: "Tunai",
  TRANSFER: "Transfer",
  QRIS: "QRIS",
  SHOPEE: "Shopee",
  TOKOPEDIA: "Tokopedia",
  TIKTOK: "TikTok",
  OTHER: "Lainnya",
};
