/* schedule.jsx — Schedule display components */

/* ── icons ── */
const IconPin = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
);
const IconUsers = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg>
);
const IconClock = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
);
const IconAlert = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
);
const IconChevron = ({open}) => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" style={{transition:'transform .2s', transform: open ? 'rotate(90deg)' : 'rotate(0deg)'}}><polyline points="9 18 15 12 9 6"/></svg>
);
const IconCalendar = () => (
  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
);

/* ── Role badge ── */
function RoleBadge({role}) {
  var bg = role === 'P1' ? 'rgba(168,218,220,0.18)' : 'rgba(179,156,208,0.18)';
  var color = role === 'P1' ? '#A8DADC' : '#B39CD0';
  return <span className="role-badge" style={{background:bg, color:color}}>{role}</span>;
}

/* ── Schedule Card ── */
function ScheduleCard({item, conflict}) {
  var ses = SESSIONS[item.session];
  var borderColor = conflict ? '#e06060' : ses.color;

  // Section badge — selalu ditampilkan di bawah badge P1/P2.
  // - Bila kelas dipecah jadi 2 ruangan: 'Atas' (section 1) / 'Bawah' (section 2)
  // - Bila kelas dipecah ke >2 ruangan: 'Section X/N' (fallback informatif)
  // - Bila kelas tidak dipecah (cuma 1 ruangan): '(1 Ruangan)'
  var sec = item.section;
  var sectionText, sectionTitle;
  if (!sec || !sec.total || sec.total <= 1) {
    sectionText = '(1 Ruangan)';
    sectionTitle = 'Kelas tidak dipecah ke ruangan lain';
  } else if (sec.total === 2) {
    sectionText = sec.index === 1 ? 'Atas' : 'Bawah';
    sectionTitle = 'Kelas dipecah ke ' + sec.rooms.join(' & ');
  } else {
    sectionText = 'Section ' + sec.index + '/' + sec.total;
    sectionTitle = 'Kelas dipecah ke ' + sec.rooms.join(', ');
  }
  // Warna badge: pakai warna pink untuk split, abu untuk non-split.
  var sectionStyle = (sec && sec.total > 1)
    ? { background: 'rgba(255,193,204,0.18)', color: '#FFC1CC' }
    : { background: 'rgba(120,120,120,0.18)', color: '#999' };

  return (
    <div className="scard" style={{borderLeftColor: borderColor}}>
      <div className="scard-top">
        <span className="scard-time" style={{color: ses.color}}>
          <IconClock /> {ses.time}
        </span>
        <div className="scard-badges">
          <RoleBadge role={item.role} />
          <span className="role-badge section-badge" style={sectionStyle} title={sectionTitle}>
            {sectionText}
          </span>
        </div>
      </div>
      <h3 className="scard-course">{item.course}</h3>
      <p className="scard-room"><IconPin /> {item.code}</p>
      <div className="scard-meta">
        <span className="scard-meta-item">{item.kelas}</span>
        <span className="scard-meta-sep">·</span>
        <span className="scard-meta-item">{item.type}</span>
      </div>
      {item.partner && (
        <div className="scard-partner">
          <IconUsers /> <span>Rekan: {item.partner}</span>
        </div>
      )}
    </div>
  );
}

/* ── Conflict alert: dua jadwal pengawasan pada sesi yang sama ── */
function ConflictAlert({count}) {
  return (
    <div className="conflict-alert">
      <IconAlert />
      <div>
        <strong>Konflik Jadwal</strong>
        <span> — {count} jadwal pada sesi yang sama.</span>
      </div>
    </div>
  );
}

/* ── Conflict alert: agenda eksternal tabrakan dengan sesi pengawasan ── */
function AgendaConflictAlert({agenda, sessionNums}) {
  var slotLabels = sessionNums.map(function (s) { return SESSIONS[s] ? SESSIONS[s].time : ('Sesi ' + s); });
  return (
    <div className="conflict-alert">
      <IconAlert />
      <div>
        <strong>Tabrakan Agenda Eksternal</strong>
        <span> — “{agenda.title}” ({agenda.start}–{agenda.end}) bertabrakan dengan {slotLabels.join(', ')}.</span>
      </div>
    </div>
  );
}

