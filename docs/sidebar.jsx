/* sidebar.jsx — Sidebar component with Jadwal + Admin tabs */
const { useState, useEffect, useRef } = React;

/* ── tiny icons ── */
const SvgSearch = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/></svg>
);
const SvgPlus = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M12 5v14M5 12h14"/></svg>
);
const SvgSync = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><path d="M1 4v6h6"/><path d="M23 20v-6h-6"/><path d="M20.49 9A9 9 0 005.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 013.51 15"/></svg>
);
const SvgLogout = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
);
const SvgLock = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
);
const SvgTrash = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/></svg>
);

/* ── Jadwal Tab ── */
function JadwalTab({ nimValue, onNimChange, onSearch, searchError, agendas, onAddAgenda, onRemoveAgenda }) {
  const [agDate, setAgDate] = useState('2026-06-25');
  const [agTitle, setAgTitle] = useState('');
  const [agStart, setAgStart] = useState('08:00');
  const [agEnd, setAgEnd] = useState('10:00');
  const [agErr, setAgErr] = useState('');

  function handleAdd() {
    if (!agTitle.trim()) { setAgErr('Judul wajib diisi'); return; }
    if (agStart >= agEnd) { setAgErr('Waktu mulai harus sebelum selesai'); return; }
    setAgErr('');
    onAddAgenda({ date: agDate, title: agTitle.trim(), start: agStart, end: agEnd, id: Date.now() });
    setAgTitle('');
  }

  return (
    <div className="sb-tab-body">
      {/* NIM search */}
      <div className="sb-section">
        <label className="sb-label">Cari NIM Pengawas</label>
        <div className="sb-search-row">
          <input
            className={'sb-input' + (searchError ? ' sb-input--error' : '')}
            placeholder="Masukkan NIM …"
            value={nimValue}
            onChange={e => onNimChange(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && onSearch()}
          />
        </div>
        {searchError && <p className="sb-error">{searchError}</p>}
        <button className="sb-btn sb-btn--primary" onClick={onSearch}>
          <SvgSearch /> Cari Jadwal
        </button>
      </div>

      {/* Tambah Agenda */}
      <div className="sb-section">
        <p className="sb-section-title">Tambah Agenda Eksternal</p>
        <label className="sb-label-sm">Hari</label>
        <input type="date" className="sb-input sb-input--sm" value={agDate} onChange={e => setAgDate(e.target.value)} />

        <label className="sb-label-sm">Judul Agenda</label>
        <input className="sb-input sb-input--sm" placeholder="cth: Rapat Organisasi" value={agTitle} onChange={e => setAgTitle(e.target.value)} />

        <div className="sb-time-row">
          <div>
            <label className="sb-label-sm">Mulai</label>
            <input type="time" className="sb-input sb-input--sm" value={agStart} onChange={e => setAgStart(e.target.value)} />
          </div>
          <div>
            <label className="sb-label-sm">Selesai</label>
            <input type="time" className="sb-input sb-input--sm" value={agEnd} onChange={e => setAgEnd(e.target.value)} />
          </div>
        </div>
        {agErr && <p className="sb-error">{agErr}</p>}
        <button className="sb-btn sb-btn--secondary" onClick={handleAdd}><SvgPlus /> Tambah Agenda</button>
      </div>

      {/* Agenda list */}
      {agendas.length > 0 && (
        <div className="sb-section">
          <p className="sb-section-title">Agenda Tersimpan</p>
          {agendas.map(ag => (
            <div key={ag.id} className="sb-agenda-chip">
              <div>
                <span className="sb-agenda-title">{ag.title}</span>
                <span className="sb-agenda-date">{formatDateIndo(ag.date).split(',')[0]}, {ag.start}–{ag.end}</span>
              </div>
              <button className="sb-agenda-remove" onClick={() => onRemoveAgenda(ag.id)} title="Hapus">×</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ── Admin Tab ── */
function AdminTab({ isAdmin, onLogin, onLogout, onReset }) {
  const [pw, setPw] = useState('');
  const [pwErr, setPwErr] = useState('');
  const [interval, setIntervalVal] = useState(60);
  const [showConfirm, setShowConfirm] = useState(false);
  const [syncMsg, setSyncMsg] = useState('');

  function handleLogin() {
    if (pw === 'admin') { onLogin(); setPwErr(''); setPw(''); }
    else { setPwErr('Password salah'); }
  }

  function simulateSync(label) {
    setSyncMsg(label + '…');
    setTimeout(() => setSyncMsg(label + ' — Berhasil ✓'), 1200);
    setTimeout(() => setSyncMsg(''), 3000);
  }

  if (!isAdmin) {
    return (
      <div className="sb-tab-body">
        <div className="sb-section sb-admin-login">
          <div className="sb-admin-login-icon"><SvgLock /></div>
          <p className="sb-section-title" style={{textAlign:'center'}}>Masuk sebagai Admin</p>
          <input className="sb-input" type="password" placeholder="Password" value={pw} onChange={e => setPw(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleLogin()} />
          {pwErr && <p className="sb-error">{pwErr}</p>}
          <button className="sb-btn sb-btn--primary" onClick={handleLogin}><SvgLock /> Login</button>
        </div>
      </div>
    );
  }

  return (
    <div className="sb-tab-body">
      {/* Sync */}
      <div className="sb-section">
        <p className="sb-section-title">Sinkronisasi Manual</p>
        <p className="sb-hint">Ambil data terbaru dari SharePoint / GitHub tanpa menunggu jadwal otomatis.</p>
        <button className="sb-btn sb-btn--primary" onClick={() => simulateSync('Get Recent Update')}><SvgSync /> Get Recent Update</button>
        <button className="sb-btn sb-btn--outline" onClick={() => simulateSync('Pull Data dari GitHub')}><SvgSync /> Pull Data dari GitHub</button>
        {syncMsg && <p className="sb-sync-msg">{syncMsg}</p>}
      </div>

      {/* Auto-refresh */}
      <div className="sb-section">
        <p className="sb-section-title">Interval Auto-Refresh</p>
        <p className="sb-hint">Atur seberapa sering Streamlit memperbarui data (minimum 5 menit).</p>
        <div className="sb-interval-row">
          <button className="sb-btn-icon" onClick={() => setIntervalVal(v => Math.max(5, v - 5))}>−</button>
          <span className="sb-interval-val">{interval} mnt</span>
          <button className="sb-btn-icon" onClick={() => setIntervalVal(v => v + 5)}>+</button>
        </div>
        <div style={{display:'flex',gap:8}}>
          <button className="sb-btn sb-btn--secondary sb-btn--sm" onClick={() => simulateSync('Interval disimpan')}>Simpan</button>
          <button className="sb-btn sb-btn--outline sb-btn--sm" onClick={() => simulateSync('Interval diterapkan')}>Pakai</button>
        </div>
      </div>

      {/* Reset */}
      <div className="sb-section">
        <p className="sb-section-title">Reset Data</p>
        <p className="sb-hint">Hapus semua cache dan agenda lokal. Tidak dapat dibatalkan.</p>
        {!showConfirm ? (
          <button className="sb-btn sb-btn--danger" onClick={() => setShowConfirm(true)}><SvgTrash /> Reset Semua Data</button>
        ) : (
          <div className="sb-confirm">
            <p>Yakin ingin reset?</p>
            <div style={{display:'flex',gap:8}}>
              <button className="sb-btn sb-btn--danger sb-btn--sm" onClick={() => { onReset(); setShowConfirm(false); }}>Ya, Reset</button>
              <button className="sb-btn sb-btn--outline sb-btn--sm" onClick={() => setShowConfirm(false)}>Batal</button>
            </div>
          </div>
        )}
      </div>

      {/* Logout */}
      <div className="sb-section" style={{borderTop:'none', paddingTop:0}}>
        <button className="sb-btn sb-btn--logout" onClick={onLogout}><SvgLogout /> Logout</button>
      </div>
    </div>
  );
}

/* ── Sidebar wrapper ── */
function Sidebar(props) {
  const { activeTab, onTabChange } = props;

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sb-brand">
        <h1 className="sb-logo">ProctorView</h1>
        <p className="sb-subtitle">Jadwal Pengawas Ujian FIF</p>
      </div>

      {/* Tabs */}
      <div className="sb-tabs">
        <button className={'sb-tab' + (activeTab === 'jadwal' ? ' sb-tab--active' : '')} onClick={() => onTabChange('jadwal')}>Jadwal</button>
        <button className={'sb-tab' + (activeTab === 'admin' ? ' sb-tab--active' : '')} onClick={() => onTabChange('admin')}>Admin</button>
      </div>

      {/* Tab content */}
      <div className="sb-scroll">
        {activeTab === 'jadwal' ? <JadwalTab {...props} /> : <AdminTab {...props} />}
      </div>

      {/* Footer — last update */}
      <div className="sb-footer">
        <div className="sb-update-dot"></div>
        <div>
          <p className="sb-update-label">Terakhir diperbarui</p>
          <p className="sb-update-time">{formatUpdateTime(LAST_UPDATE_RAW)}</p>
          <p className="sb-update-rows">{DATA_ROWS} baris data</p>
        </div>
      </div>
    </aside>
  );
}

window.Sidebar = Sidebar;
