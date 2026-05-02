"""
╔══════════════════════════════════════════════════╗
║          GudangKu - Aplikasi Manajemen Gudang    ║
║       Kelola Kardus & Penjualan dengan Mudah     ║
║                  Versi 1.0 (2026)                ║
╚══════════════════════════════════════════════════╝
Tech Stack: Python + Streamlit + SQLite + Pandas
Deploy: Streamlit Community Cloud (GRATIS)
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date, timedelta
import os
import io
import json
import time

# ─────────────────────────────────────────────
#  KONFIGURASI HALAMAN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="📦 GudangKu",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
#  CSS CUSTOM — UI BESAR, SIMPEL, RAMAH
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
    font-size: 18px !important;
}

/* ── Heading ── */
h1 { font-size: 34px !important; color: #2E7D32 !important; font-weight: 800 !important; }
h2 { font-size: 26px !important; color: #1B5E20 !important; font-weight: 700 !important; }
h3 { font-size: 22px !important; font-weight: 700 !important; }

/* ── Tab navigasi besar ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #f1f8e9;
    padding: 8px;
    border-radius: 12px;
}
.stTabs [data-baseweb="tab"] {
    font-size: 17px !important;
    font-weight: 700 !important;
    padding: 10px 20px !important;
    border-radius: 8px !important;
    min-height: 48px !important;
}
.stTabs [aria-selected="true"] {
    background-color: #2E7D32 !important;
    color: white !important;
}

/* ── Tombol besar ── */
.stButton > button {
    font-size: 18px !important;
    font-weight: 700 !important;
    min-height: 54px !important;
    border-radius: 10px !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.15) !important;
}

/* ── Input besar ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea textarea {
    font-size: 18px !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    color: #111111 !important;
}

/* ── Selectbox — HANYA warna teks, jangan ubah ukuran kotak ── */
[data-baseweb="select"] span,
[data-baseweb="select"] div,
[data-baseweb="select"] input {
    color: #111111 !important;
    font-size: 17px !important;
    font-family: 'Nunito', sans-serif !important;
}
/* Item di daftar dropdown yang terbuka */
[data-baseweb="menu"] li,
[data-baseweb="menu"] [role="option"] {
    font-size: 17px !important;
    color: #111111 !important;
    padding: 10px 16px !important;
}
[data-baseweb="menu"] li:hover,
[data-baseweb="menu"] [role="option"]:hover {
    background-color: #e8f5e9 !important;
}

/* ── Label form ── */
.stTextInput label, .stNumberInput label,
.stSelectbox label, .stTextArea label,
.stRadio label, .stDateInput label {
    font-size: 17px !important;
    font-weight: 700 !important;
    color: #1B5E20 !important;
}

/* ── Radio button besar ── */
.stRadio > div {
    gap: 16px !important;
}
.stRadio > div > label {
    font-size: 18px !important;
    padding: 8px 16px !important;
    background: #f8f8f8;
    border-radius: 8px;
    border: 2px solid #e0e0e0;
    cursor: pointer;
}

/* ── Metric card besar ── */
[data-testid="metric-container"] {
    background: white;
    border-radius: 14px;
    padding: 20px 24px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    border-left: 6px solid #2E7D32;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 16px !important;
    font-weight: 700 !important;
    color: #555 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 32px !important;
    font-weight: 800 !important;
    color: #1B5E20 !important;
}

/* ── Dataframe ── */
.dataframe { font-size: 16px !important; }

/* ── Alert / notifikasi ── */
.stSuccess, .stError, .stWarning, .stInfo {
    font-size: 18px !important;
    padding: 16px 20px !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

/* ── Divider ── */
hr { border-color: #e8f5e9 !important; margin: 20px 0 !important; }

/* ── Scrollbar cantik ── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 4px; }
::-webkit-scrollbar-thumb { background: #81c784; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LIST PRODUK ATOMY (GLOBAL DATA)
# ─────────────────────────────────────────────
ATOMY_PRODUCTS = [
    "Atomy Absolute Ampoule",
    "Atomy Absolute CellActive Skincare Set",
    "Atomy Absolute Eye-complex",
    "Atomy Absolute Lotion",
    "Atomy Absolute Nutrition Cream",
    "Atomy Absolute Serum",
    "Atomy Absolute Toner",
    "Atomy AC Special Set",
    "Atomy Adelica Lip Gloss",
    "Atomy Adelica Loose Powder",
    "Atomy Adelica Master Fit Cushion",
    "Atomy Aidam Cleanser",
    "Atomy Alaska E-Omega 3",
    "Atomy Apple Phenon",
    "Atomy Baby Body Wash & Shampoo",
    "Atomy Baby Care Set",
    "Atomy Baby Lotion",
    "Atomy BB Cream",
    "Atomy Body Cleanser",
    "Atomy Body Lotion",
    "Atomy Cafe Arabica",
    "Atomy Cafe Arabica Black",
    "Atomy Color Food Vitamin C",
    "Atomy Daily Expert Mask",
    "Atomy Deep Cleanser 150ml",
    "Atomy Dish Detergent",
    "Atomy Evening Care 4 Set",
    "Atomy Eye Lutein",
    "Atomy Fabric Detergent Powder",
    "Atomy Fabric Softener",
    "Atomy Foam Cleanser 150ml",
    "Atomy Gift Set Atomy",
    "Atomy Grilled Laver",
    "Atomy Hampers Lebaran Eksklusif",
    "Atomy Hampers Lebaran Gold",
    "Atomy Hampers Lebaran Silver",
    "Atomy Hand Soap",
    "Atomy HemoHim",
    "Atomy HemoHim Set 4",
    "Atomy Herbal Hair Conditioner",
    "Atomy Herbal Hair Shampoo",
    "Atomy Herbal Hair Tonic",
    "Atomy Hongsamdan Red Ginseng",
    "Atomy Hydra Brightening Care Set",
    "Atomy Hydra Brightening Cream",
    "Atomy Hydra Brightening Essence",
    "Atomy Kids Chewable Omega-3",
    "Atomy Kitchen Cloth",
    "Atomy Lip Glow",
    "Atomy Lip Treatment",
    "Atomy Liquid Fabric Detergent",
    "Atomy Marine Ampoule Gel Mask",
    "Atomy Men Skincare Set",
    "Atomy Mild Bubble Cleanser",
    "Atomy Milk Thistle Rhodiola",
    "Atomy Olive Oil Grilled Laver",
    "Atomy Oral Care System",
    "Atomy Organic Green Tea",
    "Atomy Paket Berkah Ramadan A",
    "Atomy Paket Berkah Ramadan B",
    "Atomy Paket Berkah Ramadan C",
    "Atomy Paket Bingkisan Lebaran",
    "Atomy Paket Glow Up Lebaran",
    "Atomy Paket Hampers Hari Raya",
    "Atomy Paket Hemat Keluarga",
    "Atomy Paket Idul Fitri Sehat",
    "Atomy Paket Kecantikan Lebaran",
    "Atomy Paket Lebaran A (Health Care)",
    "Atomy Paket Lebaran B (Skincare)",
    "Atomy Paket Lebaran C (Personal Care)",
    "Atomy Paket Ramadhan Care",
    "Atomy Paket Sehat Ramadhan",
    "Atomy Paket Suplemen Lebaran",
    "Atomy Parcel Hari Raya Idul Fitri",
    "Atomy Parcel Lebaran Atomy",
    "Atomy Peel Off Mask",
    "Atomy Peeling Gel",
    "Atomy Pomegranate Beauty",
    "Atomy Potato Ramen",
    "Atomy Probiotics 10+",
    "Atomy Pure Spirulina",
    "Atomy Pu'er Tea",
    "Atomy Scalpcare Conditioner",
    "Atomy Scalpcare Hair Care Set",
    "Atomy Scalpcare Shampoo",
    "Atomy Slim Body Shake 2.0",
    "Atomy Stainless Steel Scrubber",
    "Atomy Sun Stick",
    "Atomy Sunscreen Beige",
    "Atomy Sunscreen White",
    "Atomy The Fame Essence",
    "Atomy The Fame Eye Cream",
    "Atomy The Fame Lotion",
    "Atomy The Fame Nutrition Cream",
    "Atomy The Fame Set",
    "Atomy The Fame Toner",
    "Atomy Toothbrush",
    "Atomy Toothbrush Compact",
    "Atomy Toothpaste 200g",
    "Atomy Toothpaste 50g",
    "Atomy Travel Kit",
    "Atomy Vitamin B-Complex",
]

# ─────────────────────────────────────────────
DB_PATH = "gudangku.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS kardus (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            label           TEXT,
            nomor_pesanan   TEXT,
            nomor_id        TEXT,
            owner_name      TEXT,
            location        TEXT,
            type            TEXT,
            created_at      TEXT,
            created_by      TEXT,
            updated_at      TEXT,
            updated_by      TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            kardus_id    INTEGER,
            product_name TEXT,
            qty          INTEGER DEFAULT 0,
            unit_price   REAL    DEFAULT 0,
            added_at     TEXT,
            added_by     TEXT,
            FOREIGN KEY (kardus_id) REFERENCES kardus(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            type            TEXT,
            date            TEXT,
            kardus_id       INTEGER,
            product_name    TEXT,
            qty             INTEGER,
            price           REAL    DEFAULT 0,
            buyer_name      TEXT,
            transfer_to     TEXT,
            transfer_amount REAL    DEFAULT 0,
            performed_by    TEXT,
            notes           TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name   TEXT,
            record_id    INTEGER,
            action       TEXT,
            old_value    TEXT,
            new_value    TEXT,
            performed_by TEXT,
            timestamp    TEXT
        )
    """)

    conn.commit()
    conn.close()

def _insert_sample_data(conn, c):
    """Masukkan data contoh untuk testing."""
    now = tgl_indo(datetime.now())
    sample_kardus = [
        ("4521", "7789", "Titipan Anita",        "Rak A1", "Titipan"),
        ("4522", "7790", "Milik Saya - Budi",     "Rak B2", "Milik Sendiri"),
        ("4523", "7791", "Titipan Sari",          "Rak C3", "Titipan"),
        ("4524", "7792", "Milik Saya - Dewi",     "Lantai 2 Pojok", "Milik Sendiri"),
        ("4525", "7793", "Titipan Rudi",          "Rak A5", "Titipan"),
    ]
    kardus_ids = []
    for np, ni, own, loc, tipe in sample_kardus:
        label = f"{np}-{ni}-{own}"
        c.execute("""
            INSERT INTO kardus (label,nomor_pesanan,nomor_id,owner_name,location,type,
                                created_at,created_by,updated_at,updated_by)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (label, np, ni, own, loc, tipe, now, "Admin", now, "Admin"))
        kardus_ids.append(c.lastrowid)

    # Produk contoh
    sample_products = [
        (kardus_ids[0], "Sabun Mandi Dove",      10, 8000),
        (kardus_ids[0], "Shampo Pantene",         5, 15000),
        (kardus_ids[0], "Pasta Gigi Pepsodent",  12, 12000),
        (kardus_ids[1], "Minyak Goreng 2L",       8, 28000),
        (kardus_ids[1], "Gula Pasir 1Kg",        15, 16000),
        (kardus_ids[1], "Kopi Nescafe Sachet",   30, 3000),
        (kardus_ids[1], "Teh Celup 25pcs",       10, 14000),
        (kardus_ids[1], "Beras 5Kg",              6, 75000),
        (kardus_ids[2], "Deterjen Rinso 800g",    7, 22000),
        (kardus_ids[2], "Sabun Cuci Piring",      9, 9000),
        (kardus_ids[3], "Snack Chitato",         20, 12000),
        (kardus_ids[3], "Minuman Teh Botol",     24, 5000),
        (kardus_ids[4], "Odol Sensodyne",         5, 35000),
        (kardus_ids[4], "Vitamin C 1000mg",       8, 45000),
    ]
    for kid, pname, qty, price in sample_products:
        c.execute("""
            INSERT INTO inventory (kardus_id,product_name,qty,unit_price,added_at,added_by)
            VALUES (?,?,?,?,?,?)
        """, (kid, pname, qty, price, now, "Admin"))

    # Beberapa transaksi contoh
    sample_tx = [
        ("MASUK",     kardus_ids[0], "Sabun Mandi Dove",  10, 0,     "",       "",          "Admin"),
        ("MASUK",     kardus_ids[1], "Minyak Goreng 2L",   8, 0,     "",       "",          "Admin"),
        ("PENJUALAN", kardus_ids[1], "Gula Pasir 1Kg",     2, 32000, "Pak Ali","Milik Saya - Budi","Admin"),
        ("KELUAR",    kardus_ids[2], "Deterjen Rinso 800g",1, 0,     "",       "Titipan Sari","Admin"),
    ]
    for tipe, kid, prod, qty, price, buyer, trf, perf in sample_tx:
        c.execute("""
            INSERT INTO transactions
              (type,date,kardus_id,product_name,qty,price,buyer_name,
               transfer_to,transfer_amount,performed_by,notes)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (tipe, now, kid, prod, qty, price, buyer, trf, price, perf, "Data contoh"))

    conn.commit()

