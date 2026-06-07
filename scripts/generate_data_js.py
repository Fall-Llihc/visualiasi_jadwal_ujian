"""
generate_data_js.py
Konversi data/jadwal.csv → docs/data.js
Dijalankan oleh GitHub Actions setelah fetch_jadwal.py selesai.
"""

import os, sys, json, csv, io
from datetime import datetime, timezone, timedelta

CSV_PATH = "data/jadwal.csv"
OUT_PATH = "docs/data.js"

# Mapping waktu → nomor sesi (sesuai format data.js frontend)
SLOT_TO_SESSION = {
    '08.00 - 10.15 WIB': 1,
    '10.45 - 13.00 WIB': 2,
    '14.00 - 16.15 WIB': 3,
    '16.00 - 18.00 WIB': 4,
    '18.30 - 20.30 WIB': 5,
}

# Mapping sesi → label & warna (untuk SESSIONS di JS)
SESSIONS_JS = {
    1: {"label": "Sesi 1", "time": "08.00 – 10.15 WIB", "color": "#A8DADC", "bg": "rgba(168,218,220,0.10)"},
    2: {"label": "Sesi 2", "time": "10.45 – 13.00 WIB", "color": "#FFC1CC", "bg": "rgba(255,193,204,0.10)"},
    3: {"label": "Sesi 3", "time": "14.00 – 16.15 WIB", "color": "#B39CD0", "bg": "rgba(179,156,208,0.10)"},
    4: {"label": "Sesi 4", "time": "16.00 – 18.00 WIB", "color": "#FFD580", "bg": "rgba(255,213,128,0.10)"},
    5: {"label": "Sesi 5", "time": "18.30 – 20.30 WIB", "color": "#e06060", "bg": "rgba(224,96,96,0.10)"},
}

BULAN_STR_TO_NUM = {
    'Januari':'01','Februari':'02','Maret':'03','April':'04','Mei':'05','Juni':'06',
    'Juli':'07','Agustus':'08','September':'09','Oktober':'10','November':'11','Desember':'12'
}


def normalize_nim(v: str) -> str:
    s = str(v).strip()
    if s.upper() in {"NAN", "NONE", ""}:
        return ""
    try:
        s = str(int(float(s)))
    except (ValueError, OverflowError):
        pass
    if s.endswith(".0") and s[:-2].isdigit():
        s = s[:-2]
    return s.upper()


def to_iso_date(tanggal: str) -> str:
    """'Senin, 22 Juni 2026' → '2026-06-22'"""
    try:
        after_comma = tanggal.split(",", 1)[1].strip()   # '22 Juni 2026'
        parts = after_comma.split()                        # ['22', 'Juni', '2026']
        d, m, y = parts[0], parts[1], parts[2]
        return f"{y}-{BULAN_STR_TO_NUM.get(m, '00')}-{d.zfill(2)}"
    except Exception:
        return tanggal


def clean_name(v: str) -> str:
    s = str(v).strip()
    return s if s and s.lower() not in ("nan", "none", "-", "") else ""


# ── Read CSV ──────────────────────────────────────────────────────────────────
if not os.path.exists(CSV_PATH):
    print(f"ERROR: {CSV_PATH} tidak ditemukan. Jalankan fetch_jadwal.py dulu.")
    sys.exit(1)

