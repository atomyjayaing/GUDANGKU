import { prisma } from "@/lib/prisma";

export type AuditAction =
  | "CREATE"
  | "UPDATE"
  | "DELETE"
  | "DEACTIVATE"
  | "ACTIVATE"
  | "SALE"
  | "PAYMENT"
  | "STOCK_IN"
  | "LOGIN";

export type AuditEntity =
  | "Product"
  | "Supplier"
  | "StockEntry"
  | "Sale"
  | "SupplierPayment"
  | "User";

export async function writeAudit(params: {
  userId?: string | null;
  action: AuditAction;
  entityType: AuditEntity;
  entityId?: string | null;
  description: string;
  metadata?: Record<string, unknown> | null;
}) {
  await prisma.auditLog.create({
    data: {
      userId: params.userId ?? null,
      action: params.action,
      entityType: params.entityType,
      entityId: params.entityId ?? null,
      description: params.description,
      metadata: params.metadata ? JSON.stringify(params.metadata) : null,
    },
  });
}
