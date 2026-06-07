import streamlit as st
import pandas as pd
import html as html_lib
import io
import requests
import time
from datetime import datetime, timezone, timedelta

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ProctorView — Jadwal Pengawas Ujian FIF",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS — design baru (Plus Jakarta Sans, dark grey palette)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

:root {
  --bg:#2C2C2C; --bg-sb:#242424; --bg-card:#353535; --bg-card-h:#3e3e3e;
  --bg-input:#333; --text:#E4E4E4; --text2:#aaa; --text3:#777;
  --cyan:#A8DADC; --pink:#FFC1CC; --lav:#B39CD0;
  --border:#444; --danger:#e06060; --success:#6BCB77;
}

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] {
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
  background: var(--bg) !important;
  color: var(--text) !important;
}
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* ── Streamlit overrides ── */
[data-testid="stAppViewContainer"] { background: var(--bg) !important; }
[data-testid="stSidebar"] { background: var(--bg-sb) !important; border-right: 1px solid var(--border) !important; }
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }
[data-testid="stHeader"] { display: none !important; }
.stMainBlockContainer { padding: 36px 40px 60px !important; max-width: 100% !important; }
div[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

/* Hide streamlit default elements */
#MainMenu, footer, header { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
.stDeployButton { display: none !important; }

/* ── Sidebar brand ── */
.sb-brand { padding: 24px 20px 16px; border-bottom: 1px solid var(--border); }
.sb-logo { font-size: 22px; font-weight: 800; letter-spacing: -.5px; color: var(--cyan); margin: 0; }
.sb-subtitle { font-size: 12px; color: var(--text2); margin-top: 3px; font-weight: 500; }
.sb-period { font-size: 11px; color: var(--text3); margin-top: 1px; }

/* ── Sidebar tabs ── */
.sb-tabs-wrap { display: flex; border-bottom: 1px solid var(--border); }
.sb-tab-btn {
  flex: 1; padding: 11px 0; font-size: 13px; font-weight: 600;
  background: none; border: none; color: var(--text3); cursor: pointer;
  border-bottom: 2px solid transparent; font-family: inherit; transition: color .15s, border-color .15s;
}
.sb-tab-btn.active { color: var(--cyan); border-bottom-color: var(--cyan); }
.sb-tab-btn:hover:not(.active) { color: var(--text2); }

/* ── Sidebar sections ── */
.sb-section { padding: 14px 20px; border-bottom: 1px solid rgba(68,68,68,.5); }
.sb-section-title {
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: .8px; color: var(--text3); margin-bottom: 10px;
}
.sb-label { font-size: 12px; font-weight: 600; color: var(--text2); margin-bottom: 6px; display: block; }
.sb-label-sm { font-size: 11px; font-weight: 600; color: var(--text3); margin: 8px 0 4px; display: block; }
.sb-hint { font-size: 11px; color: var(--text3); line-height: 1.45; margin-bottom: 10px; }

/* ── Sidebar inputs (override streamlit) ── */
[data-testid="stSidebar"] .stTextInput > div > div > input,
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stNumberInput > div > div > input,
[data-testid="stSidebar"] .stTimeInput > div > div > input,
[data-testid="stSidebar"] .stDateInput > div > div > input {
  background: var(--bg-input) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: 13px !important;
}
[data-testid="stSidebar"] .stTextInput > div > div > input:focus {
  border-color: var(--cyan) !important;
  box-shadow: none !important;
}

/* ── Sidebar buttons ── */
[data-testid="stSidebar"] .stButton > button {
  width: 100%; border-radius: 8px !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: 13px !important; font-weight: 600 !important;
  border: none !important; transition: filter .15s !important;
  padding: 10px 14px !important;
}
.btn-primary [data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] [data-btn="primary"] button {
  background: var(--lav) !important; color: #1a1a1a !important;
}

/* ── Sidebar footer ── */
.sb-footer {
  padding: 14px 20px; border-top: 1px solid var(--border);
  display: flex; gap: 10px; align-items: flex-start;
  background: rgba(168,218,220,.04);
}
.sb-update-dot {
  width: 8px; height: 8px; border-radius: 50%; background: var(--success);
  margin-top: 5px; flex-shrink: 0; box-shadow: 0 0 6px rgba(107,203,119,.4);
}
.sb-update-label { font-size: 10px; color: var(--text3); text-transform: uppercase; letter-spacing: .5px; font-weight: 600; }
.sb-update-time { font-size: 13px; color: var(--text); font-weight: 700; margin-top: 2px; }
.sb-update-rows { font-size: 10px; color: var(--text3); margin-top: 2px; }

/* ── Main view header ── */
.mv-sup {
  font-size: 12px; color: var(--cyan); font-weight: 600;
  text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;
}
.mv-name { font-size: 30px; font-weight: 800; letter-spacing: -.5px; line-height: 1.2; margin-bottom: 10px; }
.mv-badges { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 28px; }
.mv-nim { background: rgba(168,218,220,.15); color: var(--cyan); font-size: 13px; font-weight: 600; padding: 4px 12px; border-radius: 20px; }
.mv-sesi-count { font-size: 13px; color: var(--text2); }

/* ── Stats ── */
.stats-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 24px; }
.stat-box { background: var(--bg-card); border-radius: 12px; padding: 18px 16px; text-align: center; }
.stat-value { font-size: 24px; font-weight: 800; line-height: 1.2; }
.stat-label { font-size: 11px; color: var(--text3); margin-top: 4px; text-transform: uppercase; letter-spacing: .4px; font-weight: 600; }

/* ── Legend ── */
.legend-row { display: flex; gap: 18px; margin-bottom: 20px; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text2); }
.legend-dot { width: 10px; height: 10px; border-radius: 3px; flex-shrink: 0; display: inline-block; }

