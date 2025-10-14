
import { useEffect, useMemo, useState } from 'react'
import { createTransaction, getTransactions, getBalanceSeries, type Transaction, type TxType, setApiBase, getApiBase, pingApi, listCategories, createCategory } from './api'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

function Header(){
  const buildTime = (import.meta as any).env?.VITE_BUILD_TIME || 'dev';
  return (<header><div className="container"><div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}><h1>OFC Transactions</h1><div><small>Inspired by Overseas Food Trading</small><br/><small style={{opacity:.8}}>Build: {buildTime}</small></div></div></div></header>);
}
function ApiBaseBar({ onApplied }:{ onApplied:()=>void }){
  const [value,setValue]=useState<string>(getApiBase()); const [status,setStatus]=useState<'checking'|'ok'|'fail'>('checking');
  useEffect(()=>{ (async()=>{ setStatus(await pingApi()?'ok':'fail') })() },[]);
  async function apply(){ setApiBase(value.trim()); setStatus('checking'); const ok=await pingApi(); setStatus(ok?'ok':'fail'); onApplied(); }
  return (<div className="card" style={{marginTop:16}}><strong>API Base URL</strong><div style={{display:'flex',gap:8,alignItems:'center',marginTop:8}}><input style={{minWidth:280,maxWidth:520}} value={value} onChange={e=>setValue(e.target.value)} placeholder="http://localhost:8080"/><button onClick={apply}>Apply</button><span style={{fontSize:12,opacity:.8}}>{status==='ok'?'Connected':status==='fail'?'Not reachable':'Checking…'}</span></div></div>);
}
function TransactionForm({ onCreated, setOutput }:{ onCreated:()=>void; setOutput:(s:string)=>void }){
  const [amount,setAmount]=useState<number>(0); const [txnType,setTxnType]=useState<TxType>('debit'); const [description,setDescription]=useState(''); const [category,setCategory]=useState(''); const [occurredAt,setOccurredAt]=useState<string>(new Date().toISOString().slice(0,16));
  const [catOptions,setCatOptions]=useState<{id:number;name:string}[]>([]);
  useEffect(()=>{ (async()=>{ try{ setCatOptions(await listCategories()) }catch{} })() },[]);
  async function handleSubmit(e:React.FormEvent){ e.preventDefault();
    const payload={ amount:Number(amount), txn_type: txnType, description, category: category||undefined, occurred_at: new Date(occurredAt).toISOString() };
    if(category.trim() && !catOptions.find(c=>c.name.toLowerCase()===category.trim().toLowerCase())){
      try{ const c=await createCategory(category.trim()); setCatOptions(p=>[...p,c].sort((a,b)=>a.name.localeCompare(b.name))) }catch{}
    }
    const created=await createTransaction(payload as any);
    setOutput(JSON.stringify(created,null,2));
    setAmount(0); setDescription(''); setCategory('');
    onCreated();
  }
  return (<form className="card" onSubmit={handleSubmit}><h3 style={{marginTop:0}}>Add Transaction</h3>
    <div style={{display:'grid',gap:8,gridTemplateColumns:'1fr 1fr'}}>
      <div><label>Amount</label><input type="number" step="0.01" value={amount} onChange={e=>setAmount(parseFloat(e.target.value||'0'))} required/></div>
      <div><label>Type</label><select value={txnType} onChange={e=>setTxnType(e.target.value as TxType)}><option value="debit">Debit</option><option value="credit">Credit</option></select></div>
      <div style={{gridColumn:'1 / span 2'}}><label>Description</label><input value={description} onChange={e=>setDescription(e.target.value)} required/></div>
      <div><label>Category</label><input list="cats" value={category} onChange={e=>setCategory(e.target.value)}/><datalist id="cats">{catOptions.map(c=><option key={c.id} value={c.name}/>)}</datalist></div>
      <div><label>Date</label><input type="datetime-local" value={occurredAt} onChange={e=>setOccurredAt(e.target.value)} required/></div>
    </div>
    <div style={{marginTop:10}}><button type="submit">Submit</button></div>
  </form>);
}
function Filters({ onChange }:{ onChange:(f:Record<string,any>)=>void }){
  const [txnType,setTxnType]=useState<string>(''); const [category,setCategory]=useState<string>(''); const [start,setStart]=useState<string>(''); const [end,setEnd]=useState<string>('');
  function apply(){ onChange({ txn_type: txnType || undefined, category: category || undefined, start: start? new Date(start).toISOString(): undefined, end: end? new Date(end).toISOString(): undefined }) }
  return (<div className="card"><div style={{display:'flex',gap:8,alignItems:'center'}}>
    <strong>Filters</strong>
    <select value={txnType} onChange={e=>setTxnType(e.target.value)}><option value="">All Types</option><option value="credit">Credit</option><option value="debit">Debit</option></select>
    <input placeholder="Category" value={category} onChange={e=>setCategory(e.target.value)}/>
    <input type="datetime-local" value={start} onChange={e=>setStart(e.target.value)}/>
    <input type="datetime-local" value={end} onChange={e=>setEnd(e.target.value)}/>
    <button onClick={apply}>Apply</button>
  </div></div>);
}
function TransactionsTable({ items }:{ items:Transaction[] }){
  return (<div className="card"><h3 style={{marginTop:0}}>Transactions</h3>
    <table className="table"><thead><tr><th>Date</th><th>Description</th><th>Category</th><th>Type</th><th>Amount</th></tr></thead>
      <tbody>{items.map(tx=>(<tr key={tx.id}><td>{new Date(tx.occurred_at).toLocaleString()}</td><td>{tx.description}</td><td>{tx.category || '-'}</td><td>{tx.txn_type}</td><td>{tx.amount.toFixed(2)}</td></tr>))}</tbody>
    </table>
  </div>);
}
function BalanceChart({ data }:{ data:{date:string; balance:number}[] }){
  const series = useMemo(()=> data.map(p=>({ date:new Date(p.date).toLocaleString(), balance:p.balance })), [data]);
  return (<div className="card"><h3 style={{marginTop:0}}>Balance Over Time</h3><div style={{width:'100%',height:280}}>
    <ResponsiveContainer><LineChart data={series}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="date" tick={{fontSize:12}}/><YAxis tick={{fontSize:12}}/><Tooltip/><Line type="monotone" dataKey="balance" dot={false}/></LineChart></ResponsiveContainer>
  </div></div>);
}
export default function App(){
  const [filters,setFilters]=useState<Record<string,any>>({}); const [items,setItems]=useState<Transaction[]>([]); const [series,setSeries]=useState<{date:string;balance:number}[]>([]); const [output,setOutput]=useState<string>('');
  async function refresh(){ const list=await getTransactions(filters); const ser=await getBalanceSeries(filters); setItems(list); setSeries(ser as any) }
  useEffect(()=>{ refresh() }, [JSON.stringify(filters)])
  return (<><Header/><div className="container"><ApiBaseBar onApplied={refresh}/><div className="layout" style={{marginTop:16}}>
    <aside className="sidebar"><TransactionForm onCreated={refresh} setOutput={setOutput}/></aside>
    <main className="main"><Filters onChange={setFilters}/><TransactionsTable items={items}/><BalanceChart data={series}/>
      <div className="card"><h3 style={{marginTop:0}}>Output (Raw JSON)</h3><pre className="output-pre">{output || '—'}</pre></div>
    </main></div></div></>);
}
