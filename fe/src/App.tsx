import React, { useEffect, useState } from 'react';
import {
  createTransaction, getTransactions, getBalanceSeries,
  listCategories, createCategory,
  type Transaction, type TxType,
  setApiBase, getApiBase, pingApi, setLogSink,
} from './api';
import './theme.css';

/* ---------------- Filters ---------------- */
type FiltersProps = { onChange: (f: Record<string, any>) => void };
function Filters({ onChange }: FiltersProps) {
  const [category, setCategory] = useState('');
  const [txnType, setTxnType] = useState(''); // '' | debit | credit
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');

  function emit() {
    const f: Record<string, any> = {};
    if (category.trim()) f.category = category.trim();
    if (txnType) f.txn_type = txnType;
    if (start) f.start = new Date(start).toISOString();
    if (end) f.end = new Date(end).toISOString();
    onChange(f);
  }

  return (
    <div className="card" style={{ marginBottom: 12 }}>
      <h3 style={{ marginTop: 0 }}>Filters</h3>
      <div className="form-grid form-grid--2">
        <div className="form-field">
          <label>Category</label>
          <input value={category} onChange={(e) => setCategory(e.target.value)} placeholder="e.g. groceries" />
        </div>
        <div className="form-field">
          <label>Type</label>
          <select value={txnType} onChange={(e)=>setTxnType(e.target.value)}>
            <option value="">(any)</option>
            <option value="debit">debit</option>
            <option value="credit">credit</option>
          </select>
        </div>
        <div className="form-field">
          <label>Start</label>
          <input type="datetime-local" value={start} onChange={(e)=>setStart(e.target.value)} />
        </div>
        <div className="form-field">
          <label>End</label>
          <input type="datetime-local" value={end} onChange={(e)=>setEnd(e.target.value)} />
        </div>
      </div>
      <div className="form-actions" style={{ marginTop: 8 }}>
        <button type="button" onClick={emit} className="btn-primary">Apply Filters</button>
        <button type="button" onClick={()=>{ setCategory(''); setTxnType(''); setStart(''); setEnd(''); onChange({}); }} style={{ marginLeft: 8 }}>
          Clear
        </button>
      </div>
    </div>
  );
}

