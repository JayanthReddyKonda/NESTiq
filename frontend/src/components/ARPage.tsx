/**
 * AR Page — uses <model-viewer> web component.
 * Supports: WebXR, Scene Viewer (Android), Quick Look (iOS).
 * model-viewer is loaded from CDN in index.html.
 */

import React, { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getARSession } from "../api/client";
import type { ARSessionResponse } from "../types";

// Extend JSX types for model-viewer web component
declare global {
    // eslint-disable-next-line @typescript-eslint/no-namespace
    namespace JSX {
        interface IntrinsicElements {
            "model-viewer": React.DetailedHTMLProps<
                React.HTMLAttributes<HTMLElement> & {
                    src?: string;
                    alt?: string;
                    "ar-modes"?: string;
                    "camera-controls"?: boolean | string;
                    "auto-rotate"?: boolean | string;
                    "shadow-intensity"?: string;
                    ar?: boolean | string;
                    "ios-src"?: string;
                    poster?: string;
                    style?: React.CSSProperties;
                },
                HTMLElement
            >;
        }
    }
}

export function ARPage() {
    const { designId } = useParams<{ designId: string }>();
    const navigate = useNavigate();
    const [session, setSession] = useState<ARSessionResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const viewerRef = useRef<HTMLElement>(null);

    useEffect(() => {
        if (!designId) return;
        getARSession(designId)
            .then(setSession)
            .catch((e) => setError(e instanceof Error ? e.message : "Failed to load AR session"))
            .finally(() => setLoading(false));
    }, [designId]);

    if (loading) {
        return (
            <div style={styles.center}>
                <Spinner />
                <p style={{ color: "#888", marginTop: 12 }}>Loading AR session…</p>
            </div>
        );
    }

    if (error || !session) {
        return (
            <div style={styles.center}>
                <p style={{ color: "#e05c5c" }}>✗ {error || "Session not found"}</p>
                <button onClick={() => navigate(-1)} style={styles.backBtn}>← Back</button>
            </div>
        );
    }

    return (
        <div style={styles.wrap}>
            {/* Header */}
            <div style={styles.header}>
                <button onClick={() => navigate(-1)} style={styles.backBtn}>← Back</button>
                <h2 style={styles.title}>Augmented Reality View</h2>
                <span style={{ color: "#666", fontSize: 13 }}>Scale: {session.scale_factor}×</span>
            </div>

            {/* model-viewer */}
            <model-viewer
                ref={viewerRef as React.RefObject<HTMLElement>}
                src={session.model_url}
                alt={`SpaceForge design ${session.design_id}`}
                ar
                ar-modes={session.ar_modes}
                camera-controls
                auto-rotate
                shadow-intensity="1"
                style={styles.viewer}
            />

            {/* Furniture positions info */}
            <div style={styles.infoPanel}>
                <h3 style={styles.infoTitle}>Furniture Positions</h3>
                <div style={styles.grid}>
                    {session.positions.map((pos) => (
                        <div key={pos.furniture_id} style={styles.posCard}>
                            <span style={styles.posId}>{pos.furniture_id.slice(0, 8)}…</span>
                            <span style={styles.posCoords}>
                                x:{pos.x.toFixed(2)} y:{pos.y.toFixed(2)} z:{pos.z.toFixed(2)}
                            </span>
                            <span style={styles.posRot}>↻ {pos.rotation_y}°</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* AR instructions */}
            <div style={styles.instructions}>
                <p>
                    <strong style={{ color: "#7c6ef0" }}>Android</strong> — opens Google Scene Viewer automatically.
                </p>
                <p>
                    <strong style={{ color: "#7c6ef0" }}>iOS</strong> — uses Apple Quick Look via USDZ fallback.
                </p>
                <p>
                    <strong style={{ color: "#7c6ef0" }}>Desktop</strong> — orbits the 3D model with mouse / touch.
                </p>
                <p style={{ color: "#555", fontSize: 12, marginTop: 8 }}>
                    AR model is a placeholder. Replace with real GLTF/USDZ in production.
                    {/* TODO: PRODUCTION */}
                </p>
            </div>
        </div>
    );
}

function Spinner() {
    return (
        <span
            style={{
                display: "block",
                width: 32,
                height: 32,
                border: "3px solid #7c6ef0",
                borderTopColor: "transparent",
                borderRadius: "50%",
                animation: "spin 0.7s linear infinite",
            }}
        />
    );
}

const styles: Record<string, React.CSSProperties> = {
    wrap: { display: "flex", flexDirection: "column", gap: 20, padding: "24px 0 48px", maxWidth: 860, margin: "0 auto" },
    center: { display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: "60vh", gap: 12 },
    header: { display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" },
    backBtn: {
        padding: "6px 14px", borderRadius: 8, border: "1px solid #3a3a4a",
        background: "transparent", color: "#aaa", cursor: "pointer", fontSize: 14,
    },
    title: { flex: 1, fontSize: 20, fontWeight: 700, color: "#e8e8ec" },
    viewer: {
        width: "100%",
        height: 480,
        background: "#111118",
        borderRadius: 16,
        border: "1px solid #2a2a3a",
    } as React.CSSProperties,
    infoPanel: { background: "#13131b", borderRadius: 12, padding: 20 },
    infoTitle: { fontSize: 15, fontWeight: 600, color: "#aaa", marginBottom: 12 },
    grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 10 },
    posCard: { background: "#1a1a26", borderRadius: 8, padding: "10px 14px", display: "flex", flexDirection: "column", gap: 4 },
    posId: { fontSize: 11, color: "#555", fontFamily: "monospace" },
    posCoords: { fontSize: 13, color: "#aaa", fontFamily: "monospace" },
    posRot: { fontSize: 12, color: "#7c6ef0" },
    instructions: { background: "#111118", borderRadius: 12, padding: 20, display: "flex", flexDirection: "column", gap: 8, fontSize: 14, color: "#888", lineHeight: 1.7 },
};
