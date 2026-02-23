import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { Home } from "./pages/Home";
import { ARPage } from "./components/ARPage";

export default function App() {
    return (
        <BrowserRouter>
            <div style={styles.app}>
                {/* Global nav */}
                <header style={styles.nav}>
                    <Link to="/" style={styles.logo}>
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#7c6ef0" strokeWidth="2">
                            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                            <polyline points="9 22 9 12 15 12 15 22" />
                        </svg>
                        <span>SpaceForge</span>
                    </Link>
                    <nav style={styles.navLinks}>
                        <Link to="/" style={styles.navLink}>Design</Link>
                        <a href="/docs" target="_blank" rel="noreferrer" style={styles.navLink}>API Docs</a>
                    </nav>
                </header>

                {/* Pages */}
                <div style={styles.content}>
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/ar/:designId" element={<ARPage />} />
                    </Routes>
                </div>

                {/* Footer */}
                <footer style={styles.footer}>
                    SpaceForge · AI Interior Design · FakeProvider active ·{" "}
                    <span style={{ color: "#555" }}># TODO: PRODUCTION</span>
                </footer>
            </div>

            {/* Global CSS animations */}
            <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        a { color: inherit; text-decoration: none; }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #111; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
      `}</style>
        </BrowserRouter>
    );
}

const styles: Record<string, React.CSSProperties> = {
    app: { minHeight: "100vh", display: "flex", flexDirection: "column" },
    nav: {
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "12px 24px", borderBottom: "1px solid #1e1e2e",
        background: "rgba(15, 15, 19, 0.95)", backdropFilter: "blur(12px)",
        position: "sticky", top: 0, zIndex: 100,
    },
    logo: {
        display: "flex", alignItems: "center", gap: 10,
        fontSize: 18, fontWeight: 800, color: "#e8e8ec", letterSpacing: -0.5,
    },
    navLinks: { display: "flex", gap: 24 },
    navLink: { fontSize: 14, color: "#888", transition: "color 0.2s" },
    content: { flex: 1, padding: "32px 24px" },
    footer: { textAlign: "center", padding: "16px 24px", color: "#444", fontSize: 12, borderTop: "1px solid #1a1a2a" },
};