# ─────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────
def tgl_indo(dt=None):
    """Format tanggal ke format Indonesia: 25 Apr 2026 14:30"""
    if dt is None:
        dt = datetime.now()
    bulan = ["","Jan","Feb","Mar","Apr","Mei","Jun",
             "Jul","Agu","Sep","Okt","Nov","Des"]
    return f"{dt.day:02d} {bulan[dt.month]} {dt.year} {dt.hour:02d}:{dt.minute:02d}"

def tgl_indo_short(dt=None):
    """Format tanggal pendek: 25 Apr 2026"""
    if dt is None:
        dt = datetime.now()
    bulan = ["","Jan","Feb","Mar","Apr","Mei","Jun",
             "Jul","Agu","Sep","Okt","Nov","Des"]
    return f"{dt.day:02d} {bulan[dt.month]} {dt.year}"

def format_rupiah(angka):
    """Format angka ke Rupiah: Rp 1.234.567"""
    try:
        return f"Rp {int(angka):,}".replace(",", ".")
    except:
        return "Rp 0"

def audit(table, record_id, action, old_val, new_val, by):
    """Catat ke audit_log."""
    conn = get_conn()
    conn.execute("""
        INSERT INTO audit_log (table_name,record_id,action,old_value,new_value,performed_by,timestamp)
        VALUES (?,?,?,?,?,?,?)
    """, (table, record_id, action,
          json.dumps(old_val, ensure_ascii=False),
          json.dumps(new_val, ensure_ascii=False),
          by, tgl_indo()))
    conn.commit()
    conn.close()

def get_all_users():
    """Ambil semua nama user unik yang pernah input."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT DISTINCT performed_by as name FROM transactions WHERE performed_by != ''
        UNION
        SELECT DISTINCT created_by as name FROM kardus WHERE created_by != ''
        ORDER BY name
    """).fetchall()
    conn.close()
    names = [r["name"] for r in rows if r["name"]]
    if not names:
        names = ["Admin"]
    return names

def get_filtered_products(search_text=""):
    """Get filtered list produk Atomy berdasarkan search"""
    if not search_text:
        return ATOMY_PRODUCTS
    search_lower = search_text.lower()
    return [p for p in ATOMY_PRODUCTS if search_lower in p.lower()]

def search_produk_di_kardus(product_name):
    """Cari produk di mana saja dan tampilkan kardus yang memilikinya"""
    conn = get_conn()
    rows = conn.execute("""
        SELECT 
            i.id as inv_id,
            i.product_name,
            i.qty,
            i.unit_price,
            k.id as kardus_id,
            k.label as kardus_label,
            k.owner_name,
            k.location,
            k.type as kardus_type,
            k.nomor_pesanan,
            k.nomor_id
        FROM inventory i
        JOIN kardus k ON i.kardus_id = k.id
        WHERE LOWER(i.product_name) LIKE LOWER(?)
        ORDER BY k.owner_name, i.product_name
    """, (f"%{product_name}%",)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def edit_inventory_item(inv_id, new_qty, new_price, performed_by):
    """Edit inventory item (qty dan harga)"""
    conn = get_conn()
    try:
        old_data = conn.execute("SELECT qty, unit_price FROM inventory WHERE id=?", (inv_id,)).fetchone()
        if not old_data:
            return False, "Item tidak ditemukan"
        
        conn.execute(
            "UPDATE inventory SET qty=?, unit_price=? WHERE id=?",
            (new_qty, new_price, inv_id)
        )
        conn.commit()
        
        # Audit
        audit("inventory", inv_id, "UPDATE",
              {"qty": old_data["qty"], "price": old_data["unit_price"]},
              {"qty": new_qty, "price": new_price},
              performed_by)
        
        return True, "✅ Item berhasil diupdate"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"
    finally:
        conn.close()

def kurangi_stok_produk(kardus_id, product_name, qty_kurangi, performed_by, notes=""):
    """Kurangi stok produk dan catat transaksi KELUAR"""
    conn = get_conn()
    try:
        # Cek stok saat ini
        inv = conn.execute(
            "SELECT id, qty FROM inventory WHERE kardus_id=? AND product_name=?",
            (kardus_id, product_name)
        ).fetchone()
        
        if not inv:
            return False, f"Produk {product_name} tidak ada di kardus ini"
        
        if inv["qty"] < qty_kurangi:
            return False, f"Stok tidak cukup! Stok saat ini: {inv['qty']} pcs"
        
        # Kurangi stok
        new_qty = inv["qty"] - qty_kurangi
        conn.execute(
            "UPDATE inventory SET qty=? WHERE id=?",
            (new_qty, inv["id"])
        )
        
        # Catat transaksi KELUAR
        now_str = tgl_indo()
        conn.execute("""
            INSERT INTO transactions
            (type,date,kardus_id,product_name,qty,price,buyer_name,transfer_to,transfer_amount,performed_by,notes)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, ("KELUAR", now_str, kardus_id, product_name, qty_kurangi, 0, "", "", 0, performed_by, notes))
        
        conn.commit()
        return True, f"✅ {qty_kurangi} pcs {product_name} berhasil diambil. Stok tersisa: {new_qty} pcs"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"
    finally:
        conn.close()

def import_database(uploaded_file_bytes):
    """Import database dari file backup .db"""
    try:
        # Simpan ke file temporary
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            tmp.write(uploaded_file_bytes)
            tmp_path = tmp.name
        
        # Validasi file SQLite dengan membuka koneksi
        test_conn = sqlite3.connect(tmp_path)
        test_cursor = test_conn.cursor()
        
        # Cek apakah tabel-tabel yang dibutuhkan ada
        tables = ["kardus", "inventory", "transactions", "audit_log"]
        for tbl in tables:
            test_cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{tbl}'")
            if test_cursor.fetchone()[0] == 0:
                test_conn.close()
                return False, f"❌ File tidak valid — tabel '{tbl}' tidak ditemukan."
        
        test_conn.close()
        
        # Backup file lama (jika ada)
        import shutil
        if os.path.exists(DB_PATH):
            backup_path = DB_PATH.replace(".db", f"_old_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            shutil.copy(DB_PATH, backup_path)
        
        # Ganti dengan file baru
        shutil.move(tmp_path, DB_PATH)
        return True, f"✅ Database berhasil di-import! File lama tersimpan sebagai backup otomatis."
    
    except Exception as e:
        return False, f"❌ Error import database: {str(e)}"

def import_excel_data(excel_file_bytes, sheet_name):
    """Import data dari Excel ke database"""
    try:
        import io
        df = pd.read_excel(io.BytesIO(excel_file_bytes), sheet_name=sheet_name)
        
        if df.empty:
            return False, f"❌ Sheet '{sheet_name}' kosong!"
        
        conn = get_conn()
        c = conn.cursor()
        now_str = tgl_indo()
        inserted_count = 0
        errors = []
        
        if sheet_name == "Kardus":
            # Format: nomor_pesanan, nomor_id, owner_name, location, type
            for idx, row in df.iterrows():
                try:
                    np = str(row.get("nomor_pesanan", "")).strip()
                    ni = str(row.get("nomor_id", "")).strip()
                    owner = str(row.get("owner_name", "")).strip()
                    loc = str(row.get("location", "")).strip()
                    tipe = str(row.get("type", "Milik Sendiri")).strip()
                    
                    if not all([np, ni, owner, loc]):
                        errors.append(f"Baris {idx+2}: data tidak lengkap")
                        continue
                    
                    label = f"{np}-{ni}-{owner}"
                    c.execute("""
                        INSERT INTO kardus 
                        (label,nomor_pesanan,nomor_id,owner_name,location,type,created_at,created_by,updated_at,updated_by)
                        VALUES (?,?,?,?,?,?,?,?,?,?)
                    """, (label, np, ni, owner, loc, tipe, now_str, "Import Excel", now_str, "Import Excel"))
                    inserted_count += 1
                except Exception as e:
                    errors.append(f"Baris {idx+2}: {str(e)}")
        
        elif sheet_name == "Inventory":
            # Format: kardus_id atau label, product_name, qty, unit_price
            for idx, row in df.iterrows():
                try:
                    kardus_ref = str(row.get("kardus_id", "")).strip()
                    prod = str(row.get("product_name", "")).strip()
                    qty = int(row.get("qty", 0)) if pd.notna(row.get("qty")) else 0
                    harga = float(row.get("unit_price", 0)) if pd.notna(row.get("unit_price")) else 0
                    
                    if not prod or qty <= 0:
                        errors.append(f"Baris {idx+2}: nama produk atau qty tidak valid")
                        continue
                    
                    # Cari kardus_id dari label atau nomor
                    kardus_id = None
                    if kardus_ref.isdigit():
                        kardus_id = int(kardus_ref)
                    else:
                        # Cari berdasarkan label
                        kr = c.execute("SELECT id FROM kardus WHERE label=?", (kardus_ref,)).fetchone()
                        if kr:
                            kardus_id = kr[0]
                    
                    if not kardus_id:
                        errors.append(f"Baris {idx+2}: kardus tidak ditemukan")
                        continue
                    
                    c.execute("""
                        INSERT INTO inventory (kardus_id,product_name,qty,unit_price,added_at,added_by)
                        VALUES (?,?,?,?,?,?)
                    """, (kardus_id, prod, qty, harga, now_str, "Import Excel"))
                    inserted_count += 1
                except Exception as e:
                    errors.append(f"Baris {idx+2}: {str(e)}")
        
        elif sheet_name == "Transactions":
            # Format: type, date, kardus_id, product_name, qty, price, buyer_name, performed_by
            for idx, row in df.iterrows():
                try:
                    tipe = str(row.get("type", "")).strip().upper()
                    tgl = str(row.get("date", now_str)).strip()
                    kardus_ref = str(row.get("kardus_id", "")).strip()
                    prod = str(row.get("product_name", "")).strip()
                    qty = int(row.get("qty", 0)) if pd.notna(row.get("qty")) else 0
                    price = float(row.get("price", 0)) if pd.notna(row.get("price")) else 0
                    buyer = str(row.get("buyer_name", "")).strip()
                    by = str(row.get("performed_by", "Import Excel")).strip()
                    
                    if tipe not in ["MASUK", "KELUAR", "PENJUALAN"]:
                        errors.append(f"Baris {idx+2}: type harus MASUK, KELUAR, atau PENJUALAN")
                        continue
                    
                    if not prod or qty <= 0:
                        errors.append(f"Baris {idx+2}: produk atau qty tidak valid")
                        continue
                    
                    # Cari kardus_id
                    kardus_id = None
                    if kardus_ref and kardus_ref.isdigit():
                        kardus_id = int(kardus_ref)
                    elif kardus_ref:
                        kr = c.execute("SELECT id FROM kardus WHERE label=?", (kardus_ref,)).fetchone()
                        if kr:
                            kardus_id = kr[0]
                    
                    c.execute("""
                        INSERT INTO transactions
                        (type,date,kardus_id,product_name,qty,price,buyer_name,transfer_to,transfer_amount,performed_by,notes)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)
                    """, (tipe, tgl, kardus_id, prod, qty, price, buyer, "", 0, by, "Import Excel"))
                    inserted_count += 1
                except Exception as e:
                    errors.append(f"Baris {idx+2}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        msg = f"✅ Berhasil import {inserted_count} data dari sheet '{sheet_name}'."
        if errors:
            msg += f"\n⚠️ Ada {len(errors)} baris yang skip:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                msg += f"\n... dan {len(errors)-5} error lainnya"
        
        return True, msg
    
    except Exception as e:
        return False, f"❌ Error import Excel: {str(e)}"

def generate_excel_template():
    """Generate template Excel kosong untuk import"""
    with pd.ExcelWriter(io.BytesIO(), engine="openpyxl") as writer:
        # Sheet 1: Kardus
        df_kardus = pd.DataFrame({
            "nomor_pesanan": ["4521", "4522"],
            "nomor_id": ["7789", "7790"],
            "owner_name": ["Titipan Anita", "Milik Saya - Budi"],
            "location": ["Rak A1", "Rak B2"],
            "type": ["Titipan", "Milik Sendiri"]
        })
        df_kardus.to_excel(writer, sheet_name="Kardus", index=False)
        
        # Sheet 2: Inventory
        df_inventory = pd.DataFrame({
            "kardus_id": ["1", "1", "2"],
            "product_name": ["Sabun Mandi", "Shampo", "Minyak Goreng"],
            "qty": [10, 5, 8],
            "unit_price": [8000, 15000, 28000]
        })
        df_inventory.to_excel(writer, sheet_name="Inventory", index=False)
        
        # Sheet 3: Transactions
        df_transactions = pd.DataFrame({
            "type": ["MASUK", "MASUK", "PENJUALAN"],
            "date": ["25 Apr 2026 10:00", "25 Apr 2026 11:00", "25 Apr 2026 14:30"],
            "kardus_id": ["1", "2", "2"],
            "product_name": ["Sabun Mandi", "Minyak Goreng", "Minyak Goreng"],
            "qty": [10, 8, 2],
            "price": [0, 0, 56000],
            "buyer_name": ["", "", "Pak Ali"],
            "performed_by": ["Admin", "Admin", "Admin"]
        })
        df_transactions.to_excel(writer, sheet_name="Transactions", index=False)

def get_kardus_list():
    """Ambil semua kardus beserta jumlah item."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT k.*, COALESCE(SUM(i.qty), 0) as total_qty
        FROM kardus k
        LEFT JOIN inventory i ON k.id = i.kardus_id
        GROUP BY k.id
        ORDER BY k.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_inventory_by_kardus(kardus_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM inventory WHERE kardus_id = ? ORDER BY product_name
    """, (kardus_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_recent_transactions(limit=5):
    conn = get_conn()
    rows = conn.execute("""
        SELECT t.*, k.label as kardus_label, k.owner_name
        FROM transactions t
        LEFT JOIN kardus k ON t.kardus_id = k.id
        ORDER BY t.id DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_dashboard_stats():
    conn = get_conn()
    today = tgl_indo_short()
    stats = {}
    stats["total_kardus"] = conn.execute("SELECT COUNT(*) FROM kardus").fetchone()[0]
    stats["total_items"]  = conn.execute("SELECT COALESCE(SUM(qty),0) FROM inventory").fetchone()[0]

    r = conn.execute(
        "SELECT COALESCE(SUM(price),0) FROM transactions WHERE type='PENJUALAN' AND date LIKE ?",
        (f"%{today}%",)
    ).fetchone()[0]
    stats["penjualan_hari_ini"] = r

    r2 = conn.execute(
        "SELECT COALESCE(SUM(qty),0) FROM transactions WHERE type='MASUK' AND date LIKE ?",
        (f"%{today}%",)
    ).fetchone()[0]
    stats["masuk_hari_ini"] = r2
    conn.close()
    return stats


# ─────────────────────────────────────────────
#  INIT DATABASE (jalankan sekali)
# ─────────────────────────────────────────────
init_db()

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0
if "selected_kardus_id" not in st.session_state:
    st.session_state.selected_kardus_id = None
if "show_detail_kardus" not in st.session_state:
    st.session_state.show_detail_kardus = False
if "konfirmasi_jual" not in st.session_state:
    st.session_state.konfirmasi_jual = False
if "konfirmasi_ambil" not in st.session_state:
    st.session_state.konfirmasi_ambil = False
if "last_jual_data" not in st.session_state:
    st.session_state.last_jual_data = {}
if "show_buat_kardus" not in st.session_state:
    st.session_state.show_buat_kardus = False
if "multiple_produk_list" not in st.session_state:
    st.session_state.multiple_produk_list = []  # NEW: list of {produk, qty, harga}

# ─────────────────────────────────────────────
#  HEADER APLIKASI
# ─────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #2E7D32 0%, #388E3C 50%, #43A047 100%);
    padding: 24px 32px;
    border-radius: 16px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 4px 20px rgba(46,125,50,0.3);
">
    <div style="font-size:52px">📦</div>
    <div>
        <div style="color:white; font-size:36px; font-weight:800; letter-spacing:-0.5px">GudangKu</div>
        <div style="color:#c8e6c9; font-size:18px; font-weight:600">Kelola Kardus &amp; Penjualan dengan Mudah</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  NAVIGASI TAB UTAMA
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏠 Dashboard",
    "📦 Daftar Kardus",
    "➕ Barang Masuk",
    "🛒 Jual / Ambil",
    "📊 Laporan",
    "⚙️ Pengaturan",
    "🔍 Cari Barang",
])


