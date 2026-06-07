"""
generate_data_js.py
Konversi data/jadwal.csv → docs/data.js
Dijalankan oleh GitHub Actions setelah fetch_jadwal.py selesai.
"""

import os, sys, json, csv, re, subprocess
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

# Rentang jam tiap sesi (untuk deteksi konflik agenda eksternal di frontend)
SESSION_TIME_RANGES = {
    1: ["08:00", "10:15"],
    2: ["10:45", "13:00"],
    3: ["14:00", "16:15"],
    4: ["16:00", "18:00"],
    5: ["18:30", "20:30"],
}

# Mapping sesi → label & warna (untuk SESSIONS di JS)
SESSIONS_JS = {
    1: {"label": "Sesi 1", "time": "08.00 – 10.15 WIB", "color": "#A8DADC", "bg": "rgba(168,218,220,0.10)",
        "start": "08:00", "end": "10:15"},
    2: {"label": "Sesi 2", "time": "10.45 – 13.00 WIB", "color": "#FFC1CC", "bg": "rgba(255,193,204,0.10)",
        "start": "10:45", "end": "13:00"},
    3: {"label": "Sesi 3", "time": "14.00 – 16.15 WIB", "color": "#B39CD0", "bg": "rgba(179,156,208,0.10)",
        "start": "14:00", "end": "16:15"},
    4: {"label": "Sesi 4", "time": "16.00 – 18.00 WIB", "color": "#FFD580", "bg": "rgba(255,213,128,0.10)",
        "start": "16:00", "end": "18:00"},
    5: {"label": "Sesi 5", "time": "18.30 – 20.30 WIB", "color": "#e06060", "bg": "rgba(224,96,96,0.10)",
        "start": "18:30", "end": "20:30"},
}

BULAN_STR_TO_NUM = {
    'januari':'01','februari':'02','maret':'03','april':'04','mei':'05','juni':'06',
    'juli':'07','agustus':'08','september':'09','oktober':'10','november':'11','desember':'12'
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
    """Konversi berbagai format tanggal → ISO 'YYYY-MM-DD'.

    Mendukung:
      - '2026-06-22'
      - '2026-06-22 00:00:00'  (format dari Excel/SharePoint)
      - '22/06/2026' atau '22-06-2026'
      - 'Senin, 22 Juni 2026'
    """
    s = str(tanggal).strip()
    if not s:
        return ""

    # 1) Sudah ISO (dengan / tanpa komponen waktu)
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # 2) Format DD/MM/YYYY atau DD-MM-YYYY
    m = re.match(r"^(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})$", s)
    if m:
        return f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"

    # 3) Format Indonesia: 'Senin, 22 Juni 2026' atau '22 Juni 2026'
    try:
        body = s.split(",", 1)[1].strip() if "," in s else s
        parts = body.split()
        d, mname, y = parts[0], parts[1], parts[2]
        mm = BULAN_STR_TO_NUM.get(mname.lower(), '00')
        return f"{y}-{mm}-{d.zfill(2)}"
    except Exception:
        return s


def normalize_jam(jam: str) -> str:
    """Normalisasi format jam: '08.00 – 10.15 WIB', '08:00-10:15', dll → '08.00 - 10.15 WIB'."""
    s = str(jam).strip()
    if not s:
        return ""
    # Ganti em-dash/en-dash dengan hyphen biasa
    s = s.replace("–", "-").replace("—", "-")
    # Ganti pemisah jam-menit ':' menjadi '.'
    s = re.sub(r"(\d{1,2}):(\d{2})", r"\1.\2", s)
    # Pad jam ke 2 digit
    s = re.sub(r"\b(\d)\.(\d{2})\b", r"0\1.\2", s)
    # Normalisasi spasi sekitar '-'
    s = re.sub(r"\s*-\s*", " - ", s)
    # Pastikan diakhiri 'WIB'
    if "WIB" not in s.upper():
        s = s + " WIB"
    s = re.sub(r"\s+", " ", s).strip()
    # Cek apakah cocok dengan salah satu slot
    for slot in SLOT_TO_SESSION.keys():
        if s.upper().replace(" ", "") == slot.upper().replace(" ", ""):
            return slot
    return s


def clean_name(v: str) -> str:
    s = str(v).strip()
    return s if s and s.lower() not in ("nan", "none", "-", "") else ""


def get_data_commit_time() -> str:
    """Ambil waktu commit terakhir pada folder data/ via git log.

    Return format: 'YYYY-MM-DD HH:MM:SS' dalam UTC. Fallback ke now() bila git log gagal.
    """
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%cI", "--", "data/"],
            text=True, stderr=subprocess.DEVNULL,
        ).strip()
        if out:
            iso = out.replace("Z", "+00:00")
            dt = datetime.fromisoformat(iso)
            return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    except Exception as ex:
        print(f"  WARN: git log gagal — {ex}")
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


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
skipped_slot = 0

