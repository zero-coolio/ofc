import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { connectTransactions } from "../ws";
import dayjs from "dayjs";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

type Kind = "credit" | "debit";
type Category = { id: number; name: string; created_at: string };
type Transaction = {
  id: number;
  amount: number;
  kind: Kind;
  occurred_at: string; // YYYY-MM-DD
  description?: string;
  category_id?: number | null;
  created_at: string;
  _optimistic?: boolean;
};

const fmt = "YYYY-MM-DD";
const today = dayjs().format(fmt);
const thirtyDaysAgo = dayjs().subtract(30, "day").format(fmt);

export default function Dashboard() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [txs, setTxs] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [wsOpen, setWsOpen] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const [fromDate, setFromDate] = useState(thirtyDaysAgo);
  const [toDate, setToDate] = useState(today);

  const [filterKind, setFilterKind] = useState<Kind | "">("");
  const [filterCategoryId, setFilterCategoryId] = useState<number | "">("");

  async function loadAll() {
    setLoading(true);
    const [catsRes, txRes] = await Promise.all([
      api.get<Category[]>("/categories"),
      api.get<Transaction[]>("/transactions"),
    ]);
    setCategories(catsRes.data);
    setTxs(txRes.data);
    setLoading(false);
  }

  useEffect(() => { loadAll().catch(console.error); }, []);

  useEffect(() => {
    const h = connectTransactions((data: any) => {
      if (data && typeof data === "object" && "amount" in data && "kind" in data) {
        setTxs((prev) => {
          const incoming = data as Transaction;
          const optimisticIdx = prev.findIndex(
            (p) =>
              p._optimistic &&
              p.amount === incoming.amount &&
              p.kind === incoming.kind &&
              p.occurred_at === incoming.occurred_at &&
              p.description === incoming.description
          );
          const next = [...prev];
          if (optimisticIdx !== -1) next.splice(optimisticIdx, 1);
          if (!next.some((p) => p.id === incoming.id)) next.push(incoming);
          return next;
        });
      }
    }, setWsOpen);
    return () => h.close();
  }, []);

  const filtered = useMemo(() => {
    const start = dayjs(fromDate, fmt).startOf("day");
    const end = dayjs(toDate, fmt).endOf("day");
    return txs.filter((t) => {
      const d = dayjs(t.occurred_at, fmt);
      if (!d.isValid()) return false;
      if (d.isBefore(start) || d.isAfter(end)) return false;
      if (filterKind && t.kind !== filterKind) return false;
      if (filterCategoryId !== "" && t.category_id !== Number(filterCategoryId)) return false;
      return true;
    });
  }, [txs, fromDate, toDate, filterKind, filterCategoryId]);

  const chartData = useMemo(() => {
    const sorted = [...filtered].sort((a, b) => a.occurred_at.localeCompare(b.occurred_at));
    let running = 0;
    return sorted.map((t) => {
      running += t.kind === "credit" ? t.amount : -t.amount;
      return { date: t.occurred_at, balance: Number(running.toFixed(2)) };
    });
  }, [filtered]);

  function showToast(msg: string) { setToast(msg); setTimeout(() => setToast(null), 2200); }

  async function onDelete(id: number) {
    const snapshot = [...txs];
    setTxs((prev) => prev.filter((t) => t.id !== id));
    try { await api.delete(`/transactions/${id}`); showToast("Deleted"); }
    catch { setTxs(snapshot); showToast("Delete failed"); }
  }

  return (
    <div className="grid">
      {toast && <div className="toast">{toast}</div>}

      {/* TOP: controls + chart */}
      <section className="card chart-card">
        <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
          <h2 style={{ margin: 0 }}>Balance Over Time</h2>
          <span className="muted">Live stream: {wsOpen ? "connected" : "disconnected"}</span>
        </div>

        <div className="row" style={{ marginTop: 8, flexWrap: "wrap", gap: 12 }}>
          <div className="row" style={{ gap: 8 }}>
            <label className="muted" style={{ alignSelf: "center" }}>From</label>
            <input type="date" value={fromDate} onChange={(e)=>setFromDate(e.target.value)} />
            <label className="muted" style={{ alignSelf: "center" }}>To</label>
            <input type="date" value={toDate} onChange={(e)=>setToDate(e.target.value)} />
          </div>
          <select value={filterKind} onChange={(e)=>setFilterKind(e.target.value as Kind | "")}>
            <option value="">All kinds</option>
            <option value="debit">Debit</option>
            <option value="credit">Credit</option>
          </select>
          <select value={filterCategoryId} onChange={(e)=>setFilterCategoryId(e.target.value === "" ? "" : Number(e.target.value))}>
            <option value="">All categories</option>
            {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>

        <div style={{ width: "100%", height: 280, marginTop: 8 }}>
          <ResponsiveContainer>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="balance" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* BOTTOM: filtered table */}
      <section className="card">
        <h2>Transactions</h2>
        {loading ? (
          <div>Loading…</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Kind</th>
                <th style={{ textAlign: "right" }}>Amount</th>
                <th>Category</th>
                <th>Description</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(t => (
                <tr key={t.id} style={t._optimistic ? { opacity: 0.6 } : undefined}>
                  <td>{t.occurred_at}</td>
                  <td>{t.kind}</td>
                  <td style={{ textAlign: "right" }}>{t.kind === "debit" ? "-" : "+"}{t.amount.toFixed(2)}</td>
                  <td>{categories.find(c => c.id === t.category_id)?.name || ""}</td>
                  <td>{t.description || ""}</td>
                  <td><button className="ghost" onClick={()=>onDelete(t.id)}>Delete</button></td>
                </tr>
              ))}
              {filtered.length === 0 && <tr><td colSpan={6} style={{ opacity: .6 }}>No transactions in this range</td></tr>}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
