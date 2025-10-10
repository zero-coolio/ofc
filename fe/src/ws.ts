import { getApiKey } from "./api";

export function makeWsUrl() {
  const cfg = (import.meta as any)?.env?.VITE_WS_URL as string | undefined;
  const key = encodeURIComponent(getApiKey());
  if (!cfg || cfg.startsWith("/")) {
    const proto = location.protocol === "https:" ? "wss:" : "ws:";
    const path = cfg || "/ws";
    const qp = key ? `?api_key=${key}` : "";
    return `${proto}//${location.host}${path}${qp}`;
  }
  const qp = key ? (cfg.includes("?") ? `&api_key=${key}` : `?api_key=${key}`) : "";
  return `${cfg}${qp}`;
}

export function connectTransactions(onMessage: (data: any) => void, onStatus?: (open: boolean) => void) {
  const url = makeWsUrl();
  const ws = new WebSocket(url);
  ws.addEventListener("open", () => onStatus && onStatus(true));
  ws.addEventListener("close", () => onStatus && onStatus(false));
  ws.addEventListener("message", (evt) => {
    try { onMessage(JSON.parse(evt.data)); } catch {}
  });
  return { close: () => ws.close() };
}
