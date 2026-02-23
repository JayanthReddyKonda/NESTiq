import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { submitRender, getRenderStatus, getARSession } from "../api/client";
import type { DesignGenerateResponse, RenderJobResponse } from "../types";
import { ThreeScene } from "./ThreeScene";
import { AgentStream } from "./AgentStream";

interface Props {
    design: DesignGenerateResponse;
    roomWidth: number;
    roomDepth: number;
}

const POLL_INTERVAL_MS = 1500;

export function DesignViewer({ design, roomWidth, roomDepth }: Props) {
    const navigate = useNavigate();
    const [renderJob, setRenderJob] = useState<RenderJobResponse | null>(null);
    const [renderError, setRenderError] = useState<string | null>(null);
    const [polling, setPolling] = useState(false);
    const [activeTab, setActiveTab] = useState<"3d" | "render" | "agent">("3d");

    // ── Render & poll ──────────────────────────────────────────────────────────
    const startRender = useCallback(async () => {
        setRenderError(null);
        try {
            const job = await submitRender(design.design_id);
            setRenderJob(job);
            setPolling(true);
            setActiveTab("render");
        } catch (e) {
            setRenderError(e instanceof Error ? e.message : "Render failed");
        }
    }, [design.design_id]);

    useEffect(() => {
        if (!polling || !renderJob) return;
        if (renderJob.status === "done" || renderJob.status === "failed") {
            setPolling(false);
            return;
        }
        const timer = setTimeout(async () => {
            try {
                const updated = await getRenderStatus(renderJob.job_id);
                setRenderJob(updated);
            } catch {
                setPolling(false);
            }
        }, POLL_INTERVAL_MS);
        return () => clearTimeout(timer);
    }, [polling, renderJob]);

    // ── AR navigation ──────────────────────────────────────────────────────────
    const openAR = async () => {
        try {
            await getARSession(design.design_id); // pre-fetch to validate
            navigate(`/ar/${design.design_id}`);
        } catch (e) {
            alert(e instanceof Error ? e.message : "Failed to start AR session");
        }
    };

    return (
        <div style={styles.wrap}>
            {/* Header */}
            <div style={styles.header}>
                <div>
                    <h2 style={styles.title}>{design.style.charAt(0).toUpperCase() + design.style.slice(1)} Design</h2>
                    <p style={styles.sub}>{design.furniture.length} pieces · ${design.estimated_cost_usd.toLocaleString()}</p>
                </div>
                <div style={styles.actions}>
                    <button style={styles.btnSecondary} onClick={startRender} disabled={polling}>
                        {polling ? "Rendering…" : "Render SDXL"}
                    </button>
                    <button style={styles.btnPrimary} onClick={openAR}>View in AR</button>
                </div>
            </div>

            {/* Color palette */}
            <div style={styles.palette}>
                {design.color_palette.map((c) => (
                    <div key={c} title={c} style={{ ...styles.swatch, background: c }} />
                ))}
                <span style={styles.paletteTxt}>Color palette</span>
            </div>

            {/* Tabs */}
            <div style={styles.tabs}>
                {(["3d", "render", "agent"] as const).map((t) => (
                    <button
                        key={t}
                        onClick={() => setActiveTab(t)}
                        style={{ ...styles.tab, ...(activeTab === t ? styles.tabActive : {}) }}
                    >
                        {t === "3d" ? "3D View" : t === "render" ? "Render" : "Procurement"}
                    </button>
                ))}
            </div>

            {/* Tab content */}
            {activeTab === "3d" && (
                <ThreeScene
                    furniture={design.furniture}
                    roomWidth={roomWidth}
                    roomDepth={roomDepth}
                    colorPalette={design.color_palette}
                />
            )}

            {activeTab === "render" && (
                <div style={styles.renderZone}>
                    {!renderJob && (
                        <div style={styles.emptyRender}>
                            <p style={{ color: "#888" }}>Click "Render SDXL" to generate a photorealistic image.</p>
                        </div>
                    )}
                    {renderJob?.status === "pending" && <p style={styles.renderStatus}>⏳ Queued…</p>}
                    {renderJob?.status === "processing" && (
                        <p style={styles.renderStatus}>
                            <RotatingIcon /> Rendering with SDXL…
                        </p>
                    )}
                    {renderJob?.status === "done" && renderJob.image_url && (
                        <img src={renderJob.image_url} alt="Rendered room" style={styles.renderedImg} />
                    )}
                    {renderJob?.status === "failed" && (
                        <p style={{ color: "#e05c5c" }}>✗ Render failed: {renderJob.error}</p>
                    )}
                    {renderError && <p style={{ color: "#e05c5c" }}>✗ {renderError}</p>}
                </div>
            )}

            {activeTab === "agent" && <AgentStream designId={design.design_id} />}

            {/* Furniture list */}
            <div style={styles.furnitureList}>
                <h3 style={styles.listTitle}>Furniture List</h3>
                {design.furniture.map((f) => (
                    <div key={f.id} style={styles.furnitureItem}>
                        <div style={{ ...styles.colorDot, background: f.color }} />
                        <div style={styles.furnitureInfo}>
                            <span style={styles.furnitureName}>{f.name}</span>
                            <span style={styles.furnitureMeta}>{f.category} · {f.vendor} · {f.sku}</span>
                        </div>
                        {f.price_usd && (
                            <span style={styles.price}>${f.price_usd.toLocaleString()}</span>
                        )}
                    </div>
                ))}
            </div>

            {/* Layout notes */}
            <div style={styles.notes}>
                <strong style={{ color: "#aaa" }}>Layout notes: </strong>
                <span style={{ color: "#888" }}>{design.layout_notes}</span>
            </div>
        </div>
    );
}

