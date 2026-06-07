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
  return (
    <div className="scard" style={{borderLeftColor: borderColor}}>
      <div className="scard-top">
        <span className="scard-time" style={{color: ses.color}}>
          <IconClock /> {ses.time}
        </span>
        <RoleBadge role={item.role} />
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

/* ── Conflict alert ── */
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

/* ── External agenda card ── */
function AgendaCard({ag}) {
  return (
    <div className="scard scard--agenda">
      <div className="scard-top">
        <span className="scard-time" style={{color:'#FFC1CC'}}><IconClock /> {ag.start} – {ag.end} WIB</span>
        <span className="role-badge" style={{background:'rgba(255,193,204,0.18)', color:'#FFC1CC'}}>Eksternal</span>
      </div>
      <h3 className="scard-course">{ag.title}</h3>
    </div>
  );
}

/* ── Day section (collapsible) ── */
function DaySection({date, items, allSchedule, agendas}) {
  const [open, setOpen] = React.useState(true);

  // count unique sessions with entries on this date
  var sessionNums = [...new Set(items.map(i => i.session))].sort();
  var hasConflict = sessionNums.some(s => isSessionConflict(allSchedule, date, s));
  var dayAgendas = agendas.filter(a => a.date === date);

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
          {sessionNums.map(sn => {
            var sessItems = items.filter(i => i.session === sn);
            var conflict = sessItems.length > 1;
            return (
              <div key={sn} className="session-group">
                {conflict && <ConflictAlert count={sessItems.length} />}
                {sessItems.map(item => (
                  <ScheduleCard key={item.id} item={item} conflict={conflict} />
                ))}
              </div>
            );
          })}
          {dayAgendas.map(ag => (
            <AgendaCard key={ag.id} ag={ag} />
          ))}
        </div>
      )}
    </div>
  );
}

/* ── Stats box ── */
function StatBox({value, label, color, accent}) {
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
  var conflicts = countConflicts(sch);
  var agendaCount = agendas.length;

  // group by date, sorted
  var dateMap = {};
  sch.forEach(function(s) {
    if (!dateMap[s.date]) dateMap[s.date] = [];
    dateMap[s.date].push(s);
  });
  var dates = Object.keys(dateMap).sort();

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
        <StatBox value={agendaCount} label="Agenda Eksternal" />
        <StatBox value={conflicts} label="Konflik Jadwal" color={conflicts > 0 ? '#e06060' : undefined} />
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
          <DaySection key={date} date={date} items={dateMap[date]} allSchedule={sch} agendas={agendas} />
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
      <h2>Selamat datang di Vis Jadwal</h2>
      <p>Masukkan NIM di sidebar untuk melihat jadwal pengawasan UAS.</p>
    </div>
  );
}

Object.assign(window, { ScheduleView, EmptyState });