/* ---------------- TransactionsTable ---------------- */
function TransactionsTable({ items }: { items: Transaction[] | any }) {
  const rows = Array.isArray(items) ? items : [];
  return (
    <div className="card" style={{ overflowX: 'auto' }}>
      <h3 style={{ marginTop: 0 }}>Transactions</h3>
      <table className="ofc-table">
        <thead>
          <tr>
            <th>Date</th><th>Type</th><th>Category</th><th>Description</th><th style={{textAlign:'right'}}>Amount</th>
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr><td colSpan={5} style={{ textAlign:'center', opacity:.7 }}>No transactions yet</td></tr>
          ) : rows.map((tx: Transaction) => (
            <tr key={tx.id}>
              <td>{new Date(tx.occurred_at).toLocaleString()}</td>
              <td style={{textTransform:'capitalize'}}>{tx.txn_type}</td>
              <td>{tx.category ?? '—'}</td>
              <td>{tx.description}</td>
              <td style={{textAlign:'right'}}>{tx.txn_type==='debit' ? '-' : '+'}{Number(tx.amount).toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ---------------- BalanceChart ---------------- */
function BalanceChart({ data }: { data: { date:string; balance:number }[] | any }) {
  const series = Array.isArray(data) ? data : [];
  if (series.length === 0) {
    return (
      <div className="card"><h3 style={{marginTop:0}}>Balance Over Time</h3><div style={{opacity:.7}}>No data</div></div>
    );
  }
  const w=640,h=160,pad=16;
  const xs=series.map((_:any,i:number)=>i);
  const ys=series.map((d:any)=>d.balance);
  const xMax=Math.max(...xs)||1, yMin=Math.min(...ys), yMax=Math.max(...ys), span=yMax-yMin||1;
  const pts=series.map((d:any,i:number)=>{
    const x=pad + (i/xMax)*(w-pad*2);
    const y=pad + (1-(d.balance-yMin)/span)*(h-pad*2);
    return `${x},${y}`;
  }).join(' ');
  const last = ys[ys.length-1];
  const lastPt = pts.split(' ').pop()!;
  const [cx,cy] = lastPt.split(',');
  return (
    <div className="card">
      <h3 style={{marginTop:0}}>Balance Over Time</h3>
      <svg viewBox={`0 0 ${w} ${h}`} width="100%" height="180">
        <polyline points={pts} fill="none" stroke="currentColor" strokeWidth="2"/>
        <circle cx={cx} cy={cy} r="3" fill="currentColor"/>
      </svg>
      <div style={{fontSize:12, opacity:.8}}>Latest balance: <strong>{Number(last).toFixed(2)}</strong></div>
    </div>
  );
}

/* ---------------- Header / API Base ---------------- */
function Header(){ return <header className="header"><h1>OFC Transactions</h1></header>; }

function ApiBaseBar({ onApplied }:{ onApplied: ()=>void }) {
  const [url,setUrl]=useState(getApiBase());
  return (
    <div className="card api-bar">
      <label>API Base URL&nbsp;</label>
      <input style={{width:'50%'}} value={url} onChange={(e)=>setUrl(e.target.value)} />
      <button onClick={async()=>{ setApiBase(url); await pingApi(); onApplied(); }}>Apply</button>
    </div>
  );
}

/* ---------------- Transaction Form (sidebar) ---------------- */
function TransactionForm({ onCreated, setOutput }:{ onCreated:()=>void; setOutput:(s:string)=>void }) {
  const [amount,setAmount]=useState<number>(0);
  const [txnType,setTxnType]=useState<TxType>('debit');
  const [description,setDescription]=useState('');
  const [category,setCategory]=useState('');
  const [occurredAt,setOccurredAt]=useState<string>(new Date().toISOString().slice(0,16));
  const [catOptions,setCatOptions]=useState<{id:number;name:string}[]>([]);

  useEffect(()=>{ (async()=>{ try{ setCatOptions(await listCategories()) }catch{} })() },[]);

  async function handleSubmit(e:React.FormEvent){
    e.preventDefault();
    const payload={ amount:Number(amount), txn_type:txnType, description, category: category||undefined, occurred_at:new Date(occurredAt).toISOString() };
    if(category.trim() && !catOptions.find(c=>c.name.toLowerCase()===category.trim().toLowerCase())){
      try { const c=await createCategory(category.trim()); setCatOptions(prev=>[...prev, c].sort((a,b)=>a.name.localeCompare(b.name))); } catch {}
    }
    const created=await createTransaction(payload as any);
    setOutput(JSON.stringify(created,null,2));
    setAmount(0); setDescription(''); setCategory('');
    onCreated();
  }

  return (
    <form className="card sidebar-form" onSubmit={handleSubmit}>
      <h3 className="form-title">Add Transaction</h3>

      <div className="form-section">
        <div className="form-section__title">Amount & Type</div>
        <div className="form-grid form-grid--2">
          <div className="form-field">
            <label>Amount</label>
            <input type="number" step="0.01" min="0" value={amount}
              onChange={e=>setAmount(parseFloat(e.target.value||'0'))} placeholder="e.g. 12.50" required />
          </div>
          <div className="form-field">
            <label>Type</label>
            <select value={txnType} onChange={e=>setTxnType(e.target.value as TxType)}>
              <option value="debit">debit</option>
              <option value="credit">credit</option>
            </select>
          </div>
        </div>
      </div>

      <div className="form-section">
        <div className="form-section__title">Details</div>
        <div className="form-grid">
          <div className="form-field">
            <label>Category</label>
            <input list="cats" value={category} onChange={e=>setCategory(e.target.value)} placeholder="e.g. Groceries" />
            <datalist id="cats">{catOptions.map(c=><option key={c.id} value={c.name} />)}</datalist>
          </div>
          <div className="form-field">
            <label>Description</label>
            <input value={description} onChange={e=>setDescription(e.target.value)} placeholder="Short note" required />
          </div>
          <div className="form-field">
            <label>Date & Time</label>
            <input type="datetime-local" value={occurredAt} onChange={e=>setOccurredAt(e.target.value)} required />
          </div>
        </div>
      </div>

      <div className="form-actions"><button type="submit" className="btn-primary">Submit</button></div>
    </form>
  );
}

/* ---------------- App ---------------- */
export default function App(){
  const [filters,setFilters]=useState<Record<string,any>>({});
  const [items,setItems]=useState<Transaction[]>([]);
  const [series,setSeries]=useState<{date:string; balance:number}[]>([]);
  const [respOutput,setRespOutput]=useState('');      // Response JSON
  const [consoleOutput,setConsoleOutput]=useState(''); // Console Messages

  useEffect(()=>{ setLogSink((line)=>{
    setConsoleOutput(prev=>{
      const next=(prev?prev+'\n':'')+line;
      return next.length>20000 ? next.slice(next.length-20000) : next;
    });
  }); },[]);

  async function refresh(){
    const list=await getTransactions(filters);
    const ser=await getBalanceSeries(filters);
    setItems(Array.isArray(list)?list:[]);
    setSeries(Array.isArray(ser)?ser:[]);
  }
  useEffect(()=>{ refresh() }, [JSON.stringify(filters)]);

  return (
    <>
      <Header/>
      <div className="container">
        <ApiBaseBar onApplied={refresh}/>
        <div className="layout" style={{marginTop:16}}>
          <aside className="sidebar">
            <TransactionForm onCreated={refresh} setOutput={setRespOutput}/>
            <div className="card">
              <h3 style={{marginTop:0}}>Response JSON</h3>
              <textarea className="log-area" readOnly value={respOutput||''} placeholder="Last API response will appear here"/>
            </div>
            <div className="card">
              <h3 style={{marginTop:0}}>Console Messages</h3>
              <textarea className="log-area" readOnly value={consoleOutput} placeholder="Axios request/response logs will stream here"/>
            </div>
          </aside>
          <main className="main">
            <Filters onChange={setFilters}/>
            <TransactionsTable items={items}/>
            <BalanceChart data={series}/>
          </main>
        </div>
      </div>
    </>
  );
}