rows = []
with open(CSV_PATH, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append({k.strip(): v for k, v in row.items()})

print(f"Read {len(rows)} rows from {CSV_PATH}")

# ── Build PROCTOR_DB ─────────────────────────────────────────────────────────
proctors = {}   # nim → {name, nim, schedule:[]}
uid      = 1

for row in rows:
    tanggal = str(row.get("Tanggal", "")).strip()
    jam     = str(row.get("Jam", "")).strip()
    if not tanggal or not jam:
        continue

    session_num = SLOT_TO_SESSION.get(jam, 0)
    if session_num == 0:
        print(f"  WARN: slot tidak dikenal '{jam}' — dilewati")
        continue

    date_iso = to_iso_date(tanggal)
    course   = str(row.get("Nama MK",    "") or "").strip()
    room     = str(row.get("Ruangan",    "") or "").strip()
    kelas    = str(row.get("Kelas",      "") or "").strip()
    jenis    = str(row.get("Jenis Ujian","") or "").strip()

    for i in ["1", "2", "3"]:
        nim  = normalize_nim(str(row.get(f"NIM (Pengawas {i})", "") or ""))
        nama = clean_name(str(row.get(f"Nama Lengkap (Pengawas {i})", "") or ""))
        if not nim:
            continue
        if not nama:
            nama = nim  # fallback ke NIM kalau nama kosong

        # Inisialisasi proctor entry
        if nim not in proctors:
            proctors[nim] = {"name": nama, "nim": nim, "schedule": []}
        elif proctors[nim]["name"] == nim and nama != nim:
            proctors[nim]["name"] = nama  # update nama dari baris lain

        # Partner(s)
        partner_labels = []
        for j in ["1", "2", "3"]:
            if j == i:
                continue
            p_nim  = normalize_nim(str(row.get(f"NIM (Pengawas {j})", "") or ""))
            p_nama = clean_name(str(row.get(f"Nama Lengkap (Pengawas {j})", "") or ""))
            if p_nim:
                partner_labels.append(p_nama if p_nama else p_nim)

        entry = {
            "id":      uid,
            "date":    date_iso,
            "session": session_num,
            "course":  course,
            "code":    room,
            "kelas":   kelas,
            "type":    jenis,
            "role":    f"P{i}",
        }
        if partner_labels:
            entry["partner"] = ", ".join(partner_labels)

        proctors[nim]["schedule"].append(entry)
        uid += 1

total_entries = sum(len(p["schedule"]) for p in proctors.values())
print(f"Built PROCTOR_DB: {len(proctors)} pengawas, {total_entries} sesi total")

# ── Timestamp WIB ────────────────────────────────────────────────────────────
ts_path = "data/last_updated.txt"
if os.path.exists(ts_path):
    with open(ts_path) as f:
        ts_raw = f.read().strip().replace(" UTC", "")
else:
    ts_raw = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

# ── Generate data.js ─────────────────────────────────────────────────────────
sessions_json    = json.dumps(SESSIONS_JS,  ensure_ascii=False, indent=2)
proctor_db_json  = json.dumps(proctors,     ensure_ascii=False, separators=(",", ":"))

os.makedirs("docs", exist_ok=True)

js_content = f"""// data.js — AUTO-GENERATED oleh GitHub Actions. JANGAN EDIT MANUAL.
// Generated: {ts_raw} UTC
(function () {{
  var HARI  = ['Minggu','Senin','Selasa','Rabu','Kamis','Jumat','Sabtu'];
  var BULAN = ['Januari','Februari','Maret','April','Mei','Juni','Juli',
               'Agustus','September','Oktober','November','Desember'];

  window.SESSIONS = {sessions_json};

  window.formatDateIndo = function (ds) {{
    var d = new Date(ds + 'T00:00:00');
    return HARI[d.getDay()] + ', ' + d.getDate() + ' ' + BULAN[d.getMonth()] + ' ' + d.getFullYear();
  }};

  window.formatUpdateTime = function (raw) {{
    // raw = "2026-06-07 14:36:29" (UTC) → convert ke WIB (+7)
    var d = new Date(raw.replace(' ', 'T') + 'Z');
    d = new Date(d.getTime() + 7 * 3600000);
    return d.getDate() + ' ' + BULAN[d.getMonth()] + ' ' + d.getFullYear() + ', ' +
      String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0') + ' WIB';
  }};

  window.HONOR_PER_SESSION = 30000;

  window.PROCTOR_DB = {proctor_db_json};

  window.countConflicts = function (schedule) {{
    var map = {{}}; var c = 0;
    schedule.forEach(function (s) {{
      var k = s.date + '-' + s.session;
      if (!map[k]) map[k] = [];
      map[k].push(s);
    }});
    Object.values(map).forEach(function (v) {{ if (v.length > 1) c++; }});
    return c;
  }};

  window.isSessionConflict = function (schedule, date, session) {{
    return schedule.filter(function (s) {{
      return s.date === date && s.session === session;
    }}).length > 1;
  }};

  window.LAST_UPDATE_RAW = '{ts_raw}';
  window.DATA_ROWS = {len(rows)};
}})();
"""

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"✓ Generated {OUT_PATH} ({len(js_content):,} bytes)")
print(f"  LAST_UPDATE_RAW = {ts_raw}")
print(f"  DATA_ROWS = {len(rows)}")