# Pass 1: bangun lookup ruangan untuk mendeteksi kelas yang dipecah ke beberapa
# ruangan (split section). Key = (date_iso, jam, course, kelas).
split_lookup: dict = {}
for row in rows:
    tanggal_raw = str(row.get("Tanggal", "")).strip()
    jam_raw     = str(row.get("Jam", "")).strip()
    if not tanggal_raw or not jam_raw:
        continue
    jam_n = normalize_jam(jam_raw)
    if jam_n not in SLOT_TO_SESSION:
        continue
    key = (
        to_iso_date(tanggal_raw),
        jam_n,
        str(row.get("Nama MK", "") or "").strip().upper(),
        str(row.get("Kelas",   "") or "").strip().upper(),
    )
    room = str(row.get("Ruangan", "") or "").strip()
    if not room:
        continue
    if key not in split_lookup:
        split_lookup[key] = []
    if room not in split_lookup[key]:
        split_lookup[key].append(room)

# Urutkan supaya nomor section konsisten di tiap reload
for k in split_lookup:
    split_lookup[k].sort()

split_kelas_count = sum(1 for v in split_lookup.values() if len(v) > 1)
print(f"Split-kelas terdeteksi: {split_kelas_count} kombinasi (date+jam+MK+kelas)")

# Pass 2: bangun PROCTOR_DB sambil isi info section bila kelasnya dipecah

for row in rows:
    tanggal_raw = str(row.get("Tanggal", "")).strip()
    jam_raw     = str(row.get("Jam", "")).strip()
    if not tanggal_raw or not jam_raw:
        continue

    jam = normalize_jam(jam_raw)
    session_num = SLOT_TO_SESSION.get(jam, 0)
    if session_num == 0:
        skipped_slot += 1
        if skipped_slot <= 5:
            print(f"  WARN: slot tidak dikenal '{jam_raw}' (norm: '{jam}') — dilewati")
        continue

    date_iso = to_iso_date(tanggal_raw)
    course   = str(row.get("Nama MK",    "") or "").strip()
    room     = str(row.get("Ruangan",    "") or "").strip()
    kelas    = str(row.get("Kelas",      "") or "").strip()
    jenis    = str(row.get("Jenis Ujian","") or "").strip()

    # Cek apakah kombinasi (date, jam, MK, kelas) ini dipecah ke beberapa ruangan.
    split_key   = (date_iso, jam, course.upper(), kelas.upper())
    split_rooms = split_lookup.get(split_key, [])
    section_info = None
    if len(split_rooms) > 1 and room in split_rooms:
        section_info = {
            "index": split_rooms.index(room) + 1,
            "total": len(split_rooms),
            "rooms": split_rooms,
        }

    for i in ["1", "2", "3"]:
        nim  = normalize_nim(str(row.get(f"NIM (Pengawas {i})", "") or ""))
        nama = clean_name(str(row.get(f"Nama Lengkap (Pengawas {i})", "") or ""))
        if not nim:
            continue
        if not nama:
            nama = nim

        if nim not in proctors:
            proctors[nim] = {"name": nama, "nim": nim, "schedule": []}
        elif proctors[nim]["name"] == nim and nama != nim:
            proctors[nim]["name"] = nama

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
        if section_info is not None:
            entry["section"] = section_info

        proctors[nim]["schedule"].append(entry)
        uid += 1

