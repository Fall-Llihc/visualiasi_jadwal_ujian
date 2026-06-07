import streamlit as st
import pandas as pd
import html as html_lib
import io
import requests
import time
import json
from datetime import datetime, timezone, timedelta

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ProctorView – Jadwal Pengawas UAS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');

html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
[data-testid="stAppViewContainer"]{background:#0B0D1A;}
[data-testid="stSidebar"]{background:#0F1120!important;border-right:1px solid #1C2040;}
[data-testid="stHeader"]{background:transparent;}
section[data-testid="stSidebar"]>div{padding-top:1.5rem;}
h1,h2,h3,h4{font-family:'Syne',sans-serif!important;color:#E8ECF8;}

.stTextInput>div>div>input{background:#12152A!important;border:1.5px solid #1C2040!important;border-radius:10px!important;color:#E8ECF8!important;font-family:'DM Sans',sans-serif!important;font-size:13px!important;}
.stTextInput>div>div>input:focus{border-color:#4F6EF7!important;box-shadow:0 0 0 3px rgba(79,110,247,.15)!important;}
.stButton>button{background:linear-gradient(135deg,#4F6EF7,#7C5CFC)!important;color:#fff!important;border:none!important;border-radius:10px!important;font-family:'Syne',sans-serif!important;font-weight:700!important;letter-spacing:.04em!important;}
.stButton>button:hover{opacity:.82!important;}

.slabel{font-family:'Syne',sans-serif;font-size:10px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#3D4A7A;margin:20px 0 6px;}
hr{border-color:#1C2040!important;}

.mcard{background:#12152A;border:1px solid #1C2040;border-radius:14px;padding:18px 16px;text-align:center;}
.mnum{font-family:'Syne',sans-serif;font-size:2.2rem;font-weight:800;line-height:1;background:linear-gradient(135deg,#4F6EF7,#A78BFA);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.mnum-red{background:linear-gradient(135deg,#E63946,#FF6B6B)!important;-webkit-background-clip:text!important;-webkit-text-fill-color:transparent!important;}
.mlbl{font-size:11px;color:#3D4A7A;margin-top:5px;}

.sec-h{font-family:'Syne',sans-serif;font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#4F6EF7;border-left:3px solid #4F6EF7;padding-left:10px;margin:28px 0 14px;}
.cbanner{background:linear-gradient(135deg,#1E0A0A,#2C0F0F);border:1px solid #E63946;border-radius:12px;padding:16px 20px;margin-bottom:12px;}
.ctitle{font-family:'Syne',sans-serif;font-size:14px;font-weight:700;color:#E63946;margin-bottom:8px;}
.citem{font-size:12px;color:#FFB3B3;margin:3px 0;line-height:1.5;}

.hero{background:linear-gradient(135deg,#12152A 0%,#181D3A 100%);border:1px solid #1C2040;border-radius:18px;padding:26px 30px;margin-bottom:22px;}
.hero-label{font-size:11px;color:#3D4A7A;letter-spacing:.12em;text-transform:uppercase;}
.hero-name{font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:800;color:#E8ECF8;margin:4px 0 8px;}
.nim-pill{background:#4F6EF7;color:#fff;border-radius:20px;padding:3px 14px;font-size:11px;font-weight:700;display:inline-block;}
.conf-pill{background:#E63946;color:#fff;border-radius:20px;padding:3px 12px;font-size:11px;font-weight:700;display:inline-block;margin-left:8px;}
.role-pill{color:#fff;border-radius:20px;padding:3px 12px;font-size:11px;font-weight:700;display:inline-block;margin-left:8px;}

.lcard{background:#12152A;border:1px solid #1C2040;border-left:4px solid var(--ac,#4F6EF7);border-radius:11px;padding:13px 16px 14px;margin-bottom:9px;position:relative;}
.lcard-title{font-family:'Syne',sans-serif;font-size:13px;font-weight:700;color:#E8ECF8;}
.lcard-meta{font-size:11px;color:#3D4A7A;margin-top:6px;}
.badge{display:inline-block;background:#1C2040;color:#A78BFA;border-radius:5px;padding:2px 7px;font-size:10px;font-weight:600;margin-right:5px;margin-top:3px;}
.ext-lcard{background:#0E1A18;border:1px solid #1A3530;border-left:4px solid #2A9D8F;border-radius:11px;padding:13px 16px;margin-bottom:9px;}

.rt-status{position:fixed;bottom:18px;left:18px;z-index:9999;background:#0F1120;border:1px solid #1C2040;border-radius:10px;padding:8px 14px;display:flex;align-items:center;gap:8px;font-size:11px;color:#5B6A9A;box-shadow:0 4px 20px rgba(0,0,0,.5);max-width:340px;pointer-events:none;}
.rt-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0;animation:pulse 1.8s ease-in-out infinite;}
.rt-dot.green{background:#2A9D8F;}.rt-dot.blue{background:#4F6EF7;}.rt-dot.red{background:#E63946;animation:none;}.rt-dot.yellow{background:#F4A261;}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1);}50%{opacity:.4;transform:scale(.75);}}
.rt-text{font-family:'DM Sans',sans-serif;line-height:1.3;}.rt-text b{color:#E8ECF8;font-weight:600;}

/* Calendar */
.cal-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch;margin-bottom:32px;}
.cal-table{border-collapse:separate;border-spacing:5px;width:100%;table-layout:fixed;}
.th-corner{width:145px;background:transparent;border:none;}
.td-time{width:145px;background:transparent;border:none;vertical-align:middle;padding:6px 10px 6px 0;text-align:right;}
.td-time span{font-family:'Syne',sans-serif;font-size:10px;font-weight:700;color:#3D4A7A;letter-spacing:.06em;white-space:nowrap;}
.th-day{background:#12152A;border:1px solid #1C2040;border-radius:10px;padding:12px 10px;text-align:center;vertical-align:middle;}
.th-day-name{font-family:'Syne',sans-serif;font-size:13px;font-weight:700;color:#E8ECF8;}
.th-day-date{font-size:10px;color:#3D4A7A;margin-top:3px;}
.td-empty{background:#0D0F1C;border:1px solid #141726;border-radius:10px;min-height:90px;}
.td-fill{vertical-align:top;background:transparent;border:none;padding:0;}

.c-exam{border-radius:10px;border-left:4px solid var(--ac,#4F6EF7);background:var(--bg,#0E1228);padding:10px 11px 28px 12px;margin-bottom:5px;box-sizing:border-box;position:relative;overflow:hidden;min-height:100px;}
.c-exam.conflict{outline:2px solid #E63946;}
.c-exam-mk{font-family:'Syne',sans-serif;font-size:11.5px;font-weight:700;color:#E8ECF8;line-height:1.35;margin-bottom:6px;}
.c-exam-room{font-size:10px;color:#8B9AC8;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.c-exam-kls{font-size:9.5px;color:#5B6A9A;}
.c-exam-type{font-size:9px;color:#3D4A7A;font-style:italic;margin-top:4px;}
.c-conf-tag{position:absolute;top:7px;right:7px;background:#E63946;color:#fff;border-radius:4px;padding:1px 5px;font-size:8.5px;font-weight:700;white-space:nowrap;}
.c-role-tag{position:absolute;bottom:7px;left:12px;border-radius:4px;padding:1px 6px;font-size:8px;font-weight:700;letter-spacing:.04em;white-space:nowrap;}
.c-role-1{background:#1C3060;color:#7BA7FF;}.c-role-2{background:#1C2A40;color:#A78BFA;}

.c-ext{border-radius:10px;border:2px dashed #2A9D8F;border-left:4px solid #2A9D8F;background:#0A1714;padding:10px 11px 10px 12px;margin-bottom:5px;box-sizing:border-box;position:relative;min-height:80px;}
.c-ext.conflict{border-color:#E63946;}
.c-ext-title{font-family:'Syne',sans-serif;font-size:11px;font-weight:700;color:#C8FAF0;line-height:1.35;margin-bottom:5px;}
.c-ext-time{font-size:10px;color:#2A9D8F;}

.legend-row{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:18px;align-items:center;}
.legend-dot{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:5px;flex-shrink:0;}
.legend-item{font-size:11px;color:#5B6A9A;display:flex;align-items:center;}

/* Cookie guide box */
.cookie-guide{background:#0E1220;border:1px solid #2A3060;border-radius:10px;padding:12px 14px;font-size:11px;color:#5B6A9A;margin:8px 0;}
.cookie-guide b{color:#E8ECF8;}
.cookie-guide code{background:#1C2040;color:#4F6EF7;border-radius:4px;padding:1px 5px;font-size:10px;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
# Urutan hari: Senin=0 … Minggu=6
DAY_ORDER = {'senin':0,'selasa':1,'rabu':2,'kamis':3,'jumat':4,'sabtu':5,'minggu':6}

TIME_SLOTS = [
    '08.00 - 10.15 WIB',
    '10.45 - 13.00 WIB',
    '14.00 - 16.15 WIB',
    '16.00 - 18.00 WIB',
    '18.30 - 20.30 WIB',
]

TIME_RANGES = {
    '08.00 - 10.15 WIB': (8.00,  10.25),
    '10.45 - 13.00 WIB': (10.75, 13.00),
    '14.00 - 16.15 WIB': (14.00, 16.25),
    '16.00 - 18.00 WIB': (16.00, 18.00),
    '18.30 - 20.30 WIB': (18.50, 20.50),
}

SLOT_STYLE = {
    '08.00 - 10.15 WIB': ('#4A9FFF', '#0E1228'),
    '10.45 - 13.00 WIB': ('#FF8C3D', '#1A1208'),
    '14.00 - 16.15 WIB': ('#FFB81D', '#1A1808'),
    '16.00 - 18.00 WIB': ('#2A9D8F', '#0B1A18'),
    '18.30 - 20.30 WIB': ('#E63946', '#1A080A'),
}
DEFAULT_STYLE = ('#4F6EF7', '#0E1228')
EXT_COLOR     = '#2A9D8F'

# URL public SharePoint (Anyone with the link, no login needed)
SHAREPOINT_URL = (
    "https://telkomuniversityofficial-my.sharepoint.com/:x:/g/personal/"
    "informaticslab_telkomuniversity_ac_id/"
    "IQDW93EEnbLMRJk2doiuFr_sAQYxTOFEXJm_Jf5cfIhhHWk?e=Zh4B0W&download=1"
)

# Raw GitHub URL — Streamlit baca dari sini (setelah GitHub Actions sync)
GITHUB_REPO   = "Fall-Llihc/visualiasi_jadwal_ujian"
RAW_DATA_URL  = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/data/jadwal.csv"
RAW_TS_URL    = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/data/last_updated.txt"
GITHUB_API_DISPATCH = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/sync_jadwal.yml/dispatches"

# Admin password — simpan di Streamlit Secrets sebagai ADMIN_PASSWORD
# Default fallback hanya untuk development
ADMIN_PASSWORD_KEY = "ADMIN_PASSWORD"

# Interval default (menit) — bisa diubah admin di runtime
DEFAULT_INTERVAL_MIN = 60


# ─────────────────────────────────────────────────────────────────────────────
# PURE HELPERS  (no Streamlit calls)
# ─────────────────────────────────────────────────────────────────────────────
def e(s):
    return html_lib.escape(str(s))

def day_rank(d: str) -> int:
    """'Senin, 22 Juni 2026' → 0  |  'Selasa, …' → 1  |  unknown → 99"""
    d = str(d).strip().lower()
    for k, v in DAY_ORDER.items():
        if d.startswith(k):
            return v
    return 99

def time_rank(t: str) -> int:
    t = str(t).strip()
    return TIME_SLOTS.index(t) if t in TIME_SLOTS else 99

def normalize_nim(value) -> str:
    s = str(value).strip()
    if s.startswith("`"):
        s = s.lstrip("`").strip()
    if s.upper() in {"NAN", "NONE", ""}:
        return ""
    # Handles float representation: '1.030523e+11' → '103052300000'
    try:
        s = str(int(float(s)))
    except (ValueError, OverflowError):
        pass
    if s.endswith(".0") and s[:-2].isdigit():
        s = s[:-2]
    return s.upper()

def parse_ext_time(t: str):
    try:
        h, m = map(int, t.split(':'))
        return h + m / 60
    except Exception:
        return None

def overlaps(s1, e1, s2, e2) -> bool:
    return s1 < e2 and s2 < e1


# ─────────────────────────────────────────────────────────────────────────────
# DATA — download + parse
# ─────────────────────────────────────────────────────────────────────────────
def _robust_parse(content_bytes: bytes):
    """
    Coba parse bytes dari SharePoint ke DataFrame.
    Urutan: XLSX magic → CSV python-engine utf-8-sig → utf-8 → latin-1 → strip-nulls.
    Selalu pakai python engine (kebal buffer-overflow C engine).
    """
    # Strategy 1 — XLSX (magic PK)
    if content_bytes[:4] == b'PK\x03\x04':
        try:
            df = pd.read_excel(io.BytesIO(content_bytes), skiprows=12, dtype=str)
            if "Tanggal" in df.columns and len(df) > 0:
                return df, None
        except Exception:
            pass

    # Strategy 2-4 — CSV semicolon, python engine
    last_err = "unknown"
    for enc, data in [
        ("utf-8-sig", content_bytes),
        ("utf-8",     content_bytes),
        ("latin-1",   content_bytes),
        ("utf-8",     content_bytes.replace(b"\x00", b"")),
    ]:
        try:
            text = data.decode(enc, errors="replace")
            df = pd.read_csv(
                io.StringIO(text),
                sep=";",
                skiprows=12,
                dtype=str,
                on_bad_lines="skip",
                engine="python",    # ← kebal buffer overflow
            )
            if "Tanggal" in df.columns and len(df) > 0:
                return df, None
        except Exception as ex:
            last_err = str(ex)

    return None, f"Semua strategi parse gagal. Error terakhir: {last_err}"


def _process_df(df: pd.DataFrame):
    """Normalise raw DataFrame dari SharePoint."""
    df = df.copy()
    df.columns = df.columns.str.strip()

    # Buang baris kosong / header duplikat
    df = df[df["Tanggal"].notna()].copy()
    df = df[df["Tanggal"].astype(str).str.strip() != ""].copy()
    df = df[~df["Tanggal"].astype(str).str.strip().str.startswith("#")].copy()

    df["Tanggal"] = df["Tanggal"].astype(str).str.strip()
    df["Jam"]     = df["Jam"].astype(str).str.strip()

    # NIM: normalise semua kolom
    for i in ["1", "2", "3"]:
        col = f"NIM (Pengawas {i})"
        df[col] = df[col].apply(normalize_nim) if col in df.columns else ""

    # Nama: strip whitespace, ganti 'nan'/'None' dengan ''
    for i in ["1", "2", "3"]:
        col = f"Nama Lengkap (Pengawas {i})"
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({"nan": "", "None": "", "NaN": ""})
        else:
            df[col] = ""

    # ROW label (1st/2nd untuk kelas yang dibagi 2 ruangan)
    from collections import Counter
    gcols = [c for c in ["Kode MK", "Kelas", "Tanggal", "Jam"] if c in df.columns]
    if len(gcols) == 4:
        keys  = [tuple(str(r[c]) for c in gcols) for _, r in df.iterrows()]
        cnt   = Counter(keys)
        seen  = {}
        lbl   = []
        for k in keys:
            if cnt[k] == 1:
                lbl.append("-")
            else:
                seen[k] = seen.get(k, 0) + 1
                lbl.append("1st" if seen[k] == 1 else "2nd")
        df["ROW"] = lbl
    else:
        df["ROW"] = "-"

    return df, None


@st.cache_data(ttl=60, show_spinner=False)
def _load_from_github(_dummy: int = 0):
    """
    Baca jadwal.csv dari raw GitHub (hasil sync GitHub Actions).
    Ini sumber utama — cepat, tidak kena IP restriction.
    """
    try:
        r = requests.get(RAW_DATA_URL, timeout=15,
                         headers={"Cache-Control": "no-cache"})
        if r.status_code == 404:
            return None, "File data/jadwal.csv belum ada di repo — jalankan GitHub Actions dulu."
        if r.status_code != 200:
            return None, f"GitHub raw: HTTP {r.status_code}"
        if len(r.content) < 100:
            return None, "File CSV kosong di GitHub."

        df = pd.read_csv(io.StringIO(r.content.decode("utf-8-sig", errors="replace")),
                         dtype=str, engine="python", on_bad_lines="skip")
        if "Tanggal" not in df.columns:
            return None, "Kolom Tanggal tidak ditemukan di CSV GitHub."
        return df, None
    except Exception as ex:
        return None, f"Gagal baca dari GitHub: {ex}"


@st.cache_data(ttl=60, show_spinner=False)
def _get_last_updated(_dummy: int = 0) -> str:
    """Baca timestamp terakhir sync dari GitHub."""
    try:
        r = requests.get(RAW_TS_URL, timeout=10,
                         headers={"Cache-Control": "no-cache"})
        if r.status_code == 200:
            return r.text.strip()
    except Exception:
        pass
    return "Belum diketahui"


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_from_sharepoint(_dummy: int = 0):
    """
    Fallback: download langsung dari SharePoint public link.
    Dipakai kalau GitHub belum punya data atau IP tidak diblokir.
    """
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
    except requests.exceptions.Timeout:
        return None, "Timeout (>30s)."
    except requests.exceptions.ConnectionError as ex:
        return None, f"Koneksi gagal: {ex}"

    ct  = resp.headers.get("Content-Type", "")
    sz  = len(resp.content)
    dbg = f"HTTP {resp.status_code} · {sz} B"

    if resp.status_code == 403:
        body = resp.content.decode(errors="replace")
        if "allowlist" in body.lower():
            return None, "403 IP diblokir SharePoint tenant."
        return None, f"403 Forbidden. {dbg}"
    if resp.status_code != 200:
        return None, f"HTTP {resp.status_code}. {dbg}"
    if "html" in ct.lower():
        return None, f"SharePoint mengembalikan HTML. {dbg}"
    if sz < 500:
        return None, f"Response terlalu kecil ({sz} B)."

    df, err = _robust_parse(resp.content)
    if err:
        return None, err
    return _process_df(df)


def trigger_github_actions(gh_token: str) -> tuple[bool, str]:
    """
    Trigger GitHub Actions workflow_dispatch via API.
    Butuh GitHub Personal Access Token (PAT) dengan scope: actions:write
    """
    if not gh_token.strip():
        return False, "GitHub Token tidak diset."
    try:
        r = requests.post(
            GITHUB_API_DISPATCH,
            headers={
                "Authorization": f"Bearer {gh_token.strip()}",
                "Accept":        "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            json={"ref": "main", "inputs": {"reason": "Manual trigger dari admin ProctorView"}},
            timeout=15,
        )
        if r.status_code == 204:
            return True, "✅ GitHub Actions berhasil di-trigger! Tunggu ~30 detik lalu klik Refresh."
        return False, f"GitHub API: HTTP {r.status_code} — {r.text[:200]}"
    except Exception as ex:
        return False, f"Gagal trigger: {ex}"


# ─────────────────────────────────────────────────────────────────────────────
# SEARCH
# ─────────────────────────────────────────────────────────────────────────────
def search_nim(df: pd.DataFrame, nim: str) -> pd.DataFrame:
    nim = normalize_nim(nim)
    mask = pd.Series([False] * len(df), index=df.index)
    for i in ["1", "2", "3"]:
        col = f"NIM (Pengawas {i})"
        if col in df.columns:
            mask = mask | (df[col] == nim)
    r = df[mask].copy()
    r["_day"]  = r["Tanggal"].apply(day_rank)
    r["_time"] = r["Jam"].apply(time_rank)
    return r.sort_values(["_day", "_time"]).reset_index(drop=True)


def get_name_role(row, nim: str):
    nim = normalize_nim(nim)
    for i in ["1", "2", "3"]:
        if normalize_nim(row.get(f"NIM (Pengawas {i})", "")) == nim:
            raw = str(row.get(f"Nama Lengkap (Pengawas {i})", "") or "").strip()
            name = raw if raw and raw.lower() not in ("nan", "none", "-", "") else "-"
            return name, f"Pengawas {i}"
    return "-", "-"


# ─────────────────────────────────────────────────────────────────────────────
# CONFLICT DETECTION
# ─────────────────────────────────────────────────────────────────────────────
def detect_conflicts(sched, ext_agendas):
    out = []
    for _, row in sched.iterrows():
        slot = str(row["Jam"]).strip()
        if slot not in TIME_RANGES:
            continue
        ss, se = TIME_RANGES[slot]
        day = str(row["Tanggal"]).strip()
        for ea in ext_agendas:
            if ea["day"] != day:
                continue
            if overlaps(ss, se, ea["start_h"], ea["end_h"]):
                out.append({
                    "day":          day,
                    "exam_slot":    slot,
                    "exam_subject": str(row.get("Nama MK", "") or "").strip(),
                    "exam_room":    str(row.get("Ruangan", "") or "").strip(),
                    "ext_title":    ea["title"],
                    "ext_time":     f"{ea['start']} – {ea['end']}",
                })
    return out


def ext_to_slot(ea):
    best, bdiff = None, 999
    for s, (start, _) in TIME_RANGES.items():
        diff = abs(start - ea["start_h"])
        if diff < bdiff:
            bdiff, best = diff, s
    return best


# ─────────────────────────────────────────────────────────────────────────────
# CALENDAR HTML
# ─────────────────────────────────────────────────────────────────────────────
def build_calendar(sched, ext_agendas, conflicts, nim):
    ck_exam = {(c["day"], c["exam_slot"]) for c in conflicts}
    ck_ext  = {(c["day"], c["ext_title"]) for c in conflicts}

    # Sort hari: Senin → Jumat
    dates = sorted({str(d).strip() for d in sched["Tanggal"].unique()}, key=day_rank)

    # Hanya slot yang benar-benar dipakai
    used = {str(j).strip() for j in sched["Jam"]}
    for ea in ext_agendas:
        s = ext_to_slot(ea)
        if s:
            used.add(s)
    slots = [s for s in TIME_SLOTS if s in used] or TIME_SLOTS[:]

    # Lookup dicts
    exam_lk = {}
    for _, row in sched.iterrows():
        k = (str(row["Tanggal"]).strip(), str(row["Jam"]).strip())
        exam_lk.setdefault(k, []).append(row)

    ext_lk = {}
    for ea in ext_agendas:
        s = ext_to_slot(ea)
        if s:
            ext_lk.setdefault((str(ea["day"]).strip(), s), []).append(ea)

    out = ['<div class="cal-wrap"><table class="cal-table">']

    # Header — Senin/Selasa/… + tanggal
    out.append("<thead><tr><th class='th-corner'></th>")
    for date in dates:
        parts    = date.split(",", 1)
        day_name = parts[0].strip()
        date_str = parts[1].strip() if len(parts) > 1 else ""
        out.append(
            f'<th class="th-day">'
            f'<div class="th-day-name">{e(day_name)}</div>'
            f'<div class="th-day-date">{e(date_str)}</div>'
            f'</th>'
        )
    out.append("</tr></thead><tbody>")

    for slot in slots:
        accent, bg = SLOT_STYLE.get(slot, DEFAULT_STYLE)
        out.append(f'<tr><td class="td-time"><span>{e(slot)}</span></td>')

        for date in dates:
            exams = exam_lk.get((date, slot), [])
            exts  = ext_lk.get((date, slot), [])

            if not exams and not exts:
                out.append('<td class="td-empty"></td>')
                continue

            cells = []

            for row in exams:
                mk    = e(str(row.get("Nama MK",    "") or "").strip())
                room  = e(str(row.get("Ruangan",    "") or "").strip())
                kelas = e(str(row.get("Kelas",      "") or "").strip())
                jenis = e(str(row.get("Jenis Ujian","") or "").strip())
                is_c  = (date, slot) in ck_exam
                conf  = " conflict" if is_c else ""
                ctag  = '<div class="c-conf-tag">⚠ KONFLIK</div>' if is_c else ""

                _, role = get_name_role(row, nim)
                rnum = role.split()[-1] if role != "-" else ""
                rtag = (
                    f'<div class="c-role-tag c-role-{rnum}">P{rnum}</div>'
                    if rnum in ("1", "2") else ""
                )

                cells.append(
                    f'<div class="c-exam{conf}" style="--ac:{accent};--bg:{bg};">'
                    f'{ctag}'
                    f'<div class="c-exam-mk">{mk}</div>'
                    f'<div class="c-exam-room">🏛 {room}</div>'
                    f'<div class="c-exam-kls">👥 {kelas}</div>'
                    f'<div class="c-exam-type">{jenis}</div>'
                    f'{rtag}'
                    f'</div>'
                )

            for ea in exts:
                is_c = (date, ea["title"]) in ck_ext
                conf = " conflict" if is_c else ""
                ctag = '<div class="c-conf-tag">⚠ KONFLIK</div>' if is_c else ""
                cells.append(
                    f'<div class="c-ext{conf}">'
                    f'{ctag}'
                    f'<div class="c-ext-title">📌 {e(ea["title"])}</div>'
                    f'<div class="c-ext-time">⏰ {e(ea["start"])} – {e(ea["end"])}</div>'
                    f'</div>'
                )

            out.append(f'<td class="td-fill">{"".join(cells)}</td>')

        out.append("</tr>")

    out.append("</tbody></table></div>")
    return "\n".join(out)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULTS = {
    "df":              None,
    "data_error":      None,
    "result":          None,
    "nim_searched":    "",
    "proctor_name":    "",
    "proctor_role":    "",
    "ext_agendas":     [],
    "fetch_count":     0,
    # Admin
    "admin_logged_in": False,
    "admin_msg":       "",
    # Auto-refresh
    "interval_min":    DEFAULT_INTERVAL_MIN,
    "last_auto_fetch": 0.0,    # epoch seconds
    "last_updated_str": "",
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Auto-refresh logic (tanpa sleep — tidak block UI) ────────────────────────
_now = time.time()
_interval_sec = st.session_state.interval_min * 60
_due = (_now - st.session_state.last_auto_fetch) >= _interval_sec

if _due and st.session_state.df is not None:
    # Saatnya refresh otomatis
    _load_from_github.clear()
    _get_last_updated.clear()
    df_auto, err_auto = _load_from_github(st.session_state.fetch_count + 1)
    if not err_auto:
        df_auto, _ = _process_df(df_auto)
        st.session_state.df           = df_auto
        st.session_state.fetch_count += 1
    st.session_state.last_auto_fetch = _now


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='padding:6px 0 22px;'>"
        "<span style='font-family:Syne;font-size:20px;font-weight:800;color:#E8ECF8;'>🎓 ProctorView</span><br>"
        "<span style='font-size:10px;color:#3D4A7A;letter-spacing:.1em;'>UAS SCHEDULE LOOKUP · TA 2025/2026</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── Tab: Main / Admin ──────────────────────────────────────────────────
    tab_main, tab_admin = st.tabs(["📋 Jadwal", "🔐 Admin"])

    # ══════════════════════════════════════════════════════════════════════
    # TAB MAIN
    # ══════════════════════════════════════════════════════════════════════
    with tab_main:
        st.markdown('<div class="slabel">📡 Data Source</div>', unsafe_allow_html=True)

        # ── First load ────────────────────────────────────────────────────
        if st.session_state.df is None and st.session_state.data_error is None:
            with st.spinner("Mengambil data dari GitHub…"):
                df_r, err = _load_from_github(st.session_state.fetch_count)
                if err:
                    # Fallback ke SharePoint langsung
                    df_r, err = _fetch_from_sharepoint(st.session_state.fetch_count)
                if err:
                    st.session_state.data_error = err
                else:
                    df_r, err2 = _process_df(df_r)
                    st.session_state.df = df_r if not err2 else None
                    if err2:
                        st.session_state.data_error = err2
                st.session_state.last_auto_fetch = time.time()
                # Ambil timestamp
                st.session_state.last_updated_str = _get_last_updated(0)
            st.rerun()

        # ── Status ────────────────────────────────────────────────────────
        if st.session_state.data_error:
            st.markdown(
                "<div class='rt-status'><div class='rt-dot red'></div>"
                "<div class='rt-text'><b>Gagal memuat data</b></div></div>",
                unsafe_allow_html=True,
            )
            st.error(f"❌ {st.session_state.data_error}")

            # Fallback upload manual
            st.markdown('<div class="slabel">📂 Upload File Manual</div>', unsafe_allow_html=True)
            uploaded = st.file_uploader("Upload CSV/XLSX", type=["csv","xlsx"],
                                        label_visibility="collapsed")
            if uploaded is not None:
                raw = uploaded.read()
                df_up, err_up = _robust_parse(raw)
                if not err_up:
                    df_up, err_up = _process_df(df_up)
                if err_up:
                    st.error(f"Gagal baca file: {err_up}")
                else:
                    st.session_state.df         = df_up
                    st.session_state.data_error = None
                    st.session_state.last_updated_str = "Upload manual"
                    st.rerun()

            if st.button("🔄 Coba Lagi", use_container_width=True):
                _load_from_github.clear()
                _fetch_from_sharepoint.clear()
                st.session_state.data_error = None
                st.session_state.df         = None
                st.rerun()

        elif st.session_state.df is not None:
            n  = len(st.session_state.df)
            ts = st.session_state.last_updated_str or "—"
            # Hitung next auto-refresh
            elapsed  = time.time() - st.session_state.last_auto_fetch
            remain   = max(0, st.session_state.interval_min * 60 - elapsed)
            remain_m = int(remain // 60)
            remain_s = int(remain % 60)

            st.markdown(
                f"<div class='rt-status'><div class='rt-dot green'></div>"
                f"<div class='rt-text'><b>Data siap</b>"
                f"<br><span style='color:#3D4A7A;font-size:10px;'>"
                f"{n} baris · sync: {ts}"
                f"</span></div></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='font-size:10px;color:#3D4A7A;margin:6px 0 10px;'>"
                f"⏱ Auto-refresh: setiap <b style='color:#4F6EF7'>{st.session_state.interval_min} menit</b>"
                f" · next ~{remain_m}m {remain_s}s</div>",
                unsafe_allow_html=True,
            )
            if st.button("🔄 Refresh Sekarang", use_container_width=True):
                _load_from_github.clear()
                _get_last_updated.clear()
                st.session_state.df               = None
                st.session_state.data_error       = None
                st.session_state.result           = None
                st.session_state.fetch_count     += 1
                st.session_state.last_auto_fetch  = 0.0
                st.rerun()

        else:
            st.markdown(
                "<div class='rt-status'><div class='rt-dot yellow'></div>"
                "<div class='rt-text'><b>Memuat data…</b></div></div>",
                unsafe_allow_html=True,
            )

        st.markdown('<hr>', unsafe_allow_html=True)

        # ── NIM search ────────────────────────────────────────────────────
        st.markdown('<div class="slabel">🔍 Cari NIM Pengawas</div>', unsafe_allow_html=True)
        nim_input  = st.text_input("NIM", placeholder="cth: 103052330051",
                                   label_visibility="collapsed")
        search_btn = st.button("🔍  Cari Jadwal", use_container_width=True)

        if search_btn:
            if st.session_state.df is None:
                st.error("Data belum dimuat.")
            elif not nim_input.strip():
                st.warning("Masukkan NIM terlebih dahulu.")
            else:
                r = search_nim(st.session_state.df, nim_input.strip())
                st.session_state.result       = r
                st.session_state.nim_searched = normalize_nim(nim_input.strip())
                st.session_state.ext_agendas  = []
                if not r.empty:
                    name, role = get_name_role(r.iloc[0], nim_input.strip())
                    st.session_state.proctor_name = name
                    st.session_state.proctor_role = role
                else:
                    st.session_state.proctor_name = ""
                    st.session_state.proctor_role = ""

        st.markdown('<hr>', unsafe_allow_html=True)

        # ── Agenda Eksternal ──────────────────────────────────────────────
        st.markdown('<div class="slabel">📌 Tambah Agenda Eksternal</div>', unsafe_allow_html=True)
        res_now     = st.session_state.result
        unique_days = (
            sorted({str(d).strip() for d in res_now["Tanggal"].unique()}, key=day_rank)
            if res_now is not None and not res_now.empty else []
        )
        ext_day   = st.selectbox("Hari", options=unique_days or ["(cari NIM dulu)"])
        ext_title = st.text_input("Judul Agenda", placeholder="cth: Rapat Organisasi")
        cs, ce    = st.columns(2)
        with cs: ext_start = st.text_input("Mulai",   value="08:00")
        with ce: ext_end   = st.text_input("Selesai", value="10:00")

        if st.button("➕  Tambah Agenda", use_container_width=True):
            if not ext_title.strip():
                st.warning("Isi judul agenda.")
            elif ext_day == "(cari NIM dulu)":
                st.warning("Cari NIM terlebih dahulu.")
            else:
                sh = parse_ext_time(ext_start)
                eh = parse_ext_time(ext_end)
                if sh is None or eh is None:
                    st.error("Format waktu salah (HH:MM).")
                elif eh <= sh:
                    st.error("Waktu selesai harus setelah waktu mulai.")
                else:
                    st.session_state.ext_agendas.append({
                        "day": ext_day, "title": ext_title.strip(),
                        "start": ext_start, "end": ext_end,
                        "start_h": sh, "end_h": eh,
                    })
                    st.success(f"✅ '{ext_title.strip()}' ditambahkan!")

        if st.session_state.ext_agendas:
            st.markdown('<div class="slabel">📋 Daftar Agenda</div>', unsafe_allow_html=True)
            for i, ea in enumerate(st.session_state.ext_agendas):
                c1, c2 = st.columns([5, 1])
                with c1:
                    dn = ea["day"].split(",")[0] if "," in ea["day"] else ea["day"]
                    st.markdown(
                        f"<div style='font-size:11px;color:#C8FAF0;'><b>{ea['title']}</b></div>"
                        f"<div style='font-size:10px;color:#3D4A7A;'>{dn} · {ea['start']}–{ea['end']}</div>",
                        unsafe_allow_html=True,
                    )
                with c2:
                    if st.button("✕", key=f"del_{i}"):
                        st.session_state.ext_agendas.pop(i)
                        st.rerun()
            if st.button("🗑 Hapus Semua", use_container_width=True):
                st.session_state.ext_agendas = []
                st.rerun()

    # ══════════════════════════════════════════════════════════════════════
    # TAB ADMIN
    # ══════════════════════════════════════════════════════════════════════
    with tab_admin:
        if not st.session_state.admin_logged_in:
            st.markdown('<div class="slabel">🔐 Login Admin</div>', unsafe_allow_html=True)
            pwd_input = st.text_input("Password", type="password",
                                      placeholder="Masukkan admin password",
                                      label_visibility="collapsed")
            if st.button("Masuk", use_container_width=True):
                try:
                    correct = st.secrets.get("ADMIN_PASSWORD", "admin123")
                except Exception:
                    correct = "admin123"
                if pwd_input == correct:
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_msg = ""
                    st.rerun()
                else:
                    st.error("Password salah.")
        else:
            # ── Admin Panel ───────────────────────────────────────────────
            st.markdown(
                "<div style='font-size:11px;color:#2A9D8F;margin-bottom:12px;'>"
                "✅ Login sebagai <b>Admin</b></div>",
                unsafe_allow_html=True,
            )

            # ── 1. Manual Trigger GitHub Actions ─────────────────────────
            st.markdown('<div class="slabel">⚡ Manual Sync Sekarang</div>', unsafe_allow_html=True)
            st.markdown(
                "<div style='font-size:10px;color:#5B6A9A;margin-bottom:8px;'>"
                "Trigger GitHub Actions untuk ambil data terbaru dari SharePoint "
                "sekarang juga (tanpa nunggu jadwal otomatis).</div>",
                unsafe_allow_html=True,
            )
            if st.button("🚀 Get Recent Update", use_container_width=True, type="primary"):
                try:
                    gh_token = st.secrets.get("GH_PAT", "")
                except Exception:
                    gh_token = ""
                ok, msg = trigger_github_actions(gh_token)
                st.session_state.admin_msg = ("✅ " if ok else "❌ ") + msg
                if ok:
                    # Tunggu sebentar lalu pull data baru dari GitHub
                    time.sleep(2)
                    _load_from_github.clear()
                    _get_last_updated.clear()

            if st.session_state.admin_msg:
                color = "#2A9D8F" if st.session_state.admin_msg.startswith("✅") else "#E63946"
                st.markdown(
                    f"<div style='font-size:11px;color:{color};margin:6px 0;padding:8px 10px;"
                    f"background:#0F1120;border-radius:8px;border:1px solid {color}40;'>"
                    f"{e(st.session_state.admin_msg)}</div>",
                    unsafe_allow_html=True,
                )

            # ── Refresh data dari GitHub (pull tanpa trigger Actions) ──────
            if st.button("🔄 Pull Data dari GitHub", use_container_width=True):
                _load_from_github.clear()
                _get_last_updated.clear()
                st.session_state.df               = None
                st.session_state.data_error       = None
                st.session_state.fetch_count     += 1
                st.session_state.last_auto_fetch  = time.time()
                st.rerun()

            st.markdown('<hr>', unsafe_allow_html=True)

            # ── 2. Atur Interval Auto-refresh ────────────────────────────
            st.markdown('<div class="slabel">⏱ Interval Auto-Refresh</div>', unsafe_allow_html=True)
            st.markdown(
                "<div style='font-size:10px;color:#5B6A9A;margin-bottom:8px;'>"
                "Interval ini mengontrol seberapa sering Streamlit otomatis "
                "pull data terbaru dari GitHub (minimum 5 menit).</div>",
                unsafe_allow_html=True,
            )

            new_interval = st.number_input(
                "Interval (menit)",
                min_value=5,
                max_value=1440,
                value=st.session_state.interval_min,
                step=5,
                label_visibility="collapsed",
            )
            st.markdown(
                f"<div style='font-size:10px;color:#3D4A7A;margin:4px 0;'>"
                f"Saat ini: setiap <b style='color:#4F6EF7'>{st.session_state.interval_min} menit</b></div>",
                unsafe_allow_html=True,
            )

            col_save, col_preset = st.columns(2)
            with col_save:
                if st.button("💾 Simpan", use_container_width=True):
                    st.session_state.interval_min = int(new_interval)
                    st.success(f"✅ Interval diset ke {new_interval} menit")
            with col_preset:
                preset = st.selectbox("Preset", ["15 mnt","30 mnt","1 jam","2 jam","6 jam"],
                                      label_visibility="collapsed")
                preset_map = {"15 mnt":15,"30 mnt":30,"1 jam":60,"2 jam":120,"6 jam":360}
                if st.button("⚡ Pakai", use_container_width=True):
                    st.session_state.interval_min = preset_map[preset]
                    st.success(f"✅ {preset}")

            st.markdown('<hr>', unsafe_allow_html=True)

            # ── 3. Info GitHub Actions schedule ──────────────────────────
            st.markdown('<div class="slabel">📋 Jadwal GitHub Actions</div>', unsafe_allow_html=True)
            st.markdown(
                "<div style='font-size:10px;color:#5B6A9A;line-height:1.6;'>"
                "Cron saat ini di <code>.github/workflows/sync_jadwal.yml</code>:<br>"
                "<code style='color:#4F6EF7'>0 * * * *</code> → tiap jam<br><br>"
                "Untuk ubah cron, edit file workflow di GitHub dan commit.<br>"
                "Format: <code>*/30 * * * *</code> = tiap 30 menit<br>"
                "<b>Minimum GitHub Actions: 5 menit</b>"
                "</div>",
                unsafe_allow_html=True,
            )

            st.markdown('<hr>', unsafe_allow_html=True)

            # ── 4. Logout ─────────────────────────────────────────────────
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.admin_logged_in = False
                st.session_state.admin_msg       = ""
                st.rerun()




# ─────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────────────────────────────────────
result = st.session_state.result
nim    = st.session_state.nim_searched
name   = st.session_state.proctor_name
role   = st.session_state.proctor_role
ext    = st.session_state.ext_agendas

# ── Empty / not-found states ─────────────────────────────────────────────────
if result is None or result.empty:
    if result is not None and result.empty:
        body = (
            f'<div style="font-family:Syne;font-size:18px;font-weight:700;color:#E8ECF8;">NIM tidak ditemukan</div>'
            f'<div style="color:#3D4A7A;margin-top:8px;">NIM <code style="color:#4F6EF7">{e(nim)}</code> '
            f'tidak ada di kolom Pengawas 1 maupun Pengawas 2.</div>'
        )
    else:
        body = (
            '<div style="font-family:Syne;font-size:22px;font-weight:700;color:#E8ECF8;">ProctorView</div>'
            '<div style="color:#3D4A7A;margin-top:10px;">Masukkan NIM untuk melihat jadwal pengawasan.</div>'
            '<div style="color:#1C2040;margin-top:28px;font-size:12px;">← Cari NIM di panel kiri</div>'
        )
    st.markdown(
        f'<div style="text-align:center;padding:80px 0;">'
        f'<div style="font-size:44px;margin-bottom:16px;">🎓</div>{body}</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ── Conflicts ─────────────────────────────────────────────────────────────────
conflicts = detect_conflicts(result, ext)

# ── Hero ─────────────────────────────────────────────────────────────────────
cp = f'<span class="conf-pill">⚠️ {len(conflicts)} KONFLIK</span>' if conflicts else ""
if role == "Pengawas 1":
    rbg, rclr = "#1C3060", "#7BA7FF"
else:
    rbg, rclr = "#1C2A40", "#A78BFA"
role_badge = (
    f'<span class="role-pill" style="background:{rbg};color:{rclr};">{e(role)}</span>'
    if role and role not in ("-", "") else ""
)
st.markdown(
    f'<div class="hero">'
    f'<div class="hero-label">Jadwal Pengawas UAS FIF — TA 2025/2026 Genap</div>'
    f'<div class="hero-name">{e(name)} {cp}</div>'
    f'<span class="nim-pill">{e(nim)}</span>{role_badge}'
    f'<span style="color:#3D4A7A;font-size:11px;margin-left:10px;">{len(result)} sesi pengawasan</span>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Metrics ───────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
honor = f"Rp {len(result) * 30_000:,}".replace(",", ".")
with m1:
    st.markdown(f'<div class="mcard"><div class="mnum">{len(result)}</div><div class="mlbl">Total Sesi</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(
        f'<div class="mcard"><div class="mnum" style="background:linear-gradient(135deg,#2A9D8F,#26D0CE);'
        f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:1.15rem;">'
        f'{honor}</div><div class="mlbl">Estimasi Honor</div></div>',
        unsafe_allow_html=True,
    )
with m3:
    st.markdown(f'<div class="mcard"><div class="mnum">{len(ext)}</div><div class="mlbl">Agenda Eksternal</div></div>', unsafe_allow_html=True)
with m4:
    rcls = " mnum-red" if conflicts else ""
    st.markdown(f'<div class="mcard"><div class="mnum{rcls}">{len(conflicts)}</div><div class="mlbl">Konflik Jadwal</div></div>', unsafe_allow_html=True)

# ── Conflict banners ─────────────────────────────────────────────────────────
if conflicts:
    st.markdown('<div class="sec-h">⚠️ Konflik Terdeteksi</div>', unsafe_allow_html=True)
    for c in conflicts:
        dn = c["day"].split(",")[0].strip()
        st.markdown(
            f'<div class="cbanner">'
            f'<div class="ctitle">⚠️ Konflik — {e(dn)}</div>'
            f'<div class="citem">🏫 <b>Pengawasan:</b> {e(c["exam_subject"])} · {e(c["exam_slot"])} · {e(c["exam_room"])}</div>'
            f'<div class="citem">📌 <b>Eksternal:</b> {e(c["ext_title"])} · {e(c["ext_time"])}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── Calendar ─────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-h">📅 Kalender Jadwal</div>', unsafe_allow_html=True)

# Legend
used_slots = {str(j).strip() for j in result["Jam"]}
leg = '<div class="legend-row">'
for slot, (ac, _) in SLOT_STYLE.items():
    if slot in used_slots:
        leg += f'<div class="legend-item"><span class="legend-dot" style="background:{ac};"></span>{e(slot)}</div>'
if ext:
    leg += (
        f'<div class="legend-item"><span class="legend-dot" style="background:{EXT_COLOR}; '
        f'border:2px dashed {EXT_COLOR};box-sizing:border-box;"></span>Agenda Eksternal</div>'
    )
if conflicts:
    leg += '<div class="legend-item"><span class="legend-dot" style="background:#E63946;"></span>Konflik</div>'
leg += (
    '<div class="legend-item"><span style="background:#1C3060;color:#7BA7FF;border-radius:3px;'
    'padding:1px 5px;font-size:9px;font-weight:700;">P1</span>&nbsp;Pengawas 1</div>'
    '<div class="legend-item"><span style="background:#1C2A40;color:#A78BFA;border-radius:3px;'
    'padding:1px 5px;font-size:9px;font-weight:700;">P2</span>&nbsp;Pengawas 2</div>'
)
leg += '</div>'
st.markdown(leg, unsafe_allow_html=True)
st.markdown(build_calendar(result, ext, conflicts, nim), unsafe_allow_html=True)

# ── Per-day detail ────────────────────────────────────────────────────────────
st.markdown('<div class="sec-h">📋 Rincian Per Hari</div>', unsafe_allow_html=True)

ck_exam = {(c["day"], c["exam_slot"]) for c in conflicts}
ck_ext  = {(c["day"], c["ext_title"])  for c in conflicts}
dates   = sorted({str(d).strip() for d in result["Tanggal"].unique()}, key=day_rank)

for date in dates:
    date = str(date).strip()
    dr   = result[result["Tanggal"].astype(str).str.strip() == date]
    dex  = [a for a in ext if str(a["day"]).strip() == date]
    dn   = date.split(",")[0].strip()
    ds2  = date.split(",")[1].strip() if "," in date else date

    with st.expander(f"**{dn}** — {ds2}  ·  {len(dr)} sesi", expanded=False):
        for _, row in dr.iterrows():
            slot   = str(row["Jam"]).strip()
            subj   = str(row.get("Nama MK",    "") or "").strip()
            room   = str(row.get("Ruangan",    "") or "").strip()
            kelas  = str(row.get("Kelas",      "") or "").strip()
            jenis  = str(row.get("Jenis Ujian","") or "").strip()
            ac     = SLOT_STYLE.get(slot, DEFAULT_STYLE)[0]
            is_c   = (date, slot) in ck_exam
            ctag   = (
                '<span style="background:#E63946;color:#fff;border-radius:4px;padding:1px 6px;'
                'font-size:9px;font-weight:700;margin-left:8px;">⚠ KONFLIK</span>'
                if is_c else ""
            )

            _, row_role = get_name_role(row, nim)
            rnum = row_role.split()[-1] if row_role != "-" else ""
            if rnum == "1":
                rbadge = '<span style="background:#1C3060;color:#7BA7FF;border-radius:4px;padding:1px 6px;font-size:9px;font-weight:700;margin-left:6px;">Pengawas 1</span>'
            elif rnum == "2":
                rbadge = '<span style="background:#1C2A40;color:#A78BFA;border-radius:4px;padding:1px 6px;font-size:9px;font-weight:700;margin-left:6px;">Pengawas 2</span>'
            else:
                rbadge = ""

            # Rekan pengawas
            rekan = []
            for i in ["1", "2", "3"]:
                r_nim  = normalize_nim(str(row.get(f"NIM (Pengawas {i})", "") or ""))
                r_nama = str(row.get(f"Nama Lengkap (Pengawas {i})", "") or "").strip()
                if r_nim and r_nim not in ("", "NAN", "NONE") and r_nim != nim.upper():
                    lbl = r_nama if r_nama and r_nama.lower() not in ("-","nan","none","") else r_nim
                    rekan.append(
                        f'<span style="display:inline-flex;align-items:center;gap:4px;background:#1C2040;'
                        f'border:1px solid #2A3060;color:#A78BFA;border-radius:6px;padding:3px 8px;'
                        f'font-size:10px;font-weight:600;margin:2px 3px 2px 0;">👤 {e(lbl)}</span>'
                    )
            rekan_html = ""
            if rekan:
                rekan_html = (
                    '<div style="margin-top:9px;padding-top:8px;border-top:1px solid #1C2040;">'
                    '<div style="font-size:9px;color:#3D4A7A;letter-spacing:.1em;text-transform:uppercase;margin-bottom:5px;">Rekan Pengawas</div>'
                    '<div style="display:flex;flex-wrap:wrap;">' + "".join(rekan) + '</div></div>'
                )

            st.markdown(
                f'<div class="lcard" style="--ac:{ac}">'
                f'<div class="lcard-title">{e(subj)}{ctag}{rbadge}</div>'
                f'<div class="lcard-meta">'
                f'<span class="badge">⏰ {e(slot)}</span>'
                f'<span class="badge">🏛 {e(room)}</span>'
                f'<span class="badge">👥 {e(kelas)}</span>'
                f'<span class="badge">{e(jenis)}</span>'
                f'</div>'
                f'{rekan_html}'
                f'</div>',
                unsafe_allow_html=True,
            )

        if dex:
            st.markdown(
                '<div style="color:#3D4A7A;font-size:10px;letter-spacing:.1em;text-transform:uppercase;margin:14px 0 6px;">📌 Agenda Eksternal</div>',
                unsafe_allow_html=True,
            )
            for ea in dex:
                ixc = (date, ea["title"]) in ck_ext
                bc  = "#E63946" if ixc else EXT_COLOR
                ctag2 = (
                    '<span style="background:#E63946;color:#fff;border-radius:4px;padding:1px 6px;'
                    'font-size:9px;font-weight:700;margin-left:8px;">⚠ KONFLIK</span>'
                    if ixc else ""
                )
                st.markdown(
                    f'<div class="ext-lcard" style="border-left-color:{bc}">'
                    f'<div class="lcard-title" style="color:#C8FAF0;">📌 {e(ea["title"])}{ctag2}</div>'
                    f'<div class="lcard-meta"><span class="badge" style="color:#2A9D8F;">⏰ {e(ea["start"])} – {e(ea["end"])}</span></div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

# ── Footer info ───────────────────────────────────────────────────────────────
st.markdown(
    f"<div style='text-align:right;font-size:9px;color:#1C2040;margin-top:24px;'>"
    "</div>",
    unsafe_allow_html=True,
)