/* ── Section header ── */
.sec-h {
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: .8px; color: var(--cyan);
  border-left: 3px solid var(--cyan); padding-left: 10px;
  margin: 28px 0 14px;
}

/* ── Day section ── */
.day-section { background: var(--bg-card); border-radius: 12px; overflow: hidden; margin-bottom: 10px; }
.day-section--conflict { box-shadow: inset 0 0 0 1px rgba(224,96,96,.3); }
.day-header {
  width: 100%; display: flex; align-items: center; gap: 10px;
  padding: 14px 18px; background: none; border: none;
  color: var(--text); cursor: pointer; font-size: 14px; font-weight: 700;
  font-family: 'Plus Jakarta Sans', sans-serif; text-align: left;
}
.day-header:hover { background: rgba(255,255,255,.02); }
.day-date { flex: 1; }
.day-count { font-size: 12px; color: var(--text3); font-weight: 500; }
.day-conflict-badge {
  font-size: 10px; font-weight: 700; color: var(--danger);
  background: rgba(224,96,96,.12); padding: 2px 8px;
  border-radius: 10px; text-transform: uppercase; letter-spacing: .5px;
}
.day-cards { padding: 0 14px 14px; display: flex; flex-direction: column; gap: 8px; }

/* ── Schedule card ── */
.scard {
  background: rgba(255,255,255,.03); border-radius: 10px; padding: 14px 16px;
  border-left: 3px solid var(--border); transition: background .15s;
}
.scard:hover { background: rgba(255,255,255,.06); }
.scard--conflict { border-left-color: var(--danger) !important; }
.scard--agenda { border-left-color: var(--pink); }
.scard-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.scard-time { display: flex; align-items: center; gap: 5px; font-size: 12px; font-weight: 600; }
.role-badge { font-size: 11px; font-weight: 700; padding: 2px 10px; border-radius: 10px; }
.scard-course { font-size: 15px; font-weight: 700; line-height: 1.3; margin-bottom: 6px; color: var(--text); }
.scard-room { font-size: 13px; color: var(--text2); margin-bottom: 6px; }
.scard-meta { display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--text3); flex-wrap: wrap; }
.scard-meta-item { background: rgba(255,255,255,.05); padding: 2px 8px; border-radius: 4px; }
.scard-partner { font-size: 11px; color: var(--lav); margin-top: 8px; padding-top: 6px; border-top: 1px solid rgba(68,68,68,.4); }
.scard-partner-chip {
  display: inline-block; background: rgba(179,156,208,.15);
  border: 1px solid rgba(179,156,208,.25); border-radius: 6px;
  padding: 2px 10px; font-size: 11px; color: var(--lav); font-weight: 600; margin-top: 4px;
}

/* ── Conflict alert ── */
.conflict-alert {
  display: flex; align-items: flex-start; gap: 8px;
  background: rgba(224,96,96,.08); border: 1px solid rgba(224,96,96,.18);
  border-radius: 8px; padding: 10px 14px; font-size: 12px;
  color: var(--danger); line-height: 1.4; margin-bottom: 4px;
}
.conflict-alert strong { font-weight: 700; }

/* ── Empty state ── */
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; min-height: 60vh; text-align: center; color: var(--text3);
}
.empty-state h2 { font-size: 20px; color: var(--text2); font-weight: 700; margin: 20px 0 8px; }
.empty-state p { font-size: 14px; max-width: 320px; line-height: 1.5; }

/* ── Admin interval row ── */
.interval-row { display: flex; align-items: center; gap: 12px; margin: 8px 0; }
.interval-val { font-size: 18px; font-weight: 700; color: var(--text); min-width: 70px; text-align: center; }
.interval-btn {
  width: 34px; height: 34px; border-radius: 8px; background: var(--bg-input);
  border: 1px solid var(--border); color: var(--text); font-size: 18px;
  cursor: pointer; display: flex; align-items: center; justify-content: center; font-family: inherit;
}
.interval-btn:hover { border-color: var(--text3); }

/* ── Sync msg ── */
.sync-msg-ok { font-size: 11px; color: var(--success); margin-top: 8px; text-align: center; padding: 6px; background: rgba(107,203,119,.08); border-radius: 6px; }
.sync-msg-err { font-size: 11px; color: var(--danger); margin-top: 8px; text-align: center; padding: 6px; background: rgba(224,96,96,.08); border-radius: 6px; }

/* ── Admin confirm ── */
.sb-confirm { background: rgba(224,96,96,.08); border: 1px solid rgba(224,96,96,.2); border-radius: 8px; padding: 12px; margin-top: 8px; }
.sb-confirm p { font-size: 12px; color: var(--danger); margin-bottom: 8px; font-weight: 600; }

/* ── Streamlit tab overrides ── */
[data-testid="stSidebar"] [data-baseweb="tab-list"] {
  background: none !important; border-bottom: 1px solid var(--border) !important; gap: 0 !important;
}
[data-testid="stSidebar"] [data-baseweb="tab"] {
  background: none !important; color: var(--text3) !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: 13px !important; font-weight: 600 !important;
  border-bottom: 2px solid transparent !important; padding: 11px 0 !important;
  flex: 1 !important; justify-content: center !important;
}
[data-testid="stSidebar"] [aria-selected="true"] {
  color: var(--cyan) !important; border-bottom-color: var(--cyan) !important;
}
[data-testid="stSidebar"] [data-baseweb="tab-highlight"] { display: none !important; }
[data-testid="stSidebar"] [data-baseweb="tab-border"] { display: none !important; }