# ══════════════════════════════════════════════
#  TAB 1: DASHBOARD
# ══════════════════════════════════════════════
with tab1:
    stats = get_dashboard_stats()

    st.markdown("### 📊 Ringkasan Hari Ini")
    st.caption("Lihat semua info penting gudang kamu dalam satu tampilan.")

    # ── 4 Kartu Metrik ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📦 Total Kardus", f"{stats['total_kardus']}")
    with c2:
        st.metric("🗃️ Total Item di Gudang", f"{stats['total_items']:,} pcs")
    with c3:
        st.metric("💰 Penjualan Hari Ini", format_rupiah(stats["penjualan_hari_ini"]))
    with c4:
        st.metric("📥 Barang Masuk Hari Ini", f"{stats['masuk_hari_ini']} pcs")

    st.markdown("---")

    # ── 2 Tombol Super Besar ──
    st.markdown("### ⚡ Aksi Cepat")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""
        <style>
        div[data-testid="column"]:nth-of-type(1) .stButton > button {
            background: linear-gradient(135deg, #2E7D32, #43A047) !important;
            color: white !important;
            font-size: 22px !important;
            min-height: 80px !important;
            border: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
        if st.button("🟢  BARANG MASUK\n\n➕ Tambah stok ke gudang", use_container_width=True):
            st.info("👆 Silakan klik tab **➕ Barang Masuk** di atas untuk menambah barang!")

    with col_b:
        st.markdown("""
        <style>
        div[data-testid="column"]:nth-of-type(2) .stButton > button {
            background: linear-gradient(135deg, #1565C0, #1976D2) !important;
            color: white !important;
            font-size: 22px !important;
            min-height: 80px !important;
            border: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
        if st.button("🔵  JUAL / AMBIL BARANG\n\n🛒 Proses penjualan atau pengambilan", use_container_width=True):
            st.info("👆 Silakan klik tab **🛒 Jual / Ambil** di atas untuk memproses penjualan!")

    st.markdown("---")

    # ── 5 Transaksi Terbaru ──
    st.markdown("### 🕐 5 Transaksi Terakhir")
    recent = get_recent_transactions(5)

    if recent:
        df_recent = pd.DataFrame(recent)
        cols_show = ["date", "type", "kardus_label", "product_name", "qty", "price", "performed_by"]
        cols_show = [c for c in cols_show if c in df_recent.columns]
        df_recent = df_recent[cols_show].copy()
        df_recent.columns = ["Tanggal", "Tipe", "Kardus", "Produk", "Qty", "Harga (Rp)", "Dilakukan Oleh"][:len(cols_show)]

        def warna_tipe(val):
            if val == "MASUK":
                return "color: #2E7D32; font-weight:700"
            elif val == "PENJUALAN":
                return "color: #1565C0; font-weight:700"
            else:
                return "color: #E65100; font-weight:700"

        styled = df_recent.style.map(warna_tipe, subset=["Tipe"])
        st.dataframe(styled, use_container_width=True, hide_index=True)
    else:
        st.info("📭 Belum ada transaksi. Mulai dengan menambah barang masuk!")

    st.markdown("---")
    st.caption("💡 Untuk laporan lengkap, klik tab **📊 Laporan** di atas.")


# ══════════════════════════════════════════════
#  TAB 2: DAFTAR KARDUS
# ══════════════════════════════════════════════
with tab2:
    st.markdown("### 📦 Daftar Semua Kardus")
    st.caption("Semua kardus yang ada di gudang ditampilkan di sini.")

    # ── Tombol Buat Kardus Baru ──
    col_btn, col_space = st.columns([1, 2])
    with col_btn:
        if st.button("➕  Buat Kardus Baru", use_container_width=True):
            st.session_state.show_buat_kardus = not st.session_state.show_buat_kardus

    # ── Form Buat Kardus Baru ──
    if st.session_state.get("show_buat_kardus", False):
        with st.container():
            st.markdown("---")
            st.markdown("#### 📝 Form Buat Kardus Baru")

            users = get_all_users()

            bk_col1, bk_col2 = st.columns(2)
            with bk_col1:
                bk_nomor_pesanan = st.text_input("Nomor Pesanan (4 digit)", max_chars=4,
                    placeholder="Contoh: 4526", key="bk_nopesanan")
                bk_nomor_id = st.text_input("Nomor ID Driver (4 digit)", max_chars=4,
                    placeholder="Contoh: 7794", key="bk_noid")
                bk_owner = st.text_input("Nama Pemilik Kardus",
                    placeholder="Contoh: Titipan Anita / Milik Saya - Budi", key="bk_owner")
            with bk_col2:
                bk_location = st.text_input("Lokasi Kardus",
                    placeholder="Contoh: Rak A3, Lantai 2", key="bk_loc")
                bk_type = st.radio("Tipe Kardus", ["Titipan", "Milik Sendiri"], key="bk_type",
                    horizontal=True)
                bk_by_opt = users + ["Ketik nama baru..."]
                bk_by_sel = st.selectbox("Dibuat Oleh", bk_by_opt, key="bk_by_sel")
                if bk_by_sel == "Ketik nama baru...":
                    bk_by = st.text_input("Nama Anda:", key="bk_by_new")
                else:
                    bk_by = bk_by_sel

            # Preview label
            if bk_nomor_pesanan and bk_nomor_id and bk_owner:
                preview_label = f"{bk_nomor_pesanan}-{bk_nomor_id}-{bk_owner}"
                st.info(f"🏷️ **Label otomatis:** `{preview_label}`")

            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button("✅  SIMPAN KARDUS BARU", use_container_width=True, key="btn_save_kardus"):
                    err = []
                    if not bk_nomor_pesanan or len(bk_nomor_pesanan) != 4:
                        err.append("Nomor Pesanan harus tepat 4 digit angka.")
                    if not bk_nomor_id or len(bk_nomor_id) != 4:
                        err.append("Nomor ID harus tepat 4 digit angka.")
                    if not bk_owner.strip():
                        err.append("Nama pemilik tidak boleh kosong.")
                    if not bk_location.strip():
                        err.append("Lokasi tidak boleh kosong.")
                    if not bk_by.strip():
                        err.append("Nama pembuat tidak boleh kosong.")
                    if err:
                        for e in err:
                            st.error(f"❌ {e}")
                    else:
                        label = f"{bk_nomor_pesanan}-{bk_nomor_id}-{bk_owner.strip()}"
                        now_str = tgl_indo()
                        conn = get_conn()
                        conn.execute("""
                            INSERT INTO kardus
                              (label,nomor_pesanan,nomor_id,owner_name,location,type,
                               created_at,created_by,updated_at,updated_by)
                            VALUES (?,?,?,?,?,?,?,?,?,?)
                        """, (label, bk_nomor_pesanan, bk_nomor_id, bk_owner.strip(),
                              bk_location.strip(), bk_type, now_str, bk_by.strip(),
                              now_str, bk_by.strip()))
                        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                        conn.commit()
                        conn.close()
                        audit("kardus", new_id, "CREATE", {}, {"label": label}, bk_by)
                        st.success(f"✅ Kardus **{label}** berhasil dibuat!")
                        st.session_state.show_buat_kardus = False
                        st.rerun()
            with col_cancel:
                if st.button("❌  Batal", use_container_width=True, key="btn_cancel_kardus"):
                    st.session_state.show_buat_kardus = False
                    st.rerun()
            st.markdown("---")

    # ── Search Bar ──
    search_kardus = st.text_input("🔍  Cari kardus (nama pemilik, label, lokasi...)",
        placeholder="Ketik untuk mencari...", key="search_kardus")

    # ── Tabel Kardus ──
    all_kardus = get_kardus_list()
    if search_kardus:
        q = search_kardus.lower()
        all_kardus = [k for k in all_kardus if
            q in k["label"].lower() or
            q in k["owner_name"].lower() or
            q in k["location"].lower()]

    if all_kardus:
        df_kardus = pd.DataFrame(all_kardus)
        df_display = df_kardus[["label","owner_name","location","type","total_qty"]].copy()
        df_display.columns = ["🏷️ Label", "👤 Pemilik", "📍 Lokasi", "🗂️ Tipe", "📊 Jumlah Item"]

        st.markdown(f"**Ditemukan: {len(all_kardus)} kardus**")
        st.dataframe(df_display, use_container_width=True, hide_index=True,
            column_config={
                "🗂️ Tipe": st.column_config.TextColumn(width="medium"),
                "📊 Jumlah Item": st.column_config.NumberColumn(format="%d pcs"),
            })

        # ── Pilih Kardus untuk Detail ──
        st.markdown("#### 🔎 Lihat Detail Kardus")
        pilihan_label = [f"{k['owner_name']} | {k['nomor_pesanan']}-{k['nomor_id']} | {k['location']}" for k in all_kardus]
        sel_kardus_str = st.selectbox("Pilih kardus untuk lihat / edit detail:",
            ["-- Pilih Kardus --"] + pilihan_label, key="sel_kardus_detail")

        if sel_kardus_str != "-- Pilih Kardus --":
            sel_idx = pilihan_label.index(sel_kardus_str)
            sel_k = all_kardus[sel_idx]
            sel_id = sel_k["id"]

            with st.container():
                st.markdown("---")
                # ── Info Kardus ──
                badge_color = "#1565C0" if sel_k["type"] == "Titipan" else "#2E7D32"
                st.markdown(f"""
                <div style="background:white; border:2px solid {badge_color};
                     border-radius:12px; padding:20px 24px; margin-bottom:16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="font-size:24px; font-weight:800; color:{badge_color}">
                                📦 {sel_k['label']}
                            </span>
                            <span style="background:{badge_color}; color:white; padding:4px 12px;
                                  border-radius:20px; font-size:14px; font-weight:700;
                                  margin-left:12px;">{sel_k['type']}</span>
                        </div>
                    </div>
                    <div style="margin-top:12px; display:grid; grid-template-columns:1fr 1fr; gap:8px;">
                        <div>👤 <b>Pemilik:</b> {sel_k['owner_name']}</div>
                        <div>📍 <b>Lokasi:</b> {sel_k['location']}</div>
                        <div>📅 <b>Dibuat:</b> {sel_k['created_at']}</div>
                        <div>👷 <b>Dibuat oleh:</b> {sel_k['created_by']}</div>
                        <div>🔄 <b>Update terakhir:</b> {sel_k['updated_at']}</div>
                        <div>🏷️ <b>Nomor Pesanan:</b> {sel_k['nomor_pesanan']} | <b>ID:</b> {sel_k['nomor_id']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── Isi Produk ──
                st.markdown("##### 📋 Isi Produk dalam Kardus Ini")
                inv = get_inventory_by_kardus(sel_id)
                if inv:
                    df_inv = pd.DataFrame(inv)
                    df_inv_disp = df_inv[["product_name","qty","unit_price"]].copy()
                    df_inv_disp.columns = ["Nama Produk","Stok (pcs)","Harga Satuan (Rp)"]
                    st.dataframe(df_inv_disp, use_container_width=True, hide_index=True,
                        column_config={
                            "Stok (pcs)": st.column_config.NumberColumn(format="%d pcs"),
                            "Harga Satuan (Rp)": st.column_config.NumberColumn(format="Rp %,.0f"),
                        })
                else:
                    st.info("📭 Kardus ini masih kosong.")

                # ── Tambah Produk ke Kardus ──
                with st.expander("➕ Tambah Produk ke Kardus Ini"):
                    users = get_all_users()
                    tp_col1, tp_col2 = st.columns(2)
                    with tp_col1:
                        tp_nama = st.text_input("Nama Produk", key=f"tp_nama_{sel_id}",
                            placeholder="Contoh: Sabun Mandi")
                        tp_qty = st.number_input("Jumlah (pcs)", min_value=1, value=1, key=f"tp_qty_{sel_id}")
                    with tp_col2:
                        tp_harga = st.number_input("Harga Satuan (Rp, opsional)", min_value=0,
                            value=0, step=500, key=f"tp_harga_{sel_id}")
                        tp_by_opt = users + ["Ketik nama baru..."]
                        tp_by_sel = st.selectbox("Dilakukan Oleh", tp_by_opt, key=f"tp_by_{sel_id}")
                        if tp_by_sel == "Ketik nama baru...":
                            tp_by = st.text_input("Nama Anda:", key=f"tp_by_new_{sel_id}")
                        else:
                            tp_by = tp_by_sel

                    if st.button("✅  Simpan Tambah Produk", key=f"btn_tp_{sel_id}", use_container_width=True):
                        if not tp_nama.strip():
                            st.error("❌ Nama produk tidak boleh kosong!")
                        elif tp_qty <= 0:
                            st.error("❌ Jumlah harus lebih dari 0!")
                        elif not tp_by.strip():
                            st.error("❌ Nama pelaksana tidak boleh kosong!")
                        else:
                            now_str = tgl_indo()
                            conn = get_conn()
                            # Cek apakah produk sudah ada
                            existing = conn.execute(
                                "SELECT id, qty FROM inventory WHERE kardus_id=? AND product_name=?",
                                (sel_id, tp_nama.strip())
                            ).fetchone()
                            if existing:
                                conn.execute("UPDATE inventory SET qty=?, added_at=?, added_by=? WHERE id=?",
                                    (existing["qty"] + tp_qty, now_str, tp_by.strip(), existing["id"]))
                            else:
                                conn.execute("""
                                    INSERT INTO inventory (kardus_id,product_name,qty,unit_price,added_at,added_by)
                                    VALUES (?,?,?,?,?,?)
                                """, (sel_id, tp_nama.strip(), tp_qty, tp_harga, now_str, tp_by.strip()))
                            # Catat transaksi MASUK
                            conn.execute("""
                                INSERT INTO transactions
                                  (type,date,kardus_id,product_name,qty,price,buyer_name,
                                   transfer_to,transfer_amount,performed_by,notes)
                                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                            """, ("MASUK", now_str, sel_id, tp_nama.strip(), tp_qty, 0,
                                  "", "", 0, tp_by.strip(), f"Tambah dari detail kardus"))
                            conn.commit()
                            conn.close()
                            st.success(f"✅ {tp_nama} sebanyak {tp_qty} pcs berhasil ditambahkan!")
                            st.rerun()

                # ── Edit Kardus ──
                with st.expander("✏️ Edit Info Kardus Ini"):
                    users = get_all_users()
                    ek_col1, ek_col2 = st.columns(2)
                    with ek_col1:
                        ek_nopesanan = st.text_input("Nomor Pesanan", value=sel_k["nomor_pesanan"],
                            max_chars=4, key=f"ek_nopesanan_{sel_id}")
                        ek_noid = st.text_input("Nomor ID Driver", value=sel_k["nomor_id"],
                            max_chars=4, key=f"ek_noid_{sel_id}")
                        ek_owner = st.text_input("Nama Pemilik", value=sel_k["owner_name"],
                            key=f"ek_owner_{sel_id}")
                    with ek_col2:
                        ek_loc = st.text_input("Lokasi", value=sel_k["location"],
                            key=f"ek_loc_{sel_id}")
                        tipe_idx = 0 if sel_k["type"] == "Titipan" else 1
                        ek_type = st.radio("Tipe", ["Titipan","Milik Sendiri"],
                            index=tipe_idx, key=f"ek_type_{sel_id}", horizontal=True)
                        ek_by_opt = users + ["Ketik nama baru..."]
                        ek_by_sel = st.selectbox("Diedit Oleh", ek_by_opt, key=f"ek_by_{sel_id}")
                        if ek_by_sel == "Ketik nama baru...":
                            ek_by = st.text_input("Nama Anda:", key=f"ek_by_new_{sel_id}")
                        else:
                            ek_by = ek_by_sel

                    if st.button("✅  Simpan Perubahan", key=f"btn_ek_{sel_id}", use_container_width=True):
                        err = []
                        if not ek_nopesanan or len(ek_nopesanan) != 4:
                            err.append("Nomor Pesanan harus 4 digit.")
                        if not ek_noid or len(ek_noid) != 4:
                            err.append("Nomor ID harus 4 digit.")
                        if not ek_owner.strip():
                            err.append("Nama pemilik tidak boleh kosong.")
                        if not ek_by.strip():
                            err.append("Nama editor tidak boleh kosong.")
                        if err:
                            for e in err:
                                st.error(f"❌ {e}")
                        else:
                            new_label = f"{ek_nopesanan}-{ek_noid}-{ek_owner.strip()}"
                            now_str = tgl_indo()
                            conn = get_conn()
                            conn.execute("""
                                UPDATE kardus
                                SET label=?,nomor_pesanan=?,nomor_id=?,owner_name=?,
                                    location=?,type=?,updated_at=?,updated_by=?
                                WHERE id=?
                            """, (new_label, ek_nopesanan, ek_noid, ek_owner.strip(),
                                  ek_loc.strip(), ek_type, now_str, ek_by.strip(), sel_id))
                            conn.commit()
                            conn.close()
                            audit("kardus", sel_id, "UPDATE",
                                  {"label": sel_k["label"]}, {"label": new_label}, ek_by)
                            st.success(f"✅ Kardus berhasil diupdate menjadi **{new_label}**!")
                            st.rerun()

                # ── Hapus Kardus ──
                with st.expander("🗑️ Hapus Kardus Ini"):
                    inv_check = get_inventory_by_kardus(sel_id)
                    total_stok = sum(i["qty"] for i in inv_check)
                    if total_stok > 0:
                        st.warning(f"⚠️ Kardus ini masih ada **{total_stok} item** stok. "
                                   f"Kosongkan dulu sebelum menghapus!")
                    else:
                        st.warning("⚠️ Menghapus kardus ini tidak bisa dibatalkan!")
                        alasan_hapus = st.text_input("Alasan menghapus (wajib diisi):",
                            key=f"alasan_hapus_{sel_id}")
                        users = get_all_users()
                        hapus_by = st.selectbox("Dihapus Oleh", users, key=f"hapus_by_{sel_id}")

                        confirm_hapus = st.checkbox(
                            f"✅ Saya yakin ingin menghapus kardus **{sel_k['label']}**",
                            key=f"chk_hapus_{sel_id}")
                        if st.button("🗑️  HAPUS KARDUS INI", key=f"btn_hapus_{sel_id}",
                                     use_container_width=True):
                            if not confirm_hapus:
                                st.error("❌ Centang kotak konfirmasi terlebih dahulu!")
                            elif not alasan_hapus.strip():
                                st.error("❌ Alasan hapus tidak boleh kosong!")
                            else:
                                audit("kardus", sel_id, "DELETE",
                                      dict(sel_k), {"alasan": alasan_hapus}, hapus_by)
                                conn = get_conn()
                                conn.execute("DELETE FROM kardus WHERE id=?", (sel_id,))
                                conn.execute("DELETE FROM inventory WHERE kardus_id=?", (sel_id,))
                                conn.commit()
                                conn.close()
                                st.success(f"✅ Kardus **{sel_k['label']}** berhasil dihapus.")
                                st.rerun()
    else:
        st.info("📭 Belum ada kardus. Klik **Buat Kardus Baru** di atas untuk mulai!")


# ══════════════════════════════════════════════
#  TAB 3: BARANG MASUK
# ══════════════════════════════════════════════
with tab3:
    st.markdown("### ➕ Catat Barang Masuk ke Gudang")
    st.caption("Pilih kardus, tulis nama barang, dan jumlahnya. Selesai!")

    all_kardus = get_kardus_list()
    users = get_all_users()

    if not all_kardus:
        st.warning("⚠️ Belum ada kardus! Buat kardus dulu di tab **📦 Daftar Kardus**.")
    else:
        with st.form("form_barang_masuk", clear_on_submit=True):
            st.markdown("#### 📋 Isi Form Barang Masuk")

            # ── Baris 1: Pilih Kardus (LEBAR PENUH) ──
            kardus_options = [f"{k['owner_name']}  |  No. {k['nomor_pesanan']}-{k['nomor_id']}  |  📍 {k['location']}" for k in all_kardus]
            bm_kardus_str = st.selectbox(
                "1️⃣  Pilih Kardus Tujuan",
                kardus_options,
                help="Pilih kardus mana yang akan diisi barang ini"
            )
            bm_kardus_idx = kardus_options.index(bm_kardus_str)
            sel_k_info = all_kardus[bm_kardus_idx]
            bm_kardus_id = sel_k_info["id"]

            # Info kardus terpilih
            st.info(f"📦 **{sel_k_info['label']}**  |  📍 {sel_k_info['location']}  |  👤 {sel_k_info['owner_name']}")

            # ── Baris 2: Nama Produk (LEBAR PENUH) ──
            bm_produk = st.text_input(
                "2️⃣  Nama Produk / Barang",
                placeholder="Contoh: Sabun Mandi Dove"
            )

            # ── Baris 3: Qty dan Harga (2 kolom, input angka — aman di kolom sempit) ──
            bm_c1, bm_c2 = st.columns(2)
            with bm_c1:
                bm_qty = st.number_input("3️⃣  Jumlah (pcs)", min_value=1, value=1)
            with bm_c2:
                bm_harga = st.number_input("Harga Satuan (Rp, opsional)", min_value=0, value=0, step=500)

            # ── Baris 4: Tipe Barang ──
            bm_type = st.radio(
                "4️⃣  Tipe Barang",
                ["Titipan", "Milik Sendiri"],
                horizontal=True,
                help="Titipan = barang milik orang lain. Milik Sendiri = barang kamu."
            )

            # ── Baris 5: Dilakukan Oleh (LEBAR PENUH) ──
            bm_by_opt = users + ["Ketik nama baru..."]
            bm_by_sel = st.selectbox("5️⃣  Dilakukan Oleh", bm_by_opt)
            if bm_by_sel == "Ketik nama baru...":
                bm_by = st.text_input("✏️  Ketik nama kamu:")
            else:
                bm_by = bm_by_sel

            # ── Baris 6: Catatan ──
            bm_notes = st.text_area("6️⃣  Catatan (opsional)",
                placeholder="Contoh: Barang datang dari Surabaya",
                height=80)

            submitted_masuk = st.form_submit_button(
                "✅  SIMPAN BARANG MASUK",
                use_container_width=True,
                type="primary"
            )

        if submitted_masuk:
            err = []
            if not bm_produk.strip():
                err.append("Nama produk tidak boleh kosong!")
            if bm_qty <= 0:
                err.append("Jumlah harus lebih dari 0!")
            final_by = bm_by if bm_by_sel != "Ketik nama baru..." else bm_by
            if not final_by.strip():
                err.append("Nama pelaksana tidak boleh kosong!")

            if err:
                for e in err:
                    st.error(f"❌ {e}")
            else:
                now_str = tgl_indo()
                conn = get_conn()
                existing = conn.execute(
                    "SELECT id, qty FROM inventory WHERE kardus_id=? AND product_name=?",
                    (bm_kardus_id, bm_produk.strip())
                ).fetchone()
                if existing:
                    conn.execute("UPDATE inventory SET qty=?, added_at=?, added_by=? WHERE id=?",
                        (existing["qty"] + bm_qty, now_str, final_by.strip(), existing["id"]))
                else:
                    conn.execute("""
                        INSERT INTO inventory (kardus_id,product_name,qty,unit_price,added_at,added_by)
                        VALUES (?,?,?,?,?,?)
                    """, (bm_kardus_id, bm_produk.strip(), bm_qty, bm_harga, now_str, final_by.strip()))

                conn.execute("""
                    INSERT INTO transactions
                      (type,date,kardus_id,product_name,qty,price,buyer_name,
                       transfer_to,transfer_amount,performed_by,notes)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """, ("MASUK", now_str, bm_kardus_id, bm_produk.strip(), bm_qty, 0,
                      "", "", 0, final_by.strip(), bm_notes))
                conn.commit()
                conn.close()

                st.success(f"✅ **{bm_qty} pcs {bm_produk}** berhasil masuk ke kardus "
                           f"**{sel_k_info['label']}**! Stok otomatis diperbarui.")
                st.balloons()


# ══════════════════════════════════════════════
#  TAB 4: JUAL / AMBIL BARANG
# ══════════════════════════════════════════════
with tab4:
    st.markdown("### 🛒 Jual / Ambil Barang dari Gudang")
    st.caption("Pilih mode: Jual ke customer (ada pembayaran) atau Ambil titipan (tanpa bayar).")

    sub_a, sub_b = st.tabs(["💰 A. Jual ke Customer", "📤 B. Ambil Titipan"])

    all_kardus = get_kardus_list()
    users = get_all_users()

    # ────────────────────────────────────────
    #  SUB TAB A: JUAL KE CUSTOMER
    # ────────────────────────────────────────
    with sub_a:
        st.markdown("#### 💰 Proses Penjualan ke Customer")
        if not all_kardus:
            st.warning("⚠️ Belum ada kardus & stok! Tambah barang masuk dulu.")
        else:
            ja_kardus_opts = [f"{k['owner_name']} | {k['nomor_pesanan']}-{k['nomor_id']} | Stok: {k['total_qty']} pcs"
                              for k in all_kardus if k["total_qty"] > 0]
            if not ja_kardus_opts:
                st.warning("⚠️ Semua kardus kosong stoknya! Tambah barang masuk dulu.")
            else:
                # ── Baris 1: Pilih Kardus (LEBAR PENUH) ──
                ja_kardus_str = st.selectbox(
                    "1️⃣  Pilih Kardus Sumber",
                    ja_kardus_opts,
                    key="ja_kardus"
                )
                kardus_ada_stok = [k for k in all_kardus if k["total_qty"] > 0]
                ja_kardus_idx = ja_kardus_opts.index(ja_kardus_str)
                ja_kardus_info = kardus_ada_stok[ja_kardus_idx]
                ja_kardus_id = ja_kardus_info["id"]

                st.info(f"📦 **{ja_kardus_info['label']}**  |  📍 {ja_kardus_info['location']}  |  👤 {ja_kardus_info['owner_name']}")

                # ── Baris 2: Pilih Produk (LEBAR PENUH) ──
                inv_kardus = get_inventory_by_kardus(ja_kardus_id)
                inv_ada = [i for i in inv_kardus if i["qty"] > 0]

                if not inv_ada:
                    st.warning("Kardus ini kosong! Pilih kardus lain.")
                else:
                    produk_opts = [f"{i['product_name']}  —  stok: {i['qty']} pcs" for i in inv_ada]
                    ja_produk_str = st.selectbox("2️⃣  Pilih Produk", produk_opts, key="ja_produk")
                    ja_produk_idx = produk_opts.index(ja_produk_str)
                    ja_produk_info = inv_ada[ja_produk_idx]
                    ja_produk_nama = ja_produk_info["product_name"]
                    ja_stok_max = ja_produk_info["qty"]
                    ja_harga_satuan = ja_produk_info.get("unit_price", 0) or 0

                    # ── Baris 3: Jumlah dan Harga (2 kolom — angka, aman sempit) ──
                    ja_c1, ja_c2 = st.columns(2)
                    with ja_c1:
                        ja_qty = st.number_input(
                            f"3️⃣  Jumlah Dijual (maks: {ja_stok_max} pcs)",
                            min_value=1, max_value=ja_stok_max, value=1, key="ja_qty"
                        )
                    with ja_c2:
                        ja_harga_total = st.number_input(
                            "4️⃣  Harga Total (Rp)",
                            min_value=0,
                            value=int(ja_harga_satuan * 1),
                            step=500,
                            key="ja_harga"
                        )

                    # ── Baris 4: Nama Pembeli (LEBAR PENUH) ──
                    ja_buyer = st.text_input("5️⃣  Nama Pembeli",
                        placeholder="Contoh: Pak Budi", key="ja_buyer")

                    # ── Baris 5: Transfer ke (LEBAR PENUH) ──
                    ja_transfer_to = st.text_input(
                        "6️⃣  Uang Ditransfer ke:",
                        value=ja_kardus_info["owner_name"],
                        key="ja_transfer"
                    )

                    # ── Baris 6: Dilakukan Oleh (LEBAR PENUH) ──
                    ja_by_opt = users + ["Ketik nama baru..."]
                    ja_by_sel = st.selectbox("7️⃣  Dilakukan Oleh", ja_by_opt, key="ja_by_sel")
                    if ja_by_sel == "Ketik nama baru...":
                        ja_by = st.text_input("✏️  Ketik nama kamu:", key="ja_by_new")
                    else:
                        ja_by = ja_by_sel

                    ja_notes = st.text_area("Catatan (opsional)", height=60, key="ja_notes")

                if inv_ada:
                    # Info ringkasan sebelum konfirmasi
                    st.markdown(f"""
                    <div style="background:#e8f5e9; border:2px solid #2E7D32;
                         border-radius:10px; padding:16px 20px; margin:12px 0;">
                        <b>📋 Ringkasan Penjualan:</b><br>
                        🏷️ Kardus: <b>{ja_kardus_info['label']}</b> &nbsp;|&nbsp;
                        📍 Lokasi: <b>{ja_kardus_info['location']}</b><br>
                        🛒 Produk: <b>{ja_produk_nama}</b> x {ja_qty} pcs &nbsp;|&nbsp;
                        💰 Total: <b>{format_rupiah(ja_harga_total)}</b><br>
                        💸 Transfer ke: <b>{ja_kardus_info['owner_name']}</b>
                    </div>
                    """, unsafe_allow_html=True)

                    if not st.session_state.konfirmasi_jual:
                        if st.button("🛒  PROSES PENJUALAN", use_container_width=True,
                                     key="btn_proses_jual"):
                            # Validasi
                            err = []
                            final_by_jual = ja_by if ja_by_sel != "Ketik nama baru..." else ja_by
                            if not ja_buyer.strip():
                                err.append("Nama pembeli tidak boleh kosong!")
                            if not final_by_jual.strip():
                                err.append("Nama pelaksana tidak boleh kosong!")
                            if err:
                                for e in err:
                                    st.error(f"❌ {e}")
                            else:
                                st.session_state.konfirmasi_jual = True
                                st.session_state.last_jual_data = {
                                    "kardus_id": ja_kardus_id,
                                    "kardus_label": ja_kardus_info["label"],
                                    "produk": ja_produk_nama,
                                    "qty": ja_qty,
                                    "harga": ja_harga_total,
                                    "buyer": ja_buyer,
                                    "transfer_to": ja_transfer_to,
                                    "by": final_by_jual,
                                    "notes": ja_notes,
                                    "inv_id": ja_produk_info["id"],
                                }
                                st.rerun()
                    else:
                        d = st.session_state.last_jual_data
                        st.warning(f"⚠️ **Yakin mau jual {d['qty']} pcs {d['produk']} "
                                   f"ke {d['buyer']} seharga {format_rupiah(d['harga'])}?**")
                        ck1, ck2 = st.columns(2)
                        with ck1:
                            if st.button("✅  YA, PROSES SEKARANG!", use_container_width=True,
                                         key="btn_konfirm_jual"):
                                now_str = tgl_indo()
                                conn = get_conn()
                                # Kurangi stok
                                conn.execute(
                                    "UPDATE inventory SET qty=qty-? WHERE id=?",
                                    (d["qty"], d["inv_id"])
                                )
                                # Catat transaksi
                                conn.execute("""
                                    INSERT INTO transactions
                                      (type,date,kardus_id,product_name,qty,price,buyer_name,
                                       transfer_to,transfer_amount,performed_by,notes)
                                    VALUES (?,?,?,?,?,?,?,?,?,?,?)
                                """, ("PENJUALAN", now_str, d["kardus_id"], d["produk"],
                                      d["qty"], d["harga"], d["buyer"], d["transfer_to"],
                                      d["harga"], d["by"], d["notes"]))
                                conn.commit()
                                conn.close()
                                st.session_state.konfirmasi_jual = False
                                st.session_state.last_jual_data = {}
                                st.success(f"✅ Penjualan berhasil! "
                                           f"**{d['qty']} pcs {d['produk']}** terjual ke "
                                           f"**{d['buyer']}** seharga **{format_rupiah(d['harga'])}**. "
                                           f"Stok otomatis dikurangi.")
                                st.balloons()
                                st.rerun()
                        with ck2:
                            if st.button("❌  Batal", use_container_width=True, key="btn_batal_jual"):
                                st.session_state.konfirmasi_jual = False
                                st.session_state.last_jual_data = {}
                                st.rerun()

    # ────────────────────────────────────────
    #  SUB TAB B: AMBIL TITIPAN
    # ────────────────────────────────────────
    with sub_b:
        st.markdown("#### 📤 Ambil Titipan (Tanpa Pembayaran)")
        st.caption("Untuk mengambil barang titipan tanpa transaksi jual-beli.")

        if not all_kardus:
            st.warning("⚠️ Belum ada kardus & stok!")
        else:
            titipan_kardus = [k for k in all_kardus if k["type"] == "Titipan" and k["total_qty"] > 0]
            if not titipan_kardus:
                st.info("ℹ️ Tidak ada kardus titipan yang punya stok.")
            else:
                at_opts = [f"{k['owner_name']}  |  No. {k['nomor_pesanan']}-{k['nomor_id']}  |  Stok: {k['total_qty']} pcs"
                           for k in titipan_kardus]

                # ── Baris 1: Pilih Kardus (LEBAR PENUH) ──
                at_kardus_str = st.selectbox("1️⃣  Pilih Kardus Titipan", at_opts, key="at_kardus")
                at_kardus_idx = at_opts.index(at_kardus_str)
                at_kardus_info = titipan_kardus[at_kardus_idx]
                at_kardus_id = at_kardus_info["id"]

                st.info(f"📦 **{at_kardus_info['label']}**  |  📍 {at_kardus_info['location']}  |  👤 {at_kardus_info['owner_name']}")

                inv_at = get_inventory_by_kardus(at_kardus_id)
                inv_at_ada = [i for i in inv_at if i["qty"] > 0]

                if inv_at_ada:
                    # ── Baris 2: Pilih Produk (LEBAR PENUH) ──
                    at_produk_opts = [f"{i['product_name']}  —  stok: {i['qty']} pcs"
                                      for i in inv_at_ada]
                    at_produk_str = st.selectbox("2️⃣  Pilih Produk", at_produk_opts, key="at_produk")
                    at_produk_idx = at_produk_opts.index(at_produk_str)
                    at_produk_info = inv_at_ada[at_produk_idx]

                    # ── Baris 3: Jumlah (LEBAR PENUH) ──
                    at_qty = st.number_input(
                        f"3️⃣  Jumlah Diambil (maks: {at_produk_info['qty']} pcs)",
                        min_value=1, max_value=at_produk_info["qty"], value=1, key="at_qty"
                    )

                    # ── Baris 4: Dilakukan Oleh (LEBAR PENUH) ──
                    at_by_opt = users + ["Ketik nama baru..."]
                    at_by_sel = st.selectbox("4️⃣  Dilakukan Oleh", at_by_opt, key="at_by_sel")
                    if at_by_sel == "Ketik nama baru...":
                        at_by = st.text_input("✏️  Ketik nama kamu:", key="at_by_new")
                    else:
                        at_by = at_by_sel

                    at_notes = st.text_area("Catatan (opsional)", height=80, key="at_notes",
                        placeholder="Contoh: Diambil langsung oleh pemilik")

                if inv_at_ada:
                    st.markdown(f"""
                    <div style="background:#e3f2fd; border:2px solid #1565C0;
                         border-radius:10px; padding:16px 20px; margin:12px 0;">
                        <b>📋 Ringkasan Pengambilan:</b><br>
                        🏷️ Kardus: <b>{at_kardus_info['label']}</b> (Titipan)<br>
                        👤 Pemilik: <b>{at_kardus_info['owner_name']}</b><br>
                        📦 Produk: <b>{at_produk_info['product_name']}</b> x {at_qty} pcs diambil
                    </div>
                    """, unsafe_allow_html=True)

                    if not st.session_state.konfirmasi_ambil:
                        if st.button("📤  PROSES PENGAMBILAN TITIPAN", use_container_width=True,
                                     key="btn_ambil"):
                            final_by_ambil = at_by if at_by_sel != "Ketik nama baru..." else at_by
                            if not final_by_ambil.strip():
                                st.error("❌ Nama pelaksana tidak boleh kosong!")
                            else:
                                st.session_state.konfirmasi_ambil = True
                                st.session_state.last_ambil_data = {
                                    "kardus_id": at_kardus_id,
                                    "kardus_label": at_kardus_info["label"],
                                    "produk": at_produk_info["product_name"],
                                    "qty": at_qty,
                                    "by": final_by_ambil,
                                    "notes": at_notes,
                                    "inv_id": at_produk_info["id"],
                                    "owner": at_kardus_info["owner_name"],
                                }
                                st.rerun()
                    else:
                        d = st.session_state.get("last_ambil_data", {})
                        if d:
                            st.warning(f"⚠️ **Yakin ambil {d['qty']} pcs {d['produk']} "
                                       f"dari kardus {d['kardus_label']} (milik {d['owner']})?**")
                            ak1, ak2 = st.columns(2)
                            with ak1:
                                if st.button("✅  YA, AMBIL SEKARANG!", use_container_width=True,
                                             key="btn_konfirm_ambil"):
                                    now_str = tgl_indo()
                                    conn = get_conn()
                                    conn.execute(
                                        "UPDATE inventory SET qty=qty-? WHERE id=?",
                                        (d["qty"], d["inv_id"])
                                    )
                                    conn.execute("""
                                        INSERT INTO transactions
                                          (type,date,kardus_id,product_name,qty,price,buyer_name,
                                           transfer_to,transfer_amount,performed_by,notes)
                                        VALUES (?,?,?,?,?,?,?,?,?,?,?)
                                    """, ("KELUAR", now_str, d["kardus_id"], d["produk"],
                                          d["qty"], 0, "", d["owner"], 0, d["by"], d["notes"]))
                                    conn.commit()
                                    conn.close()
                                    st.session_state.konfirmasi_ambil = False
                                    st.success(f"✅ **{d['qty']} pcs {d['produk']}** berhasil diambil "
                                               f"dari kardus **{d['kardus_label']}**. Stok dikurangi.")
                                    st.rerun()
                            with ak2:
                                if st.button("❌  Batal", use_container_width=True,
                                             key="btn_batal_ambil"):
                                    st.session_state.konfirmasi_ambil = False
                                    st.rerun()


# ══════════════════════════════════════════════
#  TAB 5: LAPORAN & RIWAYAT
# ══════════════════════════════════════════════
with tab5:
    st.markdown("### 📊 Laporan & Riwayat Transaksi")
    st.caption("Lihat semua aktivitas gudang dalam satu tempat.")

    # ── Filter Periode ──
    periode = st.radio(
        "Pilih Periode Laporan:",
        ["📅 Minggu Ini", "📆 Bulan Ini", "📋 Semua Data"],
        horizontal=True,
        key="lap_periode"
    )

    conn = get_conn()
    now = datetime.now()

    if periode == "📅 Minggu Ini":
        start_date = now - timedelta(days=7)
        label_periode = "7 Hari Terakhir"
    elif periode == "📆 Bulan Ini":
        start_date = now.replace(day=1)
        label_periode = f"Bulan {now.strftime('%B %Y')}"
    else:
        start_date = datetime(2000, 1, 1)
        label_periode = "Semua Waktu"

    all_tx = conn.execute("""
        SELECT t.*, k.label as kardus_label, k.owner_name, k.type as kardus_type
        FROM transactions t
        LEFT JOIN kardus k ON t.kardus_id = k.id
        ORDER BY t.id DESC
    """).fetchall()
    all_tx = [dict(r) for r in all_tx]
    conn.close()

    # Filter berdasarkan periode
    def parse_tgl(tgl_str):
        try:
            parts = tgl_str.strip().split(" ")
            bulan_map = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"Mei":5,"Jun":6,
                         "Jul":7,"Agu":8,"Sep":9,"Okt":10,"Nov":11,"Des":12}
            d = int(parts[0]); m = bulan_map.get(parts[1], 1); y = int(parts[2])
            return datetime(y, m, d)
        except:
            return datetime(2000, 1, 1)

    filtered_tx = [t for t in all_tx if parse_tgl(t["date"]) >= start_date]

    # ── Ringkasan ──
    st.markdown(f"#### 📋 Ringkasan: {label_periode}")
    r_col1, r_col2, r_col3 = st.columns(3)

    masuk_tx = [t for t in filtered_tx if t["type"] == "MASUK"]
    keluar_tx = [t for t in filtered_tx if t["type"] == "KELUAR"]
    jual_tx = [t for t in filtered_tx if t["type"] == "PENJUALAN"]

    total_masuk = sum(t["qty"] for t in masuk_tx)
    total_keluar = sum(t["qty"] for t in keluar_tx)
    total_jual_qty = sum(t["qty"] for t in jual_tx)
    total_jual_rp = sum(t["price"] for t in jual_tx)

    titipan_masuk = sum(t["qty"] for t in masuk_tx
                        if t.get("kardus_type") == "Titipan")
    sendiri_masuk = total_masuk - titipan_masuk

    with r_col1:
        st.metric("📥 Total Masuk", f"{total_masuk} pcs",
                  help=f"Titipan: {titipan_masuk} | Milik Sendiri: {sendiri_masuk}")
        st.caption(f"Titipan: {titipan_masuk} pcs | Milik Sendiri: {sendiri_masuk} pcs")
    with r_col2:
        st.metric("📤 Total Keluar", f"{total_keluar} pcs")
    with r_col3:
        st.metric("💰 Total Penjualan", format_rupiah(total_jual_rp),
                  help=f"{total_jual_qty} item terjual")
        st.caption(f"{total_jual_qty} item terjual")

    st.markdown("---")

    # ── 5 Produk Terlaris ──
    if jual_tx:
        st.markdown("#### 🏆 5 Produk Terlaris")
        from collections import Counter
        produk_counter = Counter()
        for t in jual_tx:
            produk_counter[t["product_name"]] += t["qty"]
        top5 = produk_counter.most_common(5)
        df_top5 = pd.DataFrame(top5, columns=["Produk", "Total Terjual (pcs)"])
        df_top5.index = df_top5.index + 1
        st.dataframe(df_top5, use_container_width=True)
        st.markdown("---")

    # ── Filter Tabel Riwayat ──
    st.markdown("#### 📜 Riwayat Transaksi Lengkap")

    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        filter_tipe = st.selectbox("Filter Tipe:", ["Semua", "MASUK", "KELUAR", "PENJUALAN"],
            key="filter_tipe")
    with f_col2:
        search_tx = st.text_input("🔍 Cari produk/kardus:", placeholder="Ketik untuk cari...",
            key="search_tx")
    with f_col3:
        st.write("")

    display_tx = filtered_tx.copy()
    if filter_tipe != "Semua":
        display_tx = [t for t in display_tx if t["type"] == filter_tipe]
    if search_tx:
        q = search_tx.lower()
        display_tx = [t for t in display_tx if
            q in (t.get("product_name") or "").lower() or
            q in (t.get("kardus_label") or "").lower() or
            q in (t.get("buyer_name") or "").lower()]

    if display_tx:
        df_tx = pd.DataFrame(display_tx)
        cols_tx = ["date","type","kardus_label","product_name","qty","price",
                   "buyer_name","transfer_to","performed_by","notes"]
        cols_tx = [c for c in cols_tx if c in df_tx.columns]
        df_tx = df_tx[cols_tx].copy()
        df_tx.columns = ["Tanggal","Tipe","Kardus","Produk","Qty","Harga (Rp)",
                         "Pembeli","Transfer ke","Dilakukan Oleh","Catatan"][:len(cols_tx)]

        st.markdown(f"**Ditemukan: {len(display_tx)} transaksi**")
        st.dataframe(df_tx, use_container_width=True, hide_index=True,
            column_config={
                "Harga (Rp)": st.column_config.NumberColumn(format="Rp %,.0f"),
                "Qty": st.column_config.NumberColumn(format="%d pcs"),
            })

        # ── Export Excel ──
        st.markdown("---")
        if st.button("📥  Export ke Excel (.xlsx)", use_container_width=True,
                     key="btn_export"):
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_tx.to_excel(writer, sheet_name="Riwayat Transaksi", index=False)
                # Summary sheet
                summary_data = {
                    "Keterangan": ["Periode", "Total Masuk", "Total Keluar",
                                   "Total Terjual (qty)", "Total Penjualan (Rp)"],
                    "Nilai": [label_periode, f"{total_masuk} pcs", f"{total_keluar} pcs",
                              f"{total_jual_qty} pcs", f"Rp {int(total_jual_rp):,}"]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name="Ringkasan", index=False)
            buffer.seek(0)
            st.download_button(
                label="📥  Klik di sini untuk Download Excel",
                data=buffer,
                file_name=f"GudangKu_Laporan_{now.strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    else:
        st.info("📭 Tidak ada transaksi yang sesuai filter.")

    st.markdown("---")

    # ── EDIT PRODUK (Protected dengan checkbox) ──
    with st.expander("⚙️ EDIT PRODUK (Protected - Hati-hati!)", expanded=False):
        st.warning("⚠️ **FITUR SENSITIF** — Pastikan benar-benar mau edit sebelum submit!")
        st.caption("Edit ini akan mengubah qty dan harga produk di gudang. Perubahan tidak bisa dibatalkan!")
        
        st.markdown("##### Cari Produk yang Mau Diedit")
        
        # Ambil semua produk dari database
        conn = get_conn()
        all_inventory = conn.execute("""
            SELECT i.id, i.kardus_id, i.product_name, i.qty, i.unit_price,
                   k.label as kardus_label, k.owner_name
            FROM inventory i
            JOIN kardus k ON i.kardus_id = k.id
            ORDER BY k.owner_name, i.product_name
        """).fetchall()
        conn.close()
        all_inventory = [dict(r) for r in all_inventory]
        
        if all_inventory:
            # Search + filter produk
            edit_search = st.text_input("🔍 Cari produk atau kardus:", 
                placeholder="Contoh: HEMOHIM atau Titipan Anita", key="edit_search")
            
            if edit_search:
                filtered_inv = [i for i in all_inventory if
                    edit_search.lower() in i["product_name"].lower() or
                    edit_search.lower() in i["kardus_label"].lower() or
                    edit_search.lower() in i["owner_name"].lower()]
            else:
                filtered_inv = all_inventory
            
            if filtered_inv:
                # Pilih produk
                produk_opts = [f"{i['product_name']} | Kardus: {i['kardus_label']} | Qty: {i['qty']} pcs" 
                               for i in filtered_inv]
                selected_produk_edit_str = st.selectbox(
                    "Pilih produk untuk diedit:",
                    produk_opts,
                    key="edit_produk_select"
                )
                
                selected_edit_idx = produk_opts.index(selected_produk_edit_str)
                selected_edit = filtered_inv[selected_edit_idx]
                
                # Tampilkan info saat ini
                st.markdown(f"""
                <div style="background:#e3f2fd; border:2px solid #1565C0; border-radius:10px; padding:16px 20px;">
                    <b>📦 Produk Saat Ini:</b><br>
                    🏷️ <b>{selected_edit['product_name']}</b><br>
                    📍 Kardus: <b>{selected_edit['kardus_label']}</b><br>
                    👤 Pemilik: <b>{selected_edit['owner_name']}</b><br>
                    📊 Stok saat ini: <b>{selected_edit['qty']} pcs</b><br>
                    💰 Harga saat ini: <b>Rp {int(selected_edit['unit_price']):,}</b>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("##### Edit Data")
                
                edit_c1, edit_c2 = st.columns(2)
                with edit_c1:
                    edit_new_qty = st.number_input(
                        "Qty baru (pcs):",
                        min_value=0,
                        value=selected_edit["qty"],
                        key="edit_new_qty"
                    )
                with edit_c2:
                    edit_new_price = st.number_input(
                        "Harga satuan baru (Rp):",
                        min_value=0,
                        value=int(selected_edit["unit_price"]),
                        step=500,
                        key="edit_new_price"
                    )
                
                edit_by_opt = get_all_users() + ["Ketik nama baru..."]
                edit_by_sel = st.selectbox("Diedit Oleh:", edit_by_opt, key="edit_by_sel")
                if edit_by_sel == "Ketik nama baru...":
                    edit_by = st.text_input("Nama Anda:", key="edit_by_new")
                else:
                    edit_by = edit_by_sel
                
                edit_notes = st.text_area("Alasan edit:", height=60, key="edit_notes",
                    placeholder="Contoh: Koreksi input sebelumnya, stok fisik tidak sesuai, dll")
                
                st.markdown("##### ✅ KONFIRMASI (Baca Sebelum Submit!)")
                
                # 2 checkbox konfirmasi (protective)
                conf1 = st.checkbox(
                    f"✅ Saya sudah yakin perubahan dari **Qty {selected_edit['qty']} → {edit_new_qty}** dan **Harga Rp {int(selected_edit['unit_price']):,} → Rp {int(edit_new_price):,}**",
                    key="edit_conf1"
                )
                conf2 = st.checkbox(
                    "✅ Saya mengerti perubahan tidak bisa dibatalkan dan audit log akan tercatat",
                    key="edit_conf2"
                )
                conf3 = st.checkbox(
                    "✅ Saya sudah input ALASAN edit di atas",
                    key="edit_conf3"
                )
                
                if st.button("🔴 SUBMIT EDIT SEKARANG", use_container_width=True, 
                             key="btn_edit_submit", type="secondary",
                             disabled=not (conf1 and conf2 and conf3)):
                    
                    if not edit_by.strip():
                        st.error("❌ Nama pelaksana tidak boleh kosong!")
                    elif not edit_notes.strip():
                        st.error("❌ Alasan edit harus diisi!")
                    else:
                        success, message = edit_inventory_item(
                            selected_edit["id"],
                            edit_new_qty,
                            edit_new_price,
                            edit_by.strip()
                        )
                        
                        if success:
                            st.success(message)
                            st.info(f"📝 Audit: {edit_notes}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(message)
            else:
                st.info("❌ Tidak ada produk yang sesuai pencarian.")
        else:
            st.warning("📭 Belum ada produk di gudang.")


# ══════════════════════════════════════════════
#  TAB 7: CARI BARANG
# ══════════════════════════════════════════════
with tab7:
    st.markdown("### 🔍 Cari Barang di Gudang")
    st.caption("Cari produk untuk lihat kardus mana saja yang memilikinya, dan langsung kurangi stok jika diambil.")

    users = get_all_users()

    st.markdown("#### 🔎 Cari Produk")
    
    # Search input dengan autocomplete
    search_input = st.text_input(
        "Ketik nama produk (contoh: h → akan muncul hemohim, hongsamdan, dll)",
        placeholder="Contoh: HEMOHIM, Atomy HemoHim, atau huruf h..."
    )
    
    # Filter produk berdasarkan input
    if search_input:
        filtered_products = get_filtered_products(search_input)
        
        if filtered_products:
            selected_produk = st.selectbox(
                "📦 Pilih produk dari list:",
                filtered_products,
                key="search_produk_select"
            )
            
            # Cari produk di semua kardus
            search_results = search_produk_di_kardus(selected_produk)
            
            if search_results:
                st.markdown(f"#### 📍 **{selected_produk}** ditemukan di {len(search_results)} lokasi:")
                
                # Tampilkan tabel hasil pencarian
                df_search = pd.DataFrame(search_results)
                df_display = df_search[[
                    "kardus_label", "owner_name", "location", "kardus_type", "qty", "unit_price"
                ]].copy()
                df_display.columns = ["Kardus Label", "Pemilik", "📍 Lokasi", "Tipe", "Stok (pcs)", "Harga Satuan (Rp)"]
                
                st.dataframe(df_display, use_container_width=True, hide_index=True,
                    column_config={
                        "Stok (pcs)": st.column_config.NumberColumn(format="%d pcs"),
                        "Harga Satuan (Rp)": st.column_config.NumberColumn(format="Rp %,.0f"),
                    })
                
                st.markdown("---")
                
                # ── Ambil Barang ──
                st.markdown("#### 📤 Ambil Barang dari Salah Satu Kardus")
                
                kardus_choices = [f"{r['kardus_label']} ({r['qty']} pcs)" for r in search_results]
                selected_kardus_str = st.selectbox(
                    "Pilih kardus mana yang mau diambil:",
                    kardus_choices,
                    key="search_ambil_kardus"
                )
                
                selected_idx = kardus_choices.index(selected_kardus_str)
                selected_result = search_results[selected_idx]
                max_qty = selected_result["qty"]
                
                ambil_col1, ambil_col2 = st.columns(2)
                with ambil_col1:
                    ambil_qty = st.number_input(
                        f"Jumlah yang diambil (maks: {max_qty} pcs):",
                        min_value=1,
                        max_value=max_qty,
                        value=1,
                        key="search_ambil_qty"
                    )
                
                with ambil_col2:
                    ambil_by_opt = users + ["Ketik nama baru..."]
                    ambil_by_sel = st.selectbox("Dilakukan Oleh:", ambil_by_opt, key="search_ambil_by")
                    if ambil_by_sel == "Ketik nama baru...":
                        ambil_by = st.text_input("Nama Anda:", key="search_ambil_by_new")
                    else:
                        ambil_by = ambil_by_sel
                
                ambil_notes = st.text_area("Catatan (opsional):", height=60, key="search_ambil_notes",
                    placeholder="Contoh: Diambil untuk display, dijual ke pelanggan, dll")
                
                # Konfirmasi checkbox
                confirm_ambil = st.checkbox(
                    f"✅ Saya yakin ambil {ambil_qty} pcs {selected_produk} dari kardus {selected_result['kardus_label']}",
                    key="search_confirm_ambil"
                )
                
                if st.button("📤 PROSES PENGAMBILAN", use_container_width=True, key="btn_search_ambil",
                             disabled=not confirm_ambil):
                    if not ambil_by.strip():
                        st.error("❌ Nama pelaksana tidak boleh kosong!")
                    else:
                        success, message = kurangi_stok_produk(
                            selected_result["kardus_id"],
                            selected_produk,
                            ambil_qty,
                            ambil_by.strip(),
                            ambil_notes
                        )
                        
                        if success:
                            st.success(message)
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(message)
            else:
                st.info(f"📭 Produk {selected_produk} tidak ada di gudang.")
        else:
            st.warning(f"❌ Tidak ada produk yang mengandung '{search_input}'. Coba cari yang lain!")
    else:
        st.info("💡 **Caranya:** Ketik nama produk di atas untuk mulai mencari (bisa sebagian huruf saja)")


# ══════════════════════════════════════════════
#  TAB 6: PENGATURAN
# ══════════════════════════════════════════════
with tab6:
    st.markdown("### ⚙️ Pengaturan & Info Aplikasi")

    pg_col1, pg_col2 = st.columns(2)

    with pg_col1:
        # ── Daftar User ──
        st.markdown("#### 👥 Pengguna yang Pernah Input")
        all_users = get_all_users()
        st.info(f"Ditemukan **{len(all_users)} pengguna**:")
        for u in all_users:
            st.markdown(f"- 👤 {u}")

        st.markdown("---")

        # ── Backup Database ──
        st.markdown("#### 💾 Backup Data")
        st.caption("Download file database untuk backup rutin.")
        if st.button("📥  Download Backup Database (.db)", use_container_width=True,
                     key="btn_backup"):
            if os.path.exists(DB_PATH):
                with open(DB_PATH, "rb") as f:
                    db_bytes = f.read()
                st.download_button(
                    label=f"📥  Download gudangku_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db",
                    data=db_bytes,
                    file_name=f"gudangku_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db",
                    mime="application/octet-stream",
                    use_container_width=True
                )
            else:
                st.error("File database tidak ditemukan!")

        st.markdown("---")

        # ── Import Database ──
        st.markdown("#### 📤 Restore Data dari Backup")
        st.caption("Kalau aplikasi di-reset karena idle, gunakan file backup untuk restore data.")
        
        uploaded_backup = st.file_uploader(
            "Pilih file backup (.db) untuk di-import",
            type=["db"],
            key="import_backup"
        )
        
        if uploaded_backup is not None:
            st.warning("⚠️ Perhatian! Ini akan mengganti semua data sekarang dengan data dari backup.")
            col_imp1, col_imp2 = st.columns(2)
            with col_imp1:
                if st.button("✅  Ya, IMPORT SEKARANG", use_container_width=True, key="btn_import_yes"):
                    file_bytes = uploaded_backup.read()
                    success, message = import_database(file_bytes)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            with col_imp2:
                st.info("❌ Batal")

        st.markdown("---")

        # ── Import dari Excel ──
        st.markdown("#### 📊 Import Data dari Excel")
        st.caption("Jika sudah punya data di Excel, bisa langsung import ke sini!")
        
        # Download template
        if st.button("📋  Download Template Excel Kosong", use_container_width=True,
                     key="btn_template_excel"):
            try:
                # Generate template
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    # Sheet 1: Kardus
                    df_kardus = pd.DataFrame({
                        "nomor_pesanan": ["4521", "4522", ""],
                        "nomor_id": ["7789", "7790", ""],
                        "owner_name": ["Titipan Anita", "Milik Saya - Budi", ""],
                        "location": ["Rak A1", "Rak B2", ""],
                        "type": ["Titipan", "Milik Sendiri", ""]
                    })
                    df_kardus.to_excel(writer, sheet_name="Kardus", index=False)
                    
                    # Sheet 2: Inventory
                    df_inventory = pd.DataFrame({
                        "kardus_id": ["1", "1", "2", ""],
                        "product_name": ["Sabun Mandi", "Shampo", "Minyak Goreng", ""],
                        "qty": ["10", "5", "8", ""],
                        "unit_price": ["8000", "15000", "28000", ""]
                    })
                    df_inventory.to_excel(writer, sheet_name="Inventory", index=False)
                    
                    # Sheet 3: Transactions
                    df_transactions = pd.DataFrame({
                        "type": ["MASUK", "MASUK", "PENJUALAN", ""],
                        "date": ["25 Apr 2026 10:00", "25 Apr 2026 11:00", "25 Apr 2026 14:30", ""],
                        "kardus_id": ["1", "2", "2", ""],
                        "product_name": ["Sabun Mandi", "Minyak Goreng", "Minyak Goreng", ""],
                        "qty": ["10", "8", "2", ""],
                        "price": ["0", "0", "56000", ""],
                        "buyer_name": ["", "", "Pak Ali", ""],
                        "performed_by": ["Admin", "Admin", "Admin", ""]
                    })
                    df_transactions.to_excel(writer, sheet_name="Transactions", index=False)
                
                output.seek(0)
                st.download_button(
                    label="📥  Download Template.xlsx",
                    data=output.getvalue(),
                    file_name=f"GudangKu_Template_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Error generate template: {str(e)}")
        
        st.caption("💡 **Caranya:**\n1. Download template di atas\n2. Isi dengan data kamu\n3. Upload file Excel di bawah")
        
        # Upload Excel
        uploaded_excel = st.file_uploader(
            "Upload file Excel (.xlsx) dengan data kamu",
            type=["xlsx"],
            key="upload_excel"
        )
        
        if uploaded_excel is not None:
            st.info("📝 Pilih sheet mana yang mau diimport:")
            sheet_choice = st.radio(
                "Sheet yang diimport:",
                ["Kardus", "Inventory", "Transactions"],
                horizontal=True,
                key="sheet_choice"
            )
            
            st.warning("⚠️ Data yang diimport akan **ditambahkan** ke aplikasi, bukan mengganti.")
            
            if st.button(f"✅  IMPORT DATA DARI SHEET '{sheet_choice}'", use_container_width=True,
                         key="btn_import_excel"):
                excel_bytes = uploaded_excel.read()
                success, message = import_excel_data(excel_bytes, sheet_choice)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    with pg_col2:
        # ── Info Versi ──
        st.markdown("#### ℹ️ Info Aplikasi")
        st.markdown("""
        <div style="background:#f1f8e9; border-radius:10px; padding:16px 20px;">
            <b>📦 GudangKu</b><br>
            Versi: <b>1.0 (April 2026)</b><br>
            Tech: <b>Python + Streamlit + SQLite</b><br>
            Biaya Deploy: <b>Rp 0 (GRATIS!)</b>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ── Reset Data ──
        st.markdown("#### 🗑️ Reset Semua Data")
        st.error("⚠️ BERBAHAYA! Ini akan menghapus SEMUA data dan tidak bisa dibatalkan!")
        reset_confirm1 = st.checkbox("Saya mengerti data akan terhapus permanen", key="rst1")
        reset_confirm2 = st.checkbox("Saya sudah backup data sebelumnya", key="rst2")
        reset_text = st.text_input('Ketik "HAPUS SEMUA" untuk konfirmasi:', key="rst_text")

        if st.button("🗑️  RESET SEMUA DATA", use_container_width=True, key="btn_reset",
                     disabled=not (reset_confirm1 and reset_confirm2)):
            if reset_text != "HAPUS SEMUA":
                st.error("❌ Teks konfirmasi salah! Ketik persis: HAPUS SEMUA")
            else:
                conn = get_conn()
                conn.execute("DELETE FROM transactions")
                conn.execute("DELETE FROM inventory")
                conn.execute("DELETE FROM kardus")
                conn.execute("DELETE FROM audit_log")
                try:
                    conn.execute("DELETE FROM sqlite_sequence")
                except:
                    pass
                conn.commit()
                conn.close()
                st.success("✅ Semua data berhasil dihapus! Aplikasi sekarang kosong dan siap dipakai.")
                st.rerun()

    st.markdown("---")

    # ── Panduan Deploy ──
    st.markdown("### 🚀 Cara Deploy Gratis di Streamlit Cloud (5 Menit!)")
    with st.expander("📖 Klik untuk buka panduan lengkap"):
        st.markdown("""
## 🚀 Panduan Deploy GudangKu ke Internet (GRATIS!)

---

### Langkah 1: Buat Akun GitHub (1 menit)
1. Buka **github.com** di browser
2. Klik **Sign Up** dan daftar gratis
3. Verifikasi email

### Langkah 2: Upload File ke GitHub (2 menit)
1. Di GitHub, klik **New Repository** (tombol hijau)
2. Nama repo: `gudangku` → klik **Create Repository**
3. Klik **Add file** → **Upload files**
4. Upload file **app.py** dan **requirements.txt** ini
5. Klik **Commit changes**

### Langkah 3: Deploy di Streamlit Cloud (2 menit)
1. Buka **share.streamlit.io**
2. Login dengan akun GitHub kamu
3. Klik **New app**
4. Pilih repository `gudangku`
5. Main file: `app.py`
6. Klik **Deploy!**

### Langkah 4: Share Link ke Semua Orang! 🎉
- Kamu akan dapat link seperti: `https://namaKamu-gudangku.streamlit.app`
- Share link itu ke semua rekan yang butuh akses!

---

### 💾 Cara Backup Rutin
1. Buka tab **⚙️ Pengaturan** di atas
2. Klik tombol **Download Backup Database**
3. Simpan file **.db** di HP/Laptop kamu
4. Lakukan tiap minggu untuk keamanan data

---

### 📞 Butuh Bantuan?
- Email: support@gudangku.app
- Dokumentasi Streamlit: docs.streamlit.io
        """)


# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#888; font-size:15px; padding:12px;">
    📦 <b>GudangKu v1.0</b> — Kelola Kardus & Penjualan dengan Mudah |
    Dibuat dengan ❤️ menggunakan Streamlit + SQLite |
    Deploy GRATIS di Streamlit Cloud
</div>
""", unsafe_allow_html=True)
