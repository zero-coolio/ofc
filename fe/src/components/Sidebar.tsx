// src/components/Sidebar.tsx
import { useEffect, useState } from "react";
import { useAuth } from "../auth";
import { api, getApiKey } from "../api";

type Kind = "credit" | "debit";
type Category = { id: number; name: string; created_at: string };

export default function Sidebar() {
  const { user, loginWithKey, logout, signupBootstrap } = useAuth();

  const [apiKeyInput, setApiKeyInput] = useState("");
  const [email, setEmail] = useState("");

  const [categories, setCategories] = useState<Category[]>([]);
  const [loadingCats, setLoadingCats] = useState(false);

  const [amount, setAmount] = useState<string>("");
  const [kind, setKind] = useState<Kind>("debit");
  const [occurredAt, setOccurredAt] = useState<string>(
      new Date().toISOString().slice(0, 10)
  );
  const [description, setDescription] = useState("");
  const [categoryId, setCategoryId] = useState<number | "">("");
  const [submitStatus, setSubmitStatus] = useState<"idle" | "ok" | "err">(
      "idle"
  );

  // Always compute from latest user or localStorage
  const visibleKey = (user as any)?.api_key ?? getApiKey() ?? "";

  useEffect(() => {
    (async () => {
      setLoadingCats(true);
      try {
        const { data } = await api.get<Category[]>("/categories");
        setCategories(data);
      } catch (err) {
        console.error("Failed to load categories", err);
      } finally {
        setLoadingCats(false);
      }
    })();
  }, []);

  useEffect(() => {
    console.log("[OFC] Sidebar visibleKey:", visibleKey, "user:", user);
  }, [visibleKey, user]);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    await loginWithKey(apiKeyInput.trim());
    setApiKeyInput("");
  }

  async function handleBootstrap(e: React.FormEvent) {
    e.preventDefault();
    if (!email) return;
    await signupBootstrap(email);
    setEmail("");
  }

  async function submitTransaction(e: React.FormEvent) {
    e.preventDefault();
    setSubmitStatus("idle");
    try {
      await api.post("/transactions", {
        amount: Number(amount),
        kind,
        occurred_at: occurredAt,
        description: description || undefined,
        category_id: categoryId === "" ? undefined : Number(categoryId),
      });
      setAmount("");
      setDescription("");
      setCategoryId("");
      setSubmitStatus("ok");
      setTimeout(() => setSubmitStatus("idle"), 1500);
    } catch (err) {
      console.error("Failed to submit transaction", err);
      setSubmitStatus("err");
      setTimeout(() => setSubmitStatus("idle"), 2000);
    }
  }

  return (
      <aside className="sidebar" style={{ display: "flex", flexDirection: "column" }}>
        <div>
          <h3 style={{ marginTop: 0 }}>Account</h3>

          {user ? (
              <div className="grid">
                <div>
                  <b>{user.email}</b>
                </div>

                {/* ✅ Always show the API key line */}
                <div className="grid" style={{ marginTop: 8 }}>
                  <label className="muted" style={{ fontSize: 12 }}>
                    API key = {visibleKey || "(none)"}
                  </label>
                  <div className="row">
                    <input
                        readOnly
                        value={visibleKey}
                        placeholder="no key"
                        style={{ flex: 1, fontFamily: "monospace" }}
                        onFocus={(e) => e.currentTarget.select()}
                    />
                    <button
                        type="button"
                        className="ghost"
                        onClick={() => navigator.clipboard.writeText(visibleKey)}
                    >
                      Copy
                    </button>
                  </div>
                </div>

                <button className="ghost" onClick={logout} style={{ marginTop: 8 }}>
                  Logout
                </button>
              </div>
          ) : (
              <form onSubmit={handleLogin} className="grid">
                <label>API Key</label>
                <input
                    placeholder="X-API-Key"
                    value={apiKeyInput}
                    onChange={(e) => setApiKeyInput(e.target.value)}
                />
                <button type="submit">Login</button>

                <div className="muted" style={{ fontSize: 12 }}>
                  No users yet? Enter email to bootstrap:
                </div>
                <div className="row">
                  <input
                      placeholder="email@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                  />
                  <button type="button" className="ghost" onClick={handleBootstrap}>
                    Bootstrap
                  </button>
                </div>
              </form>
          )}
        </div>

        <div style={{ flex: 1 }} />

        {/* New Transaction pinned to bottom */}
        <div className="card" style={{ marginTop: 8 }}>
          <h4 style={{ marginTop: 0, marginBottom: 8 }}>New Transaction</h4>
          <form onSubmit={submitTransaction} className="grid">
            <div className="row">
              <input
                  type="number"
                  step="0.01"
                  placeholder="Amount"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  required
              />
              <select
                  value={kind}
                  onChange={(e) => setKind(e.target.value as Kind)}
              >
                <option value="debit">Debit</option>
                <option value="credit">Credit</option>
              </select>
            </div>
            <input
                type="date"
                value={occurredAt}
                onChange={(e) => setOccurredAt(e.target.value)}
            />
            <select
                value={categoryId}
                onChange={(e) =>
                    setCategoryId(e.target.value === "" ? "" : Number(e.target.value))
                }
                disabled={loadingCats}
            >
              <option value="">
                {loadingCats ? "Loading categories…" : "(no category)"}
              </option>
              {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
              ))}
            </select>
            <input
                placeholder="Description (optional)"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
            />
            <button type="submit">Add</button>
            {submitStatus === "ok" && (
                <div className="muted" style={{ color: "#0a7f3b" }}>
                  Added!
                </div>
            )}
            {submitStatus === "err" && (
                <div className="muted" style={{ color: "#b91c1c" }}>
                  Failed to add
                </div>
            )}
          </form>
        </div>
      </aside>
  );
}
