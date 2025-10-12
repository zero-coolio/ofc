import React, { useEffect, useMemo, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { motion } from 'framer-motion'
import { Activity, Eye, EyeOff, Info, Link as LinkIcon, RefreshCw } from 'lucide-react'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { LineChart, Line, XAxis, YAxis, Tooltip as ReTooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

function usePersistedState(key, initial) {
  const [v, setV] = useState(() => {
    try { const raw = localStorage.getItem(key); return raw ? JSON.parse(raw) : initial; } catch { return initial; }
  })
  useEffect(() => { try { localStorage.setItem(key, JSON.stringify(v)); } catch {} }, [key, v])
  return [v, setV]
}

function FieldRow({ label, children, hint }) {
  return (
    <div className="grid grid-cols-12 items-center gap-3 py-2">
      <Label className="col-span-3 text-sm text-muted-foreground">{label}</Label>
      <div className="col-span-9 flex items-center gap-2">
        {children}
        {hint && (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Info className="h-4 w-4 text-muted-foreground" />
              </TooltipTrigger>
              <TooltipContent>{hint}</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        )}
      </div>
    </div>
  )
}

function pretty(obj) { try { return JSON.stringify(obj, null, 2); } catch { return String(obj); } }
function asQuery(params) {
  const sp = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => { if (v === undefined || v === null || v === '') return; sp.set(k, String(v)) })
  const qs = sp.toString()
  return qs ? `?${qs}` : ''
}

export default function App() {
  const [apiBase, setApiBase] = usePersistedState('ofc.apiBase', 'http://localhost:8080')
  const [apiKey, setApiKey] = usePersistedState('ofc.apiKey', '')
  const [debug, setDebug] = usePersistedState('ofc.debug', true)
  const [logs, setLogs] = useState([])

  const [userEmail, setUserEmail] = useState('')
  const [createUserStatus, setCreateUserStatus] = useState(null)
  const [amount, setAmount] = useState('')
  const [description, setDescription] = useState('')
  const [category, setCategory] = useState('')
  const [isDebit, setIsDebit] = useState(true)
  const [submitStatus, setSubmitStatus] = useState(null)
  const [jsonOutput, setJsonOutput] = useState(null)

  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [filterCategory, setFilterCategory] = useState('')
  const [minAmount, setMinAmount] = useState('')
  const [maxAmount, setMaxAmount] = useState('')
  const [showGraph, setShowGraph] = useState(false)
  const [transactions, setTransactions] = useState([])

  const headers = useMemo(() => ({ 'Content-Type': 'application/json', 'x-api-key': apiKey || '' }), [apiKey])
  const swaggerUrl = useMemo(() => { try { return new URL('/swagger', apiBase).toString() } catch { return '#' } }, [apiBase])

  function vlog(scope, payload) {
    if (!debug) return
    const entry = { t: new Date().toISOString(), scope, payload }
    setLogs(l => [...l.slice(-99), entry])
    try { console.debug(`[OFC][${entry.t}][${scope}]`, payload) } catch {}
  }

  async function safeFetch(path, opts = {}) {
    const url = new URL(path, apiBase).toString()
    const method = (opts.method || 'GET').toUpperCase()
    vlog('fetch.request', { url, method })
    const res = await fetch(url, { ...opts, headers: { ...headers, ...(opts.headers || {}) } })
    const text = await res.text()
    let json; try { json = JSON.parse(text) } catch { json = text }
    vlog('fetch.response', { url, status: res.status, ok: res.ok })
    return { ok: res.ok, status: res.status, json }
  }

  async function handleHealthCheck() {
    vlog('health.start')
    try { const { ok, status, json } = await safeFetch('/health', { method: 'GET' })
      setJsonOutput({ source: 'health', ok, status, json })
      vlog('health.done', json)
    } catch (e) { vlog('health.error', e) }
  }

  async function handleCreateUser() {
    vlog('users.start', { email: userEmail })
    try { const { ok, status, json } = await safeFetch('/users', { method: 'POST', body: JSON.stringify({ email: userEmail }) })
      setCreateUserStatus({ state: ok ? 'success' : 'error', status, json })
      setJsonOutput({ source: 'users', ok, status, json })
      vlog('users.done', json)
    } catch (e) { vlog('users.error', e) }
  }

  async function handleSubmitTransaction() {
    const body = { amount: Number(amount), description, category, type: isDebit ? 'debit' : 'credit' }
    vlog('tx.start', body)
    try { const { ok, status, json } = await safeFetch('/transactions', { method: 'POST', body: JSON.stringify(body) })
      setSubmitStatus({ state: ok ? 'success' : 'error', status, json })
      setJsonOutput({ source: 'transaction', ok, status, json })
      vlog('tx.done', json)
    } catch (e) { vlog('tx.error', e) }
  }

  async function handleFetchTransactions() {
    const params = { date_from: dateFrom, date_to: dateTo, category: filterCategory, min_amount: minAmount, max_amount: maxAmount }
    vlog('list.start', params)
    try { const { json } = await safeFetch(`/transactions${asQuery(params)}`, { method: 'GET' })
      const items = Array.isArray(json?.items) ? json.items : Array.isArray(json) ? json : []
      setTransactions(items)
      vlog('list.done', { count: items.length })
    } catch (e) { vlog('list.error', e) }
  }

  return (
    <div className="flex min-h-screen w-full text-slate-900">
      <aside className="w-72 bg-slate-800 text-white p-4 hidden md:block overflow-y-auto">
        <h2 className="text-lg font-semibold mb-4">OFC Console</h2>
        <nav className="space-y-1 text-sm mb-4">
          <a href="#display" className="block hover:bg-slate-700/60 p-2 rounded">Display</a>
          <a href={swaggerUrl} target="_blank" rel="noreferrer" className="block hover:bg-slate-700/60 p-2 rounded">Swagger</a>
        </nav>

        <section id="users" className="mb-6">
          <div className="text-sm font-semibold mb-2">Users</div>
          <Input placeholder="user@example.com" value={userEmail} onChange={(e)=>setUserEmail(e.target.value)} />
          <Button className="w-full mt-2" onClick={handleCreateUser} disabled={!userEmail}>Create User</Button>
        </section>

        <section id="submit" className="mb-6">
          <div className="text-sm font-semibold mb-2">Submit Transaction</div>
          <Input type="number" placeholder="Amount" value={amount} onChange={(e)=>setAmount(e.target.value)} />
          <Input placeholder="Description" value={description} onChange={(e)=>setDescription(e.target.value)} className="mt-2" />
          <Input placeholder="Category" value={category} onChange={(e)=>setCategory(e.target.value)} className="mt-2" />
          <div className="flex justify-between items-center text-xs mt-2">
            <span>Type</span>
            <Button size="sm" variant="secondary" onClick={()=>setIsDebit(!isDebit)}>{isDebit ? 'Debit' : 'Credit'}</Button>
          </div>
          <Button className="w-full mt-2" onClick={handleSubmitTransaction} disabled={!amount}>Submit</Button>
        </section>

        <section className="mt-6 border-t border-slate-700 pt-4">
          <div className="text-sm font-semibold mb-2 flex items-center gap-2"><Activity className="h-4 w-4"/>Health Check</div>
          <Button className="w-full mb-2" variant="secondary" onClick={handleHealthCheck}>Ping /health</Button>
        </section>

        <section className="mt-4 border-t border-slate-700 pt-4">
          <div className="text-sm font-semibold mb-2">JSON Output</div>
          {jsonOutput ? (
            <pre className="rounded bg-slate-900/60 text-slate-100 p-2 text-[10px] overflow-auto border border-slate-700 max-h-60">{pretty(jsonOutput)}</pre>
          ) : (
            <p className="text-xs text-slate-400">No output yet.</p>
          )}
        </section>

        <section className="mt-4 border-t border-slate-700 pt-4">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm font-semibold">Debug Console</div>
            <div className="flex items-center gap-2">
              <Button size="sm" variant="secondary" onClick={()=>setLogs([])}>Clear Logs</Button>
            </div>
          </div>
          {logs.length === 0 ? (
            <p className="text-xs text-slate-400">No logs yet.</p>
          ) : (
            <pre className="rounded bg-slate-900/60 text-slate-100 p-2 text-[10px] overflow-auto border border-slate-700 max-h-60">
              {logs.map((l,i)=>(`${i+1}. [${l.t}] ${l.scope}\n`)).join('')}
            </pre>
          )}
        </section>
      </aside>

      <main className="flex-1 bg-gradient-to-b from-slate-50 to-white">
        <div className="mx-auto max-w-7xl px-4 py-6 md:py-10">
          <motion.h1 initial={{opacity:0,y:-8}} animate={{opacity:1,y:0}} transition={{duration:0.4}} className="text-2xl md:text-3xl font-semibold tracking-tight mb-6">OFC — Admin & Transactions Console</motion.h1>

          <Card id="settings" className="mb-6">
            <CardHeader className="pb-2"><CardTitle>Settings</CardTitle></CardHeader>
            <CardContent>
              <FieldRow label="API Base URL" hint="Used for all requests and Swagger link">
                <Input value={apiBase} onChange={(e)=>setApiBase(e.target.value)} placeholder="https://api.example.com" />
              </FieldRow>
              <FieldRow label="API Key" hint="Sent as x-api-key in every request">
                <Input type="password" value={apiKey} onChange={(e)=>setApiKey(e.target.value)} placeholder="••••••" />
              </FieldRow>
              <FieldRow label="Verbose Logging">
                <Switch checked={!!debug} onCheckedChange={setDebug} />
              </FieldRow>
            </CardContent>
          </Card>

          <Card id="filters" className="mb-6">
            <CardHeader className="pb-2"><CardTitle>Filter Transactions</CardTitle></CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FieldRow label="Date From"><Input type="date" value={dateFrom} onChange={(e)=>setDateFrom(e.target.value)} /></FieldRow>
                <FieldRow label="Date To"><Input type="date" value={dateTo} onChange={(e)=>setDateTo(e.target.value)} /></FieldRow>
                <FieldRow label="Category"><Input value={filterCategory} onChange={(e)=>setFilterCategory(e.target.value)} /></FieldRow>
                <FieldRow label="Min Amount"><Input type="number" value={minAmount} onChange={(e)=>setMinAmount(e.target.value)} /></FieldRow>
                <FieldRow label="Max Amount"><Input type="number" value={maxAmount} onChange={(e)=>setMaxAmount(e.target.value)} /></FieldRow>
              </div>
              <div className="flex items-center gap-3 pt-2">
                <Button onClick={handleFetchTransactions}>Retrieve Transactions</Button>
                <Button variant="outline" onClick={()=>setShowGraph(s=>!s)}>{showGraph ? (<><EyeOff className="mr-2 h-4 w-4"/>Show List</>) : (<><Eye className="mr-2 h-4 w-4"/>Show Graph</>)}</Button>
              </div>
            </CardContent>
          </Card>

          <Card id="display" className="mt-6">
            <CardHeader className="pb-2"><CardTitle>Transactions Display</CardTitle></CardHeader>
            <CardContent>
              <div className={showGraph ? "hidden" : "block"}>
                {transactions.length === 0 ? <p className="text-sm text-muted-foreground">No transactions yet.</p> : (
                  <div className="overflow-auto rounded-lg border">
                    <table className="min-w-full text-sm">
                      <thead className="bg-slate-50">
                        <tr><th className="text-left p-2">Date</th><th className="text-left p-2">Description</th><th className="text-left p-2">Category</th><th className="text-right p-2">Type</th><th className="text-right p-2">Amount</th></tr>
                      </thead>
                      <tbody>
                        {transactions.map((t,i)=>(<tr key={i} className="odd:bg-white even:bg-slate-50"><td className="p-2">{(t.date||t.created_at||"").slice(0,10)}</td><td className="p-2">{t.description||"—"}</td><td className="p-2">{t.category||"—"}</td><td className="p-2 text-right">{t.type||"—"}</td><td className="p-2 text-right">{Number(t.amount)?.toFixed?.(2)??t.amount}</td></tr>))}
                      </tbody>
                    </table>
                  </div>)}
              </div>
              <div className={showGraph ? "block" : "hidden"}>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={transactions.map(t=>({ date:(t.date||t.created_at||"").slice(0,10), value:Number(t.amount)||0 }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" /><YAxis /><ReTooltip />
                    <Line type="monotone" dataKey="value" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
