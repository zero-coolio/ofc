import axios from 'axios';

// -------- Base URL handling --------
const envBase = (import.meta as any).env?.VITE_API_BASE as string | undefined;
const savedBase =
  typeof window !== 'undefined'
    ? localStorage.getItem('apiBase') || undefined
    : undefined;

let BASE = savedBase || envBase || 'http://localhost:8080';

export const api = axios.create({ baseURL: BASE, timeout: 10000 });

export function setApiBase(url: string) {
  BASE = url;
  api.defaults.baseURL = url;
  try { localStorage.setItem('apiBase', url); } catch {}
}
export function getApiBase() { return BASE; }
export async function pingApi() {
  try { await api.get('/transactions', { params: { limit: 1, offset: 0 } }); return true; }
  catch { return false; }
}

// -------- Log sink (for Console Messages pane) --------
let logSink: (line: string) => void = () => {};
export function setLogSink(fn: (line: string) => void) { logSink = fn; }
function pushLog(line: string){ try { logSink(line); } catch {} }

api.interceptors.request.use((c)=>{
  const line = `📤 ${c.method?.toUpperCase()} ${c.baseURL}${c.url} :: params=${JSON.stringify(c.params||{})} body=${JSON.stringify(c.data||{})}`;
  console.log(line); pushLog(line); return c;
});
api.interceptors.response.use((r)=>{
  const line = `📥 ${r.status} ${r.config.baseURL}${r.config.url} :: ${JSON.stringify(r.data).slice(0,800)}`;
  console.log(line); pushLog(line); return r;
}, (err)=>{
  const cfg = err?.config||{};
  const line = `❌ ${cfg.method?.toUpperCase()} ${(cfg.baseURL||'')+(cfg.url||'')} :: ${err?.message||'error'}`;
  console.warn(line, err?.response?.data);
  pushLog(line + (err?.response?.data ? ` :: ${JSON.stringify(err.response.data)}` : ''));
  return Promise.reject(err);
});

// -------- Types & endpoints --------
export type TxType='credit'|'debit';

export interface Transaction{
  id:number; amount:number; txn_type:TxType; description:string;
  category?:string|null; occurred_at:string; created_at:string;
}
export interface CreateTransaction{
  amount:number; txn_type:TxType; description:string; category?:string|null; occurred_at:string;
}

export async function createTransaction(p: CreateTransaction){
  const {data}=await api.post('/transactions', p); return data as Transaction;
}

// Defensive: always return arrays
export async function getTransactions(params:Record<string,any>={}){
  const {data}=await api.get('/transactions',{params});
  if (Array.isArray(data)) return data as Transaction[];
  if (data && Array.isArray((data as any).items)) return (data as any).items as Transaction[];
  console.warn('getTransactions: unexpected shape', data);
  return [];
}

export async function getBalanceSeries(params:Record<string,any>={}){
  const {data}=await api.get('/stats/balance_over_time',{params});
  if (Array.isArray(data)) return data as {date:string; balance:number}[];
  if (data && Array.isArray((data as any).series)) return (data as any).series as {date:string; balance:number}[];
  console.warn('getBalanceSeries: unexpected shape', data);
  return [];
}

export async function listCategories(q?:string){
  const {data}=await api.get('/categories',{params: q?{q}:{}});
  if (Array.isArray(data)) return data as {id:number; name:string}[];
  if (data && Array.isArray((data as any).items)) return (data as any).items as {id:number; name:string}[];
  console.warn('listCategories: unexpected shape', data);
  return [];
}

export async function createCategory(name:string){
  const {data}=await api.post('/categories',{name});
  return data as {id:number; name:string};
}
