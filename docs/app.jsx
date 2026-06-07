/* app.jsx — Root App component (read-only user view) */
const { useState, useEffect, useCallback } = React;

function App() {
  const [nim, setNim] = useState('');
  const [searchError, setSearchError] = useState('');
  const [proctor, setProctor] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(window.LAST_UPDATE_RAW || '');
  const [agendas, setAgendas] = useState(() => {
    try { return JSON.parse(localStorage.getItem('vj_agendas') || '[]'); }
    catch { return []; }
  });

  // persist agendas
  useEffect(() => {
    localStorage.setItem('vj_agendas', JSON.stringify(agendas));
  }, [agendas]);

  // restore last searched NIM
  useEffect(() => {
    var last = localStorage.getItem('vj_last_nim');
    if (last && PROCTOR_DB[last]) {
      setNim(last);
      setProctor(PROCTOR_DB[last]);
    }
  }, []);

  // Refresh waktu commit terakhir folder /data via GitHub API.
  // Kalau gagal, tetap pakai LAST_UPDATE_RAW yang sudah di-embed di data.js.
  useEffect(() => {
    if (typeof window.fetchLatestCommitTime === 'function') {
      window.fetchLatestCommitTime(function (raw) {
        if (raw) setLastUpdate(raw);
      });
    }
  }, []);

  const handleSearch = useCallback(() => {
    setSearchError('');
    var v = nim.trim();
    if (!v) { setSearchError('NIM tidak boleh kosong'); return; }
    if (/[^0-9]/.test(v)) { setSearchError('Mohon masukkan NIM (angka), bukan nama.'); return; }
    var p = PROCTOR_DB[v];
    if (!p) { setSearchError('NIM ' + v + ' tidak ditemukan.'); return; }
    setProctor(p);
    localStorage.setItem('vj_last_nim', v);
  }, [nim]);

  function addAgenda(ag) { setAgendas(prev => [...prev, ag]); }
  function removeAgenda(id) { setAgendas(prev => prev.filter(a => a.id !== id)); }

  return (
    <div className="app-layout">
      <Sidebar
        nimValue={nim}
        onNimChange={v => { setNim(v); setSearchError(''); }}
        onSearch={handleSearch}
        searchError={searchError}
        agendas={agendas}
        onAddAgenda={addAgenda}
        onRemoveAgenda={removeAgenda}
        lastUpdate={lastUpdate}
        dataRows={window.DATA_ROWS || 0}
      />
      <main className="main-content">
        {proctor ? <ScheduleView proctor={proctor} agendas={agendas} /> : <EmptyState />}
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
