import React, { useState, useRef, useCallback } from "react";
import { streamProcure } from "../api/client";
import type { AgentEvent } from "../types";

interface Props {
    designId: string;
}

export function AgentStream({ designId }: Props) {
    const [events, setEvents] = useState<AgentEvent[]>([]);
    const [running, setRunning] = useState(false);
    const [done, setDone] = useState(false);
    const [budget, setBudget] = useState<string>("");
    const ctrlRef = useRef<AbortController | null>(null);
    const bottomRef = useRef<HTMLDivElement>(null);

    const start = useCallback(() => {
        setEvents([]);
        setDone(false);
        setRunning(true);

        ctrlRef.current = streamProcure(
            designId,
            budget ? parseFloat(budget) : null,
            (ev) => {
                setEvents((prev) => [...prev, ev as AgentEvent]);
                setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
            },
            () => { setRunning(false); setDone(true); },
            (err) => { setRunning(false); setEvents((prev) => [...prev, { event: "error", data: err.message }]); }
        );
    }, [designId, budget]);

    const stop = () => {
        ctrlRef.current?.abort();
        setRunning(false);
    };

    return (
        <div style={styles.wrap}>
            <div style={styles.controls}>
                <input
                    type="number"
                    placeholder="Budget (USD, optional)"
                    value={budget}
                    onChange={(e) => setBudget(e.target.value)}
                    style={styles.input}
                    disabled={running}
                />
                {!running ? (
                    <button onClick={start} style={styles.btnStart}>Run Procurement Agent</button>
                ) : (
                    <button onClick={stop} style={styles.btnStop}>Stop</button>
                )}
            </div>

            <div style={styles.log}>
                {events.length === 0 && !running && (
                    <p style={{ color: "#555", padding: 16 }}>No events yet. Click "Run Procurement Agent" to start.</p>
                )}
                {events.map((ev, i) => (
                    <EventRow key={i} event={ev} />
                ))}
                {done && <p style={{ color: "#4caf7d", padding: "4px 16px" }}>✓ Procurement complete.</p>}
                <div ref={bottomRef} />
            </div>
        </div>
    );
}

function EventRow({ event }: { event: AgentEvent }) {
    const icon = {
        thought: "💭",
        action: "⚡",
        result: "📦",
        summary: "📊",
        error: "❌",
        done: "✅",
    }[event.event] ?? "•";

    const color = {
        thought: "#aaa",
        action: "#7c6ef0",
        result: "#4caf7d",
        summary: "#f0ca7c",
        error: "#e05c5c",
        done: "#4caf7d",
    }[event.event] ?? "#888";

    const dataTxt =
        typeof event.data === "string"
            ? event.data
            : JSON.stringify(event.data, null, 2);

    return (
        <div style={{ ...styles.row, borderLeftColor: color }}>
            <span style={styles.icon}>{icon}</span>
            <span style={{ ...styles.badge, color }}>{event.event}</span>
            <pre style={styles.data}>{dataTxt}</pre>
        </div>
    );
}

const styles: Record<string, React.CSSProperties> = {
    wrap: { display: "flex", flexDirection: "column", gap: 12 },
    controls: { display: "flex", gap: 10, alignItems: "center" },
    input: {
        flex: 1, padding: "8px 12px", borderRadius: 8,
        border: "1px solid #3a3a4a", background: "#111118", color: "#e8e8ec", fontSize: 14,
    },
    btnStart: {
        padding: "8px 18px", borderRadius: 8, border: "none", cursor: "pointer",
        background: "#7c6ef0", color: "#fff", fontWeight: 600, fontSize: 14, whiteSpace: "nowrap",
    },
    btnStop: {
        padding: "8px 18px", borderRadius: 8, border: "none", cursor: "pointer",
        background: "#e05c5c", color: "#fff", fontWeight: 600, fontSize: 14,
    },
    log: { background: "#111118", borderRadius: 10, minHeight: 200, maxHeight: 360, overflowY: "auto", display: "flex", flexDirection: "column" },
    row: {
        display: "flex", alignItems: "flex-start", gap: 8, padding: "8px 14px",
        borderLeft: "3px solid transparent", borderBottom: "1px solid #1a1a24",
    },
    icon: { fontSize: 16, flexShrink: 0 },
    badge: { fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: 0.5, flexShrink: 0, paddingTop: 2 },
    data: { fontSize: 12, color: "#aaa", margin: 0, whiteSpace: "pre-wrap", wordBreak: "break-all", flex: 1 },
};
