import { useState } from "react";
import { useAuth } from "../auth";

export default function Signup() {
  const { signupBootstrap, signupAdmin } = useAuth();
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [mode, setMode] = useState<"bootstrap" | "admin">("bootstrap");
  const [err, setErr] = useState<string | null>(null);
  const [apiKey, setApiKeyLocal] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setApiKeyLocal(null);
    try {
      const u = mode === "bootstrap" ? await signupBootstrap(email, name || undefined) : await signupAdmin(email, name || undefined);
      setApiKeyLocal(u.api_key);
      setEmail(""); setName("");
    } catch (e: any) { setErr(e?.response?.data?.detail || "Signup failed"); }
  }

  return (
    <div className="card" style={{ maxWidth: 560, marginTop: 16 }}>
      <h2>Create User</h2>
      <div className="row">
        <label><input type="radio" checked={mode === "bootstrap"} onChange={() => setMode("bootstrap")} /> Bootstrap</label>
        <label><input type="radio" checked={mode === "admin"} onChange={() => setMode("admin")} /> Admin Create</label>
      </div>
      <form onSubmit={onSubmit} className="grid">
        <input placeholder="email@example.com" value={email} onChange={(e)=>setEmail(e.target.value)} required />
        <input placeholder="Name (optional)" value={name} onChange={(e)=>setName(e.target.value)} />
        {err && <div style={{ color: "#b91c1c" }}>{err}</div>}
        <button type="submit">Create User</button>
      </form>

      {apiKey && (
        <div className="card" style={{ marginTop: 16 }}>
          <h3 style={{ marginTop: 0 }}>Your API Key</h3>
          <div className="row">
            <input readOnly value={apiKey} style={{ flex: 1, fontFamily: "monospace" }} onFocus={(e) => e.currentTarget.select()} />
            <button type="button" className="ghost" onClick={() => navigator.clipboard.writeText(apiKey)}>Copy</button>
          </div>
          <div className="muted" style={{ marginTop: 8, fontSize: 12 }}>Stored locally for this demo and shown in the sidebar.</div>
        </div>
      )}
    </div>
  );
}
