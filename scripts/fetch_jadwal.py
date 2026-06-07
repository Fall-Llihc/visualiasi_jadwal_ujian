"""
fetch_jadwal.py
Dijalankan oleh GitHub Actions untuk download file jadwal dari SharePoint
dan menyimpannya sebagai CSV bersih di data/jadwal.csv

Robust terhadap perubahan layout sumber: header row dideteksi otomatis
dengan mencari sel berisi "Tanggal" (case-insensitive). Layout SharePoint
sebelumnya pakai banner 12 baris di atas header, tapi struktur ini bisa
berubah kapan saja — auto-detect mencegah CI gagal saat itu terjadi.
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
DOWNLOAD_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "application/octet-stream,*/*;q=0.8",
    "Accept-Encoding": "identity",
}

try:
    resp = requests.get(SHAREPOINT_URL, headers=DOWNLOAD_HEADERS, timeout=30, allow_redirects=True)
except Exception as ex:
    print(f"ERROR: Download gagal — {ex}")
    sys.exit(1)

print(
    f"Status: {resp.status_code} | "
    f"Size: {len(resp.content)} B | "
    f"CT: {resp.headers.get('Content-Type','')[:60]}"
)

if resp.status_code != 200:
    print(f"ERROR: HTTP {resp.status_code}")
    print("Body:", resp.content[:200].decode(errors="replace"))
    sys.exit(1)


# ── Helpers ──────────────────────────────────────────────────────────────────
EXPECTED_HEADER_TOKENS = ("tanggal", "jam")
MAX_HEADER_SCAN_ROWS   = 50  # cukup untuk sumber yg sebenarnya (banner historis 12 baris)


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


def _row_is_header(row_values) -> bool:
    """True kalau baris ini berisi minimal 'Tanggal' DAN 'Jam' (case-insensitive)."""
    flat = " | ".join(str(v).strip().lower() for v in row_values if v is not None)
    return all(tok in flat for tok in EXPECTED_HEADER_TOKENS)


def _detect_header_row(df_no_header: pd.DataFrame) -> int | None:
    """Cari index baris yang punya kolom 'Tanggal' & 'Jam'. Return index atau None."""
    limit = min(len(df_no_header), MAX_HEADER_SCAN_ROWS)
    for i in range(limit):
        if _row_is_header(df_no_header.iloc[i].tolist()):
            return i
    return None


def _read_xlsx_smart(content_bytes: bytes) -> pd.DataFrame:
    """Baca XLSX dengan auto-detect header row. Coba semua sheet bila perlu."""
    bio = io.BytesIO(content_bytes)
    xl  = pd.ExcelFile(bio, engine="openpyxl")
    print(f"  XLSX sheets: {xl.sheet_names}")

    for sheet in xl.sheet_names:
        # Baca tanpa header dulu untuk detect baris header
        try:
            raw = pd.read_excel(
                io.BytesIO(content_bytes), sheet_name=sheet,
                header=None, dtype=str, engine="openpyxl",
            )
        except Exception as ex:
            print(f"  WARN: gagal baca sheet '{sheet}' — {ex}")
            continue

        hdr = _detect_header_row(raw)
        if hdr is None:
            print(f"  Sheet '{sheet}': header 'Tanggal'+'Jam' tidak ditemukan dalam {MAX_HEADER_SCAN_ROWS} baris pertama")
            continue

        print(f"  Sheet '{sheet}': header terdeteksi di baris {hdr + 1} (0-idx {hdr})")
        df = pd.read_excel(
            io.BytesIO(content_bytes), sheet_name=sheet,
            header=hdr, dtype=str, engine="openpyxl",
        )
        # Buang kolom yang nama-nya NaN / 'Unnamed:' setelah header dipasang
        df.columns = [str(c).strip() for c in df.columns]
        df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
        df = df.loc[:, df.columns != ""]
        return df

    # Fallback terakhir: pakai skiprows=12 (perilaku lama) dengan harapan kompatibilitas
    print("  WARN: auto-detect gagal di semua sheet, fallback ke skiprows=12")
    return pd.read_excel(io.BytesIO(content_bytes), skiprows=12, dtype=str, engine="openpyxl")


def _read_csv_smart(content_bytes: bytes) -> pd.DataFrame | None:
    """Baca CSV dengan auto-detect header row. Coba beberapa encoding & separator."""
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            text = content_bytes.decode(enc, errors="replace")
        except Exception:
            continue

        for sep in (";", ",", "\t"):
            try:
                raw = pd.read_csv(
                    io.StringIO(text), sep=sep, header=None, dtype=str,
                    engine="python", on_bad_lines="skip",
                )
            except Exception:
                continue
            if raw.empty or raw.shape[1] < 3:
                continue

            hdr = _detect_header_row(raw)
            if hdr is None:
                continue
            print(f"  CSV: encoding={enc} sep='{sep}' header di baris {hdr + 1} (0-idx {hdr})")
            df = pd.read_csv(
                io.StringIO(text), sep=sep, skiprows=hdr, dtype=str,
                engine="python", on_bad_lines="skip",
            )
            df.columns = [str(c).strip() for c in df.columns]
            df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
            df = df.loc[:, df.columns != ""]
            return df
    return None


def parse_content(content_bytes: bytes) -> pd.DataFrame:
    if content_bytes[:4] == b"PK\x03\x04":
        print("Format: XLSX (auto-detect header)")
        df = _read_xlsx_smart(content_bytes)
    else:
        print("Format: CSV (auto-detect header)")
        df = _read_csv_smart(content_bytes)
        if df is None:
            raise ValueError("Tidak bisa parse — bukan XLSX/CSV yang valid")

    # Canonicalize: "Tanggal Ujian" / "Tgl" / "Tanggal " → "Tanggal"; idem "Jam".
    def _canonical(df_, expected, prefixes):
        if expected in df_.columns:
            return df_
        for col in list(df_.columns):
            cl = str(col).strip().lower()
            if any(cl.startswith(p) for p in prefixes):
                print(f"  Rename kolom '{col}' → '{expected}'")
                return df_.rename(columns={col: expected})
        return df_

    df = _canonical(df, "Tanggal", ("tanggal", "tgl"))
    df = _canonical(df, "Jam",     ("jam", "waktu"))
    return df


# ── Parse ────────────────────────────────────────────────────────────────────
df = parse_content(resp.content)
print(f"Parsed: {df.shape[0]} rows, {df.shape[1]} cols")
print(f"Columns: {list(df.columns)[:8]}{' …' if df.shape[1] > 8 else ''}")

if "Tanggal" not in df.columns:
    print("\nERROR: Kolom 'Tanggal' tidak ada di hasil parse.")
    print("First 5 rows of parsed data (untuk debug):")
    print(df.head().to_string(max_cols=10))
    sys.exit(1)


# ── Bersihkan ────────────────────────────────────────────────────────────────
df.columns = df.columns.str.strip()

# Buang baris kosong / komentar
df = df[df["Tanggal"].notna()].copy()
df = df[df["Tanggal"].astype(str).str.strip() != ""].copy()
df = df[~df["Tanggal"].astype(str).str.strip().str.startswith("#")].copy()

df["Tanggal"] = df["Tanggal"].astype(str).str.strip()
if "Jam" in df.columns:
    df["Jam"] = df["Jam"].astype(str).str.strip()

# Normalise NIM
for i in ("1", "2", "3"):
    col = f"NIM (Pengawas {i})"
    if col in df.columns:
        df[col] = df[col].apply(normalize_nim)
    else:
        df[col] = ""

# Nama: bersihkan nan/None
for i in ("1", "2", "3"):
    col = f"Nama Lengkap (Pengawas {i})"
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip().replace({"nan": "", "None": "", "NaN": ""})
    else:
        df[col] = ""

# Buang kolom Unnamed yang masih lolos
df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

print(f"After clean: {df.shape[0]} rows × {df.shape[1]} cols")


# ── Simpan ───────────────────────────────────────────────────────────────────
os.makedirs("data", exist_ok=True)
output_path = "data/jadwal.csv"
df.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"Saved: {output_path}")

# Simpan timestamp terakhir update (jadi fallback bila git log gagal di
# generate_data_js.py)
ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
with open("data/last_updated.txt", "w") as f:
    f.write(ts)
print(f"Timestamp: {ts}")

print("✓ Selesai")
