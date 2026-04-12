import streamlit as st
import pandas as pd
import html as html_lib

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ProctorView – Jadwal Pengawas UTS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
[data-testid="stAppViewContainer"] { background: #0B0D1A; }
[data-testid="stSidebar"]          { background: #0F1120 !important; border-right: 1px solid #1C2040; }
[data-testid="stHeader"]           { background: transparent; }
section[data-testid="stSidebar"] > div { padding-top: 1.5rem; }
h1,h2,h3,h4 { font-family: 'Syne', sans-serif !important; color: #E8ECF8; }

.stTextInput > div > div > input {
    background: #12152A !important; border: 1.5px solid #1C2040 !important;
    border-radius: 10px !important; color: #E8ECF8 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 13px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #4F6EF7 !important;
    box-shadow: 0 0 0 3px rgba(79,110,247,.15) !important;
}
[data-testid="stFileUploader"] {
    background: #12152A; border: 1.5px dashed #1C2040; border-radius: 12px;
}
.stButton > button {
    background: linear-gradient(135deg,#4F6EF7,#7C5CFC) !important;
    color:#fff !important; border:none !important; border-radius:10px !important;
    font-family:'Syne',sans-serif !important; font-weight:700 !important;
    letter-spacing:.04em !important; transition:opacity .2s !important;
}
.stButton > button:hover { opacity:.82 !important; }

.slabel {
    font-family:'Syne',sans-serif; font-size:10px; font-weight:700;
    letter-spacing:.14em; text-transform:uppercase; color:#3D4A7A; margin:20px 0 6px;
}
hr { border-color:#1C2040 !important; }

.mcard { background:#12152A; border:1px solid #1C2040; border-radius:14px; padding:18px 16px; text-align:center; }
.mnum {
    font-family:'Syne',sans-serif; font-size:2.2rem; font-weight:800; line-height:1;
    background:linear-gradient(135deg,#4F6EF7,#A78BFA);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.mnum-red { background:linear-gradient(135deg,#E63946,#FF6B6B) !important; }
.mlbl { font-size:11px; color:#3D4A7A; margin-top:5px; }

.sec-h {
    font-family:'Syne',sans-serif; font-size:11px; font-weight:700;
    letter-spacing:.12em; text-transform:uppercase; color:#4F6EF7;
    border-left:3px solid #4F6EF7; padding-left:10px; margin:28px 0 14px;
}

.cbanner { background:linear-gradient(135deg,#1E0A0A,#2C0F0F); border:1px solid #E63946; border-radius:12px; padding:16px 20px; margin-bottom:12px; }
.ctitle  { font-family:'Syne',sans-serif; font-size:14px; font-weight:700; color:#E63946; margin-bottom:8px; }
.citem   { font-size:12px; color:#FFB3B3; margin:3px 0; line-height:1.5; }

.hero { background:linear-gradient(135deg,#12152A 0%,#181D3A 100%); border:1px solid #1C2040; border-radius:18px; padding:26px 30px; margin-bottom:22px; }
.hero-label { font-size:11px; color:#3D4A7A; letter-spacing:.12em; text-transform:uppercase; }
.hero-name  { font-family:'Syne',sans-serif; font-size:1.9rem; font-weight:800; color:#E8ECF8; margin:4px 0 8px; }
.nim-pill   { background:#4F6EF7; color:#fff; border-radius:20px; padding:3px 14px; font-size:11px; font-weight:700; display:inline-block; }
.conf-pill  { background:#E63946; color:#fff; border-radius:20px; padding:3px 12px; font-size:11px; font-weight:700; display:inline-block; margin-left:8px; }

.lcard { background:#12152A; border:1px solid #1C2040; border-left:4px solid var(--ac,#4F6EF7); border-radius:11px; padding:13px 16px; margin-bottom:9px; }
.lcard-title { font-family:'Syne',sans-serif; font-size:13px; font-weight:700; color:#E8ECF8; }
.lcard-meta  { font-size:11px; color:#3D4A7A; margin-top:6px; }
.badge { display:inline-block; background:#1C2040; color:#A78BFA; border-radius:5px; padding:2px 7px; font-size:10px; font-weight:600; margin-right:5px; }
.ext-lcard { background:#0E1A18; border:1px solid #1A3530; border-left:4px solid #2A9D8F; border-radius:11px; padding:13px 16px; margin-bottom:9px; }

/* ─── CALENDAR ─── */
.cal-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; margin-bottom: 32px; }

.cal-table {
    border-collapse: separate;
    border-spacing: 5px;
    width: 100%;
    table-layout: fixed;
}

/* corner + time column */
.th-corner { width: 145px; background: transparent; border: none; }
.td-time {
    width: 145px;
    background: transparent;
    border: none;
    vertical-align: middle;
    padding: 6px 10px 6px 0;
    text-align: right;
}
.td-time span {
    font-family: 'Syne', sans-serif;
    font-size: 10px;
    font-weight: 700;
    color: #3D4A7A;
    letter-spacing: .06em;
    white-space: nowrap;
}

/* day header */
.th-day {
    background: #12152A;
    border: 1px solid #1C2040;
    border-radius: 10px;
    padding: 12px 10px;
    text-align: center;
    vertical-align: middle;
}
.th-day-name { font-family:'Syne',sans-serif; font-size:13px; font-weight:700; color:#E8ECF8; }
.th-day-date { font-size:10px; color:#3D4A7A; margin-top:3px; }

/* empty cell */
.td-empty {
    background: #0D0F1C;
    border: 1px solid #141726;
    border-radius: 10px;
    min-height: 110px;
}

/* filled cell wrapper — no padding, contains stacked items */
.td-fill {
    vertical-align: top;
    background: transparent;
    border: none;
    padding: 0;
}

/* individual exam card inside cell */
.c-exam {
    border-radius: 10px;
    border-left: 4px solid var(--ac, #4F6EF7);
    background: var(--bg, #0E1228);
    outline: 2px solid transparent;
    outline-offset: -2px;
    padding: 10px 11px 10px 12px;
    margin-bottom: 5px;
    box-sizing: border-box;
    position: relative;
    overflow: hidden;
    min-height: 110px;
}
.c-exam.conflict { outline: 2px solid #E63946; }

.c-exam-mk   { font-family:'Syne',sans-serif; font-size:11.5px; font-weight:700; color:#E8ECF8; line-height:1.35; margin-bottom:7px; }
.c-exam-room { font-size:10px; color:#8B9AC8; margin-bottom:3px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.c-exam-kls  { font-size:9.5px; color:#5B6A9A; }
.c-exam-type { font-size:9px; color:#3D4A7A; font-style:italic; margin-top:5px; }

/* conflict badge inside card */
.c-conf-tag {
    position: absolute; top: 7px; right: 7px;
    background: #E63946; color: #fff;
    border-radius: 4px; padding: 1px 5px;
    font-size: 8.5px; font-weight: 700; letter-spacing:.03em;
    white-space: nowrap;
}

/* external card inside cell */
.c-ext {
    border-radius: 10px;
    border: 2px dashed #2A9D8F;
    border-left: 4px solid #2A9D8F;
    background: #0A1714;
    padding: 10px 11px 10px 12px;
    margin-bottom: 5px;
    box-sizing: border-box;
    position: relative;
    overflow: hidden;
    min-height: 90px;
}
.c-ext.conflict { border-color: #E63946; }
.c-ext-icon  { font-size: 13px; margin-bottom: 4px; }
.c-ext-title { font-family:'Syne',sans-serif; font-size:11px; font-weight:700; color:#C8FAF0; line-height:1.35; margin-bottom:5px; }
.c-ext-time  { font-size:10px; color:#2A9D8F; }

/* legend */
.legend-row { display:flex; flex-wrap:wrap; gap:10px; margin-bottom:18px; align-items:center; }
.legend-dot  { display:inline-block; width:11px; height:11px; border-radius:3px; margin-right:5px; flex-shrink:0; }
.legend-item { font-size:11px; color:#5B6A9A; display:flex; align-items:center; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
DAY_ORDER = {'senin':0,'selasa':1,'rabu':2,'kamis':3,'jumat':4,'sabtu':5,'minggu':6}

TIME_SLOTS = [
    '08.00 - 10.15 WIB',
    '10.45 - 13.00 WIB',
    '13.00 - 15.00 WIB',
    '13.30 - Selesai',
    '14.00 - 16.15 WIB',
    '18.30 - 20.30 WIB',
]

TIME_RANGES = {
    '08.00 - 10.15 WIB': (8.00,  10.25),
    '10.45 - 13.00 WIB': (10.75, 13.00),
    '13.00 - 15.00 WIB': (13.00, 15.00),
    '13.30 - Selesai':   (13.50, 17.00),
    '14.00 - 16.15 WIB': (14.00, 16.25),
    '18.30 - 20.30 WIB': (18.50, 20.50),
}

SLOT_STYLE = {
    '08.00 - 10.15 WIB': ('#4F6EF7', '#0E1228'),
    '10.45 - 13.00 WIB': ('#F4A261', '#1A1208'),
    '13.00 - 15.00 WIB': ('#2A9D8F', '#0B1A18'),
    '13.30 - Selesai':   ('#8338EC', '#130E20'),
    '14.00 - 16.15 WIB': ('#E9C46A', '#1A1808'),
    '18.30 - 20.30 WIB': ('#E63946', '#1A080A'),
}
DEFAULT_STYLE = ('#4F6EF7', '#0E1228')
EXT_COLOR = '#2A9D8F'


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def day_rank(d):
    d = str(d).strip().lower()
    for k, v in DAY_ORDER.items():
        if d.startswith(k): return v
    return 99

def time_rank(t):
    t = str(t).strip()
    return TIME_SLOTS.index(t) if t in TIME_SLOTS else 99

def load_csv(file):
    df = pd.read_csv(file, sep=';', skiprows=12, header=0)
    df.columns = df.columns.str.strip()
    df = df[df['Tanggal'].notna() & (df['Tanggal'].astype(str).str.strip() != '')].copy()
    for col in ['NIM (Pengawas 1)', 'NIM (Pengawas 2)', 'NIM (Pengawas 3)']:
        df[col] = df[col].astype(str).str.strip().str.lstrip('`').str.upper()
        df[col] = df[col].replace({'NAN':'','NONE':''})
    return df

def search_nim(df, nim):
    nim = nim.strip().upper()
    mask = (
        (df['NIM (Pengawas 1)'] == nim) |
        (df['NIM (Pengawas 2)'] == nim) |
        (df['NIM (Pengawas 3)'] == nim)
    )
    r = df[mask].copy()
    r['_day']  = r['Tanggal'].apply(day_rank)
    r['_time'] = r['Jam'].apply(time_rank)
    return r.sort_values(['_day','_time']).reset_index(drop=True)

def get_name(row, nim):
    nim = nim.strip().upper()
    for i in ['1','2','3']:
        v = str(row.get(f'NIM (Pengawas {i})','') or '').strip().upper()
        if v == nim:
            return str(row.get(f'Nama Lengkap (Pengawas {i})','') or '-').strip()
    return '-'

def parse_ext_time(t):
    try:
        h, m = map(int, t.split(':'))
        return h + m/60
    except: return None

def overlaps(s1,e1,s2,e2): return s1 < e2 and s2 < e1

def detect_conflicts(schedule_df, ext_agendas):
    conflicts = []
    for _, srow in schedule_df.iterrows():
        slot = str(srow['Jam']).strip()
        if slot not in TIME_RANGES: continue
        ss, se = TIME_RANGES[slot]
        day = str(srow['Tanggal']).strip()
        for ea in ext_agendas:
            if ea['day'] != day: continue
            if overlaps(ss, se, ea['start_h'], ea['end_h']):
                conflicts.append({
                    'day': day,
                    'exam_slot': slot,
                    'exam_subject': str(srow['Nama MK']).strip(),
                    'exam_room': str(srow['Ruangan']).strip(),
                    'ext_title': ea['title'],
                    'ext_time': f"{ea['start']} – {ea['end']}",
                })
    return conflicts

def ext_to_slot(ea):
    """Map an external agenda to the nearest TIME_SLOT by start time."""
    best, bdiff = None, 999
    for s, rng in TIME_RANGES.items():
        diff = abs(rng[0] - ea['start_h'])
        if diff < bdiff:
            bdiff, best = diff, s
    return best


# ─────────────────────────────────────────────────────────────────────────────
# CALENDAR HTML — pure table, no Plotly
# ─────────────────────────────────────────────────────────────────────────────
def build_calendar_html(schedule_df, ext_agendas, conflicts):
    conflict_exam_keys = {(c['day'], c['exam_slot']) for c in conflicts}
    conflict_ext_keys  = {(c['day'], c['ext_title'])  for c in conflicts}

    dates = sorted(schedule_df['Tanggal'].unique(), key=day_rank)

    # Determine active slots (only rows that have at least one item)
    used = set(schedule_df['Jam'].astype(str).str.strip().tolist())
    for ea in ext_agendas:
        s = ext_to_slot(ea)
        if s: used.add(s)
    active_slots = [s for s in TIME_SLOTS if s in used]
    if not active_slots:
        active_slots = TIME_SLOTS[:]

    # Lookups
    exam_lk: dict = {}
    for _, row in schedule_df.iterrows():
        k = (str(row['Tanggal']).strip(), str(row['Jam']).strip())
        exam_lk.setdefault(k, []).append(row)

    ext_lk: dict = {}
    for ea in ext_agendas:
        s = ext_to_slot(ea)
        if s:
            ext_lk.setdefault((ea['day'], s), []).append(ea)

    def e(s): return html_lib.escape(str(s))

    out = ['<div class="cal-wrap"><table class="cal-table">']

    # ── Header ───────────────────────────────────────────────────────────────
    out.append('<thead><tr>')
    out.append('<th class="th-corner"></th>')
    for date in dates:
        parts    = date.split(',', 1)
        day_name = parts[0].strip()
        date_str = parts[1].strip() if len(parts) > 1 else ''
        out.append(
            f'<th class="th-day">'
            f'<div class="th-day-name">{e(day_name)}</div>'
            f'<div class="th-day-date">{e(date_str)}</div>'
            f'</th>'
        )
    out.append('</tr></thead>')

    # ── Body ─────────────────────────────────────────────────────────────────
    out.append('<tbody>')
    for slot in active_slots:
        accent, bg = SLOT_STYLE.get(slot, DEFAULT_STYLE)
        out.append('<tr>')
        out.append(f'<td class="td-time"><span>{e(slot)}</span></td>')

        for date in dates:
            key   = (date, slot)
            exams = exam_lk.get(key, [])
            exts  = ext_lk.get(key, [])

            if not exams and not exts:
                out.append('<td class="td-empty"></td>')
                continue

            items = []

            for row in exams:
                mk    = e(str(row.get('Nama MK','') or '').strip())
                room  = e(str(row.get('Ruangan','') or '').strip())
                kelas = e(str(row.get('Kelas','') or '').strip())
                jenis = e(str(row.get('Jenis Ujian','') or '').strip())
                is_c  = key in conflict_exam_keys
                cf    = ' conflict' if is_c else ''
                ct    = '<div class="c-conf-tag">⚠ KONFLIK</div>' if is_c else ''
                items.append(
                    f'<div class="c-exam{cf}" style="--ac:{accent};--bg:{bg};">'
                    f'{ct}'
                    f'<div class="c-exam-mk">{mk}</div>'
                    f'<div class="c-exam-room">🏛 {room}</div>'
                    f'<div class="c-exam-kls">👥 {kelas}</div>'
                    f'<div class="c-exam-type">{jenis}</div>'
                    f'</div>'
                )

            for ea in exts:
                is_c = (date, ea['title']) in conflict_ext_keys
                cf   = ' conflict' if is_c else ''
                ct   = '<div class="c-conf-tag">⚠ KONFLIK</div>' if is_c else ''
                items.append(
                    f'<div class="c-ext{cf}">'
                    f'{ct}'
                    f'<div class="c-ext-icon">📌</div>'
                    f'<div class="c-ext-title">{e(ea["title"])}</div>'
                    f'<div class="c-ext-time">⏰ {e(ea["start"])} – {e(ea["end"])}</div>'
                    f'</div>'
                )

            out.append(f'<td class="td-fill">{"".join(items)}</td>')

        out.append('</tr>')

    out.append('</tbody></table></div>')
    return '\n'.join(out)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
for key, val in [
    ('ext_agendas', []),
    ('df', None),
    ('result', None),
    ('nim_searched', ''),
    ('proctor_name', ''),
]:
    if key not in st.session_state:
        st.session_state[key] = val


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:6px 0 22px;'>
        <span style='font-family:Syne;font-size:20px;font-weight:800;color:#E8ECF8;'>🎓 ProctorView</span><br>
        <span style='font-size:10px;color:#3D4A7A;letter-spacing:.1em;'>UTS SCHEDULE LOOKUP</span>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="slabel">📂 Data Source</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload CSV", type=['csv'], label_visibility='collapsed')
    if uploaded:
        try:
            st.session_state.df = load_csv(uploaded)
            st.success(f"✅ {len(st.session_state.df)} baris dimuat")
        except Exception as ex:
            st.error(f"Gagal membaca CSV: {ex}")

    st.markdown('<div class="slabel">🔍 Cari NIM Pengawas</div>', unsafe_allow_html=True)
    nim_input  = st.text_input("NIM", placeholder="cth: 1302223029", label_visibility='collapsed')
    search_btn = st.button("🔍  Cari Jadwal", use_container_width=True)

    if search_btn:
        if st.session_state.df is None:
            st.error("Upload CSV terlebih dahulu.")
        elif not nim_input.strip():
            st.warning("Masukkan NIM.")
        else:
            r = search_nim(st.session_state.df, nim_input.strip())
            st.session_state.result       = r
            st.session_state.nim_searched = nim_input.strip().upper()
            st.session_state.proctor_name = get_name(r.iloc[0], nim_input.strip()) if not r.empty else ''
            st.session_state.ext_agendas  = []

    st.markdown('<hr>', unsafe_allow_html=True)

    st.markdown('<div class="slabel">📌 Tambah Agenda Eksternal</div>', unsafe_allow_html=True)
    res_now = st.session_state.result
    unique_days = (
        sorted(res_now['Tanggal'].unique(), key=day_rank)
        if res_now is not None and not res_now.empty else []
    )
    ext_day   = st.selectbox("Hari", options=unique_days or ['(cari NIM dulu)'])
    ext_title = st.text_input("Judul Agenda", placeholder="cth: Rapat Organisasi")
    col_s, col_e = st.columns(2)
    with col_s: ext_start = st.text_input("Mulai",   value="08:00")
    with col_e: ext_end   = st.text_input("Selesai", value="10:00")

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
                st.error("Waktu selesai harus setelah waktu mulai.")
            else:
                st.session_state.ext_agendas.append({
                    'day': ext_day, 'title': ext_title.strip(),
                    'start': ext_start, 'end': ext_end,
                    'start_h': sh, 'end_h': eh,
                })
                st.success(f"✅ '{ext_title.strip()}' ditambahkan!")

    if st.session_state.ext_agendas:
        st.markdown('<div class="slabel">📋 Daftar Agenda</div>', unsafe_allow_html=True)
        for i, ea in enumerate(st.session_state.ext_agendas):
            c1, c2 = st.columns([5,1])
            with c1:
                ds = ea['day'].split(',')[0] if ',' in ea['day'] else ea['day']
                st.markdown(
                    f"<div style='font-size:11px;color:#C8FAF0;'><b>{ea['title']}</b></div>"
                    f"<div style='font-size:10px;color:#3D4A7A;'>{ds} · {ea['start']}–{ea['end']}</div>",
                    unsafe_allow_html=True
                )
            with c2:
                if st.button("✕", key=f"del_{i}"):
                    st.session_state.ext_agendas.pop(i)
                    st.rerun()
        if st.button("🗑 Hapus Semua", use_container_width=True):
            st.session_state.ext_agendas = []
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
result = st.session_state.result
nim    = st.session_state.nim_searched
name   = st.session_state.proctor_name
ext    = st.session_state.ext_agendas

def e(s): return html_lib.escape(str(s))

# ── Empty states ──────────────────────────────────────────────────────────────
if result is None or result.empty:
    if result is not None and result.empty:
        body = (f'<div style="font-family:Syne;font-size:18px;font-weight:700;color:#E8ECF8;">NIM tidak ditemukan</div>'
                f'<div style="color:#3D4A7A;margin-top:8px;">NIM <code style="color:#4F6EF7">{e(nim)}</code> tidak ada dalam data.</div>')
    else:
        body = ('<div style="font-family:Syne;font-size:22px;font-weight:700;color:#E8ECF8;">ProctorView</div>'
                '<div style="color:#3D4A7A;margin-top:10px;">Upload CSV &amp; masukkan NIM untuk melihat jadwal pengawasan.</div>'
                '<div style="color:#1C2040;margin-top:28px;font-size:12px;">← Gunakan panel kiri untuk memulai</div>')
    st.markdown(f'<div style="text-align:center;padding:80px 0;"><div style="font-size:44px;margin-bottom:16px;">🎓</div>{body}</div>', unsafe_allow_html=True)
    st.stop()

# ── Conflicts ─────────────────────────────────────────────────────────────────
conflicts = detect_conflicts(result, ext)

# ── Hero ─────────────────────────────────────────────────────────────────────
cp = f'<span class="conf-pill">⚠️ {len(conflicts)} KONFLIK</span>' if conflicts else ''
st.markdown(f"""
<div class="hero">
    <div class="hero-label">Jadwal Pengawas UTS FIF</div>
    <div class="hero-name">{e(name)} {cp}</div>
    <span class="nim-pill">{e(nim)}</span>
    <span style="color:#3D4A7A;font-size:11px;margin-left:10px;">{len(result)} sesi pengawasan</span>
</div>
""", unsafe_allow_html=True)

# ── Metrics ───────────────────────────────────────────────────────────────────
m1,m2,m3,m4 = st.columns(4)
with m1: st.markdown(f'<div class="mcard"><div class="mnum">{len(result)}</div><div class="mlbl">Total Sesi</div></div>', unsafe_allow_html=True)
with m2: st.markdown(f'<div class="mcard"><div class="mnum">{result["Tanggal"].nunique()}</div><div class="mlbl">Hari Aktif</div></div>', unsafe_allow_html=True)
with m3: st.markdown(f'<div class="mcard"><div class="mnum">{len(ext)}</div><div class="mlbl">Agenda Eksternal</div></div>', unsafe_allow_html=True)
with m4:
    rcls = ' mnum-red' if conflicts else ''
    st.markdown(f'<div class="mcard"><div class="mnum{rcls}">{len(conflicts)}</div><div class="mlbl">Konflik Jadwal</div></div>', unsafe_allow_html=True)

# ── Conflict banners ──────────────────────────────────────────────────────────
if conflicts:
    st.markdown('<div class="sec-h">⚠️ Konflik Terdeteksi</div>', unsafe_allow_html=True)
    for c in conflicts:
        ds = c['day'].split(',')[0].strip()
        st.markdown(f"""
        <div class="cbanner">
            <div class="ctitle">⚠️ Konflik — {e(ds)}</div>
            <div class="citem">🏫 <b>Pengawasan:</b> {e(c['exam_subject'])} &nbsp;·&nbsp; {e(c['exam_slot'])} &nbsp;·&nbsp; {e(c['exam_room'])}</div>
            <div class="citem">📌 <b>Eksternal:</b> {e(c['ext_title'])} &nbsp;·&nbsp; {e(c['ext_time'])}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Calendar ──────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-h">📅 Kalender Jadwal</div>', unsafe_allow_html=True)

# Legend
used_slots = set(result['Jam'].astype(str).str.strip().tolist())
leg = '<div class="legend-row">'
for slot, (ac, _) in SLOT_STYLE.items():
    if slot in used_slots:
        leg += f'<div class="legend-item"><span class="legend-dot" style="background:{ac};"></span>{e(slot)}</div>'
if ext:
    leg += f'<div class="legend-item"><span class="legend-dot" style="background:{EXT_COLOR};border:2px dashed {EXT_COLOR};box-sizing:border-box;"></span>Agenda Eksternal</div>'
if conflicts:
    leg += '<div class="legend-item"><span class="legend-dot" style="background:#E63946;"></span>Konflik</div>'
leg += '</div>'
st.markdown(leg, unsafe_allow_html=True)

st.markdown(build_calendar_html(result, ext, conflicts), unsafe_allow_html=True)

# ── Per-day detail list ───────────────────────────────────────────────────────
st.markdown('<div class="sec-h">📋 Rincian Per Hari</div>', unsafe_allow_html=True)

cek  = {(c['day'], c['exam_slot']) for c in conflicts}
cxk  = {(c['day'], c['ext_title'])  for c in conflicts}
dates = sorted(result['Tanggal'].unique(), key=day_rank)

for date in dates:
    dr  = result[result['Tanggal'] == date]
    dex = [a for a in ext if a['day'] == date]
    dn  = date.split(',')[0].strip()
    ds2 = date.split(',')[1].strip() if ',' in date else date

    with st.expander(f"**{dn}** — {ds2}  ·  {len(dr)} sesi", expanded=False):
        for _, row in dr.iterrows():
            slot  = str(row['Jam']).strip()
            subj  = str(row.get('Nama MK','') or '').strip()
            room  = str(row.get('Ruangan','') or '').strip()
            kelas = str(row.get('Kelas','') or '').strip()
            jenis = str(row.get('Jenis Ujian','') or '').strip()
            ac    = SLOT_STYLE.get(slot, DEFAULT_STYLE)[0]
            ic    = (date, slot) in cek
            ct    = ('<span style="background:#E63946;color:#fff;border-radius:4px;padding:1px 6px;font-size:9px;font-weight:700;margin-left:8px;">⚠ KONFLIK</span>'
                     if ic else '')
            st.markdown(f"""
            <div class="lcard" style="--ac:{ac}">
                <div class="lcard-title">{e(subj)}{ct}</div>
                <div class="lcard-meta">
                    <span class="badge">⏰ {e(slot)}</span>
                    <span class="badge">🏛 {e(room)}</span>
                    <span class="badge">👥 {e(kelas)}</span>
                    <span class="badge">{e(jenis)}</span>
                </div>
            </div>""", unsafe_allow_html=True)

        if dex:
            st.markdown('<div style="color:#3D4A7A;font-size:10px;letter-spacing:.1em;text-transform:uppercase;margin:14px 0 6px;">📌 Agenda Eksternal</div>', unsafe_allow_html=True)
            for ea in dex:
                ixc = (date, ea['title']) in cxk
                bc  = '#E63946' if ixc else EXT_COLOR
                ct2 = ('<span style="background:#E63946;color:#fff;border-radius:4px;padding:1px 6px;font-size:9px;font-weight:700;margin-left:8px;">⚠ KONFLIK</span>'
                       if ixc else '')
                st.markdown(f"""
                <div class="ext-lcard" style="border-left-color:{bc}">
                    <div class="lcard-title" style="color:#C8FAF0;">📌 {e(ea['title'])}{ct2}</div>
                    <div class="lcard-meta">
                        <span class="badge" style="color:#2A9D8F;">⏰ {e(ea['start'])} – {e(ea['end'])}</span>
                    </div>
                </div>""", unsafe_allow_html=True)