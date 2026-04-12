import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time
import re

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Jadwal Pengawas UTS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.main { background: #0D0F1A; }
[data-testid="stAppViewContainer"] { background: #0D0F1A; }
[data-testid="stSidebar"] {
    background: #111320 !important;
    border-right: 1px solid #1E2235;
}
[data-testid="stHeader"] { background: transparent; }

/* ── Typography ── */
h1,h2,h3 { font-family: 'Syne', sans-serif !important; }

/* ── Sidebar labels ── */
.sidebar-label {
    font-family: 'Syne', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #5B6A9A;
    margin: 18px 0 6px 0;
}

/* ── Metric cards ── */
.metric-card {
    background: #13162A;
    border: 1px solid #1E2235;
    border-radius: 16px;
    padding: 20px 22px;
    text-align: center;
    transition: border-color .2s;
}
.metric-card:hover { border-color: #4F6EF7; }
.metric-num {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    line-height: 1;
    background: linear-gradient(135deg, #4F6EF7, #A78BFA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-label { font-size: 12px; color: #5B6A9A; margin-top: 4px; }

/* ── Section header ── */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: #4F6EF7;
    border-left: 3px solid #4F6EF7;
    padding-left: 10px;
    margin: 28px 0 14px 0;
}

/* ── Conflict banner ── */
.conflict-banner {
    background: linear-gradient(135deg, #2D1010, #3D1515);
    border: 1px solid #E63946;
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 16px;
}
.conflict-title {
    font-family: 'Syne', sans-serif;
    font-size: 15px;
    font-weight: 700;
    color: #E63946;
    margin-bottom: 8px;
}
.conflict-item { font-size: 13px; color: #FFB3B3; margin: 4px 0; }

/* ── Schedule card ── */
.sched-card {
    background: #13162A;
    border: 1px solid #1E2235;
    border-left: 4px solid var(--accent, #4F6EF7);
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
    transition: transform .15s, border-color .15s;
}
.sched-card:hover { transform: translateX(4px); border-left-color: #A78BFA; }
.sched-mk { font-family: 'Syne', sans-serif; font-size: 14px; font-weight: 700; color: #E8ECF8; }
.sched-meta { font-size: 12px; color: #5B6A9A; margin-top: 5px; }
.sched-badge {
    display: inline-block;
    background: #1E2235;
    color: #A78BFA;
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 6px;
}
.conflict-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #E63946;
    margin-right: 6px;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%,100% { opacity:1; } 50% { opacity:.3; }
}

/* ── External agenda card ── */
.ext-card {
    background: #13162A;
    border: 1px solid #2A3A1A;
    border-left: 4px solid #2A9D8F;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
}

/* ── Name hero ── */
.name-hero {
    background: linear-gradient(135deg, #13162A, #1A1E35);
    border: 1px solid #1E2235;
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
}
.name-greeting { font-size: 12px; color: #5B6A9A; letter-spacing: .12em; text-transform: uppercase; }
.name-big {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #E8ECF8;
    margin: 4px 0 6px 0;
}
.nim-chip {
    background: #4F6EF7;
    color: #fff;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
}

/* ── Inputs ── */
[data-testid="stFileUploader"] {
    background: #13162A;
    border: 1.5px dashed #2A2E4A;
    border-radius: 14px;
    padding: 10px;
}
.stTextInput > div > div > input {
    background: #13162A !important;
    border: 1.5px solid #1E2235 !important;
    border-radius: 10px !important;
    color: #E8ECF8 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #4F6EF7 !important;
    box-shadow: 0 0 0 3px rgba(79,110,247,.15) !important;
}
.stButton > button {
    background: linear-gradient(135deg, #4F6EF7, #7C5CFC) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: .05em !important;
    padding: 10px 24px !important;
    transition: opacity .2s !important;
}
.stButton > button:hover { opacity: .85 !important; }

/* ── Time select ── */
[data-testid="stSelectbox"] > div > div {
    background: #13162A !important;
    border: 1.5px solid #1E2235 !important;
    border-radius: 10px !important;
    color: #E8ECF8 !important;
}

/* ── Divider ── */
hr { border-color: #1E2235 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0D0F1A; }
::-webkit-scrollbar-thumb { background: #2A2E4A; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

DAY_ORDER = {'senin': 0, 'selasa': 1, 'rabu': 2, 'kamis': 3, 'jumat': 4, 'sabtu': 5, 'minggu': 6}
DAY_EN    = {0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}

TIME_SLOTS = [
    '08.00 - 10.15 WIB',
    '10.45 - 13.00 WIB',
    '13.00 - 15.00 WIB',
    '13.30 - Selesai',
    '14.00 - 16.15 WIB',
    '18.30 - 20.30 WIB',
]

# Slot → (start_hour, end_hour) for overlap detection
TIME_RANGES = {
    '08.00 - 10.15 WIB': (8.00,  10.25),
    '10.45 - 13.00 WIB': (10.75, 13.00),
    '13.00 - 15.00 WIB': (13.00, 15.00),
    '13.30 - Selesai':   (13.50, 17.00),
    '14.00 - 16.15 WIB': (14.00, 16.25),
    '18.30 - 20.30 WIB': (18.50, 20.50),
}

SLOT_COLORS = {
    '08.00 - 10.15 WIB': '#4F6EF7',
    '10.45 - 13.00 WIB': '#F4A261',
    '13.00 - 15.00 WIB': '#2A9D8F',
    '13.30 - Selesai':   '#8338EC',
    '14.00 - 16.15 WIB': '#E9C46A',
    '18.30 - 20.30 WIB': '#E63946',
}
EXT_COLOR = '#2A9D8F'


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def day_rank(d: str) -> int:
    d = str(d).strip().lower()
    for k, v in DAY_ORDER.items():
        if d.startswith(k):
            return v
    return 99

def time_rank(t: str) -> int:
    t = str(t).strip()
    return TIME_SLOTS.index(t) if t in TIME_SLOTS else 99

def load_csv(file) -> pd.DataFrame:
    df = pd.read_csv(file, sep=';', skiprows=12, header=0)
    df.columns = df.columns.str.strip()
    df = df[df['Tanggal'].notna() & (df['Tanggal'].astype(str).str.strip() != '')].copy()
    for col in ['NIM (Pengawas 1)', 'NIM (Pengawas 2)', 'NIM (Pengawas 3)']:
        df[col] = df[col].astype(str).str.strip().str.lstrip('`').str.upper()
        df[col] = df[col].replace({'NAN': '', 'NONE': ''})
    return df

def search_nim(df: pd.DataFrame, nim: str) -> pd.DataFrame:
    nim = nim.strip().upper()
    mask = (
        (df['NIM (Pengawas 1)'] == nim) |
        (df['NIM (Pengawas 2)'] == nim) |
        (df['NIM (Pengawas 3)'] == nim)
    )
    result = df[mask].copy()
    result['_day']  = result['Tanggal'].apply(day_rank)
    result['_time'] = result['Jam'].apply(time_rank)
    return result.sort_values(['_day', '_time']).reset_index(drop=True)

def get_name(row, nim: str) -> str:
    nim = nim.strip().upper()
    for i in ['1', '2', '3']:
        if str(row.get(f'NIM (Pengawas {i})', '')).strip().upper() == nim:
            return str(row.get(f'Nama Lengkap (Pengawas {i})', '-')).strip()
    return '-'

def parse_ext_time(t: str):
    """Parse 'HH:MM' string to float hour."""
    try:
        h, m = map(int, t.split(':'))
        return h + m / 60
    except:
        return None

def overlaps(s1, e1, s2, e2):
    return s1 < e2 and s2 < e1

def detect_conflicts(schedule_rows, ext_agendas):
    """Return list of conflict dicts."""
    conflicts = []
    for _, srow in schedule_rows.iterrows():
        slot = str(srow['Jam']).strip()
        if slot not in TIME_RANGES:
            continue
        ss, se = TIME_RANGES[slot]
        day = str(srow['Tanggal']).strip()
        for ea in ext_agendas:
            if ea['day'] != day:
                continue
            es, ee = ea['start_h'], ea['end_h']
            if overlaps(ss, se, es, ee):
                conflicts.append({
                    'day': day,
                    'exam_slot': slot,
                    'exam_subject': str(srow['Nama MK']).strip(),
                    'exam_room': str(srow['Ruangan']).strip(),
                    'ext_title': ea['title'],
                    'ext_time': f"{ea['start']} – {ea['end']}",
                })
    return conflicts


# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY CALENDAR
# ─────────────────────────────────────────────────────────────────────────────

def build_calendar(schedule_df: pd.DataFrame, ext_agendas: list, conflicts: list) -> go.Figure:
    conflict_keys = set()
    for c in conflicts:
        conflict_keys.add((c['day'], c['exam_slot']))

    dates = sorted(schedule_df['Tanggal'].unique(), key=day_rank)
    all_slots = sorted(
        set(schedule_df['Jam'].tolist()) | {e['time_slot'] for e in ext_agendas if 'time_slot' in e},
        key=time_rank
    )
    if not all_slots:
        all_slots = TIME_SLOTS

    # Map slots → y index (inverted: slot 0 at top)
    slot_y = {s: i for i, s in enumerate(all_slots)}
    day_x  = {d: i for i, d in enumerate(dates)}

    fig = go.Figure()

    # ── Draw exam session cards ──────────────────────────────────────────────
    for _, row in schedule_df.iterrows():
        day  = str(row['Tanggal']).strip()
        slot = str(row['Jam']).strip()
        if day not in day_x or slot not in slot_y:
            continue
        xi = day_x[day]
        yi = slot_y[slot]
        color = SLOT_COLORS.get(slot, '#4F6EF7')
        is_conflict = (day, slot) in conflict_keys

        subject = str(row['Nama MK']).strip()
        room    = str(row['Ruangan']).strip()
        kelas   = str(row['Kelas']).strip()
        jenis   = str(row['Jenis Ujian']).strip()

        bg_color = 'rgba(227,50,60,0.15)' if is_conflict else f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.13)'
        border   = '#E63946' if is_conflict else color

        # Card shape
        fig.add_shape(
            type='rect',
            x0=xi + 0.04, x1=xi + 0.96,
            y0=yi + 0.04, y1=yi + 0.96,
            fillcolor=bg_color,
            line=dict(color=border, width=2),
            layer='below',
        )
        # Left accent bar
        fig.add_shape(
            type='rect',
            x0=xi + 0.04, x1=xi + 0.10,
            y0=yi + 0.04, y1=yi + 0.96,
            fillcolor=border,
            line=dict(width=0),
        )

        label = f"{'⚠️ ' if is_conflict else ''}<b>{subject}</b><br><span style='font-size:10px'>🏛 {room} | {kelas}</span><br><span style='font-size:10px;color:#999'>{jenis}</span>"
        fig.add_annotation(
            x=xi + 0.53, y=yi + 0.50,
            text=label,
            showarrow=False,
            font=dict(size=11, color='#E8ECF8'),
            align='left',
            xref='x', yref='y',
        )

    # ── Draw external agenda cards ───────────────────────────────────────────
    for ea in ext_agendas:
        day = ea['day']
        slot = ea.get('time_slot', '')
        if day not in day_x:
            continue
        xi = day_x[day]
        yi_base = max(slot_y.values()) + 1.5  # default below
        # Try to find closest slot
        ea_start = ea['start_h']
        best_slot, best_diff = None, 999
        for s, yi2 in slot_y.items():
            sr = TIME_RANGES.get(s)
            if sr and abs(sr[0] - ea_start) < best_diff:
                best_diff = abs(sr[0] - ea_start)
                best_slot = s
        yi = slot_y.get(best_slot, yi_base) if best_slot else yi_base

        is_conflict = any(c['day'] == day and c['ext_title'] == ea['title'] for c in conflicts)
        border = '#E63946' if is_conflict else EXT_COLOR
        bg     = 'rgba(227,50,60,0.12)' if is_conflict else 'rgba(42,157,143,0.13)'

        fig.add_shape(
            type='rect',
            x0=xi + 0.04, x1=xi + 0.96,
            y0=yi + 0.04, y1=yi + 0.96,
            fillcolor=bg,
            line=dict(color=border, width=2, dash='dot'),
            layer='below',
        )
        fig.add_annotation(
            x=xi + 0.50, y=yi + 0.50,
            text=f"{'⚠️ ' if is_conflict else '📌 '}<b>{ea['title']}</b><br><span style='font-size:10px'>{ea['start']} – {ea['end']}</span>",
            showarrow=False,
            font=dict(size=11, color='#C8FAF0'),
            align='center',
            xref='x', yref='y',
        )

    # ── Axes ────────────────────────────────────────────────────────────────
    fig.update_xaxes(
        tickvals=list(range(len(dates))),
        ticktext=[f"<b>{d.split(',')[0]}</b><br>{d.split(',')[1].strip()}" for d in dates],
        tickfont=dict(size=12, color='#A0AECF', family='Syne'),
        showgrid=False, zeroline=False,
        range=[-0.1, len(dates) - 0.1],
    )
    fig.update_yaxes(
        tickvals=list(range(len(all_slots))),
        ticktext=[f"<b>{s}</b>" for s in all_slots],
        tickfont=dict(size=10.5, color='#A0AECF', family='DM Sans'),
        showgrid=True, gridcolor='#1A1D30', gridwidth=1,
        zeroline=False,
        range=[len(all_slots) - 0.1, -0.5],
    )

    fig.update_layout(
        paper_bgcolor='#0D0F1A',
        plot_bgcolor='#0D0F1A',
        margin=dict(l=200, r=30, t=30, b=40),
        height=max(400, len(all_slots) * 110 + 80),
        showlegend=False,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if 'ext_agendas' not in st.session_state:
    st.session_state.ext_agendas = []
if 'df' not in st.session_state:
    st.session_state.df = None
if 'result' not in st.session_state:
    st.session_state.result = None
if 'nim_searched' not in st.session_state:
    st.session_state.nim_searched = ''
if 'proctor_name' not in st.session_state:
    st.session_state.proctor_name = ''


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 8px 0 20px 0;'>
        <span style='font-family:Syne;font-size:22px;font-weight:800;color:#E8ECF8;'>🎓 ProctorView</span><br>
        <span style='font-size:11px;color:#5B6A9A;letter-spacing:.08em;'>UTS Schedule Lookup</span>
    </div>
    """, unsafe_allow_html=True)

    # ── CSV Upload ──
    st.markdown('<div class="sidebar-label">📂 Data Source</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload CSV Daftar Pengawas", type=['csv'], label_visibility='collapsed')
    if uploaded:
        try:
            st.session_state.df = load_csv(uploaded)
            st.success(f"✅ {len(st.session_state.df)} baris dimuat")
        except Exception as e:
            st.error(f"Gagal membaca CSV: {e}")

    # ── NIM Search ──
    st.markdown('<div class="sidebar-label">🔍 Cari NIM</div>', unsafe_allow_html=True)
    nim_input = st.text_input("NIM Pengawas", placeholder="cth: 1302223029", label_visibility='collapsed')
    search_btn = st.button("🔍  Cari Jadwal", use_container_width=True)

    if search_btn and st.session_state.df is not None and nim_input.strip():
        result = search_nim(st.session_state.df, nim_input.strip())
        st.session_state.result = result
        st.session_state.nim_searched = nim_input.strip().upper()
        if not result.empty:
            st.session_state.proctor_name = get_name(result.iloc[0], nim_input.strip())
        else:
            st.session_state.proctor_name = ''
    elif search_btn and st.session_state.df is None:
        st.error("Upload CSV terlebih dahulu.")

    st.markdown("---")

    # ── External Agenda ──
    st.markdown('<div class="sidebar-label">📌 Tambah Agenda Eksternal</div>', unsafe_allow_html=True)

    unique_days = []
    if st.session_state.result is not None and not st.session_state.result.empty:
        unique_days = sorted(st.session_state.result['Tanggal'].unique(), key=day_rank)

    ext_day = st.selectbox(
        "Hari",
        options=unique_days if unique_days else ['(cari NIM dulu)'],
        label_visibility='visible',
    )
    ext_title = st.text_input("Judul Agenda", placeholder="cth: Rapat Organisasi", label_visibility='visible')

    col_s, col_e = st.columns(2)
    with col_s:
        ext_start = st.text_input("Mulai", value="08:00", placeholder="HH:MM", label_visibility='visible')
    with col_e:
        ext_end = st.text_input("Selesai", value="10:00", placeholder="HH:MM", label_visibility='visible')

    add_btn = st.button("➕  Tambah Agenda", use_container_width=True)

    if add_btn:
        if not ext_title.strip():
            st.warning("Isi judul agenda.")
        elif ext_day == '(cari NIM dulu)':
            st.warning("Cari NIM terlebih dahulu.")
        else:
            sh = parse_ext_time(ext_start)
            eh = parse_ext_time(ext_end)
            if sh is None or eh is None:
                st.error("Format waktu salah (HH:MM).")
            elif eh <= sh:
                st.error("Waktu selesai harus setelah mulai.")
            else:
                st.session_state.ext_agendas.append({
                    'day': ext_day,
                    'title': ext_title.strip(),
                    'start': ext_start,
                    'end': ext_end,
                    'start_h': sh,
                    'end_h': eh,
                })
                st.success(f"Agenda '{ext_title.strip()}' ditambahkan!")

    # Show existing ext agendas
    if st.session_state.ext_agendas:
        st.markdown('<div class="sidebar-label">📋 Agenda Eksternal</div>', unsafe_allow_html=True)
        for i, ea in enumerate(st.session_state.ext_agendas):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"<span style='color:#C8FAF0;font-size:12px;'>📌 <b>{ea['title']}</b><br>{ea['day'].split(',')[0]} | {ea['start']}–{ea['end']}</span>", unsafe_allow_html=True)
            with c2:
                if st.button("✕", key=f"del_{i}"):
                    st.session_state.ext_agendas.pop(i)
                    st.rerun()

    if st.session_state.ext_agendas:
        if st.button("🗑  Hapus Semua", use_container_width=True):
            st.session_state.ext_agendas = []
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────────────────────────────────────

result = st.session_state.result
nim    = st.session_state.nim_searched
name   = st.session_state.proctor_name
ext    = st.session_state.ext_agendas

# ── Empty state ──────────────────────────────────────────────────────────────
if result is None or result.empty:
    if result is not None and result.empty:
        st.markdown(f"""
        <div style='text-align:center;padding:80px 0;'>
            <div style='font-size:48px;margin-bottom:16px;'>🔍</div>
            <div style='font-family:Syne;font-size:22px;font-weight:700;color:#E8ECF8;'>NIM tidak ditemukan</div>
            <div style='color:#5B6A9A;margin-top:8px;'>NIM <code style='color:#4F6EF7'>{nim}</code> tidak ada dalam daftar pengawas</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align:center;padding:80px 0;'>
            <div style='font-size:48px;margin-bottom:16px;'>🎓</div>
            <div style='font-family:Syne;font-size:24px;font-weight:700;color:#E8ECF8;'>ProctorView</div>
            <div style='color:#5B6A9A;margin-top:10px;font-size:15px;'>Upload CSV dan masukkan NIM untuk melihat jadwal pengawasan</div>
            <div style='color:#2A2E4A;margin-top:32px;font-size:13px;'>← Gunakan panel kiri untuk memulai</div>
        </div>
        """, unsafe_allow_html=True)
    st.stop()


# ── Conflict detection ───────────────────────────────────────────────────────
conflicts = detect_conflicts(result, ext)

# ── Name hero ───────────────────────────────────────────────────────────────
conflict_badge = f"<span style='background:#E63946;color:white;border-radius:20px;padding:3px 12px;font-size:11px;font-weight:700;margin-left:10px;'>⚠️ {len(conflicts)} KONFLIK</span>" if conflicts else ""
st.markdown(f"""
<div class="name-hero">
    <div class="name-greeting">Jadwal Pengawas UTS FIF</div>
    <div class="name-big">{name} {conflict_badge}</div>
    <span class="nim-chip">{nim}</span>
    <span style='color:#5B6A9A;font-size:12px;margin-left:12px;'>{len(result)} sesi pengawasan</span>
</div>
""", unsafe_allow_html=True)

# ── Metrics ──────────────────────────────────────────────────────────────────
n_days    = result['Tanggal'].nunique()
n_ext     = len(ext)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-num">{len(result)}</div><div class="metric-label">Total Sesi</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><div class="metric-num">{n_days}</div><div class="metric-label">Hari Aktif</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><div class="metric-num">{n_ext}</div><div class="metric-label">Agenda Eksternal</div></div>', unsafe_allow_html=True)
with c4:
    conflict_color = '#E63946' if conflicts else '#2A9D8F'
    st.markdown(f'<div class="metric-card"><div class="metric-num" style="background:linear-gradient(135deg,{conflict_color},{conflict_color});-webkit-background-clip:text;">{len(conflicts)}</div><div class="metric-label">Konflik Jadwal</div></div>', unsafe_allow_html=True)

# ── Conflict banners ─────────────────────────────────────────────────────────
if conflicts:
    st.markdown('<div class="section-header">⚠️ Konflik Terdeteksi</div>', unsafe_allow_html=True)
    for c in conflicts:
        st.markdown(f"""
        <div class="conflict-banner">
            <div class="conflict-title">⚠️ Konflik pada {c['day'].split(',')[0]}</div>
            <div class="conflict-item">
                🏫 <b>Pengawasan:</b> {c['exam_subject']} · {c['exam_slot']} · {c['exam_room']}
            </div>
            <div class="conflict-item">
                📌 <b>Agenda Eksternal:</b> {c['ext_title']} · {c['ext_time']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Calendar ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📅 Kalender Jadwal</div>', unsafe_allow_html=True)
fig = build_calendar(result, ext, conflicts)
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ── Per-day schedule list ────────────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Rincian Per Hari</div>', unsafe_allow_html=True)
dates = sorted(result['Tanggal'].unique(), key=day_rank)

for date in dates:
    day_rows = result[result['Tanggal'] == date]
    day_ext  = [e for e in ext if e['day'] == date]
    day_name = date.split(',')[0].strip()
    date_str = date.split(',')[1].strip() if ',' in date else date

    with st.expander(f"**{day_name}** — {date_str}  ·  {len(day_rows)} sesi pengawasan", expanded=True):
        for _, row in day_rows.iterrows():
            slot    = str(row['Jam']).strip()
            subject = str(row['Nama MK']).strip()
            room    = str(row['Ruangan']).strip()
            kelas   = str(row['Kelas']).strip()
            jenis   = str(row['Jenis Ujian']).strip()
            color   = SLOT_COLORS.get(slot, '#4F6EF7')
            is_conf = (date, slot) in {(c['day'], c['exam_slot']) for c in conflicts}

            conf_html = '<span class="conflict-dot"></span><span style="color:#E63946;font-size:11px;font-weight:600;">KONFLIK</span>' if is_conf else ''
            st.markdown(f"""
            <div class="sched-card" style="--accent:{color}">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div class="sched-mk">{subject}</div>
                    <div>{conf_html}</div>
                </div>
                <div class="sched-meta">
                    <span class="sched-badge">⏰ {slot}</span>
                    <span class="sched-badge">🏛 {room}</span>
                    <span class="sched-badge">👥 {kelas}</span>
                    <span class="sched-badge">{jenis}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if day_ext:
            st.markdown('<div style="color:#5B6A9A;font-size:11px;letter-spacing:.08em;text-transform:uppercase;margin:12px 0 6px 0;">📌 Agenda Eksternal</div>', unsafe_allow_html=True)
            for ea in day_ext:
                is_conf_ext = any(c['day'] == date and c['ext_title'] == ea['title'] for c in conflicts)
                border_ext  = '#E63946' if is_conf_ext else EXT_COLOR
                st.markdown(f"""
                <div class="ext-card" style="border-left-color:{border_ext}">
                    <div class="sched-mk" style="color:#C8FAF0;">{'⚠️ ' if is_conf_ext else '📌 '}{ea['title']}</div>
                    <div class="sched-meta">
                        <span class="sched-badge" style="color:#2A9D8F;">⏰ {ea['start']} – {ea['end']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)