/* app.jsx — Root App component */
const { useState, useEffect, useCallback } = React;

function App() {
  const [tab, setTab] = useState('jadwal');
  const [nim, setNim] = useState('');
  const [searchError, setSearchError] = useState('');
  const [proctor, setProctor] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
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
  function handleReset() { setAgendas([]); setProctor(null); setNim(''); localStorage.removeItem('vj_last_nim'); }

  return (
    <div className="app-layout">
      <Sidebar
        activeTab={tab}
        onTabChange={setTab}
        nimValue={nim}
        onNimChange={v => { setNim(v); setSearchError(''); }}
        onSearch={handleSearch}
        searchError={searchError}
        isAdmin={isAdmin}
        onLogin={() => setIsAdmin(true)}
        onLogout={() => setIsAdmin(false)}
        onReset={handleReset}
        agendas={agendas}
        onAddAgenda={addAgenda}
        onRemoveAgenda={removeAgenda}
      />
      <main className="main-content">
        {proctor ? <ScheduleView proctor={proctor} agendas={agendas} /> : <EmptyState />}
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