/* ── Day section (collapsible) ── */
function DaySection({date, items, allSchedule, dayAgendas}) {
  const [open, setOpen] = React.useState(true);

  var sessionNums = [...new Set(items.map(i => i.session))].sort();
  var hasSchedConflict = sessionNums.some(s => isSessionConflict(allSchedule, date, s));

  // Cek tiap agenda eksternal — apakah bertabrakan dengan sesi pengawasan di hari ini.
  var agendaConflicts = dayAgendas
    .map(function (ag) {
      var conflictSessions = findAgendaSessionConflicts(allSchedule, ag);
      return conflictSessions.length ? { agenda: ag, sessions: conflictSessions } : null;
    })
    .filter(Boolean);

  var hasConflict = hasSchedConflict || agendaConflicts.length > 0;

  return (
    <div className={'day-section' + (hasConflict ? ' day-section--conflict' : '')}>
      <button className="day-header" onClick={() => setOpen(!open)}>
        <IconChevron open={open} />
        <span className="day-date">{formatDateIndo(date)}</span>
        <span className="day-count">{items.length} sesi</span>
        {hasConflict && <span className="day-conflict-badge">Konflik</span>}
      </button>

      {open && (
        <div className="day-cards">
          {/* Peringatan konflik agenda muncul di atas daftar sesi */}
          {agendaConflicts.map(function (c) {
            return <AgendaConflictAlert key={'ag-' + c.agenda.id} agenda={c.agenda} sessionNums={c.sessions} />;
          })}

          {/* Sesi pengawasan utama (agenda eksternal TIDAK ditampilkan di sini) */}
          {sessionNums.map(sn => {
            var sessItems = items.filter(i => i.session === sn);
            var conflict = sessItems.length > 1;
            return (
              <div key={sn} className="session-group">
                {conflict && <ConflictAlert count={sessItems.length} />}
                <div className="session-cards">
                  {sessItems.map(item => (
                    <ScheduleCard key={item.id} item={item} conflict={conflict} />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ── Stats box ── */
function StatBox({value, label, color}) {
  return (
    <div className="stat-box">
      <p className="stat-value" style={{color: color || '#E4E4E4'}}>{value}</p>
      <p className="stat-label">{label}</p>
    </div>
  );
}

/* ── Main ScheduleView ── */
function ScheduleView({proctor, agendas}) {
  var sch = proctor.schedule;
  var totalSesi = sch.length;
  var honor = totalSesi * HONOR_PER_SESSION;
  var schedConflicts = countConflicts(sch);

  // Hitung jumlah agenda eksternal yang bertabrakan dengan sesi pengawasan
  var agendaConflictCount = agendas.reduce(function (acc, ag) {
    var c = findAgendaSessionConflicts(sch, ag);
    return acc + (c.length > 0 ? 1 : 0);
  }, 0);
  var totalConflicts = schedConflicts + agendaConflictCount;

  // Group sesi by date (hanya tanggal, abaikan komponen waktu) lalu sort.
  var dateMap = {};
  sch.forEach(function (s) {
    var iso = isoDateOnly(s.date);
    if (!dateMap[iso]) dateMap[iso] = [];
    dateMap[iso].push(s);
  });
  var dates = Object.keys(dateMap).sort();

  // Kelompokkan agenda eksternal per tanggal (untuk dilewatkan ke DaySection
  // demi deteksi konflik — TIDAK akan dirender sebagai sesi).
  var agendaMap = {};
  agendas.forEach(function (a) {
    var iso = isoDateOnly(a.date);
    if (!agendaMap[iso]) agendaMap[iso] = [];
    agendaMap[iso].push(a);
  });

  return (
    <div className="main-view">
      {/* Header */}
      <div className="mv-header">
        <p className="mv-sup">Jadwal Pengawas Ujian FIF</p>
        <h1 className="mv-name">{proctor.name}</h1>
        <div className="mv-badges">
          <span className="mv-nim">{proctor.nim}</span>
          <span className="mv-sesi-count">{totalSesi} sesi pengawasan</span>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-row">
        <StatBox value={totalSesi} label="Total Sesi" color="#A8DADC" />
        <StatBox value={'Rp ' + honor.toLocaleString('id-ID')} label="Estimasi Honor" color="#FFC1CC" />
        <StatBox value={agendas.length} label="Agenda Eksternal" />
        <StatBox value={totalConflicts} label="Konflik Jadwal" color={totalConflicts > 0 ? '#e06060' : undefined} />
      </div>

      {/* Legend */}
      <div className="legend-row">
        {[1,2,3].map(s => (
          <div key={s} className="legend-item">
            <span className="legend-dot" style={{background: SESSIONS[s].color}}></span>
            <span>{SESSIONS[s].time}</span>
          </div>
        ))}
      </div>

      {/* Schedule by day */}
      <div className="schedule-list">
        {dates.map(date => (
          <DaySection
            key={date}
            date={date}
            items={dateMap[date]}
            allSchedule={sch}
            dayAgendas={agendaMap[date] || []}
          />
        ))}
      </div>
    </div>
  );
}

/* ── Empty state ── */
function EmptyState() {
  return (
    <div className="empty-state">
      <div className="empty-icon"><IconCalendar /></div>
      <h2>Selamat datang di ProctorView</h2>
      <p>Masukkan NIM di sidebar untuk melihat jadwal pengawasan UAS.</p>
    </div>
  );
}

Object.assign(window, { ScheduleView, EmptyState });
