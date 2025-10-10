import { Link } from "react-router-dom";
import { useAuth } from "../auth";
import Sidebar from "../components/Sidebar";
import Dashboard from "./Dashboard";
import logo from "/oft-logo.svg";

export default function App() {
  const { user } = useAuth();
  const key = (user as any)?.api_key || localStorage.getItem("ofc_api_key") || "";
  const short = key ? `${key.slice(0, 6)}…${key.slice(-4)}` : "";

  return (
    <div className="app">
      <header>
        <div className="brand">
          <img src={logo} alt="OFT" />
          <strong>Overseas Food Trading — Alpha</strong>
        </div>
        <nav>
          <Link to="/signup">Create User</Link>
          {!user && <Link to="/login">Login</Link>}
          {short && (
            <span title={key} style={{ marginLeft: 8, padding: "4px 8px", borderRadius: 8, background: "rgba(255,255,255,.2)" }}>
              key: {short}
            </span>
          )}
        </nav>
      </header>

      <div className="layout">
        <Sidebar />
        <main className="main">
          {/* Always visible Dashboard */}
          <Dashboard />
        </main>
      </div>

      <footer>© {new Date().getFullYear()} Overseas Food Trading — Alpha</footer>
    </div>
  );
}
