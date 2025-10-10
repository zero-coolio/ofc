// src/auth.tsx
import React, { createContext, useContext, useEffect, useState } from "react";
import { api, loadApiKey, setApiKey } from "./api";

export type User = {
  id: number;
  email: string;
  name?: string;
  api_key: string;        // ensure the shape the UI expects
  created_at: string;
};

type Ctx = {
  user: User | null;
  loading: boolean;
  loginWithKey: (k: string) => Promise<User>;
  logout: () => void;
  signupBootstrap: (email: string, name?: string) => Promise<User>;
  signupAdmin: (email: string, name?: string) => Promise<User>;
};

const AuthContext = createContext<Ctx>(null!);

// Helper: accept different server field names for the key
function extractKey(obj: any): string | undefined {
  return obj?.api_key || obj?.apiKey || obj?.key || obj?.token;
}

export const AuthProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // On mount, try to use existing key from localStorage
  useEffect(() => {
    const existing = loadApiKey(); // sets axios header if present
    if (!existing) {
      setLoading(false);
      return;
    }
    api
        .get<User>("/users/me")
        .then((r) => {
          // if backend’s /users/me doesn’t include api_key, keep stored key
          const key = extractKey(r.data) || existing;
          setUser({ ...r.data, api_key: key });
        })
        .catch(() => {
          // invalid/expired key -> clear
          setApiKey(undefined);
        })
        .finally(() => setLoading(false));
  }, []);

  async function loginWithKey(k: string) {
    setApiKey(k);
    const { data } = await api.get<User>("/users/me");
    const key = extractKey(data) || k;
    const u: User = { ...data, api_key: key };
    setUser(u);
    return u;
  }

  function logout() {
    setApiKey(undefined);
    setUser(null);
  }

  // POST /users  -> returns api_key on bootstrap (first user)
  async function signupBootstrap(email: string, name?: string) {
    const body = { email, ...(name ? { name } : {}) };
    // Debug trace (visible in devtools console)
    // console.log("[SignupBootstrap] payload:", body);
    const { data } = await api.post<User | any>("/users", body, {
      headers: { "Content-Type": "application/json" },
    });
    const key = extractKey(data);
    if (key) setApiKey(key);

    // Normalize shape for UI: ensure api_key exists on the user object
    const user: User = {
      id: data.id,
      email: data.email,
      name: data.name,
      api_key: key ?? data.api_key ?? "",
      created_at: data.created_at,
    };
    setUser(user);
    return user;
  }

  // POST /users/create -> admin path; should also return api_key
  async function signupAdmin(email: string, name?: string) {
    const body = { email, ...(name ? { name } : {}) };
    // console.log("[SignupAdmin] payload:", body);
    const { data } = await api.post<User | any>("/users/create", body, {
      headers: { "Content-Type": "application/json" },
    });
    const key = extractKey(data);
    if (key) setApiKey(key);

    const user: User = {
      id: data.id,
      email: data.email,
      name: data.name,
      api_key: key ?? data.api_key ?? "",
      created_at: data.created_at,
    };
    setUser(user);
    return user;
  }

  return (
      <AuthContext.Provider
          value={{ user, loading, loginWithKey, logout, signupBootstrap, signupAdmin }}
      >
        {children}
      </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
