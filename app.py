"""
╔══════════════════════════════════════════════════╗
║          GudangKu v2.0 - Atomy Edition           ║
║     Database: Google Sheets (Permanent!)         ║
║     Fitur Baru: Searchable Product, Bulk Input,  ║
║                 Auto-merge, Excel Import         ║
╚══════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os
import io
import json
import time
import re

# Google Sheets
import gspread
from google.oauth2.service_account import Credentials

# ─────────────────────────────────────────────
#  KONFIGURASI HALAMAN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="📦 GudangKu Atomy",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
#  CSS CUSTOM — UI BESAR, SIMPEL, RAMAH
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
    font-size: 18px !important;
}

h1 { font-size: 34px !important; color: #2E7D32 !important; font-weight: 800 !important; }
h2 { font-size: 26px !important; color: #1B5E20 !important; font-weight: 700 !important; }
h3 { font-size: 22px !important; font-weight: 700 !important; }

.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #f1f8e9;
    padding: 8px;
    border-radius: 12px;
    flex-wrap: wrap;
}
.stTabs [data-baseweb="tab"] {
    font-size: 16px !important;
    font-weight: 700 !important;
    padding: 10px 18px !important;
    border-radius: 8px !important;
    min-height: 48px !important;
}
.stTabs [aria-selected="true"] {
    background-color: #2E7D32 !important;
    color: white !important;
}

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

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea textarea {
    font-size: 18px !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    color: #111111 !important;
}

[data-baseweb="select"] span,
[data-baseweb="select"] div,
[data-baseweb="select"] input {
    color: #111111 !important;
    font-size: 17px !important;
    font-family: 'Nunito', sans-serif !important;
}
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

.stTextInput label, .stNumberInput label, .stSelectbox label,
.stTextArea label, .stRadio label, .stDateInput label {
    font-size: 17px !important;
    font-weight: 700 !important;
    color: #1B5E20 !important;
}

.stRadio > div { gap: 16px !important; }

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

.stSuccess, .stError, .stWarning, .stInfo {
    font-size: 17px !important;
    padding: 14px 18px !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

hr { border-color: #e8f5e9 !important; margin: 20px 0 !important; }
</style>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════
#  LIST PRODUK ATOMY (102 Master List)
# ═════════════════════════════════════════════════
ATOMY_PRODUCTS = [
    "Atomy Absolute Ampoule", "Atomy Absolute CellActive Skincare Set",
    "Atomy Absolute Eye-complex", "Atomy Absolute Lotion",
    "Atomy Absolute Nutrition Cream", "Atomy Absolute Serum",
    "Atomy Absolute Toner", "Atomy AC Special Set",
    "Atomy Adelica Lip Gloss", "Atomy Adelica Loose Powder",
    "Atomy Adelica Master Fit Cushion", "Atomy Aidam Cleanser",
    "Atomy Alaska E-Omega 3", "Atomy Apple Phenon",
    "Atomy Baby Body Wash & Shampoo", "Atomy Baby Care Set",
    "Atomy Baby Lotion", "Atomy BB Cream",
    "Atomy Body Cleanser", "Atomy Body Lotion",
    "Atomy Cafe Arabica", "Atomy Cafe Arabica Black",
    "Atomy Color Food Vitamin C", "Atomy Daily Expert Mask",
    "Atomy Deep Cleanser 150ml", "Atomy Dish Detergent",
    "Atomy Evening Care 4 Set", "Atomy Eye Lutein",
    "Atomy Fabric Detergent Powder", "Atomy Fabric Softener",
    "Atomy Foam Cleanser 150ml", "Atomy Gift Set Atomy",
    "Atomy Grilled Laver", "Atomy Hampers Lebaran Eksklusif",
    "Atomy Hampers Lebaran Gold", "Atomy Hampers Lebaran Silver",
    "Atomy Hand Soap", "Atomy HemoHim",
    "Atomy HemoHim Set 4", "Atomy Herbal Hair Conditioner",
    "Atomy Herbal Hair Shampoo", "Atomy Herbal Hair Tonic",
    "Atomy Hongsamdan Red Ginseng", "Atomy Hydra Brightening Care Set",
    "Atomy Hydra Brightening Cream", "Atomy Hydra Brightening Essence",
    "Atomy Kids Chewable Omega-3", "Atomy Kitchen Cloth",
    "Atomy Lip Glow", "Atomy Lip Treatment",
    "Atomy Liquid Fabric Detergent", "Atomy Marine Ampoule Gel Mask",
    "Atomy Men Skincare Set", "Atomy Mild Bubble Cleanser",
    "Atomy Milk Thistle Rhodiola", "Atomy Olive Oil Grilled Laver",
    "Atomy Oral Care System", "Atomy Organic Green Tea",
    "Atomy Paket Berkah Ramadan A", "Atomy Paket Berkah Ramadan B",
    "Atomy Paket Berkah Ramadan C", "Atomy Paket Bingkisan Lebaran",
    "Atomy Paket Glow Up Lebaran", "Atomy Paket Hampers Hari Raya",
    "Atomy Paket Hemat Keluarga", "Atomy Paket Idul Fitri Sehat",
    "Atomy Paket Kecantikan Lebaran", "Atomy Paket Lebaran A (Health Care)",
    "Atomy Paket Lebaran B (Skincare)", "Atomy Paket Lebaran C (Personal Care)",
    "Atomy Paket Ramadhan Care", "Atomy Paket Sehat Ramadhan",
    "Atomy Paket Suplemen Lebaran", "Atomy Parcel Hari Raya Idul Fitri",
    "Atomy Parcel Lebaran Atomy", "Atomy Peel Off Mask",
    "Atomy Peeling Gel", "Atomy Pomegranate Beauty",
    "Atomy Potato Ramen", "Atomy Probiotics 10+",
    "Atomy Pure Spirulina", "Atomy Pu'er Tea",
    "Atomy Scalpcare Conditioner", "Atomy Scalpcare Hair Care Set",
    "Atomy Scalpcare Shampoo", "Atomy Slim Body Shake 2.0",
    "Atomy Stainless Steel Scrubber", "Atomy Sun Stick",
    "Atomy Sunscreen Beige", "Atomy Sunscreen White",
    "Atomy The Fame Essence", "Atomy The Fame Eye Cream",
    "Atomy The Fame Lotion", "Atomy The Fame Nutrition Cream",
    "Atomy The Fame Set", "Atomy The Fame Toner",
    "Atomy Toothbrush", "Atomy Toothbrush Compact",
    "Atomy Toothpaste 200g", "Atomy Toothpaste 50g",
    "Atomy Travel Kit", "Atomy Vitamin B-Complex",
]

# ═════════════════════════════════════════════════
#  AUTO-MAPPING: nama lama → nama Atomy resmi
#  (Berdasarkan analisis data backup user)
# ═════════════════════════════════════════════════
PRODUCT_MERGE_MAP = {
    # HemoHim variants (paling banyak)
    "HEMOHIM": "Atomy HemoHim",
    "Hemohim": "Atomy HemoHim",
    "hemohim": "Atomy HemoHim",
    "HEMOHIM 1": "Atomy HemoHim",
    "HEMOHIM 1 SET": "Atomy HemoHim Set 4",
    
    # Body Lotion variants
    "BODY LOTION": "Atomy Body Lotion",
    "BODY CARE BODY LOTION": "Atomy Body Lotion",
    "BODYCARE BODY LOTION": "Atomy Body Lotion",
    "EVENING CARE BODY LOTION": "Atomy Body Lotion",
    "body care body lotion": "Atomy Body Lotion",
    
    # Body Cleanser
    "BODY CLEANSER": "Atomy Body Cleanser",
    "HERBAL BODY CLEANSER": "Atomy Body Cleanser",
    "herbal body cleanser": "Atomy Body Cleanser",
    
    # Aidam
    "BODY CARE AIDAM CLEANSER": "Atomy Aidam Cleanser",
    
    # Foam Cleanser
    "FOAM CLEANSER": "Atomy Foam Cleanser 150ml",
    "EVENING CARE FOAM CLEANSER": "Atomy Foam Cleanser 150ml",
    "evening care foam cleanser": "Atomy Foam Cleanser 150ml",
    
    # Deep Cleanser
    "DEEP CLEANSER": "Atomy Deep Cleanser 150ml",
    "evening care deep cleanser": "Atomy Deep Cleanser 150ml",
    
    # Evening Care Set
    "EVENING CARE SET": "Atomy Evening Care 4 Set",
    "EVENING CARE 4 SET": "Atomy Evening Care 4 Set",
    "EVENING 4 CARE SET": "Atomy Evening Care 4 Set",
    "EVENIN G CARE SET": "Atomy Evening Care 4 Set",
    "evening care 4 set": "Atomy Evening Care 4 Set",
    
    # Absolute / Cellactive
    "ABSOLOUTE CELLACTIVE AMPOULE": "Atomy Absolute Ampoule",
    "ABSOLUTE CEELACTIVE AMPOULE": "Atomy Absolute Ampoule",
    "CELLACTIVE AMPOULE": "Atomy Absolute Ampoule",
    "absolute cellactive ampoule": "Atomy Absolute Ampoule",
    "ABSOLOUTE CELL ACTIVE SKIN": "Atomy Absolute CellActive Skincare Set",
    "ABSOULOUTE CELLACTIVE SKIN": "Atomy Absolute CellActive Skincare Set",
    "ATOMY ABSOLOUTE CELLACTIVE SKIN": "Atomy Absolute CellActive Skincare Set",
    "absolute cell active": "Atomy Absolute CellActive Skincare Set",
    "absolute snow set": "Atomy Absolute CellActive Skincare Set",
    "A- SOLUTE SELECTIVE EYE COMPLEX": "Atomy Absolute Eye-complex",
    "ABSOLUTE SELECTIVE LOTION": "Atomy Absolute Lotion",
    "ABSOLUTE SELECTIVELOTION": "Atomy Absolute Lotion",
    "a solute cellactive lotion": "Atomy Absolute Lotion",
    "a solute selective toner": "Atomy Absolute Toner",
    "ABSOLUTE ESSENCE SUNSCREEN": "Atomy Sunscreen White",
    "absolute essence sunscreen": "Atomy Sunscreen White",
    
    # Hair products
    "HAIR CONDITIONER": "Atomy Herbal Hair Conditioner",
    "HERBAL HAIR CONDITIONER": "Atomy Herbal Hair Conditioner",
    "herbal hair conditioner": "Atomy Herbal Hair Conditioner",
    "HAIR SHAMPOO": "Atomy Herbal Hair Shampoo",
    "HERBAL HAIR SHAMPOO": "Atomy Herbal Hair Shampoo",
    "HERBAL SHAMPOO": "Atomy Herbal Hair Shampoo",
    "ATOMY HERBAL HAIR SHAMPOO": "Atomy Herbal Hair Shampoo",
    "herbal hair sampoo": "Atomy Herbal Hair Shampoo",
    "HAIR TONIC": "Atomy Herbal Hair Tonic",
    "SAENGMODAN HAIR TONIC": "Atomy Herbal Hair Tonic",
    "saengmodan hair tonic": "Atomy Herbal Hair Tonic",
    "HAIR ESSENTIAL OIL": "Atomy Herbal Hair Tonic",
    "HAIR ESSENTIALS OIL": "Atomy Herbal Hair Tonic",
    "ATOMY HAIR ESSENTIAL OIL": "Atomy Herbal Hair Tonic",
    "hair essential oil": "Atomy Herbal Hair Tonic",
    
    # Vitamin C
    "VIT C": "Atomy Color Food Vitamin C",
    "VIT C 2": "Atomy Color Food Vitamin C",
    "VITAMIN C": "Atomy Color Food Vitamin C",
    
    # Vitamin B
    "VITAMIN B COMPLEX": "Atomy Vitamin B-Complex",
    
    # Hongsamdan
    "HONGSAMDAN": "Atomy Hongsamdan Red Ginseng",
    
    # Spirulina
    "SPIRULINA": "Atomy Pure Spirulina",
    
    # Sunscreen
    "SUN SCREEN BEIGE": "Atomy Sunscreen Beige",
    "SUNSCREEN BEIGE": "Atomy Sunscreen Beige",
    "sunscreen beige": "Atomy Sunscreen Beige",
    "SUNSCREEN WHITE": "Atomy Sunscreen White",
    "sunscreen white": "Atomy Sunscreen White",
    
    # Toothpaste / Toothbrush
    "ODOL BESAR": "Atomy Toothpaste 200g",
    "odol besar": "Atomy Toothpaste 200g",
    "ODOL KECIL": "Atomy Toothpaste 50g",
    "ODOL KECIL 50GR": "Atomy Toothpaste 50g",
    "Odol kecil": "Atomy Toothpaste 50g",
    "odol kecil": "Atomy Toothpaste 50g",
    "SIKAT GIGI": "Atomy Toothbrush",
    "sikat gigi": "Atomy Toothbrush",
    
    # Coffee
    "ARABICA 200STICK": "Atomy Cafe Arabica",
    "KOPI ARABICA 50 STICKS": "Atomy Cafe Arabica",
    "KOPI KECIL": "Atomy Cafe Arabica",
    "arabica cafe 200 stik": "Atomy Cafe Arabica",
    
    # Hydra
    "HYDRA BRIGHTENING CARE SET": "Atomy Hydra Brightening Care Set",
    
    # Healthy Glow
    "HEALTHY GLOW BASE": "Atomy BB Cream",
    "healthy glow base": "Atomy BB Cream",
    
    # Acne / Scrubber
    "ACNE CLEAR EXPERT SYSTEM": "Atomy Stainless Steel Scrubber",
    "acne scratch free scruber": "Atomy Stainless Steel Scrubber",
    
    # Baby
    "CARABEBE LOTION": "Atomy Baby Lotion",
    
    # Misc to product (best guess)
    "FINEZYME": "Atomy Probiotics 10+",  # probiotic enzyme
    "PSYLIUM HUSK": "Atomy Slim Body Shake 2.0",
    "KOYO": "Atomy Travel Kit",  # placeholder
    "koyo": "Atomy Travel Kit",
    
    # Paket Ramadhan
    "PAKET RAMADHAN": "Atomy Paket Ramadhan Care",
    "PAKET RAMADHAN 1": "Atomy Paket Berkah Ramadan A",
    "PAKET RAMDHAN 1": "Atomy Paket Berkah Ramadan A",
    "RAMADHAN 1": "Atomy Paket Berkah Ramadan A",
    "RAMADHAN 2": "Atomy Paket Berkah Ramadan B",
    "RAMDHAN 1": "Atomy Paket Berkah Ramadan A",
    "Ramadhan 1": "Atomy Paket Berkah Ramadan A",
    "ramadhan 1": "Atomy Paket Berkah Ramadan A",
    
    # Lebaran
    "LEBARAN 1": "Atomy Paket Bingkisan Lebaran",
}

def normalize_product_name(name):
    """Normalisasi nama produk: lookup di merge map, kalau tidak ada return as-is"""
    if not name:
        return name
    name_clean = name.strip()
    if name_clean in PRODUCT_MERGE_MAP:
        return PRODUCT_MERGE_MAP[name_clean]
    # Cek case-insensitive
    for key, val in PRODUCT_MERGE_MAP.items():
        if key.lower() == name_clean.lower():
            return val
    return name_clean

# ═════════════════════════════════════════════════
#  GOOGLE SHEETS BACKEND
# ═════════════════════════════════════════════════
SHEET_NAMES = {
    "kardus": "kardus",
    "inventory": "inventory",
    "transactions": "transactions",
    "audit_log": "audit_log",
}

KARDUS_HEADERS = ["id", "label", "nomor_pesanan", "nomor_id", "owner_name",
                  "location", "type", "created_at", "created_by",
                  "updated_at", "updated_by"]
INVENTORY_HEADERS = ["id", "kardus_id", "product_name", "qty", "unit_price",
                     "added_at", "added_by"]
TRANSACTIONS_HEADERS = ["id", "type", "date", "kardus_id", "product_name",
                        "qty", "price", "buyer_name", "transfer_to",
                        "transfer_amount", "performed_by", "notes"]
AUDIT_HEADERS = ["id", "table_name", "record_id", "action", "old_value",
                 "new_value", "performed_by", "timestamp"]

@st.cache_resource
def get_gspread_client():
    """Get authenticated gspread client menggunakan secrets dari Streamlit"""
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        # Coba dari Streamlit secrets dulu
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        else:
            # Fallback: file lokal credentials.json
            creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"❌ Gagal koneksi Google Sheets: {e}")
        st.info("💡 Pastikan kamu sudah setup Service Account dan upload credentials ke Streamlit Secrets.")
        st.stop()

@st.cache_resource
def get_spreadsheet():
    """Get the spreadsheet by URL or name from secrets"""
    try:
        client = get_gspread_client()
        if "spreadsheet_url" in st.secrets:
            url = st.secrets["spreadsheet_url"]
            sh = client.open_by_url(url)
        elif "spreadsheet_name" in st.secrets:
            sh = client.open(st.secrets["spreadsheet_name"])
        else:
            sh = client.open("GudangKu Database")
        return sh
    except gspread.SpreadsheetNotFound:
        st.error("❌ Spreadsheet 'GudangKu Database' tidak ditemukan!")
        st.info("💡 Buat spreadsheet baru dengan nama 'GudangKu Database' dan share ke service account email.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.stop()

def get_worksheet(name):
    """Get atau buat worksheet dengan headers yang sesuai"""
    sh = get_spreadsheet()
    headers_map = {
        "kardus": KARDUS_HEADERS,
        "inventory": INVENTORY_HEADERS,
        "transactions": TRANSACTIONS_HEADERS,
        "audit_log": AUDIT_HEADERS,
    }
    try:
        ws = sh.worksheet(name)
        # Pastikan header ada
        existing_headers = ws.row_values(1)
        expected = headers_map.get(name, [])
        if not existing_headers or existing_headers[:len(expected)] != expected:
            ws.clear()
            ws.append_row(expected)
        return ws
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=name, rows=1000, cols=20)
        ws.append_row(headers_map.get(name, []))
        return ws

def init_sheets():
    """Pastikan semua worksheet ada"""
    for name in ["kardus", "inventory", "transactions", "audit_log"]:
        get_worksheet(name)

# ═════════════════════════════════════════════════
#  CRUD FUNCTIONS via Google Sheets
# ═════════════════════════════════════════════════

@st.cache_data(ttl=10)
def load_table(table_name):
    """Load semua data dari worksheet sebagai list of dicts"""
    ws = get_worksheet(table_name)
    records = ws.get_all_records()
    return records

def clear_cache():
    """Clear cache supaya next load fetch fresh data"""
    load_table.clear()

def get_next_id(table_name):
    """Generate next ID berdasarkan max existing ID"""
    rows = load_table(table_name)
    if not rows:
        return 1
    ids = [int(r.get("id", 0) or 0) for r in rows if r.get("id")]
    return max(ids) + 1 if ids else 1

def insert_row(table_name, data):
    """Insert satu baris ke worksheet"""
    ws = get_worksheet(table_name)
    headers_map = {
        "kardus": KARDUS_HEADERS,
        "inventory": INVENTORY_HEADERS,
        "transactions": TRANSACTIONS_HEADERS,
        "audit_log": AUDIT_HEADERS,
    }
    headers = headers_map[table_name]
    if "id" not in data or not data.get("id"):
        data["id"] = get_next_id(table_name)
    row = [str(data.get(h, "")) for h in headers]
    ws.append_row(row)
    clear_cache()
    return data["id"]

def insert_rows_batch(table_name, data_list):
    """Insert banyak baris sekaligus (BATCH - jauh lebih cepat)"""
    if not data_list:
        return []
    ws = get_worksheet(table_name)
    headers_map = {
        "kardus": KARDUS_HEADERS,
        "inventory": INVENTORY_HEADERS,
        "transactions": TRANSACTIONS_HEADERS,
        "audit_log": AUDIT_HEADERS,
    }
    headers = headers_map[table_name]
    next_id = get_next_id(table_name)
    rows_to_insert = []
    inserted_ids = []
    for d in data_list:
        if "id" not in d or not d.get("id"):
            d["id"] = next_id
            next_id += 1
        row = [str(d.get(h, "")) for h in headers]
        rows_to_insert.append(row)
        inserted_ids.append(d["id"])
    ws.append_rows(rows_to_insert)
    clear_cache()
    return inserted_ids

def update_row(table_name, row_id, updates):
    """Update baris berdasarkan id"""
    ws = get_worksheet(table_name)
    all_data = ws.get_all_records()
    headers_map = {
        "kardus": KARDUS_HEADERS,
        "inventory": INVENTORY_HEADERS,
        "transactions": TRANSACTIONS_HEADERS,
        "audit_log": AUDIT_HEADERS,
    }
    headers = headers_map[table_name]
    for idx, row in enumerate(all_data):
        if str(row.get("id")) == str(row_id):
            row_num = idx + 2  # +2 karena header di row 1, dan idx 0-based
            new_row = dict(row)
            new_row.update(updates)
            updated_values = [str(new_row.get(h, "")) for h in headers]
            ws.update(f"A{row_num}:{chr(65+len(headers)-1)}{row_num}", [updated_values])
            clear_cache()
            return True
    return False

def delete_row(table_name, row_id):
    """Hapus baris berdasarkan id"""
    ws = get_worksheet(table_name)
    all_data = ws.get_all_records()
    for idx, row in enumerate(all_data):
        if str(row.get("id")) == str(row_id):
            row_num = idx + 2
            ws.delete_rows(row_num)
            clear_cache()
            return True
    return False

def query_filter(table_name, **filters):
    """Filter rows berdasarkan kriteria"""
    rows = load_table(table_name)
    result = []
    for row in rows:
        match = True
        for k, v in filters.items():
            if str(row.get(k, "")) != str(v):
                match = False
                break
        if match:
            result.append(row)
    return result

# ═════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═════════════════════════════════════════════════
def tgl_indo(dt=None):
    if dt is None:
        dt = datetime.now()
    bulan = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
             "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
    return f"{dt.day:02d} {bulan[dt.month]} {dt.year} {dt.hour:02d}:{dt.minute:02d}"

def tgl_indo_short(dt=None):
    if dt is None:
        dt = datetime.now()
    bulan = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
             "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
    return f"{dt.day:02d} {bulan[dt.month]} {dt.year}"

def format_rupiah(angka):
    try:
        return f"Rp {int(float(angka)):,}".replace(",", ".")
    except:
        return "Rp 0"

def parse_tgl(tgl_str):
    try:
        parts = str(tgl_str).strip().split(" ")
        bulan_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "Mei": 5, "Jun": 6,
                     "Jul": 7, "Agu": 8, "Sep": 9, "Okt": 10, "Nov": 11, "Des": 12}
        d = int(parts[0])
        m = bulan_map.get(parts[1], 1)
        y = int(parts[2])
        return datetime(y, m, d)
    except:
        return datetime(2000, 1, 1)

def audit(table, record_id, action, old_val, new_val, by):
    insert_row("audit_log", {
        "table_name": table,
        "record_id": record_id,
        "action": action,
        "old_value": json.dumps(old_val, ensure_ascii=False),
        "new_value": json.dumps(new_val, ensure_ascii=False),
        "performed_by": by,
        "timestamp": tgl_indo()
    })

def get_all_users():
    """Ambil nama user unik dari transactions + kardus"""
    tx = load_table("transactions")
    kr = load_table("kardus")
    names = set()
    for t in tx:
        if t.get("performed_by"):
            names.add(t["performed_by"])
    for k in kr:
        if k.get("created_by"):
            names.add(k["created_by"])
    names = sorted([n for n in names if n])
    if not names:
        names = ["Admin"]
    return names

def get_kardus_list():
    """Get all kardus + total qty per kardus, sorted by created_at DESC (newest first)"""
    kardus_rows = load_table("kardus")
    inv_rows = load_table("inventory")
    
    qty_by_kardus = {}
    for inv in inv_rows:
        kid = str(inv.get("kardus_id", ""))
        try:
            q = int(inv.get("qty", 0) or 0)
        except:
            q = 0
        qty_by_kardus[kid] = qty_by_kardus.get(kid, 0) + q
    
    result = []
    for k in kardus_rows:
        k_copy = dict(k)
        k_copy["total_qty"] = qty_by_kardus.get(str(k.get("id", "")), 0)
        result.append(k_copy)
    
    # Sort by id DESCENDING (id incremental, jadi newest first)
    result.sort(key=lambda x: int(x.get("id", 0) or 0), reverse=True)
    return result

def get_inventory_by_kardus(kardus_id):
    rows = query_filter("inventory", kardus_id=kardus_id)
    rows.sort(key=lambda x: x.get("product_name", ""))
    return rows

def get_recent_transactions(limit=5):
    tx = load_table("transactions")
    kr = load_table("kardus")
    kardus_map = {str(k.get("id")): k for k in kr}
    tx_sorted = sorted(tx, key=lambda x: int(x.get("id", 0) or 0), reverse=True)
    result = []
    for t in tx_sorted[:limit]:
        t_copy = dict(t)
        kid = str(t.get("kardus_id", ""))
        if kid in kardus_map:
            t_copy["kardus_label"] = kardus_map[kid].get("label", "")
            t_copy["owner_name"] = kardus_map[kid].get("owner_name", "")
        result.append(t_copy)
    return result

def get_dashboard_stats():
    today = tgl_indo_short()
    kr = load_table("kardus")
    inv = load_table("inventory")
    tx = load_table("transactions")
    
    total_items = 0
    for i in inv:
        try:
            total_items += int(i.get("qty", 0) or 0)
        except:
            pass
    
    penjualan_today = 0
    masuk_today = 0
    for t in tx:
        date_str = str(t.get("date", ""))
        if today in date_str:
            if t.get("type") == "PENJUALAN":
                try:
                    penjualan_today += float(t.get("price", 0) or 0)
                except:
                    pass
            elif t.get("type") == "MASUK":
                try:
                    masuk_today += int(t.get("qty", 0) or 0)
                except:
                    pass
    
    return {
        "total_kardus": len(kr),
        "total_items": total_items,
        "penjualan_hari_ini": penjualan_today,
        "masuk_hari_ini": masuk_today,
    }

def search_produk_di_kardus(product_name):
    """Cari produk di semua kardus"""
    inv = load_table("inventory")
    kr = load_table("kardus")
    kardus_map = {str(k.get("id")): k for k in kr}
    
    pname_lower = product_name.lower()
    result = []
    for i in inv:
        if pname_lower in str(i.get("product_name", "")).lower():
            try:
                qty = int(i.get("qty", 0) or 0)
            except:
                qty = 0
            if qty <= 0:
                continue
            kid = str(i.get("kardus_id", ""))
            if kid in kardus_map:
                k = kardus_map[kid]
                result.append({
                    "inv_id": i.get("id"),
                    "product_name": i.get("product_name"),
                    "qty": qty,
                    "unit_price": float(i.get("unit_price", 0) or 0),
                    "kardus_id": kid,
                    "kardus_label": k.get("label", ""),
                    "owner_name": k.get("owner_name", ""),
                    "location": k.get("location", ""),
                    "kardus_type": k.get("type", ""),
                })
    return result

def get_filtered_products(search_text=""):
    """Filter list produk Atomy"""
    if not search_text:
        return ATOMY_PRODUCTS
    s = search_text.lower()
    return [p for p in ATOMY_PRODUCTS if s in p.lower()]

def kurangi_stok(kardus_id, product_name, qty_kurangi, performed_by, tipe="KELUAR",
                 buyer="", price=0, transfer_to="", notes=""):
    """Kurangi stok dan catat transaksi"""
    inv_rows = load_table("inventory")
    target_inv = None
    for i in inv_rows:
        if (str(i.get("kardus_id")) == str(kardus_id) and
            str(i.get("product_name")) == str(product_name)):
            target_inv = i
            break
    
    if not target_inv:
        return False, f"Produk '{product_name}' tidak ditemukan di kardus ini"
    
    current_qty = int(target_inv.get("qty", 0) or 0)
    if current_qty < qty_kurangi:
        return False, f"Stok tidak cukup! Stok saat ini: {current_qty} pcs"
    
    new_qty = current_qty - qty_kurangi
    update_row("inventory", target_inv.get("id"), {"qty": new_qty})
    
    # Catat transaksi
    insert_row("transactions", {
        "type": tipe,
        "date": tgl_indo(),
        "kardus_id": kardus_id,
        "product_name": product_name,
        "qty": qty_kurangi,
        "price": price,
        "buyer_name": buyer,
        "transfer_to": transfer_to,
        "transfer_amount": price if tipe == "PENJUALAN" else 0,
        "performed_by": performed_by,
        "notes": notes
    })
    
    return True, f"✅ Berhasil! Stok tersisa: {new_qty} pcs"

def edit_inventory_item(inv_id, new_qty, new_price, performed_by, notes=""):
    """Edit qty & harga inventory"""
    inv_rows = load_table("inventory")
    target = None
    for i in inv_rows:
        if str(i.get("id")) == str(inv_id):
            target = i
            break
    if not target:
        return False, "Item tidak ditemukan"
    
    old = {"qty": target.get("qty"), "price": target.get("unit_price")}
    update_row("inventory", inv_id, {"qty": new_qty, "unit_price": new_price})
    audit("inventory", inv_id, "UPDATE", old,
          {"qty": new_qty, "price": new_price, "notes": notes}, performed_by)
    return True, "✅ Berhasil diupdate"

# ═════════════════════════════════════════════════
#  IMPORT BACKUP DARI SQLite (.db) → Google Sheets
# ═════════════════════════════════════════════════
def import_sqlite_backup(uploaded_bytes, normalize=True, performed_by="Admin"):
    """Import data dari .db SQLite backup ke Google Sheets, dengan auto-normalize nama produk"""
    import sqlite3
    import tempfile
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            tmp.write(uploaded_bytes)
            tmp_path = tmp.name
        
        conn = sqlite3.connect(tmp_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Validasi
        for tbl in ["kardus", "inventory", "transactions"]:
            c.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{tbl}'")
            if c.fetchone()[0] == 0:
                conn.close()
                return False, f"Tabel '{tbl}' tidak ada di backup"
        
        # Bersihkan worksheets dulu
        for name in ["kardus", "inventory", "transactions", "audit_log"]:
            ws = get_worksheet(name)
            ws.clear()
            headers_map = {
                "kardus": KARDUS_HEADERS,
                "inventory": INVENTORY_HEADERS,
                "transactions": TRANSACTIONS_HEADERS,
                "audit_log": AUDIT_HEADERS,
            }
            ws.append_row(headers_map[name])
        
        # Migrate kardus
        kardus_rows = c.execute("SELECT * FROM kardus").fetchall()
        kardus_data = []
        for k in kardus_rows:
            kardus_data.append({
                "id": k["id"],
                "label": k["label"],
                "nomor_pesanan": k["nomor_pesanan"],
                "nomor_id": k["nomor_id"],
                "owner_name": k["owner_name"],
                "location": k["location"],
                "type": k["type"],
                "created_at": k["created_at"],
                "created_by": k["created_by"],
                "updated_at": k["updated_at"],
                "updated_by": k["updated_by"],
            })
        if kardus_data:
            insert_rows_batch("kardus", kardus_data)
        
        # Migrate inventory dengan auto-normalize
        inv_rows = c.execute("SELECT * FROM inventory").fetchall()
        inv_data = []
        normalized_count = 0
        for i in inv_rows:
            original_name = i["product_name"]
            name = normalize_product_name(original_name) if normalize else original_name
            if name != original_name:
                normalized_count += 1
            inv_data.append({
                "id": i["id"],
                "kardus_id": i["kardus_id"],
                "product_name": name,
                "qty": i["qty"],
                "unit_price": i["unit_price"],
                "added_at": i["added_at"],
                "added_by": i["added_by"],
            })
        if inv_data:
            insert_rows_batch("inventory", inv_data)
        
        # Migrate transactions dengan auto-normalize
        tx_rows = c.execute("SELECT * FROM transactions").fetchall()
        tx_data = []
        for t in tx_rows:
            original_name = t["product_name"]
            name = normalize_product_name(original_name) if normalize else original_name
            tx_data.append({
                "id": t["id"],
                "type": t["type"],
                "date": t["date"],
                "kardus_id": t["kardus_id"],
                "product_name": name,
                "qty": t["qty"],
                "price": t["price"],
                "buyer_name": t["buyer_name"],
                "transfer_to": t["transfer_to"],
                "transfer_amount": t["transfer_amount"],
                "performed_by": t["performed_by"],
                "notes": t["notes"],
            })
        if tx_data:
            insert_rows_batch("transactions", tx_data)
        
        conn.close()
        os.unlink(tmp_path)
        
        return True, (f"✅ Migrasi selesai!\n"
                      f"- Kardus: {len(kardus_data)} baris\n"
                      f"- Inventory: {len(inv_data)} baris ({normalized_count} produk dinormalisasi)\n"
                      f"- Transactions: {len(tx_data)} baris")
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def merge_duplicate_products(performed_by="Admin"):
    """Merge produk yang sebenarnya sama tapi nama berbeda → consolidate inventory"""
    inv_rows = load_table("inventory")
    
    # Group by (kardus_id, normalized_name)
    groups = {}
    for i in inv_rows:
        kid = str(i.get("kardus_id"))
        original_name = i.get("product_name", "")
        normalized = normalize_product_name(original_name)
        key = (kid, normalized)
        if key not in groups:
            groups[key] = []
        groups[key].append(i)
    
    merge_count = 0
    rename_count = 0
    
    for (kid, normalized), items in groups.items():
        if len(items) > 1:
            # Multiple items perlu di-merge jadi 1
            total_qty = sum(int(it.get("qty", 0) or 0) for it in items)
            # Ambil unit_price dari yang paling besar
            unit_price = max(float(it.get("unit_price", 0) or 0) for it in items)
            
            # Update item pertama
            first_item = items[0]
            update_row("inventory", first_item["id"], {
                "product_name": normalized,
                "qty": total_qty,
                "unit_price": unit_price,
            })
            
            # Hapus sisa
            for it in items[1:]:
                delete_row("inventory", it["id"])
                merge_count += 1
        elif len(items) == 1:
            # Single item, cukup rename kalau perlu
            it = items[0]
            if it.get("product_name") != normalized:
                update_row("inventory", it["id"], {"product_name": normalized})
                rename_count += 1
    
    # Normalize semua transaksi juga
    tx_rows = load_table("transactions")
    tx_renamed = 0
    for t in tx_rows:
        original = t.get("product_name", "")
        normalized = normalize_product_name(original)
        if normalized != original:
            update_row("transactions", t["id"], {"product_name": normalized})
            tx_renamed += 1
    
    audit("inventory", 0, "MERGE",
          {}, {"merged": merge_count, "renamed": rename_count, "tx_renamed": tx_renamed},
          performed_by)
    
    return merge_count, rename_count, tx_renamed

# ═════════════════════════════════════════════════
#  HEADER & INIT
# ═════════════════════════════════════════════════
init_sheets()

# Session state
for key, default in [
    ("active_tab", 0),
    ("show_buat_kardus", False),
    ("show_detail_kardus", False),
    ("konfirmasi_jual", False),
    ("konfirmasi_ambil", False),
    ("last_jual_data", {}),
    ("last_ambil_data", {}),
    ("bulk_produk_list", []),  # list of {product_name, qty, unit_price}
]:
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown("""
<div style="
    background: linear-gradient(135deg, #2E7D32 0%, #388E3C 50%, #43A047 100%);
    padding: 24px 32px; border-radius: 16px; margin-bottom: 24px;
    display: flex; align-items: center; gap: 16px;
    box-shadow: 0 4px 20px rgba(46,125,50,0.3);">
    <div style="font-size:52px">📦</div>
    <div>
        <div style="color:white; font-size:34px; font-weight:800;">GudangKu Atomy</div>
        <div style="color:#c8e6c9; font-size:17px; font-weight:600">
            Kelola Kardus & Penjualan • Database Permanen di Google Sheets
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "🏠 Dashboard",
    "📦 Daftar Kardus",
    "➕ Barang Masuk",
    "🛒 Jual / Ambil",
    "🔍 Cari Barang",
    "📊 Laporan",
    "⚙️ Pengaturan",
])
tab_dashboard, tab_kardus, tab_masuk, tab_jual, tab_cari, tab_laporan, tab_setting = tabs

