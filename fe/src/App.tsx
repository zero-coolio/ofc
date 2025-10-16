import React, { useEffect, useMemo, useState } from "react";
import { Routes, Route, useNavigate } from "react-router-dom";
import "./index.css";
import Banner from "./components/Banner";
import Readme from "./pages/Readme";

/* ───────────────────────── Types ───────────────────────── */
type Transaction = {
  id?: number;
  amount: number; // signed in DB (credit positive, debit negative)
  txn_type: "debit" | "credit";
  description: string;
  category?: string | null;
  occurred_at: string;
  created_at?: string;
};
type Category = { id?: number; name: string; created_at?: string };

/* ─────────────── Helpers (defensive parsing, etc.) ─────────────── */
function toArray<T = any>(data: any): T[] {
  if (Array.isArray(data)) return data as T[];
  if (data && Array.isArray((data as any).items)) return (data as any).items as T[];
  if (data && Array.isArray((data as any).transactions)) return (data as any).transactions as T[];
  if (data && typeof data === "object" && !Array.isArray(data)) {
    const vals = Object.values(data);
    if (vals.every((v) => typeof v === "object")) return vals as T[];
  }
  return [];
}

/* ────────────────────── Tiny SVG sparkline ────────────────────── */
/* (unchanged) — uses running balance from txns, do not modify */
function TransactionsSparkline({ txns }: { txns: Transaction[] }) {
  const list = toArray<Transaction>(txns);
  if (!list || list.length === 0) return <div className="subtle">No data to chart.</div>;

  const sorted = [...list].sort(
      (a, b) =>
          new Date(a.occurred_at).getTime() - new Date(b.occurred_at).getTime()
  );

  let running = 0;
  const pts = sorted.map((t) => {
    // NOTE: amounts are already signed in DB
    running += t.amount;
    return { x: new Date(t.occurred_at).getTime(), y: running };
  });

  const W = 520, H = 140, P = 12;
  const xs = pts.map((p) => p.x), ys = pts.map((p) => p.y);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const spanX = Math.max(1, maxX - minX), spanY = Math.max(1, maxY - minY);
  const sx = (x: number) => P + ((x - minX) * (W - 2 * P)) / spanX;
  const sy = (y: number) => H - P - ((y - minY) * (H - 2 * P)) / spanY;
  const d = pts.map((p, i) => `${i ? "L" : "M"} ${sx(p.x)},${sy(p.y)}`).join(" ");

  return (
      <svg width="100%" height={H} viewBox={`0 0 ${W} ${H}`}>
        <rect x="0" y="0" width={W} height={H} fill="#f9fdfa" stroke="#dbe9e8" />
        <path d={d} fill="none" stroke="#0f766e" strokeWidth="2" />
      </svg>
  );
}

/* ───────────────────── JSON + App Log Panel ───────────────────── */
function DebugPanel({
                      results,
                      logs,
                    }: {
  results: any;
  logs: { time: string; msg: string }[];
}) {
  const json = JSON.stringify(toArray(results) ?? [], null, 2);
  const [tab, setTab] = useState<"json" | "log">("json");
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(json);
      alert("Copied JSON");
    } catch {}
  };
  return (
      <div className="card">
        <div
            className="pad-4"
            style={{
              display: "flex",
              gap: 8,
              alignItems: "center",
              background: "#e9f7f5",
              borderTopLeftRadius: 12,
              borderTopRightRadius: 12,
            }}
        >
          <button
              onClick={() => setTab("json")}
              className="pill"
              style={{ fontWeight: tab === "json" ? 700 : 400 }}
          >
            Results JSON
          </button>
          <button
              onClick={() => setTab("log")}
              className="pill"
              style={{ fontWeight: tab === "log" ? 700 : 400 }}
          >
            App Log
          </button>
          {tab === "json" && (
              <div style={{ marginLeft: "auto" }}>
                <button className="copy-btn" onClick={copy}>
                  Copy JSON
                </button>
              </div>
          )}
        </div>
        {tab === "json" ? (
            <pre className="json">{json}</pre>
        ) : (
            <div
                className="pad-4"
                style={{
                  background: "var(--bg)",
                  maxHeight: 256,
                  overflow: "auto",
                  borderTop: "1px solid var(--line)",
                }}
            >
              {logs.length === 0 && <div className="subtle">No log entries yet.</div>}
              {logs.map((l, i) => (
                  <div key={i}>
                    <span style={{ color: "var(--brand)" }}>{l.time}</span> — {l.msg}
                  </div>
              ))}
            </div>
        )}
      </div>
  );
}

