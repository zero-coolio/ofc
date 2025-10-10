import { useState } from "react";
import { useAuth } from "../auth";

export default function Login() {
  const { loginWithKey } = useAuth();
  const [apiKey, setApiKey] = useState("");
  const [err, setErr] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    try {
      await loginWithKey(apiKey.trim());
      setApiKey("");
    } catch (e: any) {
      setErr(e?.response?.data?.detail || "Login failed");
    }
  }

  return (
    <div className="card" style={{ maxWidth: 520, marginTop: 16 }}>
      <h2>Login</h2>
      <form onSubmit={onSubmit} className="grid">
        <input placeholder="X-API-Key" value={apiKey} onChange={(e)=>setApiKey(e.target.value)} required />
        {err && <div style={{ color: "#b91c1c" }}>{err}</div>}
        <button type="submit">Login</button>
      </form>
    </div>
  );
}