/* Expander override */
[data-testid="stExpander"] {
  background: var(--bg-card) !important; border: none !important;
  border-radius: 12px !important; overflow: hidden; margin-bottom: 10px;
}
[data-testid="stExpander"] summary {
  font-size: 14px !important; font-weight: 700 !important;
  color: var(--text) !important; padding: 14px 18px !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stExpander"] summary:hover { background: rgba(255,255,255,.02) !important; }
[data-testid="stExpanderDetails"] { padding: 0 14px 14px !important; }

/* ── Responsive ── */
@media(max-width:860px) {
  .stMainBlockContainer { padding: 20px !important; }
  .stats-row { grid-template-columns: repeat(2,1fr) !important; }
  .mv-name { font-size: 22px !important; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
DAY_ORDER = {'senin':0,'selasa':1,'rabu':2,'kamis':3,'jumat':4,'sabtu':5,'minggu':6}

# Semua slot dari CSV UAS
TIME_SLOTS = [
    '08.00 - 10.15 WIB',
    '10.45 - 13.00 WIB',
    '14.00 - 16.15 WIB',
    '16.00 - 18.00 WIB',
    '18.30 - 20.30 WIB',
]

# Warna tiap slot (sesuai palette baru)
SLOT_COLOR = {
    '08.00 - 10.15 WIB': '#A8DADC',
    '10.45 - 13.00 WIB': '#FFC1CC',
    '14.00 - 16.15 WIB': '#B39CD0',
    '16.00 - 18.00 WIB': '#FFD580',
    '18.30 - 20.30 WIB': '#e06060',
}

TIME_RANGES = {
    '08.00 - 10.15 WIB': (8.00,  10.25),
    '10.45 - 13.00 WIB': (10.75, 13.00),
    '14.00 - 16.15 WIB': (14.00, 16.25),
    '16.00 - 18.00 WIB': (16.00, 18.00),
    '18.30 - 20.30 WIB': (18.50, 20.50),
}

HONOR_PER_SESSION = 30_000

GITHUB_REPO         = "Fall-Llihc/visualiasi_jadwal_ujian"
RAW_DATA_URL        = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/data/jadwal.csv"
RAW_TS_URL          = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/data/last_updated.txt"
GITHUB_API_DISPATCH = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/sync_jadwal.yml/dispatches"

SHAREPOINT_URL = (
    "https://telkomuniversityofficial-my.sharepoint.com/:x:/g/personal/"
    "informaticslab_telkomuniversity_ac_id/"
    "IQDW93EEnbLMRJk2doiuFr_sAQYxTOFEXJm_Jf5cfIhhHWk?e=Zh4B0W&download=1"
)

DEFAULT_INTERVAL_MIN = 60

BULAN_ID = {
    1:'Januari',2:'Februari',3:'Maret',4:'April',5:'Mei',6:'Juni',
    7:'Juli',8:'Agustus',9:'September',10:'Oktober',11:'November',12:'Desember'
}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def e(s): return html_lib.escape(str(s))

def day_rank(d: str) -> int:
    d = str(d).strip().lower()
    for k, v in DAY_ORDER.items():
        if d.startswith(k): return v
    return 99

def time_rank(t: str) -> int:
    t = str(t).strip()
    return TIME_SLOTS.index(t) if t in TIME_SLOTS else 99

def normalize_nim(value) -> str:
    s = str(value).strip()
    if s.upper() in {"NAN", "NONE", ""}: return ""
    try: s = str(int(float(s)))
    except (ValueError, OverflowError): pass
    if s.endswith(".0") and s[:-2].isdigit(): s = s[:-2]
    return s.upper()

def format_tanggal_full(tanggal_str: str) -> str:
    """'Senin, 22 Juni 2026' → tetap seperti itu (sudah bagus)"""
    return str(tanggal_str).strip()

def format_last_updated_wib(raw: str) -> str:
    """'2026-06-07 14:36:29 UTC' → '7 Juni 2026, 21:36 WIB'"""
    try:
        raw = raw.replace(" UTC", "").strip()
        dt  = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S")
        dt_wib = dt + timedelta(hours=7)
        return f"{dt_wib.day} {BULAN_ID[dt_wib.month]} {dt_wib.year}, {dt_wib.strftime('%H:%M')} WIB"
    except Exception:
        return raw

def overlaps(s1, e1, s2, e2) -> bool:
    return s1 < e2 and s2 < e1

def parse_ext_time(t: str):
    try:
        h, m = map(int, t.split(':'))
        return h + m / 60
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# DATA — download + parse
# ─────────────────────────────────────────────────────────────────────────────
def _robust_parse(content_bytes: bytes):
    if content_bytes[:4] == b'PK\x03\x04':
        try:
            df = pd.read_excel(io.BytesIO(content_bytes), skiprows=12, dtype=str)
            if "Tanggal" in df.columns and len(df) > 0: return df, None
        except Exception: pass

    last_err = "unknown"
    for enc, data in [
        ("utf-8-sig", content_bytes),
        ("utf-8",     content_bytes),
        ("latin-1",   content_bytes),
        ("utf-8",     content_bytes.replace(b"\x00", b"")),
    ]:
        try:
            text = data.decode(enc, errors="replace")
            df = pd.read_csv(io.StringIO(text), sep=";", skiprows=12,
                             dtype=str, on_bad_lines="skip", engine="python")
            if "Tanggal" in df.columns and len(df) > 0: return df, None
        except Exception as ex: last_err = str(ex)
    return None, f"Gagal parse file: {last_err}"


def _process_df(df: pd.DataFrame):
    df = df.copy()
    df.columns = df.columns.str.strip()
    df = df[df["Tanggal"].notna()].copy()
    df = df[df["Tanggal"].astype(str).str.strip() != ""].copy()
    df = df[~df["Tanggal"].astype(str).str.strip().str.startswith("#")].copy()
    df["Tanggal"] = df["Tanggal"].astype(str).str.strip()
    df["Jam"]     = df["Jam"].astype(str).str.strip()
    for i in ["1","2","3"]:
        col = f"NIM (Pengawas {i})"
        df[col] = df[col].apply(normalize_nim) if col in df.columns else ""
    for i in ["1","2","3"]:
        col = f"Nama Lengkap (Pengawas {i})"
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({"nan":"","None":"","NaN":""})
        else:
            df[col] = ""
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    return df, None


@st.cache_data(ttl=60, show_spinner=False)
def _load_from_github(_dummy: int = 0):
    try:
        r = requests.get(RAW_DATA_URL, timeout=15,
                         headers={"Cache-Control":"no-cache"})
        if r.status_code == 404:
            return None, "File data/jadwal.csv belum ada di repo — jalankan GitHub Actions dulu."
        if r.status_code != 200:
            return None, f"GitHub: HTTP {r.status_code}"
        df = pd.read_csv(io.StringIO(r.content.decode("utf-8-sig", errors="replace")),
                         dtype=str, engine="python", on_bad_lines="skip")
        if "Tanggal" not in df.columns:
            return None, "Kolom Tanggal tidak ditemukan."
        return df, None
    except Exception as ex:
        return None, f"Gagal baca GitHub: {ex}"


@st.cache_data(ttl=60, show_spinner=False)
def _get_last_updated(_dummy: int = 0) -> str:
    try:
        r = requests.get(RAW_TS_URL, timeout=10,
                         headers={"Cache-Control":"no-cache"})
        if r.status_code == 200: return r.text.strip()
    except Exception: pass
    return ""


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_from_sharepoint(_dummy: int = 0):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/octet-stream,*/*;q=0.8",
        "Accept-Encoding": "identity",
    }
    try:
        resp = requests.get(SHAREPOINT_URL, headers=headers,
                            timeout=30, allow_redirects=True)
    except Exception as ex:
        return None, f"Koneksi gagal: {ex}"
    ct = resp.headers.get("Content-Type","")
    sz = len(resp.content)
    if resp.status_code == 403:
        body = resp.content.decode(errors="replace")
        if "allowlist" in body.lower():
            return None, "403 IP diblokir SharePoint tenant."
        return None, f"403 Forbidden."
    if resp.status_code != 200: return None, f"HTTP {resp.status_code}."
    if "html" in ct.lower(): return None, "SharePoint mengembalikan HTML."
    if sz < 500: return None, f"Response terlalu kecil ({sz} B)."
    df, err = _robust_parse(resp.content)
    if err: return None, err
    return _process_df(df)


def trigger_github_actions(gh_token: str) -> tuple:
    if not gh_token.strip(): return False, "GitHub Token (GH_PAT) tidak diset di Secrets."
    try:
        r = requests.post(
            GITHUB_API_DISPATCH,
            headers={
                "Authorization": f"Bearer {gh_token.strip()}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            json={"ref":"main","inputs":{"reason":"Manual trigger dari ProctorView Admin"}},
            timeout=15,
        )
        if r.status_code == 204:
            return True, "GitHub Actions berhasil di-trigger! Tunggu ~30 detik lalu klik Pull Data."
        return False, f"GitHub API: HTTP {r.status_code} — {r.text[:150]}"
    except Exception as ex:
        return False, f"Gagal trigger: {ex}"


# ─────────────────────────────────────────────────────────────────────────────
# SEARCH
# ─────────────────────────────────────────────────────────────────────────────
def search_nim(df: pd.DataFrame, nim: str) -> pd.DataFrame:
    nim = normalize_nim(nim)
    mask = pd.Series([False]*len(df), index=df.index)
    for i in ["1","2","3"]:
        col = f"NIM (Pengawas {i})"
        if col in df.columns: mask = mask | (df[col] == nim)
    r = df[mask].copy()
    r["_day"]  = r["Tanggal"].apply(day_rank)
    r["_time"] = r["Jam"].apply(time_rank)
    return r.sort_values(["_day","_time"]).reset_index(drop=True)


def get_name_role(row, nim: str):
    nim = normalize_nim(nim)
    for i in ["1","2","3"]:
        if normalize_nim(row.get(f"NIM (Pengawas {i})","")) == nim:
            raw = str(row.get(f"Nama Lengkap (Pengawas {i})","") or "").strip()
            name = raw if raw and raw.lower() not in ("nan","none","-","") else "-"
            return name, f"P{i}"
    return "-", "-"


def detect_conflicts(sched):
    from collections import defaultdict
    groups = defaultdict(list)
    for _, row in sched.iterrows():
        k = (str(row["Tanggal"]).strip(), str(row["Jam"]).strip())
        groups[k].append(row)
    return {k for k, v in groups.items() if len(v) > 1}


def detect_ext_conflicts(sched, ext_agendas):
    conflicts = []
    for _, row in sched.iterrows():
        slot = str(row["Jam"]).strip()
        if slot not in TIME_RANGES: continue
        ss, se = TIME_RANGES[slot]
        day = str(row["Tanggal"]).strip()
        for ea in ext_agendas:
            if ea["day"] != day: continue
            if overlaps(ss, se, ea["start_h"], ea["end_h"]):
                conflicts.append((day, slot, ea["title"]))
    return conflicts


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULTS = {
    "df":              None,
    "data_error":      None,
    "result":          None,
    "nim_searched":    "",
    "proctor_name":    "",
    "ext_agendas":     [],
    "fetch_count":     0,
    "admin_logged_in": False,
    "admin_msg":       "",
    "admin_msg_ok":    True,
    "interval_min":    DEFAULT_INTERVAL_MIN,
    "last_auto_fetch": 0.0,
    "last_updated_str":"",
    "show_reset_confirm": False,
    "interval_input":  DEFAULT_INTERVAL_MIN,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

# Auto-refresh check (non-blocking)
_now = time.time()
if (st.session_state.df is not None and
    (_now - st.session_state.last_auto_fetch) >= st.session_state.interval_min * 60):
    _load_from_github.clear()
    _get_last_updated.clear()
    df_auto, err_auto = _load_from_github(st.session_state.fetch_count + 1)
    if not err_auto:
        df_auto, _ = _process_df(df_auto)
        st.session_state.df          = df_auto
        st.session_state.fetch_count += 1
        ts_raw = _get_last_updated(st.session_state.fetch_count)
        st.session_state.last_updated_str = format_last_updated_wib(ts_raw) if ts_raw else ""
    st.session_state.last_auto_fetch = _now


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown(
        "<div class='sb-brand'>"
        "<h1 class='sb-logo'>ProctorView</h1>"
        "<p class='sb-subtitle'>Jadwal Pengawas Ujian FIF</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # Tabs
    tab_jadwal, tab_admin = st.tabs(["📋 Jadwal", "🔐 Admin"])

    # ══════════════════════════════════════════════════════════════════════
    # TAB JADWAL
    # ══════════════════════════════════════════════════════════════════════
    with tab_jadwal:
        # ── Data source status ────────────────────────────────────────────
        st.markdown("<div style='padding:14px 20px 0;'>", unsafe_allow_html=True)
        st.markdown("<p class='sb-section-title' style='margin-bottom:6px;'>📡 Data Source</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # First load
        if st.session_state.df is None and st.session_state.data_error is None:
            with st.spinner("Mengambil data…"):
                df_r, err = _load_from_github(st.session_state.fetch_count)
                if err:
                    df_r, err = _fetch_from_sharepoint(st.session_state.fetch_count)
                if not err:
                    df_r, err = _process_df(df_r)
                if err:
                    st.session_state.data_error = err
                else:
                    st.session_state.df = df_r
                    ts_raw = _get_last_updated(0)
                    st.session_state.last_updated_str = format_last_updated_wib(ts_raw) if ts_raw else ""
                st.session_state.last_auto_fetch = time.time()
            st.rerun()

        if st.session_state.data_error:
            st.error(f"❌ {st.session_state.data_error}")
            uploaded = st.file_uploader("Upload CSV/XLSX manual",
                                        type=["csv","xlsx"], label_visibility="visible")
            if uploaded:
                raw = uploaded.read()
                df_up, err_up = _robust_parse(raw)
                if not err_up: df_up, err_up = _process_df(df_up)
                if err_up: st.error(f"Gagal: {err_up}")
                else:
                    st.session_state.df         = df_up
                    st.session_state.data_error = None
                    st.session_state.last_updated_str = "Upload manual"
                    st.rerun()
            if st.button("🔄 Coba Lagi", use_container_width=True):
                _load_from_github.clear(); _fetch_from_sharepoint.clear()
                st.session_state.data_error = None; st.session_state.df = None
                st.rerun()

        elif st.session_state.df is not None:
            n        = len(st.session_state.df)
            elapsed  = time.time() - st.session_state.last_auto_fetch
            remain   = max(0, st.session_state.interval_min * 60 - elapsed)
            rm, rs   = int(remain // 60), int(remain % 60)
            st.markdown(
                f"<div style='padding:0 20px;font-size:10px;color:#777;margin-bottom:8px;'>"
                f"⏱ Auto-refresh: setiap <b style='color:#A8DADC'>{st.session_state.interval_min} mnt</b>"
                f" · next ~{rm}m {rs}s</div>",
                unsafe_allow_html=True,
            )
            if st.button("🔄 Refresh Sekarang", use_container_width=True):
                _load_from_github.clear(); _get_last_updated.clear()
                st.session_state.df = None; st.session_state.data_error = None
                st.session_state.result = None; st.session_state.fetch_count += 1
                st.session_state.last_auto_fetch = 0.0
                st.rerun()

        # ── NIM Search ────────────────────────────────────────────────────
        st.markdown("<div class='sb-section'>", unsafe_allow_html=True)
        st.markdown("<p class='sb-section-title'>🔍 Cari NIM Pengawas</p>", unsafe_allow_html=True)
        nim_input = st.text_input("NIM", placeholder="Masukkan NIM…",
                                  label_visibility="collapsed")
        if st.button("🔍  Cari Jadwal", use_container_width=True):
            if not nim_input.strip():
                st.warning("NIM tidak boleh kosong.")
            elif not nim_input.strip().isdigit():
                st.warning("Mohon masukkan NIM (angka), bukan nama.")
            elif st.session_state.df is None:
                st.error("Data belum dimuat.")
            else:
                r = search_nim(st.session_state.df, nim_input.strip())
                st.session_state.result       = r
                st.session_state.nim_searched = normalize_nim(nim_input.strip())
                st.session_state.ext_agendas  = []
                if not r.empty:
                    name, _ = get_name_role(r.iloc[0], nim_input.strip())
                    st.session_state.proctor_name = name
                else:
                    st.session_state.proctor_name = ""
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Agenda Eksternal ──────────────────────────────────────────────
        st.markdown("<div class='sb-section'>", unsafe_allow_html=True)
        st.markdown("<p class='sb-section-title'>📌 Tambah Agenda Eksternal</p>", unsafe_allow_html=True)
        res_now     = st.session_state.result
        unique_days = (
            sorted({str(d).strip() for d in res_now["Tanggal"].unique()}, key=day_rank)
            if res_now is not None and not res_now.empty else []
        )
        ext_day   = st.selectbox("Hari", options=unique_days or ["(cari NIM dulu)"],
                                 label_visibility="collapsed")
        st.markdown("<p class='sb-label-sm'>Judul Agenda</p>", unsafe_allow_html=True)
        ext_title = st.text_input("Judul", placeholder="cth: Rapat Organisasi",
                                  label_visibility="collapsed")
        cs, ce = st.columns(2)
        with cs:
            st.markdown("<p class='sb-label-sm'>Mulai</p>", unsafe_allow_html=True)
            ext_start = st.text_input("Mulai", value="08:00", label_visibility="collapsed")
        with ce:
            st.markdown("<p class='sb-label-sm'>Selesai</p>", unsafe_allow_html=True)
            ext_end = st.text_input("Selesai", value="10:00", label_visibility="collapsed")
        if st.button("➕ Tambah Agenda", use_container_width=True):
            if not ext_title.strip():
                st.warning("Judul wajib diisi.")
            elif ext_day == "(cari NIM dulu)":
                st.warning("Cari NIM terlebih dahulu.")
            else:
                sh = parse_ext_time(ext_start)
                eh = parse_ext_time(ext_end)
                if sh is None or eh is None: st.error("Format waktu salah (HH:MM).")
                elif eh <= sh: st.error("Waktu selesai harus setelah mulai.")
                else:
                    st.session_state.ext_agendas.append({
                        "day":ext_day, "title":ext_title.strip(),
                        "start":ext_start, "end":ext_end,
                        "start_h":sh, "end_h":eh,
                    })
                    st.success(f"✅ Ditambahkan!")
        if st.session_state.ext_agendas:
            st.markdown("<p class='sb-label-sm' style='margin-top:12px;'>Agenda Tersimpan</p>", unsafe_allow_html=True)
            for i, ea in enumerate(st.session_state.ext_agendas):
                c1, c2 = st.columns([5,1])
                with c1:
                    dn = ea["day"].split(",")[0] if "," in ea["day"] else ea["day"]
                    st.markdown(
                        f"<div style='background:#333;border-radius:8px;padding:7px 10px;margin-bottom:4px;'>"
                        f"<div style='font-size:12px;font-weight:600;color:#E4E4E4;'>{e(ea['title'])}</div>"
                        f"<div style='font-size:10px;color:#777;'>{e(dn)} · {e(ea['start'])}–{e(ea['end'])}</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                with c2:
                    if st.button("×", key=f"del_{i}"):
                        st.session_state.ext_agendas.pop(i); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════
    # TAB ADMIN
    # ══════════════════════════════════════════════════════════════════════
    with tab_admin:
        if not st.session_state.admin_logged_in:
            st.markdown("<div class='sb-section' style='padding-top:40px;text-align:center;'>", unsafe_allow_html=True)
            st.markdown("<p class='sb-section-title' style='text-align:center;'>Masuk sebagai Admin</p>", unsafe_allow_html=True)
            pwd = st.text_input("Password", type="password", placeholder="Password",
                                label_visibility="collapsed")
            if st.button("🔐 Login", use_container_width=True):
                try: correct = st.secrets.get("ADMIN_PASSWORD","admin123")
                except: correct = "admin123"
                if pwd == correct:
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("Password salah.")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='padding:10px 20px;font-size:11px;color:#6BCB77;'>✅ Login sebagai Admin</div>", unsafe_allow_html=True)

            # ── Manual Sync ───────────────────────────────────────────────
            st.markdown("<div class='sb-section'>", unsafe_allow_html=True)
            st.markdown("<p class='sb-section-title'>⚡ Manual Sync Sekarang</p>", unsafe_allow_html=True)
            st.markdown("<p class='sb-hint'>Ambil data terbaru dari SharePoint / GitHub tanpa menunggu jadwal otomatis.</p>", unsafe_allow_html=True)

            if st.button("🚀 Get Recent Update", use_container_width=True, type="primary"):
                try: gh_token = st.secrets.get("GH_PAT","")
                except: gh_token = ""
                ok, msg = trigger_github_actions(gh_token)
                st.session_state.admin_msg    = msg
                st.session_state.admin_msg_ok = ok
                if ok:
                    _load_from_github.clear(); _get_last_updated.clear()

            if st.button("🔄 Pull Data dari GitHub", use_container_width=True):
                _load_from_github.clear(); _get_last_updated.clear()
                st.session_state.df = None; st.session_state.data_error = None
                st.session_state.fetch_count += 1; st.session_state.last_auto_fetch = time.time()
                st.rerun()

            if st.session_state.admin_msg:
                cls = "sync-msg-ok" if st.session_state.admin_msg_ok else "sync-msg-err"
                icon = "✅" if st.session_state.admin_msg_ok else "❌"
                st.markdown(f"<div class='{cls}'>{icon} {e(st.session_state.admin_msg)}</div>",
                            unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # ── Interval ──────────────────────────────────────────────────
            st.markdown("<div class='sb-section'>", unsafe_allow_html=True)
            st.markdown("<p class='sb-section-title'>⏱ Interval Auto-Refresh</p>", unsafe_allow_html=True)
            st.markdown("<p class='sb-hint'>Atur seberapa sering Streamlit memperbarui data (minimum 5 menit).</p>", unsafe_allow_html=True)

            c_minus, c_val, c_plus = st.columns([1,2,1])
            with c_minus:
                if st.button("−", use_container_width=True):
                    st.session_state.interval_input = max(5, st.session_state.interval_input - 5)
            with c_val:
                st.markdown(
                    f"<div style='text-align:center;font-size:18px;font-weight:700;color:#E4E4E4;padding:8px 0;'>"
                    f"{st.session_state.interval_input} mnt</div>",
                    unsafe_allow_html=True,
                )
            with c_plus:
                if st.button("+", use_container_width=True):
                    st.session_state.interval_input = st.session_state.interval_input + 5

            st.markdown(f"<p style='font-size:10px;color:#777;text-align:center;margin:4px 0;'>Saat ini: <b style='color:#A8DADC'>{st.session_state.interval_min} mnt</b></p>", unsafe_allow_html=True)

            ca, cb = st.columns(2)
            with ca:
                if st.button("💾 Simpan", use_container_width=True):
                    st.session_state.interval_min = st.session_state.interval_input
                    st.success(f"✅ {st.session_state.interval_input} mnt")
            with cb:
                preset = st.selectbox("Preset", ["15 mnt","30 mnt","1 jam","2 jam","6 jam"],
                                      label_visibility="collapsed")
                if st.button("⚡ Pakai", use_container_width=True):
                    pmap = {"15 mnt":15,"30 mnt":30,"1 jam":60,"2 jam":120,"6 jam":360}
                    st.session_state.interval_min   = pmap[preset]
                    st.session_state.interval_input = pmap[preset]
                    st.success(f"✅ {preset}")
            st.markdown("</div>", unsafe_allow_html=True)

            # ── GitHub Actions info ───────────────────────────────────────
            st.markdown("<div class='sb-section'>", unsafe_allow_html=True)
            st.markdown("<p class='sb-section-title'>📋 Jadwal GitHub Actions</p>", unsafe_allow_html=True)
            st.markdown(
                "<p class='sb-hint'>Cron saat ini di "
                "<code style='color:#A8DADC'>.github/workflows/sync_jadwal.yml</code>: "
                "<code>0 * * * *</code> → tiap jam.<br>"
                "Format: <code>*/30 * * * *</code> = tiap 30 menit. "
                "<b>Minimum GitHub Actions: 5 menit</b></p>",
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

            # ── Reset ─────────────────────────────────────────────────────
            st.markdown("<div class='sb-section'>", unsafe_allow_html=True)
            st.markdown("<p class='sb-section-title'>🗑 Reset Data</p>", unsafe_allow_html=True)
            st.markdown("<p class='sb-hint'>Hapus semua cache dan agenda lokal.</p>", unsafe_allow_html=True)
            if not st.session_state.show_reset_confirm:
                if st.button("🗑 Reset Semua Data", use_container_width=True):
                    st.session_state.show_reset_confirm = True
                    st.rerun()
            else:
                st.markdown("<div class='sb-confirm'><p>Yakin ingin reset semua data?</p></div>",
                            unsafe_allow_html=True)
                cr1, cr2 = st.columns(2)
                with cr1:
                    if st.button("Ya, Reset", use_container_width=True):
                        for k in ["df","data_error","result","nim_searched",
                                  "proctor_name","ext_agendas","last_updated_str"]:
                            st.session_state[k] = _DEFAULTS.get(k)
                        _load_from_github.clear(); _fetch_from_sharepoint.clear()
                        st.session_state.show_reset_confirm = False
                        st.rerun()
                with cr2:
                    if st.button("Batal", use_container_width=True):
                        st.session_state.show_reset_confirm = False
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            # ── Logout ────────────────────────────────────────────────────
            st.markdown("<div style='padding:14px 20px;'>", unsafe_allow_html=True)
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.admin_logged_in = False
                st.session_state.admin_msg = ""
                st.session_state.show_reset_confirm = False
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # ── Footer — last updated ─────────────────────────────────────────────
    ts_display = st.session_state.last_updated_str or "—"
    n_rows     = len(st.session_state.df) if st.session_state.df is not None else 0
    st.markdown(
        f"<div class='sb-footer'>"
        f"<div class='sb-update-dot'></div>"
        f"<div>"
        f"<p class='sb-update-label'>Terakhir diperbarui</p>"
        f"<p class='sb-update-time'>{e(ts_display)}</p>"
        f"<p class='sb-update-rows'>{n_rows} baris data</p>"
        f"</div></div>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────────────────────────────────────
result = st.session_state.result
nim    = st.session_state.nim_searched
name   = st.session_state.proctor_name
ext    = st.session_state.ext_agendas

# ── Empty state ───────────────────────────────────────────────────────────────
if result is None or result.empty:
    if result is not None and result.empty:
        st.markdown(
            f"<div class='empty-state'>"
            f"<svg width='48' height='48' viewBox='0 0 24 24' fill='none' stroke='#444' stroke-width='1.4' stroke-linecap='round'><rect x='3' y='4' width='18' height='18' rx='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/><line x1='3' y1='10' x2='21' y2='10'/></svg>"
            f"<h2>NIM tidak ditemukan</h2>"
            f"<p>NIM <code style='color:#A8DADC'>{e(nim)}</code> tidak ada di kolom Pengawas 1 maupun Pengawas 2.</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div class='empty-state'>"
            "<svg width='48' height='48' viewBox='0 0 24 24' fill='none' stroke='#444' stroke-width='1.4' stroke-linecap='round'><rect x='3' y='4' width='18' height='18' rx='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/><line x1='3' y1='10' x2='21' y2='10'/></svg>"
            "<h2>Selamat datang di ProctorView</h2>"
            "<p>Masukkan NIM di sidebar untuk melihat jadwal pengawasan UAS.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
    st.stop()

# ── Detect conflicts ──────────────────────────────────────────────────────────
conflict_keys = detect_conflicts(result)   # set of (tanggal, jam) with >1 row
ext_conflicts  = detect_ext_conflicts(result, ext)
total_conflicts = len(conflict_keys) + len(ext_conflicts)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    f"<p class='mv-sup'>Jadwal Pengawas Ujian FIF</p>"
    f"<h1 class='mv-name'>{e(name)}</h1>"
    f"<div class='mv-badges'>"
    f"<span class='mv-nim'>{e(nim)}</span>"
    f"<span class='mv-sesi-count'>{len(result)} sesi pengawasan</span>"
    f"</div>",
    unsafe_allow_html=True,
)

# ── Stats ─────────────────────────────────────────────────────────────────────
honor = f"Rp {len(result) * HONOR_PER_SESSION:,}".replace(",",".")
conf_color = "#e06060" if total_conflicts > 0 else "#E4E4E4"
st.markdown(
    f"<div class='stats-row'>"
    f"<div class='stat-box'><p class='stat-value' style='color:#A8DADC'>{len(result)}</p><p class='stat-label'>Total Sesi</p></div>"
    f"<div class='stat-box'><p class='stat-value' style='color:#FFC1CC'>{e(honor)}</p><p class='stat-label'>Estimasi Honor</p></div>"
    f"<div class='stat-box'><p class='stat-value'>{len(ext)}</p><p class='stat-label'>Agenda Eksternal</p></div>"
    f"<div class='stat-box'><p class='stat-value' style='color:{conf_color}'>{total_conflicts}</p><p class='stat-label'>Konflik Jadwal</p></div>"
    f"</div>",
    unsafe_allow_html=True,
)

# ── Legend ────────────────────────────────────────────────────────────────────
used_slots = {str(j).strip() for j in result["Jam"]}
leg = "<div class='legend-row'>"
for slot, color in SLOT_COLOR.items():
    if slot in used_slots:
        leg += (f"<div class='legend-item'>"
                f"<span class='legend-dot' style='background:{color};'></span>"
                f"{e(slot)}</div>")
if ext:
    leg += ("<div class='legend-item'>"
            "<span class='legend-dot' style='background:#FFC1CC;'></span>Agenda Eksternal</div>")
leg += "</div>"
st.markdown(leg, unsafe_allow_html=True)

# ── Per-day sections ──────────────────────────────────────────────────────────
dates = sorted({str(d).strip() for d in result["Tanggal"].unique()}, key=day_rank)

for date in dates:
    date = str(date).strip()
    dr   = result[result["Tanggal"].astype(str).str.strip() == date]
    dex  = [a for a in ext if str(a["day"]).strip() == date]

    # Check if this day has any conflict
    day_has_conflict = any((date, str(r["Jam"]).strip()) in conflict_keys
                           for _, r in dr.iterrows())
    day_has_conflict |= any((day, slot, _) for (day, slot, _) in ext_conflicts if day == date)

    badge = " 🔴" if day_has_conflict else ""
    with st.expander(f"{e(date)}  ·  {len(dr)} sesi{badge}", expanded=True):
        # Group by slot (Jam)
        slots_in_day = sorted(dr["Jam"].unique(), key=time_rank)
        for slot in slots_in_day:
            slot_rows = dr[dr["Jam"].astype(str).str.strip() == slot]
            is_sched_conflict = (date, slot) in conflict_keys
            color = SLOT_COLOR.get(slot, "#777")

            if is_sched_conflict:
                st.markdown(
                    f"<div class='conflict-alert'>"
                    f"<svg width='15' height='15' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2.2' stroke-linecap='round'><path d='M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z'/><line x1='12' y1='9' x2='12' y2='13'/><line x1='12' y1='17' x2='12.01' y2='17'/></svg>"
                    f"<div><strong>Konflik Jadwal</strong>"
                    f" — {len(slot_rows)} jadwal pada sesi yang sama.</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            for _, row in slot_rows.iterrows():
                subj   = str(row.get("Nama MK","") or "").strip()
                room   = str(row.get("Ruangan","") or "").strip()
                kelas  = str(row.get("Kelas","") or "").strip()
                jenis  = str(row.get("Jenis Ujian","") or "").strip()
                _, role_label = get_name_role(row, nim)

                if role_label == "P1":
                    rbg, rclr = "rgba(168,218,220,0.18)", "#A8DADC"
                elif role_label == "P2":
                    rbg, rclr = "rgba(179,156,208,0.18)", "#B39CD0"
                else:
                    rbg, rclr = "rgba(100,100,100,0.18)", "#777"

                role_badge = (
                    f"<span class='role-badge' style='background:{rbg};color:{rclr};'>"
                    f"Pengawas {role_label[-1] if role_label.startswith('P') else role_label}</span>"
                )

                # Rekan pengawas
                rekan_parts = []
                for i in ["1","2","3"]:
                    r_nim  = normalize_nim(str(row.get(f"NIM (Pengawas {i})","") or ""))
                    r_nama = str(row.get(f"Nama Lengkap (Pengawas {i})","") or "").strip()
                    if r_nim and r_nim not in ("","NAN","NONE") and r_nim != nim.upper():
                        lbl = r_nama if r_nama and r_nama.lower() not in ("-","nan","none","") else r_nim
                        rekan_parts.append(f"<span class='scard-partner-chip'>{e(lbl)}</span>")

                rekan_html = ""
                if rekan_parts:
                    rekan_html = (
                        f"<div class='scard-partner'>"
                        f"<div style='font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:#555;margin-bottom:4px;'>Rekan Pengawas</div>"
                        f"{''.join(rekan_parts)}"
                        f"</div>"
                    )

                border_color = "#e06060" if is_sched_conflict else color
                st.markdown(
                    f"<div class='scard' style='border-left-color:{border_color};'>"
                    f"<div class='scard-top'>"
                    f"<span class='scard-time' style='color:{color};'>⏱ {e(slot)}</span>"
                    f"{role_badge}"
                    f"</div>"
                    f"<h3 class='scard-course'>{e(subj)}</h3>"
                    f"<p class='scard-room'>📍 {e(room)}</p>"
                    f"<div class='scard-meta'>"
                    f"<span class='scard-meta-item'>{e(kelas)}</span>"
                    f"<span style='color:#555'>·</span>"
                    f"<span class='scard-meta-item'>{e(jenis)}</span>"
                    f"</div>"
                    f"{rekan_html}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # External agendas for this day
        for ea in dex:
            is_ec = any(d == date and t == ea["title"] for d,_,t in ext_conflicts)
            bc    = "#e06060" if is_ec else "#FFC1CC"
            st.markdown(
                f"<div class='scard scard--agenda' style='border-left-color:{bc};'>"
                f"<div class='scard-top'>"
                f"<span class='scard-time' style='color:#FFC1CC;'>⏱ {e(ea['start'])} – {e(ea['end'])} WIB</span>"
                f"<span class='role-badge' style='background:rgba(255,193,204,.18);color:#FFC1CC;'>Eksternal</span>"
                f"</div>"
                f"<h3 class='scard-course'>{e(ea['title'])}</h3>"
                f"</div>",
                unsafe_allow_html=True,
            )