/* ───────────────────────── Dashboard ───────────────────────── */
function Dashboard() {
  // API base & joiner (prevents //)
  const [apiBase, setApiBase] = useState(
      localStorage.getItem("ofc_api_base") || (import.meta.env.VITE_API_BASE || "")
  );
  useEffect(() => {
    if (apiBase) localStorage.setItem("ofc_api_base", apiBase);
  }, [apiBase]);
  const getUrl = (path: string) => {
    if (!apiBase) return path;
    const base = apiBase.replace(/\/+$/, "");
    const p = path.replace(/^\/+/, "");
    return `${base}/${p}`;
  };
  const headers: HeadersInit = useMemo(
      () => ({ "Content-Type": "application/json" }),
      []
  );

  // Data state
  const [categories, setCategories] = useState<Category[]>([]);
  const [transactions, setTransactions] = useState<Transaction[] | any>([]);
  const [message, setMessage] = useState("");
  const [selected, setSelected] = useState<Transaction | null>(null);

  // Log state
  const [logs, setLogs] = useState<{ time: string; msg: string }[]>([]);
  const log = (msg: string) =>
      setLogs((p) => [...p, { time: new Date().toLocaleTimeString(), msg }]);

  // Health ping (helps detect wrong base URL quickly)
  const [apiOk, setApiOk] = useState<boolean>(false);
  const pingHealth = async () => {
    try {
      const res = await fetch(getUrl("/health"), { cache: "no-store" });
      setApiOk(res.ok);
      log(`Health: ${res.status} ${res.statusText}`);
    } catch (e: any) {
      setApiOk(false);
      log(`Health error: ${String(e)}`);
    }
  };
  useEffect(() => {
    if (apiBase) pingHealth();
  }, [apiBase]);

  // Filters
  const [filters, setFilters] = useState({
    type: "all" as "all" | "debit" | "credit",
    category: "all" as string | "all",
    search: "",
    dateFrom: "",
    dateTo: "",
  });

  const filteredTxns: Transaction[] = useMemo(() => {
    const list = toArray<Transaction>(transactions);
    const from = filters.dateFrom ? new Date(filters.dateFrom).getTime() : -Infinity;
    const to = filters.dateTo ? new Date(filters.dateTo).getTime() : Infinity;
    const q = filters.search.trim().toLowerCase();
    const out = list.filter((t) => {
      if (filters.type !== "all" && t.txn_type !== filters.type) return false;
      if (filters.category !== "all" && (t.category || "") !== filters.category)
        return false;
      const ts = t.occurred_at ? new Date(t.occurred_at).getTime() : 0;
      if (ts < from || ts > to) return false;
      if (q) {
        const hay = `${t.description ?? ""} ${t.category ?? ""}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
    return out.sort(
        (a, b) =>
            new Date(b.occurred_at).getTime() - new Date(a.occurred_at).getTime()
    );
  }, [transactions, filters]);

  // Loaders (cache-busting GETs)
  const loadCategories = async () => {
    log("Loading categories…");
    try {
      const res = await fetch(getUrl("/categories"), { headers, cache: "no-store" });
      const raw = await res.json();
      const arr = toArray<Category>(raw);
      setCategories(arr);
      log(`Categories loaded (${arr.length}).`);
    } catch {
      log("Failed to load categories.");
    }
  };
  const loadTransactions = async () => {
    log("Loading transactions…");
    try {
      const res = await fetch(getUrl(`/transactions?t=${Date.now()}`), {
        headers,
        cache: "no-store",
      });
      const raw = await res.json();
      const arr = toArray<Transaction>(raw).sort(
          (a, b) =>
              new Date(b.occurred_at).getTime() - new Date(a.occurred_at).getTime()
      );
      setTransactions(arr);
      log(`Transactions loaded (${arr.length}).`);
    } catch {
      log("Failed to load transactions.");
    }
  };
  const refreshAll = async () => {
    await Promise.all([loadCategories(), loadTransactions()]);
    log("Refresh complete.");
  };

  // Create form
  const [form, setForm] = useState<Transaction>({
    amount: 0,
    txn_type: "debit",
    description: "",
    category: "",
    occurred_at: new Date().toISOString(),
  });

  const submitTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage("");

    if (!apiBase) {
      const msg = "API base is empty. Set it above, then Connect / Refresh.";
      setMessage(msg);
      log(msg);
      return;
    }
    if (!apiOk) {
      log("Warning: /health failed; attempting POST anyway.");
    }

    const url = getUrl("/transactions");
    const payload = {
      amount: Number(form.amount), // send as is; backend determines sign from amount or txn_type
      txn_type: form.txn_type === "credit" ? "credit" : "debit",
      description: String(form.description || "").trim(), // optional
      category: form.category ? String(form.category) : null,
      occurred_at: new Date(form.occurred_at).toISOString(),
    };

    log("Creating transaction…");
    try {
      const res = await fetch(url, {
        method: "POST",
        headers,
        cache: "no-store",
        body: JSON.stringify(payload),
      });

      const txt = await res.text();
      let body: any = null;
      try {
        body = txt ? JSON.parse(txt) : null;
      } catch {
        body = txt;
      }

      if (!res.ok) {
        const errMsg = `POST /transactions -> ${res.status} ${res.statusText}`;
        setMessage(`❌ ${errMsg}`);
        log(`${errMsg} :: ${typeof body === "string" ? body : JSON.stringify(body)}`);
        alert(`${errMsg}\n${typeof body === "string" ? body : JSON.stringify(body, null, 2)}`);
        return;
      }

      const created = body as Transaction;
      if (!created || typeof created !== "object" || !("id" in created)) {
        const errMsg = "Unexpected POST response (missing id).";
        setMessage(`❌ ${errMsg}`);
        log(errMsg);
        return;
      }

      setMessage("✅ Transaction created");
      log(`Transaction ${created.id} created.`);

      // Optimistic prepend (newest first)
      setTransactions((prev: Transaction[]) => {
        const arr = toArray<Transaction>(prev);
        const next = [created, ...arr];
        return next.sort(
            (a, b) =>
                new Date(b.occurred_at).getTime() - new Date(a.occurred_at).getTime()
        );
      });

      // Reset form (keep txn_type)
      setForm({
        amount: 0,
        txn_type: form.txn_type,
        description: "",
        category: "",
        occurred_at: new Date().toISOString(),
      });

      // Sync with server
      await loadTransactions();
    } catch (err: any) {
      const msg = `Network/JS error during POST: ${String(err)}`;
      setMessage(`❌ ${msg}`);
      log(msg);
      alert(msg);
    }
  };

  // Delete
  const deleteTransaction = async (id?: number) => {
    if (!id) return;
    if (!confirm("Delete this transaction?")) return;
    log(`Deleting transaction ${id}…`);
    try {
      const res = await fetch(getUrl(`/transactions/${id}`), { method: "DELETE" });
      if (res.ok) {
        setTransactions((prev: Transaction[]) => prev.filter((t) => t.id !== id));
        if (selected?.id === id) setSelected(null);
        log(`Transaction ${id} deleted.`);
      } else {
        log(`Delete failed for ${id}.`);
        alert("Delete failed: " + (await res.text()));
      }
    } catch (e) {
      log(`Delete error for ${id}.`);
      alert("Delete failed: " + String(e));
    }
  };

  // Initial load
  useEffect(() => {
    if (apiBase) refreshAll();
  }, [apiBase]);

  return (
      <>
        {/* Top bar */}
        <section className="header-strip">
          <label style={{ color: "var(--brand)", fontWeight: 600 }}>
            API Base:&nbsp;
            <input
                className="api-input"
                value={apiBase}
                onChange={(e) => setApiBase(e.target.value)}
                placeholder="https://ofc-backend-…a.run.app"
            />
          </label>
          <button
              className="btn btn-primary"
              style={{ marginLeft: 12 }}
              onClick={refreshAll}
          >
            Connect / Refresh
          </button>
        </section>

        {/* Layout */}
        <div className="wrap">
          <div className="layout">
            {/* LEFT SIDEBAR (1/4) */}
            <aside className="sidebar">
              {/* Create */}
              <form className="card pad-5" onSubmit={submitTransaction}>
                <h2 className="section-title">Create Transaction</h2>

                <div style={{ marginBottom: 8 }}>
                  <label className="subtle">Amount</label>
                  <input
                      type="number"
                      step="0.01"
                      style={{ width: "100%", padding: 6, border: "1px solid #ccc", borderRadius: 6 }}
                      value={form.amount}
                      onChange={(e) => setForm({ ...form, amount: Number(e.target.value) })}
                      required
                  />
                </div>

                <div style={{ marginBottom: 8 }}>
                  <label className="subtle">Type</label>
                  <select
                      style={{ width: "100%", padding: 6, border: "1px solid #ccc", borderRadius: 6 }}
                      value={form.txn_type}
                      onChange={(e) => setForm({ ...form, txn_type: e.target.value as any })}
                  >
                    <option value="debit">debit</option>
                    <option value="credit">credit</option>
                  </select>
                </div>

                <div style={{ marginBottom: 8 }}>
                  <label className="subtle">Description (optional)</label>
                  <input
                      style={{ width: "100%", padding: 6, border: "1px solid #ccc", borderRadius: 6 }}
                      value={form.description}
                      onChange={(e) => setForm({ ...form, description: e.target.value })}
                      placeholder="Optional note or label"
                  />
                </div>

                <div style={{ marginBottom: 8 }}>
                  <label className="subtle">Category</label>
                  <input
                      list="category-list"
                      style={{ width: "100%", padding: 6, border: "1px solid #ccc", borderRadius: 6 }}
                      value={form.category ?? ""}
                      onChange={(e) => setForm({ ...form, category: e.target.value })}
                      placeholder="(optional)"
                  />
                  <datalist id="category-list">
                    {categories.map((c) => (
                        <option key={c.name} value={c.name}>
                          {c.name}
                        </option>
                    ))}
                  </datalist>
                </div>

                <div style={{ marginBottom: 8 }}>
                  <label className="subtle">Occurred At</label>
                  <input
                      type="datetime-local"
                      style={{ width: "100%", padding: 6, border: "1px solid #ccc", borderRadius: 6 }}
                      value={new Date(form.occurred_at).toISOString().slice(0, 16)}
                      onChange={(e) =>
                          setForm({ ...form, occurred_at: new Date(e.target.value).toISOString() })
                      }
                      required
                  />
                </div>

                <button
                    type="submit"
                    className="btn btn-primary"
                    style={{ width: "100%", marginTop: 6 }}
                >
                  Create
                </button>

                {message && <p className="subtle" style={{ marginTop: 8 }}>{message}</p>}
              </form>

              {/* Modify (preview; wire to PUT/PATCH when available) */}
              <form className="card pad-5">
                <h2 className="section-title">Modify Transaction</h2>
                {!selected && <p className="subtle">Click a transaction row to load here.</p>}
                {selected && (
                    <>
                      <div className="subtle" style={{ marginBottom: 8 }}>
                        ID: #{selected.id}
                      </div>
                      <div style={{ marginBottom: 8 }}>
                        <label className="subtle">Amount</label>
                        <input
                            type="number"
                            step="0.01"
                            value={selected.amount}
                            readOnly
                            style={{ width: "100%", padding: 6, border: "1px solid #ccc", borderRadius: 6 }}
                        />
                      </div>
                      <button
                          className="btn"
                          style={{ background: "#eee", width: "100%" }}
                          type="button"
                          onClick={() => setSelected(null)}
                      >
                        Cancel
                      </button>
                    </>
                )}
              </form>
            </aside>

            {/* RIGHT MAIN (3/4): Filters → Balance → List → Graph → JSON/Log */}
            <section className="main">
              {/* Filters */}
              <div className="card pad-4">
                <h3 className="section-title">Filters</h3>
                <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(5, minmax(0,1fr))",
                      gap: 12,
                    }}
                >
                  <div>
                    <label className="subtle">Type</label>
                    <select
                        style={{ width: "100%", padding: 6, border: "1px solid #ccc", borderRadius: 6 }}
                        value={filters.type}
                        onChange={(e) => setFilters({ ...filters, type: e.target.value as any })}
                    >
                      <option value="all">all</option>
                      <option value="debit">debit</option>
                      <option value="credit">credit</option>
                    </select>
                  </div>
                  <div>
                    <label className="subtle">Category</label>
                    <select
                        style={{ width: "100%", padding: 6, border: "1px solid #ccc", borderRadius: 6 }}
                        value={filters.category}
                        onChange={(e) => setFilters({ ...filters, category: e.target.value })}
                    >
                      <option value="all">all</option>
                      {categories.map((c) => (
                          <option key={c.name} value={c.name}>
                            {c.name}
                          </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="subtle">Search</label>
                    <input
                        style={{ width: "100%", padding: 6, border: "1px solid #ccc", borderRadius: 6 }}
                        value={filters.search}
                        onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                        placeholder="desc / category"
                    />
                  </div>
                  <div>
                    <label className="subtle">From</label>
                    <input
                        type="date"
                        style={{ width: "100%", padding: 6, border: "1px solid #ccc", borderRadius: 6 }}
                        value={filters.dateFrom}
                        onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="subtle">To</label>
                    <input
                        type="date"
                        style={{ width: "100%", padding: 6, border: "1px solid #ccc", borderRadius: 6 }}
                        value={filters.dateTo}
                        onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
                    />
                  </div>
                </div>
              </div>

              {/* Balance Summary (signed amounts) */}
              <div className="card pad-5">
                <h2 className="section-title">Current Balance</h2>
                <p style={{ fontSize: "1.5rem", color: "#0f766e", fontWeight: 600 }}>
                  {(() => {
                    const list = toArray<Transaction>(filteredTxns);
                    const total = list.reduce((acc, t) => acc + Number(t.amount || 0), 0);
                    return `$${total.toFixed(2)}`;
                  })()}
                </p>
                <p className="subtle" style={{ marginTop: -6 }}>
                  (sum of signed amounts in filtered transactions)
                </p>
              </div>

              {/* Transactions */}
              <div className="card pad-5" style={{ overflow: "auto" }}>
                <h2 className="section-title">Transactions</h2>
                {toArray<Transaction>(filteredTxns).length === 0 ? (
                    <p>No transactions match your filters.</p>
                ) : (
                    <table>
                      <thead>
                      <tr style={{ background: "#e9f7f5" }}>
                        <th>Date</th>
                        <th>Type</th>
                        <th>Amount</th>
                        <th>Category</th>
                        <th>Description</th>
                        <th style={{ textAlign: "right" }}>Actions</th>
                      </tr>
                      </thead>
                      <tbody>
                      {toArray<Transaction>(filteredTxns).map((t) => (
                          <tr key={t.id} onClick={() => setSelected(t)}>
                            <td>{t.occurred_at ? new Date(t.occurred_at).toLocaleString() : "—"}</td>
                            <td>{t.txn_type}</td>
                            <td style={{ color: Number(t.amount) < 0 ? "#b00020" : "#0f766e" }}>
                              {Number(t.amount).toFixed(2)}
                            </td>
                            <td>{t.category || "—"}</td>
                            <td>{t.description}</td>
                            <td style={{ textAlign: "right" }}>
                              <button
                                  className="btn"
                                  style={{ color: "#b00020", background: "#ffecec" }}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    deleteTransaction(t.id);
                                  }}
                                  title={`Delete transaction #${t.id}`}
                              >
                                Delete
                              </button>
                            </td>
                          </tr>
                      ))}
                      </tbody>
                    </table>
                )}
              </div>

              {/* Graph */}
              <div className="card pad-5">
                <h3 className="section-title">Balance (filtered results)</h3>
                <TransactionsSparkline txns={filteredTxns} />
              </div>

              {/* JSON + Log */}
              <DebugPanel results={filteredTxns} logs={logs} />
            </section>
          </div>
        </div>
      </>
  );
}

/* ───────────────────────── App Shell ───────────────────────── */
export default function App() {
  const navigate = useNavigate();
  return (
      <div className="min-h-screen">
        <div style={{ position: "relative" }}>
          <Banner />
          <nav
              style={{
                position: "absolute",
                left: 0,
                right: 0,
                top: 8,
                display: "flex",
                justifyContent: "center",
                gap: 12,
              }}
          >
            <button className="pill" onClick={() => navigate("/")}>Dashboard</button>
            <button className="pill" onClick={() => navigate("/readme")}>Readme</button>
            <a
                className="pill"
                href="https://ofc-backend-291082004564.us-central1.run.app/docs"
                target="_blank"
                rel="noreferrer"
            >
              API Docs
            </a>
          </nav>
        </div>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/readme" element={<Readme />} />
        </Routes>
      </div>
  );
}