# ════════════════════════════════════════════════════
#  TAB: DASHBOARD
# ════════════════════════════════════════════════════
with tab_dashboard:
    stats = get_dashboard_stats()
    
    st.markdown("### 📊 Ringkasan Hari Ini")
    st.caption("Lihat semua info penting gudang dalam satu tampilan.")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📦 Total Kardus", f"{stats['total_kardus']}")
    with c2:
        st.metric("🗃️ Total Item", f"{stats['total_items']:,} pcs")
    with c3:
        st.metric("💰 Penjualan Hari Ini", format_rupiah(stats["penjualan_hari_ini"]))
    with c4:
        st.metric("📥 Masuk Hari Ini", f"{stats['masuk_hari_ini']} pcs")
    
    st.markdown("---")
    st.markdown("### 🕐 5 Transaksi Terakhir")
    
    recent = get_recent_transactions(5)
    if recent:
        df = pd.DataFrame(recent)
        cols_show = ["date", "type", "kardus_label", "product_name", "qty", "price", "performed_by"]
        cols_show = [c for c in cols_show if c in df.columns]
        df = df[cols_show].copy()
        df.columns = ["Tanggal", "Tipe", "Kardus", "Produk", "Qty", "Harga (Rp)", "Oleh"][:len(cols_show)]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("📭 Belum ada transaksi.")

