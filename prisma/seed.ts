import { PrismaClient } from "@prisma/client";
import bcrypt from "bcryptjs";

const prisma = new PrismaClient();

async function main() {
  const adminEmail = "admin@sje.local";
  const adminPassword = "admin123";

  const existing = await prisma.user.findUnique({ where: { email: adminEmail } });
  if (!existing) {
    const passwordHash = await bcrypt.hash(adminPassword, 10);
    await prisma.user.create({
      data: {
        name: "Owner Toko",
        email: adminEmail,
        passwordHash,
      },
    });
    console.log(`[seed] Admin user dibuat:`);
    console.log(`        email   : ${adminEmail}`);
    console.log(`        password: ${adminPassword}`);
  } else {
    console.log(`[seed] Admin user sudah ada: ${adminEmail}`);
  }

  const supplierCount = await prisma.supplier.count();
  if (supplierCount === 0) {
    const s1 = await prisma.supplier.create({
      data: {
        name: "PT Elektronik Jaya",
        phone: "081200000001",
        address: "Jakarta",
        notes: "Supplier utama TV & kulkas",
      },
    });
    const s2 = await prisma.supplier.create({
      data: {
        name: "CV Sumber Dingin",
        phone: "081200000002",
        address: "Surabaya",
        notes: "Supplier AC & kipas",
      },
    });
    console.log(`[seed] 2 supplier contoh dibuat`);

    await prisma.product.createMany({
      data: [
        {
          sku: "TV-LG-32",
          name: "TV LED LG 32 inch",
          category: "TV",
          brand: "LG",
          model: "32LM550",
          defaultSupplierId: s1.id,
          costPrice: 2200000,
          sellPrice: 2600000,
          stock: 0,
        },
        {
          sku: "KLK-SHP-180",
          name: "Kulkas Sharp 2 Pintu 180L",
          category: "Kulkas",
          brand: "Sharp",
          model: "SJ-186XG",
          defaultSupplierId: s1.id,
          costPrice: 3100000,
          sellPrice: 3550000,
          stock: 0,
        },
        {
          sku: "MC-SAM-7KG",
          name: "Mesin Cuci Samsung 7kg",
          category: "Mesin Cuci",
          brand: "Samsung",
          model: "WA70H4000",
          defaultSupplierId: s1.id,
          costPrice: 2800000,
          sellPrice: 3250000,
          stock: 0,
        },
        {
          sku: "KP-MIY-16",
          name: "Kipas Angin Miyako 16 inch",
          category: "Kipas Angin",
          brand: "Miyako",
          model: "KAS-1689",
          defaultSupplierId: s2.id,
          costPrice: 180000,
          sellPrice: 235000,
          stock: 0,
        },
        {
          sku: "AC-PNS-1PK",
          name: "AC Panasonic 1PK",
          category: "AC",
          brand: "Panasonic",
          model: "CS-PN9WKJ",
          defaultSupplierId: s2.id,
          costPrice: 3500000,
          sellPrice: 4100000,
          stock: 0,
        },
      ],
    });
    console.log(`[seed] 5 produk contoh dibuat`);
  } else {
    console.log(`[seed] Data supplier sudah ada, skip seed contoh.`);
  }
}

main()
  .then(async () => {
    await prisma.$disconnect();
  })
  .catch(async (e) => {
    console.error(e);
    await prisma.$disconnect();
    process.exit(1);
  });
