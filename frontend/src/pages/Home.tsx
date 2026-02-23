import React, { useState } from "react";
import { generateDesign } from "../api/client";
import type { DesignGenerateResponse, RoomAnalyzeResponse } from "../types";
import { RoomUploader } from "../components/RoomUploader";
import { DesignViewer } from "../components/DesignViewer";

const STYLES = ["modern", "scandinavian", "industrial", "bohemian", "minimalist", "traditional"];

export function Home() {
    const [analysis, setAnalysis] = useState<RoomAnalyzeResponse | null>(null);
    const [design, setDesign] = useState<DesignGenerateResponse | null>(null);
    const [generating, setGenerating] = useState(false);
    const [genError, setGenError] = useState<string | null>(null);
    const [selectedStyle, setSelectedStyle] = useState("modern");

    const handleAnalyzed = (result: RoomAnalyzeResponse) => {
        setAnalysis(result);
        setDesign(null);
    };

    const handleGenerate = async () => {
        if (!analysis) return;
        setGenerating(true);
        setGenError(null);
        try {
            const d = await generateDesign(analysis.room_id, selectedStyle);
            setDesign(d);
        } catch (e) {
            setGenError(e instanceof Error ? e.message : "Generation failed");
        } finally {
            setGenerating(false);
        }
    };

    return (
        <main style={styles.main}>
            {/* Step 1 — Upload */}
            <section style={styles.section}>
                <StepBadge n={1} />
                <RoomUploader onAnalyzed={handleAnalyzed} />
            </section>

            {/* Analysis result */}
            {analysis && (
                <section style={styles.section}>
                    <div style={styles.analysisCard}>
                        <h3 style={styles.cardTitle}>Room Analysis</h3>
                        <div style={styles.analysisGrid}>
                            <Chip label="Type" value={analysis.analysis.room_type.replace("_", " ")} />
                            <Chip label="Lighting" value={analysis.analysis.lighting} />
                            <Chip label="Width" value={`${analysis.analysis.dimensions.width}m`} />
                            <Chip label="Depth" value={`${analysis.analysis.dimensions.depth}m`} />
                            <Chip label="Confidence" value={`${Math.round(analysis.analysis.confidence * 100)}%`} />
                            <Chip label="Features" value={analysis.analysis.existing_features.join(", ")} />
                        </div>
                    </div>
                </section>
            )}

            {/* Step 2 — Generate */}
            {analysis && (
                <section style={styles.section}>
                    <StepBadge n={2} />
                    <div style={styles.genSection}>
                        <h2 style={styles.sectionTitle}>Generate Design</h2>
                        <div style={styles.styleRow}>
                            {STYLES.map((s) => (
                                <button
                                    key={s}
                                    onClick={() => setSelectedStyle(s)}
                                    style={{
                                        ...styles.styleBtn,
                                        ...(selectedStyle === s ? styles.styleBtnActive : {}),
                                    }}
                                >
                                    {s.charAt(0).toUpperCase() + s.slice(1)}
                                </button>
                            ))}
                        </div>
                        <button onClick={handleGenerate} disabled={generating} style={styles.generateBtn}>
                            {generating ? "Generating…" : "Generate Design"}
                        </button>
                        {genError && <p style={{ color: "#e05c5c", fontSize: 13 }}>✗ {genError}</p>}
                    </div>
                </section>
            )}

            {/* Step 3 — Design Viewer */}
            {design && (
                <section style={styles.section}>
                    <StepBadge n={3} />
                    <h2 style={styles.sectionTitle}>Your Design</h2>
                    <DesignViewer
                        design={design}
                        roomWidth={analysis?.analysis.dimensions.width ?? 4}
                        roomDepth={analysis?.analysis.dimensions.depth ?? 6}
                    />
                </section>
            )}
        </main>
    );
}

function StepBadge({ n }: { n: number }) {
    return (
        <div style={styles.stepBadge}>
            <span>{n}</span>
        </div>
    );
}

function Chip({ label, value }: { label: string; value: string }) {
    return (
        <div style={styles.chip}>
            <span style={styles.chipLabel}>{label}</span>
            <span style={styles.chipValue}>{value}</span>
        </div>
    );
}

const styles: Record<string, React.CSSProperties> = {
    main: { maxWidth: 860, margin: "0 auto", padding: "0 16px 64px", display: "flex", flexDirection: "column", gap: 32 },
    section: { position: "relative", display: "flex", flexDirection: "column", gap: 16 },
    sectionTitle: { fontSize: 18, fontWeight: 700, color: "#e8e8ec" },
    stepBadge: {
        width: 28, height: 28, borderRadius: "50%", background: "#7c6ef0",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 13, fontWeight: 700, color: "#fff",
        position: "absolute", top: 0, left: -40,
    },
    analysisCard: { background: "#13131b", borderRadius: 12, padding: "16px 20px" },
    cardTitle: { fontSize: 14, fontWeight: 600, color: "#aaa", marginBottom: 12 },
    analysisGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 10 },
    chip: { background: "#1a1a26", borderRadius: 8, padding: "8px 12px", display: "flex", flexDirection: "column", gap: 2 },
    chipLabel: { fontSize: 11, color: "#666", textTransform: "uppercase", letterSpacing: 0.5 },
    chipValue: { fontSize: 13, color: "#e8e8ec", fontWeight: 600 },
    genSection: { display: "flex", flexDirection: "column", gap: 14 },
    styleRow: { display: "flex", flexWrap: "wrap", gap: 8 },
    styleBtn: {
        padding: "6px 14px", borderRadius: 20, border: "1px solid #3a3a4a",
        background: "transparent", color: "#888", cursor: "pointer", fontSize: 13,
    },
    styleBtnActive: { background: "#7c6ef0", color: "#fff", border: "1px solid #7c6ef0" },
    generateBtn: {
        padding: "10px 28px", borderRadius: 10, border: "none", cursor: "pointer",
        background: "linear-gradient(135deg, #7c6ef0 0%, #a06cf0 100%)",
        color: "#fff", fontWeight: 700, fontSize: 15, alignSelf: "flex-start",
    },
};