# ════════════════════════════════════════════════════
#  TAB: DAFTAR KARDUS
# ════════════════════════════════════════════════════
with tab_kardus:
    st.markdown("### 📦 Daftar Semua Kardus")
    st.caption("Kardus terbaru ditampilkan paling atas. 🆕 = dibuat dalam 1 jam terakhir.")
    
    col_btn, _ = st.columns([1, 2])
    with col_btn:
        if st.button("➕  Buat Kardus Baru", use_container_width=True):
            st.session_state.show_buat_kardus = not st.session_state.show_buat_kardus
    
    # Form Buat Kardus Baru
    if st.session_state.show_buat_kardus:
        st.markdown("---")
        st.markdown("#### 📝 Form Buat Kardus Baru")
        users = get_all_users()
        c1, c2 = st.columns(2)
        with c1:
            bk_np = st.text_input("Nomor Pesanan (4 digit)", max_chars=4, key="bk_np")
            bk_ni = st.text_input("Nomor ID Driver (4 digit)", max_chars=4, key="bk_ni")
            bk_owner = st.text_input("Nama Pemilik", key="bk_owner",
                placeholder="Contoh: Titipan Anita")
        with c2:
            bk_loc = st.text_input("Lokasi", key="bk_loc", placeholder="Contoh: Rak A1")
            bk_type = st.radio("Tipe", ["Titipan", "Milik Sendiri"], horizontal=True, key="bk_type")
            bk_by_opt = users + ["Ketik nama baru..."]
            bk_by_sel = st.selectbox("Dibuat Oleh", bk_by_opt, key="bk_by")
            if bk_by_sel == "Ketik nama baru...":
                bk_by = st.text_input("Nama Anda:", key="bk_by_new")
            else:
                bk_by = bk_by_sel
        
        if bk_np and bk_ni and bk_owner:
            st.info(f"🏷️ Label otomatis: `{bk_np}-{bk_ni}-{bk_owner}`")
        
        cs, cc = st.columns(2)
        with cs:
            if st.button("✅  SIMPAN", use_container_width=True, key="btn_save_kardus"):
                err = []
                if not bk_np or len(bk_np) != 4: err.append("Nomor Pesanan harus 4 digit.")
                if not bk_ni or len(bk_ni) != 4: err.append("Nomor ID harus 4 digit.")
                if not bk_owner.strip(): err.append("Pemilik tidak boleh kosong.")
                if not bk_loc.strip(): err.append("Lokasi tidak boleh kosong.")
                if not bk_by.strip(): err.append("Pembuat tidak boleh kosong.")
                if err:
                    for e in err: st.error(f"❌ {e}")
                else:
                    label = f"{bk_np}-{bk_ni}-{bk_owner.strip()}"
                    now_str = tgl_indo()
                    new_id = insert_row("kardus", {
                        "label": label, "nomor_pesanan": bk_np, "nomor_id": bk_ni,
                        "owner_name": bk_owner.strip(), "location": bk_loc.strip(),
                        "type": bk_type, "created_at": now_str, "created_by": bk_by.strip(),
                        "updated_at": now_str, "updated_by": bk_by.strip(),
                    })
                    audit("kardus", new_id, "CREATE", {}, {"label": label}, bk_by.strip())
                    st.success(f"✅ Kardus **{label}** berhasil dibuat!")
                    st.session_state.show_buat_kardus = False
                    time.sleep(0.5)
                    st.rerun()
        with cc:
            if st.button("❌  Batal", use_container_width=True, key="btn_cancel_kardus"):
                st.session_state.show_buat_kardus = False
                st.rerun()
        st.markdown("---")
    
    search = st.text_input("🔍 Cari kardus", placeholder="Ketik nama, label, atau lokasi...",
                            key="search_kardus")
    
    all_kardus = get_kardus_list()
    if search:
        q = search.lower()
        all_kardus = [k for k in all_kardus if
            q in str(k.get("label", "")).lower() or
            q in str(k.get("owner_name", "")).lower() or
            q in str(k.get("location", "")).lower()]
    
    if all_kardus:
        # Tag NEW untuk kardus < 1 jam
        now = datetime.now()
        df_data = []
        for k in all_kardus:
            created = parse_tgl(k.get("created_at", ""))
            tag = ""
            try:
                # Parse waktu juga
                parts = str(k.get("created_at", "")).split(" ")
                if len(parts) >= 4:
                    tm = parts[3].split(":")
                    created = created.replace(hour=int(tm[0]), minute=int(tm[1]))
                if (now - created).total_seconds() < 3600:
                    tag = "🆕 "
            except:
                pass
            df_data.append({
                "🏷️ Label": tag + str(k.get("label", "")),
                "👤 Pemilik": k.get("owner_name", ""),
                "📍 Lokasi": k.get("location", ""),
                "🗂️ Tipe": k.get("type", ""),
                "📊 Item": k.get("total_qty", 0),
            })
        
        df = pd.DataFrame(df_data)
        st.markdown(f"**Ditemukan: {len(all_kardus)} kardus**")
        st.dataframe(df, use_container_width=True, hide_index=True,
            column_config={"📊 Item": st.column_config.NumberColumn(format="%d pcs")})
        
        # Detail kardus
        st.markdown("#### 🔎 Lihat Detail Kardus")
        opts = [f"{k['owner_name']} | {k.get('nomor_pesanan')}-{k.get('nomor_id')} | {k.get('location')}"
                for k in all_kardus]
        sel = st.selectbox("Pilih:", ["-- Pilih --"] + opts, key="sel_detail")
        
        if sel != "-- Pilih --":
            idx = opts.index(sel)
            sk = all_kardus[idx]
            sid = sk["id"]
            
            badge = "#1565C0" if sk.get("type") == "Titipan" else "#2E7D32"
            st.markdown(f"""
            <div style="background:white; border:2px solid {badge}; border-radius:12px;
                 padding:18px 22px; margin:12px 0;">
                <div style="font-size:20px; font-weight:800; color:{badge};">📦 {sk.get('label')}</div>
                <div style="margin-top:10px;">
                  <b>👤 Pemilik:</b> {sk.get('owner_name')} &nbsp; | &nbsp;
                  <b>📍 Lokasi:</b> {sk.get('location')} &nbsp; | &nbsp;
                  <b>🗂️ Tipe:</b> {sk.get('type')}<br>
                  <b>📅 Dibuat:</b> {sk.get('created_at')} oleh {sk.get('created_by')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            inv = get_inventory_by_kardus(sid)
            if inv:
                df_inv = pd.DataFrame(inv)
                df_show = df_inv[["product_name", "qty", "unit_price"]].copy()
                df_show.columns = ["Produk", "Stok", "Harga"]
                st.dataframe(df_show, use_container_width=True, hide_index=True,
                    column_config={
                        "Stok": st.column_config.NumberColumn(format="%d pcs"),
                        "Harga": st.column_config.NumberColumn(format="Rp %d"),
                    })
            else:
                st.info("📭 Kardus ini masih kosong.")
            
            # Hapus Kardus (kalau kosong)
            with st.expander("🗑️ Hapus Kardus Ini"):
                total_stok = sum(int(i.get("qty", 0) or 0) for i in inv)
                if total_stok > 0:
                    st.warning(f"⚠️ Kardus berisi {total_stok} item. Kosongkan dulu.")
                else:
                    users = get_all_users()
                    alasan = st.text_input("Alasan hapus:", key=f"alasan_{sid}")
                    by = st.selectbox("Oleh:", users, key=f"hby_{sid}")
                    chk = st.checkbox(f"Yakin hapus **{sk.get('label')}**?", key=f"chk_{sid}")
                    if st.button("🗑️ HAPUS", key=f"btn_hps_{sid}", use_container_width=True):
                        if not chk:
                            st.error("Centang konfirmasi dulu!")
                        elif not alasan.strip():
                            st.error("Alasan wajib!")
                        else:
                            audit("kardus", sid, "DELETE", dict(sk), {"alasan": alasan}, by)
                            delete_row("kardus", sid)
                            st.success("✅ Terhapus!")
                            time.sleep(0.5)
                            st.rerun()
    else:
        st.info("📭 Belum ada kardus. Klik **Buat Kardus Baru** di atas!")

# ════════════════════════════════════════════════════
#  TAB: BARANG MASUK (BULK MULTI-PRODUCT INPUT)
# ════════════════════════════════════════════════════
with tab_masuk:
    st.markdown("### ➕ Barang Masuk (Bulk Multi-Produk)")
    st.caption("Pilih kardus 1x, tambah banyak produk sekaligus, lalu submit semua dalam 1 klik!")
    
    all_kardus = get_kardus_list()
    users = get_all_users()
    
    if not all_kardus:
        st.warning("⚠️ Belum ada kardus! Buat kardus dulu di tab Daftar Kardus.")
    else:
        # Step 1: Pilih kardus (sorted newest first dengan tag 🆕)
        now = datetime.now()
        kardus_options = []
        for k in all_kardus:
            tag = ""
            try:
                created = parse_tgl(k.get("created_at", ""))
                parts = str(k.get("created_at", "")).split(" ")
                if len(parts) >= 4:
                    tm = parts[3].split(":")
                    created = created.replace(hour=int(tm[0]), minute=int(tm[1]))
                if (now - created).total_seconds() < 3600:
                    tag = "🆕 "
            except:
                pass
            kardus_options.append(
                f"{tag}{k['owner_name']} | No. {k.get('nomor_pesanan')}-{k.get('nomor_id')} | 📍 {k.get('location')}"
            )
        
        sel_kardus_str = st.selectbox(
            "1️⃣  Pilih Kardus Tujuan (kardus baru = 🆕 di atas)",
            kardus_options,
            key="bm_kardus"
        )
        kid_idx = kardus_options.index(sel_kardus_str)
        sel_k = all_kardus[kid_idx]
        kardus_id = sel_k["id"]
        
        st.info(f"📦 **{sel_k.get('label')}**  |  📍 {sel_k.get('location')}  |  👤 {sel_k.get('owner_name')}")
        
        st.markdown("---")
        
        # Step 2: Daftar produk yang akan dimasukkan
        st.markdown("#### 📋 Daftar Produk Yang Akan Dimasukkan")
        
        if st.session_state.bulk_produk_list:
            for idx, item in enumerate(st.session_state.bulk_produk_list):
                cols = st.columns([5, 2, 2, 1])
                with cols[0]:
                    st.markdown(f"**{idx+1}. {item['product_name']}**")
                with cols[1]:
                    st.markdown(f"Qty: **{item['qty']} pcs**")
                with cols[2]:
                    st.markdown(f"Harga: **Rp {int(item.get('unit_price', 0)):,}**")
                with cols[3]:
                    if st.button("❌", key=f"rm_{idx}", help="Hapus item ini"):
                        st.session_state.bulk_produk_list.pop(idx)
                        st.rerun()
            st.success(f"✅ {len(st.session_state.bulk_produk_list)} produk siap disubmit")
        else:
            st.info("Belum ada produk. Tambahkan di bawah ⬇️")
        
        st.markdown("---")
        
        # Step 3: Tambah produk ke list (searchable dropdown!)
        st.markdown("#### ➕ Tambah Produk ke Daftar")
        
        # Searchable: ketik beberapa huruf, dropdown filter otomatis
        c_prod, c_qty, c_harga = st.columns([3, 1, 1])
        with c_prod:
            # Streamlit selectbox sudah punya fitur "type to search" built-in!
            new_produk = st.selectbox(
                "Cari & Pilih Produk Atomy (ketik untuk cari)",
                [""] + ATOMY_PRODUCTS,
                key="bm_new_produk",
                help="Ketik beberapa huruf untuk cari, contoh: 'h' → muncul HemoHim, Hongsamdan, dll"
            )
        with c_qty:
            new_qty = st.number_input("Qty", min_value=1, value=1, key="bm_new_qty")
        with c_harga:
            new_harga = st.number_input("Harga Satuan (Rp)", min_value=0, value=0, step=500,
                                         key="bm_new_harga")
        
        ca, cb = st.columns(2)
        with ca:
            if st.button("➕  Tambah ke Daftar", use_container_width=True, key="btn_add_bulk"):
                if not new_produk:
                    st.error("Pilih produk dulu!")
                elif new_qty <= 0:
                    st.error("Qty harus > 0!")
                else:
                    st.session_state.bulk_produk_list.append({
                        "product_name": new_produk,
                        "qty": new_qty,
                        "unit_price": new_harga,
                    })
                    st.rerun()
        with cb:
            if st.button("🗑️  Bersihkan Semua", use_container_width=True, key="btn_clear_bulk"):
                st.session_state.bulk_produk_list = []
                st.rerun()
        
        st.markdown("---")
        
        # Step 4: Final submit info + button
        st.markdown("#### 4️⃣ Info Tambahan")
        
        c1, c2 = st.columns(2)
        with c1:
            by_opt = users + ["Ketik nama baru..."]
            by_sel = st.selectbox("Dilakukan Oleh", by_opt, key="bm_by_sel")
            if by_sel == "Ketik nama baru...":
                bm_by = st.text_input("Nama:", key="bm_by_new")
            else:
                bm_by = by_sel
        with c2:
            bm_notes = st.text_area("Catatan (opsional)", height=100,
                placeholder="Contoh: barang dari Surabaya", key="bm_notes")
        
        if st.button(
            f"💾  SIMPAN SEMUA {len(st.session_state.bulk_produk_list)} PRODUK SEKALIGUS",
            use_container_width=True,
            type="primary",
            disabled=len(st.session_state.bulk_produk_list) == 0
        ):
            if not bm_by.strip():
                st.error("Nama pelaksana wajib!")
            else:
                with st.spinner(f"Menyimpan {len(st.session_state.bulk_produk_list)} produk..."):
                    now_str = tgl_indo()
                    
                    # Cek existing inventory untuk kardus ini
                    existing_inv = get_inventory_by_kardus(kardus_id)
                    existing_map = {i.get("product_name"): i for i in existing_inv}
                    
                    # Prepare batch data
                    inv_to_insert = []
                    inv_to_update = []
                    tx_to_insert = []
                    
                    for item in st.session_state.bulk_produk_list:
                        pname = item["product_name"]
                        qty = item["qty"]
                        price = item.get("unit_price", 0)
                        
                        if pname in existing_map:
                            # Update existing
                            ex = existing_map[pname]
                            new_qty = int(ex.get("qty", 0) or 0) + qty
                            inv_to_update.append((ex["id"], {
                                "qty": new_qty,
                                "unit_price": price if price > 0 else ex.get("unit_price", 0),
                                "added_at": now_str,
                                "added_by": bm_by.strip(),
                            }))
                        else:
                            # Insert new
                            inv_to_insert.append({
                                "kardus_id": kardus_id,
                                "product_name": pname,
                                "qty": qty,
                                "unit_price": price,
                                "added_at": now_str,
                                "added_by": bm_by.strip(),
                            })
                        
                        # Selalu catat transaksi
                        tx_to_insert.append({
                            "type": "MASUK",
                            "date": now_str,
                            "kardus_id": kardus_id,
                            "product_name": pname,
                            "qty": qty,
                            "price": 0,
                            "buyer_name": "",
                            "transfer_to": "",
                            "transfer_amount": 0,
                            "performed_by": bm_by.strip(),
                            "notes": bm_notes,
                        })
                    
                    # Execute batch
                    if inv_to_insert:
                        insert_rows_batch("inventory", inv_to_insert)
                    for inv_id, updates in inv_to_update:
                        update_row("inventory", inv_id, updates)
                    if tx_to_insert:
                        insert_rows_batch("transactions", tx_to_insert)
                
                total = len(st.session_state.bulk_produk_list)
                st.session_state.bulk_produk_list = []
                st.success(f"✅ Berhasil! {total} produk masuk ke kardus **{sel_k.get('label')}**!")
                st.balloons()
                time.sleep(1)
                st.rerun()

# ════════════════════════════════════════════════════
#  TAB: JUAL / AMBIL
# ════════════════════════════════════════════════════
with tab_jual:
    st.markdown("### 🛒 Jual / Ambil Barang")
    st.caption("Mode A: Jual ke customer (dengan harga). Mode B: Ambil titipan (tanpa bayar).")
    
    sub_a, sub_b = st.tabs(["💰 A. Jual ke Customer", "📤 B. Ambil Titipan"])
    
    all_kardus = get_kardus_list()
    users = get_all_users()
    
    with sub_a:
        st.markdown("#### 💰 Proses Penjualan")
        kardus_punya_stok = [k for k in all_kardus if k.get("total_qty", 0) > 0]
        
        if not kardus_punya_stok:
            st.warning("⚠️ Tidak ada kardus dengan stok!")
        else:
            opts = [f"{k['owner_name']} | No. {k.get('nomor_pesanan')}-{k.get('nomor_id')} | Stok: {k.get('total_qty')} pcs"
                    for k in kardus_punya_stok]
            sel_str = st.selectbox("1️⃣  Pilih Kardus Sumber", opts, key="ja_kardus")
            sel_idx = opts.index(sel_str)
            sel_k = kardus_punya_stok[sel_idx]
            kid = sel_k["id"]
            
            st.info(f"📦 **{sel_k.get('label')}** | 📍 {sel_k.get('location')} | 👤 {sel_k.get('owner_name')}")
            
            inv = get_inventory_by_kardus(kid)
            inv_ada = [i for i in inv if int(i.get("qty", 0) or 0) > 0]
            
            if not inv_ada:
                st.warning("Kardus ini kosong.")
            else:
                prod_opts = [f"{i.get('product_name')} — stok: {i.get('qty')} pcs" for i in inv_ada]
                sel_p_str = st.selectbox("2️⃣  Pilih Produk", prod_opts, key="ja_produk")
                p_idx = prod_opts.index(sel_p_str)
                p_info = inv_ada[p_idx]
                max_qty = int(p_info.get("qty", 0) or 0)
                harga_satuan = float(p_info.get("unit_price", 0) or 0)
                
                cc1, cc2 = st.columns(2)
                with cc1:
                    qty = st.number_input(f"Qty (max {max_qty})", min_value=1, max_value=max_qty,
                                          value=1, key="ja_qty")
                with cc2:
                    harga = st.number_input("Harga Total (Rp)", min_value=0,
                        value=int(harga_satuan * qty) if harga_satuan else 0, step=500, key="ja_harga")
                
                buyer = st.text_input("Nama Pembeli", placeholder="Pak Budi", key="ja_buyer")
                tr_to = st.text_input("Uang Ditransfer ke:", value=sel_k.get("owner_name", ""),
                                      key="ja_tr")
                by_opt = users + ["Ketik nama baru..."]
                by_sel = st.selectbox("Dilakukan Oleh", by_opt, key="ja_by")
                ja_by = st.text_input("Nama:", key="ja_by_new") if by_sel == "Ketik nama baru..." else by_sel
                ja_notes = st.text_area("Catatan (opsional)", height=60, key="ja_notes")
                
                if not st.session_state.konfirmasi_jual:
                    if st.button("🛒  PROSES PENJUALAN", use_container_width=True, key="btn_jual"):
                        if not buyer.strip(): st.error("Nama pembeli wajib!")
                        elif not ja_by.strip(): st.error("Nama pelaksana wajib!")
                        else:
                            st.session_state.konfirmasi_jual = True
                            st.session_state.last_jual_data = {
                                "kid": kid, "label": sel_k.get("label"),
                                "produk": p_info.get("product_name"),
                                "qty": qty, "harga": harga, "buyer": buyer,
                                "tr_to": tr_to, "by": ja_by, "notes": ja_notes,
                            }
                            st.rerun()
                else:
                    d = st.session_state.last_jual_data
                    st.warning(f"⚠️ **Konfirmasi**: Jual {d['qty']} pcs {d['produk']} ke {d['buyer']} "
                               f"seharga {format_rupiah(d['harga'])}?")
                    cy, cn = st.columns(2)
                    with cy:
                        if st.button("✅ YA, PROSES!", use_container_width=True, key="btn_konfirm_jual"):
                            success, msg = kurangi_stok(
                                d["kid"], d["produk"], d["qty"], d["by"],
                                tipe="PENJUALAN", buyer=d["buyer"], price=d["harga"],
                                transfer_to=d["tr_to"], notes=d["notes"]
                            )
                            st.session_state.konfirmasi_jual = False
                            st.session_state.last_jual_data = {}
                            if success:
                                st.success(f"✅ Penjualan berhasil! {msg}")
                                st.balloons()
                            else:
                                st.error(msg)
                            time.sleep(1)
                            st.rerun()
                    with cn:
                        if st.button("❌ Batal", use_container_width=True, key="btn_batal_jual"):
                            st.session_state.konfirmasi_jual = False
                            st.rerun()
    
    with sub_b:
        st.markdown("#### 📤 Ambil Titipan (Tanpa Pembayaran)")
        titipan_kardus = [k for k in all_kardus if k.get("type") == "Titipan" and k.get("total_qty", 0) > 0]
        
        if not titipan_kardus:
            st.info("Tidak ada kardus titipan dengan stok.")
        else:
            opts = [f"{k['owner_name']} | No. {k.get('nomor_pesanan')}-{k.get('nomor_id')} | Stok: {k.get('total_qty')} pcs"
                    for k in titipan_kardus]
            sel_str = st.selectbox("1️⃣  Pilih Kardus Titipan", opts, key="at_kardus")
            sel_idx = opts.index(sel_str)
            sel_k = titipan_kardus[sel_idx]
            kid = sel_k["id"]
            
            st.info(f"📦 **{sel_k.get('label')}** | 📍 {sel_k.get('location')} | 👤 {sel_k.get('owner_name')}")
            
            inv = get_inventory_by_kardus(kid)
            inv_ada = [i for i in inv if int(i.get("qty", 0) or 0) > 0]
            
            if inv_ada:
                prod_opts = [f"{i.get('product_name')} — stok: {i.get('qty')} pcs" for i in inv_ada]
                sel_p_str = st.selectbox("2️⃣  Pilih Produk", prod_opts, key="at_produk")
                p_idx = prod_opts.index(sel_p_str)
                p_info = inv_ada[p_idx]
                max_qty = int(p_info.get("qty", 0) or 0)
                
                qty = st.number_input(f"Jumlah Diambil (max {max_qty})",
                    min_value=1, max_value=max_qty, value=1, key="at_qty")
                by_opt = users + ["Ketik nama baru..."]
                by_sel = st.selectbox("Oleh", by_opt, key="at_by")
                at_by = st.text_input("Nama:", key="at_by_new") if by_sel == "Ketik nama baru..." else by_sel
                at_notes = st.text_area("Catatan", height=60, key="at_notes")
                
                if not st.session_state.konfirmasi_ambil:
                    if st.button("📤  PROSES PENGAMBILAN", use_container_width=True, key="btn_ambil"):
                        if not at_by.strip(): st.error("Nama wajib!")
                        else:
                            st.session_state.konfirmasi_ambil = True
                            st.session_state.last_ambil_data = {
                                "kid": kid, "produk": p_info.get("product_name"),
                                "qty": qty, "by": at_by, "notes": at_notes,
                                "owner": sel_k.get("owner_name"),
                                "label": sel_k.get("label"),
                            }
                            st.rerun()
                else:
                    d = st.session_state.last_ambil_data
                    st.warning(f"⚠️ Konfirmasi: Ambil {d['qty']} pcs {d['produk']} dari {d['label']}?")
                    cy, cn = st.columns(2)
                    with cy:
                        if st.button("✅ YA!", use_container_width=True, key="btn_konfirm_ambil"):
                            success, msg = kurangi_stok(d["kid"], d["produk"], d["qty"], d["by"],
                                tipe="KELUAR", transfer_to=d["owner"], notes=d["notes"])
                            st.session_state.konfirmasi_ambil = False
                            st.session_state.last_ambil_data = {}
                            if success:
                                st.success(f"✅ {msg}")
                            else:
                                st.error(msg)
                            time.sleep(1)
                            st.rerun()
                    with cn:
                        if st.button("❌ Batal", use_container_width=True, key="btn_batal_ambil"):
                            st.session_state.konfirmasi_ambil = False
                            st.rerun()

# ════════════════════════════════════════════════════
#  TAB: CARI BARANG
# ════════════════════════════════════════════════════
with tab_cari:
    st.markdown("### 🔍 Cari Barang di Gudang")
    st.caption("Cari produk untuk lihat di kardus mana saja, dan langsung ambil jika perlu.")
    
    users = get_all_users()
    
    search_input = st.text_input(
        "Ketik nama produk (contoh: 'h' → muncul HemoHim, Hongsamdan, dll)",
        placeholder="HemoHim, vitamin, paket, sunscreen..."
    )
    
    if search_input:
        filtered = get_filtered_products(search_input)
        if filtered:
            sel_produk = st.selectbox("📦 Pilih produk:", filtered, key="cari_pilih")
            
            results = search_produk_di_kardus(sel_produk)
            
            if results:
                st.markdown(f"#### 📍 **{sel_produk}** ada di {len(results)} kardus:")
                
                df = pd.DataFrame(results)
                df_show = df[["kardus_label", "owner_name", "location", "kardus_type",
                              "qty", "unit_price"]].copy()
                df_show.columns = ["Kardus", "Pemilik", "📍 Lokasi", "Tipe", "Stok", "Harga"]
                st.dataframe(df_show, use_container_width=True, hide_index=True,
                    column_config={
                        "Stok": st.column_config.NumberColumn(format="%d pcs"),
                        "Harga": st.column_config.NumberColumn(format="Rp %d"),
                    })
                
                st.markdown("---")
                st.markdown("#### 📤 Ambil Barang")
                
                kardus_choices = [f"{r['kardus_label']} ({r['qty']} pcs)" for r in results]
                sel_kardus_amb = st.selectbox("Dari kardus:", kardus_choices, key="cari_amb_kardus")
                amb_idx = kardus_choices.index(sel_kardus_amb)
                amb_target = results[amb_idx]
                max_qty = amb_target["qty"]
                
                ac1, ac2 = st.columns(2)
                with ac1:
                    amb_qty = st.number_input(f"Qty (max {max_qty})", min_value=1,
                        max_value=max_qty, value=1, key="cari_amb_qty")
                with ac2:
                    by_opt = users + ["Ketik nama baru..."]
                    by_sel = st.selectbox("Oleh", by_opt, key="cari_amb_by")
                    amb_by = st.text_input("Nama:", key="cari_amb_by_new") if by_sel == "Ketik nama baru..." else by_sel
                
                amb_notes = st.text_area("Catatan", height=60, key="cari_amb_notes")
                
                conf = st.checkbox(
                    f"✅ Yakin ambil {amb_qty} pcs {sel_produk} dari {amb_target['kardus_label']}",
                    key="cari_conf"
                )
                
                if st.button("📤 PROSES PENGAMBILAN", use_container_width=True,
                             key="btn_cari_ambil", disabled=not conf):
                    if not amb_by.strip():
                        st.error("Nama wajib!")
                    else:
                        success, msg = kurangi_stok(amb_target["kardus_id"], sel_produk,
                            amb_qty, amb_by.strip(), tipe="KELUAR",
                            transfer_to=amb_target["owner_name"], notes=amb_notes)
                        if success:
                            st.success(msg)
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg)
            else:
                st.info(f"📭 {sel_produk} tidak ada di gudang.")
        else:
            st.warning("❌ Tidak ada produk match. Coba kata lain.")
    else:
        st.info("💡 Ketik beberapa huruf untuk mulai cari produk.")

# ════════════════════════════════════════════════════
#  TAB: LAPORAN
# ════════════════════════════════════════════════════
with tab_laporan:
    st.markdown("### 📊 Laporan & Riwayat")
    
    periode = st.radio("Periode:", ["📅 Minggu Ini", "📆 Bulan Ini", "📋 Semua"],
                       horizontal=True, key="lap_p")
    
    now = datetime.now()
    if periode == "📅 Minggu Ini":
        start = now - timedelta(days=7)
        label_p = "7 Hari Terakhir"
    elif periode == "📆 Bulan Ini":
        start = now.replace(day=1)
        label_p = f"Bulan {now.strftime('%B %Y')}"
    else:
        start = datetime(2000, 1, 1)
        label_p = "Semua Waktu"
    
    all_tx = load_table("transactions")
    all_kr = load_table("kardus")
    kardus_map = {str(k.get("id")): k for k in all_kr}
    
    # Enrich transactions
    enriched = []
    for t in all_tx:
        t_copy = dict(t)
        kid = str(t.get("kardus_id", ""))
        if kid in kardus_map:
            t_copy["kardus_label"] = kardus_map[kid].get("label", "")
            t_copy["kardus_type"] = kardus_map[kid].get("type", "")
        enriched.append(t_copy)
    
    filtered_tx = [t for t in enriched if parse_tgl(t.get("date", "")) >= start]
    
    masuk = [t for t in filtered_tx if t.get("type") == "MASUK"]
    keluar = [t for t in filtered_tx if t.get("type") == "KELUAR"]
    jual = [t for t in filtered_tx if t.get("type") == "PENJUALAN"]
    
    total_masuk = sum(int(t.get("qty", 0) or 0) for t in masuk)
    total_keluar = sum(int(t.get("qty", 0) or 0) for t in keluar)
    total_jual_qty = sum(int(t.get("qty", 0) or 0) for t in jual)
    total_jual_rp = sum(float(t.get("price", 0) or 0) for t in jual)
    
    st.markdown(f"#### 📋 Ringkasan: {label_p}")
    r1, r2, r3 = st.columns(3)
    with r1: st.metric("📥 Masuk", f"{total_masuk} pcs")
    with r2: st.metric("📤 Keluar", f"{total_keluar} pcs")
    with r3: st.metric("💰 Penjualan", format_rupiah(total_jual_rp))
    
    if jual:
        st.markdown("#### 🏆 5 Produk Terlaris")
        from collections import Counter
        cnt = Counter()
        for t in jual:
            cnt[t.get("product_name", "")] += int(t.get("qty", 0) or 0)
        top5 = cnt.most_common(5)
        st.dataframe(pd.DataFrame(top5, columns=["Produk", "Total Terjual"]),
                     use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("#### 📜 Riwayat Transaksi")
    
    fc1, fc2 = st.columns(2)
    with fc1:
        f_tipe = st.selectbox("Filter Tipe", ["Semua", "MASUK", "KELUAR", "PENJUALAN"], key="f_tipe")
    with fc2:
        s_tx = st.text_input("🔍 Cari produk/kardus", key="s_tx")
    
    disp = filtered_tx
    if f_tipe != "Semua":
        disp = [t for t in disp if t.get("type") == f_tipe]
    if s_tx:
        q = s_tx.lower()
        disp = [t for t in disp if
            q in str(t.get("product_name", "")).lower() or
            q in str(t.get("kardus_label", "")).lower() or
            q in str(t.get("buyer_name", "")).lower()]
    
    disp.sort(key=lambda x: int(x.get("id", 0) or 0), reverse=True)
    
    if disp:
        df = pd.DataFrame(disp)
        cols = ["date", "type", "kardus_label", "product_name", "qty", "price",
                "buyer_name", "performed_by"]
        cols = [c for c in cols if c in df.columns]
        df = df[cols].copy()
        df.columns = ["Tanggal", "Tipe", "Kardus", "Produk", "Qty", "Harga",
                      "Pembeli", "Oleh"][:len(cols)]
        st.dataframe(df, use_container_width=True, hide_index=True,
            column_config={
                "Harga": st.column_config.NumberColumn(format="Rp %d"),
                "Qty": st.column_config.NumberColumn(format="%d pcs"),
            })
        
        if st.button("📥 Export ke Excel", use_container_width=True):
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as w:
                df.to_excel(w, sheet_name="Riwayat", index=False)
                pd.DataFrame({
                    "Keterangan": ["Periode", "Total Masuk", "Total Keluar", "Total Penjualan"],
                    "Nilai": [label_p, f"{total_masuk} pcs", f"{total_keluar} pcs",
                              format_rupiah(total_jual_rp)],
                }).to_excel(w, sheet_name="Ringkasan", index=False)
            buf.seek(0)
            st.download_button("📥 Download Excel", buf,
                file_name=f"GudangKu_Laporan_{now.strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
    else:
        st.info("📭 Tidak ada transaksi.")
    
    # ─── EDIT PRODUK (Protected) ───
    st.markdown("---")
    with st.expander("⚙️ EDIT PRODUK (Protected — Hati-hati!)", expanded=False):
        st.warning("⚠️ FITUR SENSITIF — Pastikan benar-benar yakin!")
        
        all_inv = load_table("inventory")
        all_inv_enriched = []
        for i in all_inv:
            i_copy = dict(i)
            kid = str(i.get("kardus_id", ""))
            if kid in kardus_map:
                i_copy["kardus_label"] = kardus_map[kid].get("label", "")
                i_copy["owner_name"] = kardus_map[kid].get("owner_name", "")
            all_inv_enriched.append(i_copy)
        
        if all_inv_enriched:
            edit_search = st.text_input("🔍 Cari produk/kardus:", key="edit_s")
            
            if edit_search:
                fil = [i for i in all_inv_enriched if
                    edit_search.lower() in str(i.get("product_name", "")).lower() or
                    edit_search.lower() in str(i.get("kardus_label", "")).lower()]
            else:
                fil = all_inv_enriched
            
            if fil:
                opts = [f"{i.get('product_name')} | Kardus: {i.get('kardus_label')} | Qty: {i.get('qty')}"
                        for i in fil]
                sel_e_str = st.selectbox("Pilih produk:", opts, key="edit_sel")
                sel_e_idx = opts.index(sel_e_str)
                sel_e = fil[sel_e_idx]
                
                st.markdown(f"**Sekarang:** Qty `{sel_e.get('qty')}` | "
                            f"Harga `Rp {int(float(sel_e.get('unit_price', 0) or 0)):,}`")
                
                ec1, ec2 = st.columns(2)
                with ec1:
                    new_qty = st.number_input("Qty Baru", min_value=0,
                        value=int(sel_e.get("qty", 0) or 0), key="edit_q")
                with ec2:
                    new_price = st.number_input("Harga Baru (Rp)", min_value=0,
                        value=int(float(sel_e.get("unit_price", 0) or 0)), step=500, key="edit_p")
                
                edit_by_opt = get_all_users() + ["Ketik nama baru..."]
                edit_by_sel = st.selectbox("Oleh", edit_by_opt, key="edit_by")
                edit_by = st.text_input("Nama:", key="edit_by_new") if edit_by_sel == "Ketik nama baru..." else edit_by_sel
                edit_notes = st.text_area("Alasan edit (wajib):", height=60, key="edit_n")
                
                c1 = st.checkbox(f"✅ Saya yakin Qty {sel_e.get('qty')} → {new_qty}", key="ec1")
                c2 = st.checkbox("✅ Tidak bisa dibatalkan, audit log tercatat", key="ec2")
                c3 = st.checkbox("✅ Alasan sudah diisi", key="ec3")
                
                if st.button("🔴 SUBMIT EDIT", use_container_width=True,
                             disabled=not (c1 and c2 and c3), key="btn_edit_sbm"):
                    if not edit_by.strip(): st.error("Nama wajib!")
                    elif not edit_notes.strip(): st.error("Alasan wajib!")
                    else:
                        success, msg = edit_inventory_item(sel_e["id"], new_qty, new_price,
                                                           edit_by.strip(), edit_notes)
                        if success:
                            st.success(msg)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg)
            else:
                st.info("Tidak ada match.")
        else:
            st.info("Belum ada produk.")

# ════════════════════════════════════════════════════
#  TAB: PENGATURAN
# ════════════════════════════════════════════════════
with tab_setting:
    st.markdown("### ⚙️ Pengaturan")
    
    st.success("☁️ **Database: Google Sheets** — Data permanen, tidak hilang lagi!")
    
    pg1, pg2 = st.columns(2)
    
    with pg1:
        st.markdown("#### 👥 Pengguna")
        users_l = get_all_users()
        for u in users_l:
            st.markdown(f"- 👤 {u}")
        
        st.markdown("---")
        st.markdown("#### 🔄 Refresh Data")
        st.caption("Klik kalau ada data terbaru dari user lain.")
        if st.button("🔄  Refresh Sekarang", use_container_width=True):
            clear_cache()
            st.success("✅ Cache cleared!")
            time.sleep(0.5)
            st.rerun()
        
        st.markdown("---")
        st.markdown("#### 📦 Migrate dari Backup .db")
        st.caption("Import data dari file backup SQLite lama (.db) ke Google Sheets, lengkap dengan auto-normalisasi nama produk.")
        
        upload_db = st.file_uploader("Upload file .db lama", type=["db"], key="upload_db")
        if upload_db:
            normalize = st.checkbox("✅ Auto-normalisasi nama produk (rekomendasi)",
                                     value=True, key="norm_db")
            st.warning("⚠️ Ini akan MENGGANTI semua data Google Sheets dengan data dari .db!")
            conf_db = st.checkbox("Saya yakin", key="conf_db")
            if st.button("📤  IMPORT SEKARANG", use_container_width=True, disabled=not conf_db):
                with st.spinner("Migrating..."):
                    success, msg = import_sqlite_backup(upload_db.read(), normalize=normalize)
                if success:
                    st.success(msg)
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(msg)
    
    with pg2:
        st.markdown("#### 🧹 Tool Merge Produk")
        st.caption("Gabungkan nama produk yang typo/inkonsisten ke nama Atomy resmi. "
                   "Misal: 'hemohim', 'HEMOHIM', 'Hemohim' → semuanya jadi 'Atomy HemoHim'.")
        
        # Preview produk yang akan ter-merge
        all_inv_check = load_table("inventory")
        unique_names = sorted(set(i.get("product_name", "") for i in all_inv_check))
        
        will_merge = []
        for name in unique_names:
            normalized = normalize_product_name(name)
            if normalized != name:
                will_merge.append((name, normalized))
        
        if will_merge:
            st.info(f"📊 Ditemukan **{len(will_merge)} nama** yang bisa dinormalisasi.")
            with st.expander("Lihat preview perubahan"):
                for old, new in will_merge[:30]:
                    st.markdown(f"- `{old}` → **{new}**")
                if len(will_merge) > 30:
                    st.caption(f"... dan {len(will_merge)-30} lainnya")
            
            conf_merge = st.checkbox("✅ Saya yakin merge & rename produk", key="conf_merge")
            if st.button("🧹  JALANKAN MERGE", use_container_width=True, disabled=not conf_merge,
                         key="btn_merge"):
                with st.spinner("Merging..."):
                    merged, renamed, tx_renamed = merge_duplicate_products()
                st.success(f"✅ Selesai!\n- Merged: {merged} duplicate items\n"
                           f"- Renamed: {renamed} inventory\n- Tx renamed: {tx_renamed}")
                time.sleep(2)
                st.rerun()
        else:
            st.success("✅ Semua nama produk sudah konsisten!")
        
        st.markdown("---")
        
        # Bulk Excel Import
        st.markdown("#### 📥 Bulk Import dari Excel")
        st.caption("Upload Excel dengan kardus + produk untuk import sekaligus.")
        
        # Template
        if st.button("📋 Download Template Excel", use_container_width=True, key="btn_tpl"):
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as w:
                pd.DataFrame({
                    "nomor_pesanan": ["4521", "4522"],
                    "nomor_id": ["7789", "7790"],
                    "owner_name": ["Titipan Anita", "Milik Saya - Budi"],
                    "location": ["Rak A1", "Rak B2"],
                    "type": ["Titipan", "Milik Sendiri"],
                }).to_excel(w, sheet_name="Kardus", index=False)
                pd.DataFrame({
                    "kardus_label_or_id": ["4521-7789-Titipan Anita", "1"],
                    "product_name": ["Atomy HemoHim", "Atomy Vitamin B-Complex"],
                    "qty": [10, 5],
                    "unit_price": [350000, 150000],
                }).to_excel(w, sheet_name="Inventory", index=False)
            buf.seek(0)
            st.download_button("📥 Download", buf, file_name="GudangKu_Template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        
        upload_xlsx = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"], key="up_xlsx")
        if upload_xlsx:
            sheet_choice = st.radio("Sheet untuk diimport:", ["Kardus", "Inventory"],
                                     horizontal=True, key="sheet_imp")
            if st.button(f"✅ IMPORT '{sheet_choice}'", use_container_width=True, key="btn_imp_xlsx"):
                try:
                    df = pd.read_excel(upload_xlsx, sheet_name=sheet_choice)
                    now_str = tgl_indo()
                    inserted = 0
                    errors = []
                    
                    if sheet_choice == "Kardus":
                        kardus_to_insert = []
                        for idx, row in df.iterrows():
                            try:
                                np = str(row.get("nomor_pesanan", "")).strip()
                                ni = str(row.get("nomor_id", "")).strip()
                                ow = str(row.get("owner_name", "")).strip()
                                lc = str(row.get("location", "")).strip()
                                tp = str(row.get("type", "Milik Sendiri")).strip()
                                if not all([np, ni, ow, lc]):
                                    errors.append(f"Baris {idx+2}: data tidak lengkap")
                                    continue
                                kardus_to_insert.append({
                                    "label": f"{np}-{ni}-{ow}",
                                    "nomor_pesanan": np, "nomor_id": ni, "owner_name": ow,
                                    "location": lc, "type": tp,
                                    "created_at": now_str, "created_by": "Excel Import",
                                    "updated_at": now_str, "updated_by": "Excel Import",
                                })
                                inserted += 1
                            except Exception as e:
                                errors.append(f"Baris {idx+2}: {e}")
                        if kardus_to_insert:
                            insert_rows_batch("kardus", kardus_to_insert)
                    
                    elif sheet_choice == "Inventory":
                        kardus_data = load_table("kardus")
                        kardus_lookup = {}
                        for k in kardus_data:
                            kardus_lookup[str(k.get("id"))] = k.get("id")
                            kardus_lookup[k.get("label", "")] = k.get("id")
                        
                        inv_to_insert = []
                        for idx, row in df.iterrows():
                            try:
                                kref = str(row.get("kardus_label_or_id", "")).strip()
                                pname = str(row.get("product_name", "")).strip()
                                qty = int(row.get("qty", 0) or 0)
                                price = float(row.get("unit_price", 0) or 0)
                                
                                if kref not in kardus_lookup:
                                    errors.append(f"Baris {idx+2}: kardus '{kref}' tidak ada")
                                    continue
                                if not pname or qty <= 0:
                                    errors.append(f"Baris {idx+2}: produk/qty invalid")
                                    continue
                                
                                # Normalize nama
                                pname = normalize_product_name(pname)
                                
                                inv_to_insert.append({
                                    "kardus_id": kardus_lookup[kref],
                                    "product_name": pname,
                                    "qty": qty, "unit_price": price,
                                    "added_at": now_str, "added_by": "Excel Import",
                                })
                                inserted += 1
                            except Exception as e:
                                errors.append(f"Baris {idx+2}: {e}")
                        if inv_to_insert:
                            insert_rows_batch("inventory", inv_to_insert)
                    
                    msg = f"✅ {inserted} baris berhasil"
                    if errors:
                        msg += f"\n⚠️ {len(errors)} error:\n" + "\n".join(errors[:5])
                    st.success(msg)
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    st.markdown("---")
    st.markdown("### 🚀 Setup Google Sheets (Sekali Saja)")
    with st.expander("📖 Panduan Setup Google Sheets"):
        st.markdown("""
**Sudah jalan? Berarti setup sudah benar! Tutup panduan ini.**

**Belum setup? Ikuti langkah ini:**

### 1. Buat Google Sheets (1 menit)
- Buka [sheets.google.com](https://sheets.google.com)
- Buat spreadsheet baru, beri nama **GudangKu Database**
- Copy URL-nya (di address bar browser)

### 2. Setup Google Cloud (5 menit)
- Buka [console.cloud.google.com](https://console.cloud.google.com)
- **Create New Project** → nama: `gudangku`
- Menu **APIs & Services** → **Library**:
  - Search **Google Sheets API** → klik **Enable**
  - Search **Google Drive API** → klik **Enable**
- Menu **APIs & Services** → **Credentials**
- Klik **+ Create Credentials** → **Service Account**
  - Name: `gudangku-bot` → Create → Done
- Klik service account yang baru dibuat → tab **Keys**
  - **Add Key** → **Create New Key** → JSON → Create
  - File JSON otomatis terdownload

### 3. Share Spreadsheet ke Service Account
- Buka file JSON, cari email seperti `gudangku-bot@xxx.iam.gserviceaccount.com`
- Buka Google Sheets `GudangKu Database`
- Klik **Share** → paste email service account → **Editor** → Send

### 4. Upload Credentials ke Streamlit
- Buka [share.streamlit.io](https://share.streamlit.io)
- Klik aplikasimu → **Settings** → **Secrets**
- Paste isi seperti ini:

```toml
spreadsheet_url = "URL_GOOGLE_SHEETS_DI_SINI"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"
client_email = "gudangku-bot@...iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

(Copy isinya dari file JSON yang didownload tadi)

- Klik **Save**
- Aplikasi auto-restart

### 5. Selesai!
Aplikasimu sekarang pakai Google Sheets sebagai database. Data permanen!
""")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#888; font-size:14px; padding:10px;">
📦 <b>GudangKu v2.0 Atomy</b> | Database: Google Sheets ☁️ | Dibuat dengan Streamlit
</div>
""", unsafe_allow_html=True)
