import axios from "axios";

const base = (import.meta as any)?.env?.VITE_API_BASE || "http://127.0.0.1:8000";
export const api = axios.create({ baseURL: base });

// ✅ Ensure JSON is sent on POSTs
api.defaults.headers.post["Content-Type"] = "application/json";

// (keep your existing setApiKey/getApiKey/etc.)


export function setApiKey(key?: string) {
  if (key) {
    api.defaults.headers.common["X-API-Key"] = key;
    localStorage.setItem("ofc_api_key", key);
  } else {
    delete api.defaults.headers.common["X-API-Key"];
    localStorage.removeItem("ofc_api_key");
  }
}
export function getApiKey() { return localStorage.getItem("ofc_api_key") || ""; }
export function loadApiKey() { const k = getApiKey(); if (k) setApiKey(k); return k; }

if ((import.meta as any)?.env?.DEV) {
  console.log("[OFC] API base:", api.defaults.baseURL);
  api.interceptors.request.use((cfg) => {
    console.log(`[OFC] ${cfg.method?.toUpperCase()} ${cfg.baseURL}${cfg.url}`);
    return cfg;
  });
}
