"""
fetch_jadwal.py
Dijalankan oleh GitHub Actions untuk download file jadwal dari SharePoint
dan menyimpannya sebagai CSV bersih di data/jadwal.csv
"""

import os
import sys
import io
import requests
import pandas as pd
from datetime import datetime, timezone

# ── URL dari environment variable (disimpan di GitHub Secrets) ──────────────
SHAREPOINT_URL = os.environ.get("SHAREPOINT_URL", "").strip()

if not SHAREPOINT_URL:
    print("ERROR: SHAREPOINT_URL tidak diset di GitHub Secrets")
    sys.exit(1)

# Tambah &download=1 kalau belum ada
if "download=1" not in SHAREPOINT_URL:
    SHAREPOINT_URL += ("&" if "?" in SHAREPOINT_URL else "?") + "download=1"

print(f"Fetching: {SHAREPOINT_URL[:80]}...")

# ── Download ─────────────────────────────────────────────────────────────────
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "application/octet-stream,*/*;q=0.8",
    "Accept-Encoding": "identity",
}

try:
    resp = requests.get(SHAREPOINT_URL, headers=headers, timeout=30, allow_redirects=True)
except Exception as ex:
    print(f"ERROR: Download gagal — {ex}")
    sys.exit(1)

print(f"Status: {resp.status_code} | Size: {len(resp.content)} B | CT: {resp.headers.get('Content-Type','')[:60]}")

if resp.status_code != 200:
    print(f"ERROR: HTTP {resp.status_code}")
    print("Body:", resp.content[:200].decode(errors="replace"))
    sys.exit(1)


# ── Parse ────────────────────────────────────────────────────────────────────
def normalize_nim(value) -> str:
    s = str(value).strip()
    if s.upper() in {"NAN", "NONE", ""}:
        return ""
    try:
        s = str(int(float(s)))
    except (ValueError, OverflowError):
        pass
    if s.endswith(".0") and s[:-2].isdigit():
        s = s[:-2]
    return s.upper()


def parse_content(content_bytes: bytes) -> pd.DataFrame:
    # Strategy 1: XLSX
    if content_bytes[:4] == b"PK\x03\x04":
        print("Format: XLSX")
        df = pd.read_excel(io.BytesIO(content_bytes), skiprows=12, dtype=str)
        return df

    # Strategy 2-4: CSV semicolon, python engine
    for enc in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            text = content_bytes.decode(enc, errors="replace")
            df = pd.read_csv(
                io.StringIO(text),
                sep=";",
                skiprows=12,
                dtype=str,
                on_bad_lines="skip",
                engine="python",
            )
            if "Tanggal" in df.columns and len(df) > 0:
                print(f"Format: CSV ({enc})")
                return df
        except Exception as ex:
            print(f"  {enc} failed: {ex}")

    raise ValueError("Tidak bisa parse file — bukan CSV atau XLSX yang valid")


df = parse_content(resp.content)
print(f"Parsed: {df.shape[0]} rows, {df.shape[1]} cols")

# ── Bersihkan ────────────────────────────────────────────────────────────────
df.columns = df.columns.str.strip()

# Buang baris kosong
df = df[df["Tanggal"].notna()].copy()
df = df[df["Tanggal"].astype(str).str.strip() != ""].copy()
df = df[~df["Tanggal"].astype(str).str.strip().str.startswith("#")].copy()

df["Tanggal"] = df["Tanggal"].astype(str).str.strip()
df["Jam"]     = df["Jam"].astype(str).str.strip()

# Normalise NIM
for i in ["1", "2", "3"]:
    col = f"NIM (Pengawas {i})"
    if col in df.columns:
        df[col] = df[col].apply(normalize_nim)
    else:
        df[col] = ""

# Nama: bersihkan nan/None
for i in ["1", "2", "3"]:
    col = f"Nama Lengkap (Pengawas {i})"
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip().replace({"nan": "", "None": "", "NaN": ""})
    else:
        df[col] = ""

# Buang kolom Unnamed
df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

print(f"After clean: {df.shape[0]} rows")

# ── Simpan ───────────────────────────────────────────────────────────────────
os.makedirs("data", exist_ok=True)

output_path = "data/jadwal.csv"
df.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"Saved: {output_path}")

# Simpan timestamp terakhir update
ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
with open("data/last_updated.txt", "w") as f:
    f.write(ts)
print(f"Timestamp: {ts}")

print("✓ Selesai")
