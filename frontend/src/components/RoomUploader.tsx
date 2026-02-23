import React, { useCallback, useState } from "react";
import { analyzeRoom } from "../api/client";
import type { RoomAnalyzeResponse } from "../types";

interface Props {
    onAnalyzed: (result: RoomAnalyzeResponse) => void;
}

type UploadState = "idle" | "uploading" | "done" | "error";

export function RoomUploader({ onAnalyzed }: Props) {
    const [state, setState] = useState<UploadState>("idle");
    const [error, setError] = useState<string | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [dragging, setDragging] = useState(false);

    const handle = useCallback(
        async (file: File) => {
            setPreview(URL.createObjectURL(file));
            setState("uploading");
            setError(null);
            try {
                const result = await analyzeRoom(file);
                setState("done");
                onAnalyzed(result);
            } catch (e) {
                setState("error");
                setError(e instanceof Error ? e.message : "Upload failed");
            }
        },
        [onAnalyzed]
    );

    const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) handle(file);
    };

    const onDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setDragging(false);
        const file = e.dataTransfer.files?.[0];
        if (file) handle(file);
    };

    return (
        <div style={styles.wrap}>
            <h2 style={styles.heading}>Upload Your Room</h2>
            <p style={styles.sub}>Drag &amp; drop a photo or click to browse</p>

            <label
                style={{
                    ...styles.dropzone,
                    borderColor: dragging ? "#7c6ef0" : "#3a3a4a",
                    background: dragging ? "#1e1e30" : "#16161f",
                }}
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={onDrop}
            >
                {preview ? (
                    <img src={preview} alt="preview" style={styles.preview} />
                ) : (
                    <div style={styles.placeholder}>
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#7c6ef0" strokeWidth="1.5">
                            <path d="M4 16l4-4 4 4 4-6 4 6" />
                            <rect x="2" y="3" width="20" height="18" rx="2" />
                        </svg>
                        <span style={{ color: "#888", marginTop: 8 }}>JPG · PNG · WEBP</span>
                    </div>
                )}
                <input type="file" accept="image/*" style={{ display: "none" }} onChange={onFileChange} />
            </label>

            {state === "uploading" && (
                <div style={styles.status}>
                    <Spinner /> Analysing room…
                </div>
            )}
            {state === "done" && (
                <div style={{ ...styles.status, color: "#4caf7d" }}>✓ Analysis complete</div>
            )}
            {state === "error" && (
                <div style={{ ...styles.status, color: "#e05c5c" }}>✗ {error}</div>
            )}
        </div>
    );
}

function Spinner() {
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
            }}
        />
    );
}

const styles: Record<string, React.CSSProperties> = {
    wrap: { display: "flex", flexDirection: "column", alignItems: "center", gap: 12, padding: 24 },
    heading: { fontSize: 22, fontWeight: 700, color: "#e8e8ec" },
    sub: { color: "#888", fontSize: 14 },
    dropzone: {
        width: "100%",
        maxWidth: 520,
        minHeight: 220,
        border: "2px dashed",
        borderRadius: 12,
        cursor: "pointer",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        transition: "border-color 0.2s, background 0.2s",
        overflow: "hidden",
    },
    placeholder: { display: "flex", flexDirection: "column", alignItems: "center" },
    preview: { width: "100%", height: "100%", objectFit: "cover", maxHeight: 300 },
    status: { display: "flex", alignItems: "center", fontSize: 14, color: "#aaa" },
};