function RotatingIcon() {
    return (
        <span
            style={{
                display: "inline-block",
                width: 16,
                height: 16,
                border: "2px solid #7c6ef0",
                borderTopColor: "transparent",
                borderRadius: "50%",
                animation: "spin 0.7s linear infinite",
                marginRight: 8,
                verticalAlign: "middle",
            }}
        />
    );
}

const styles: Record<string, React.CSSProperties> = {
    wrap: { display: "flex", flexDirection: "column", gap: 16, padding: "0 0 32px" },
    header: { display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12 },
    title: { fontSize: 20, fontWeight: 700, color: "#e8e8ec" },
    sub: { color: "#888", fontSize: 13, marginTop: 2 },
    actions: { display: "flex", gap: 10 },
    btnPrimary: {
        padding: "8px 20px", borderRadius: 8, border: "none", cursor: "pointer",
        background: "#7c6ef0", color: "#fff", fontWeight: 600, fontSize: 14,
    },
    btnSecondary: {
        padding: "8px 20px", borderRadius: 8, border: "1px solid #3a3a4a", cursor: "pointer",
        background: "transparent", color: "#aaa", fontWeight: 600, fontSize: 14,
    },
    palette: { display: "flex", alignItems: "center", gap: 8 },
    swatch: { width: 24, height: 24, borderRadius: 6, border: "1px solid rgba(255,255,255,0.1)" },
    paletteTxt: { color: "#666", fontSize: 12, marginLeft: 4 },
    tabs: { display: "flex", gap: 4, borderBottom: "1px solid #2a2a3a", paddingBottom: 0 },
    tab: {
        padding: "8px 18px", borderRadius: "8px 8px 0 0", border: "none",
        background: "transparent", color: "#888", cursor: "pointer", fontSize: 14,
    },
    tabActive: { background: "#1e1e30", color: "#e8e8ec", borderBottom: "2px solid #7c6ef0" },
    renderZone: { minHeight: 300, display: "flex", alignItems: "center", justifyContent: "center", background: "#111118", borderRadius: 12 },
    emptyRender: { textAlign: "center", padding: 40 },
    renderStatus: { color: "#aaa", display: "flex", alignItems: "center" },
    renderedImg: { width: "100%", borderRadius: 12, objectFit: "cover" },
    furnitureList: { display: "flex", flexDirection: "column", gap: 8 },
    listTitle: { fontSize: 15, fontWeight: 600, color: "#aaa", marginBottom: 4 },
    furnitureItem: { display: "flex", alignItems: "center", gap: 12, padding: "10px 14px", background: "#16161f", borderRadius: 8 },
    colorDot: { width: 16, height: 16, borderRadius: 4, flexShrink: 0 },
    furnitureInfo: { flex: 1, display: "flex", flexDirection: "column" },
    furnitureName: { fontSize: 14, fontWeight: 600, color: "#e8e8ec" },
    furnitureMeta: { fontSize: 12, color: "#666" },
    price: { fontSize: 14, fontWeight: 600, color: "#7c6ef0" },
    notes: { fontSize: 13, padding: "12px 16px", background: "#13131b", borderRadius: 8, lineHeight: 1.6 },
};