total_entries = sum(len(p["schedule"]) for p in proctors.values())
print(f"Built PROCTOR_DB: {len(proctors)} pengawas, {total_entries} sesi total"
      + (f" ({skipped_slot} baris dilewati)" if skipped_slot else ""))

# ── Timestamp dari commit folder data/ ───────────────────────────────────────
ts_raw = get_data_commit_time()
print(f"Last data commit (UTC): {ts_raw}")

# ── Generate data.js ─────────────────────────────────────────────────────────
sessions_json    = json.dumps(SESSIONS_JS,        ensure_ascii=False, indent=2)
proctor_db_json  = json.dumps(proctors,           ensure_ascii=False, separators=(",", ":"))
session_ranges_json = json.dumps(SESSION_TIME_RANGES, ensure_ascii=False)

os.makedirs("docs", exist_ok=True)

# GitHub repo info untuk frontend bisa fetch commit time terbaru via API (fallback)
GITHUB_REPO = "Fall-Llihc/visualiasi_jadwal_ujian"

js_content = f"""// data.js — AUTO-GENERATED oleh GitHub Actions. JANGAN EDIT MANUAL.
// Generated: {ts_raw} UTC
(function () {{
  var HARI  = ['Minggu','Senin','Selasa','Rabu','Kamis','Jumat','Sabtu'];
  var BULAN = ['Januari','Februari','Maret','April','Mei','Juni','Juli',
               'Agustus','September','Oktober','November','Desember'];

  window.SESSIONS = {sessions_json};

  // Rentang waktu tiap sesi dalam format "HH:MM" (untuk deteksi konflik agenda)
  window.SESSION_TIME_RANGES = {session_ranges_json};

  // Helper: konversi "HH:MM" → menit total
  function toMinutes(t) {{
    var p = String(t).split(':');
    return parseInt(p[0], 10) * 60 + parseInt(p[1] || '0', 10);
  }}
  window.toMinutes = toMinutes;

  // Helper: cek overlap dua interval waktu (dalam string "HH:MM")
  window.timeOverlap = function (s1, e1, s2, e2) {{
    return toMinutes(s1) < toMinutes(e2) && toMinutes(s2) < toMinutes(e1);
  }};

  // Ambil hanya bagian "YYYY-MM-DD" agar kompatibel dengan beragam format input.
  function isoDateOnly(ds) {{
    if (!ds) return '';
    var m = String(ds).match(/^(\\d{{4}})-(\\d{{2}})-(\\d{{2}})/);
    return m ? (m[1] + '-' + m[2] + '-' + m[3]) : String(ds);
  }}
  window.isoDateOnly = isoDateOnly;

  window.formatDateIndo = function (ds) {{
    var iso = isoDateOnly(ds);
    if (!/^\\d{{4}}-\\d{{2}}-\\d{{2}}$/.test(iso)) return String(ds || '');
    var parts = iso.split('-');
    var y = parseInt(parts[0], 10);
    var mo = parseInt(parts[1], 10) - 1;
    var d = parseInt(parts[2], 10);
    // Pakai UTC agar tidak tergeser oleh timezone browser.
    var date = new Date(Date.UTC(y, mo, d));
    return HARI[date.getUTCDay()] + ', ' + d + ' ' + BULAN[mo] + ' ' + y;
  }};

  // Format "YYYY-MM-DD HH:MM:SS" (UTC) → "<tgl> <bulan> <tahun>, HH:MM WIB"
  // Memakai UTC + offset agar tidak double-shift ke timezone lokal browser.
  window.formatUpdateTime = function (raw) {{
    if (!raw) return '—';
    var s = String(raw).trim().replace(' UTC', '').replace(' ', 'T');
    if (!/Z|[+-]\\d{{2}}:?\\d{{2}}$/.test(s)) s += 'Z';
    var d = new Date(s);
    if (isNaN(d.getTime())) return String(raw);
    // Tambah offset WIB (UTC+7) lalu pakai getUTC* agar konsisten lintas timezone.
    var wib = new Date(d.getTime() + 7 * 3600000);
    var hh = String(wib.getUTCHours()).padStart(2, '0');
    var mm = String(wib.getUTCMinutes()).padStart(2, '0');
    return wib.getUTCDate() + ' ' + BULAN[wib.getUTCMonth()] + ' ' + wib.getUTCFullYear()
         + ', ' + hh + ':' + mm + ' WIB';
  }};

  window.HONOR_PER_SESSION = 30000;

  window.PROCTOR_DB = {proctor_db_json};

  // Hitung jumlah sesi konflik (multiple jadwal pada slot yg sama)
  window.countConflicts = function (schedule) {{
    var map = {{}}; var c = 0;
    schedule.forEach(function (s) {{
      var k = isoDateOnly(s.date) + '-' + s.session;
      if (!map[k]) map[k] = [];
      map[k].push(s);
    }});
    Object.values(map).forEach(function (v) {{ if (v.length > 1) c++; }});
    return c;
  }};

  window.isSessionConflict = function (schedule, date, session) {{
    var iso = isoDateOnly(date);
    return schedule.filter(function (s) {{
      return isoDateOnly(s.date) === iso && s.session === session;
    }}).length > 1;
  }};

  // Cek apakah agenda eksternal (date+start+end) bertabrakan dengan sesi pengawasan
  // pada hari yang sama. Mengembalikan array sesi-num yang konflik.
  window.findAgendaSessionConflicts = function (schedule, agenda) {{
    var iso = isoDateOnly(agenda.date);
    var conflicts = [];
    var seen = {{}};
    schedule.forEach(function (s) {{
      if (isoDateOnly(s.date) !== iso) return;
      var range = window.SESSION_TIME_RANGES[s.session];
      if (!range) return;
      if (window.timeOverlap(agenda.start, agenda.end, range[0], range[1])) {{
        if (!seen[s.session]) {{
          conflicts.push(s.session);
          seen[s.session] = 1;
        }}
      }}
    }});
    return conflicts;
  }};

  window.LAST_UPDATE_RAW   = '{ts_raw}';
  window.GITHUB_REPO       = '{GITHUB_REPO}';
  window.DATA_ROWS         = {len(rows)};
  window.DATA_PROCTORS     = {len(proctors)};
  window.DATA_SESSIONS     = {total_entries};

  // Fetch waktu commit terakhir folder /data via GitHub API → akurat ke detik.
  // Fallback: pakai LAST_UPDATE_RAW kalau API gagal / offline.
  window.fetchLatestCommitTime = function (cb) {{
    try {{
      var url = 'https://api.github.com/repos/' + window.GITHUB_REPO + '/commits?path=data&per_page=1';
      fetch(url).then(function (r) {{
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      }}).then(function (arr) {{
        if (Array.isArray(arr) && arr.length && arr[0].commit && arr[0].commit.committer) {{
          var iso = arr[0].commit.committer.date; // sudah ISO UTC
          var d = new Date(iso);
          var pad = function (n) {{ return String(n).padStart(2, '0'); }};
          var raw = d.getUTCFullYear() + '-' + pad(d.getUTCMonth()+1) + '-' + pad(d.getUTCDate())
                  + ' ' + pad(d.getUTCHours()) + ':' + pad(d.getUTCMinutes()) + ':' + pad(d.getUTCSeconds());
          cb(raw);
        }}
      }}).catch(function (err) {{
        console.warn('fetchLatestCommitTime gagal:', err);
      }});
    }} catch (e) {{
      console.warn('fetchLatestCommitTime error:', e);
    }}
  }};
}})();
"""

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"✓ Generated {OUT_PATH} ({len(js_content):,} bytes)")
print(f"  LAST_UPDATE_RAW = {ts_raw}")
print(f"  DATA_ROWS = {len(rows)}, PROCTORS = {len(proctors)}, SESSIONS = {total_entries}")
