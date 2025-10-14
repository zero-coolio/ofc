
import axios from 'axios';
const envBase = (import.meta as any).env?.VITE_API_BASE as string | undefined;
const savedBase = typeof window!=='undefined'? localStorage.getItem('apiBase') || undefined : undefined;
let BASE = savedBase || envBase || 'http://localhost:8080';
export const api = axios.create({ baseURL: BASE, timeout: 10000 });
export function setApiBase(url:string){ BASE=url; api.defaults.baseURL=url; try{ localStorage.setItem('apiBase', url) }catch{} }
export function getApiBase(){ return BASE }
export async function pingApi(){ try{ await api.get('/transactions', { params: { limit:1, offset:0 } }); return true } catch { return false } }
api.interceptors.request.use(c=>{ console.log('📤', c.method?.toUpperCase(), c.baseURL+c.url, {params:c.params, data:c.data}); return c });
api.interceptors.response.use(r=>{ console.log('📥', r.status, r.config.baseURL+r.config.url, r.data); return r });

export type TxType='credit'|'debit';
export interface Transaction{ id:number; amount:number; txn_type:TxType; description:string; category?:string|null; occurred_at:string; created_at:string }
export interface CreateTransaction{ amount:number; txn_type:TxType; description:string; category?:string|null; occurred_at:string }

export async function createTransaction(p:CreateTransaction){ const {data}=await api.post('/transactions', p); return data as Transaction }
export async function getTransactions(params:Record<string,any>={}){ const {data}=await api.get('/transactions',{params}); return data as Transaction[] }
export async function getBalanceSeries(params:Record<string,any>={}){ const {data}=await api.get('/stats/balance_over_time',{params}); return data as {date:string; balance:number}[] }
export async function listCategories(q?:string){ const {data}=await api.get('/categories',{params:q?{q}:{}}); return data as {id:number; name:string}[] }
export async function createCategory(name:string){ const {data}=await api.post('/categories',{name}); return data as {id:number; name:string} }
