/**
 * Typed API client for SpaceForge backend.
 * Base URL is injected at build time via VITE_BACKEND_URL (falls back to "" which
 * means same-origin, useful when backend serves the frontend directly).
 */

import type {
    ARSessionResponse,
    DesignGenerateResponse,
    RenderJobResponse,
    RoomAnalyzeResponse,
} from "../types";

const BASE = (import.meta.env.VITE_BACKEND_URL as string | undefined) ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
    const res = await fetch(`${BASE}${path}`, init);
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`API ${res.status}: ${text}`);
    }
    return res.json() as Promise<T>;
}

// ── Rooms ─────────────────────────────────────────────────────────────────────

export async function analyzeRoom(file: File): Promise<RoomAnalyzeResponse> {
    const form = new FormData();
    form.append("file", file);
    return request<RoomAnalyzeResponse>("/api/rooms/analyze", {
        method: "POST",
        body: form,
    });
}

// ── Designs ───────────────────────────────────────────────────────────────────

export async function generateDesign(
    roomId: string,
    style: string,
    preferences: Record<string, unknown> = {}
): Promise<DesignGenerateResponse> {
    return request<DesignGenerateResponse>("/api/designs/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ room_id: roomId, style, preferences }),
    });
}

export async function submitRender(designId: string): Promise<RenderJobResponse> {
    return request<RenderJobResponse>("/api/designs/render", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ design_id: designId }),
    });
}

export async function getRenderStatus(jobId: string): Promise<RenderJobResponse> {
    return request<RenderJobResponse>(`/api/designs/render/${jobId}`);
}

// ── AR ────────────────────────────────────────────────────────────────────────

export async function getARSession(designId: string): Promise<ARSessionResponse> {
    return request<ARSessionResponse>(`/api/ar/session/${designId}`);
}

// ── Agent / SSE ───────────────────────────────────────────────────────────────

export function streamProcure(
    designId: string,
    budgetUsd: number | null,
    onEvent: (event: { event: string; data: unknown }) => void,
    onDone: () => void,
    onError: (err: Error) => void
): AbortController {
    const ctrl = new AbortController();

    (async () => {
        try {
            const res = await fetch(`${BASE}/api/agent/procure`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ design_id: designId, budget_usd: budgetUsd }),
                signal: ctrl.signal,
            });

            if (!res.ok || !res.body) throw new Error(`SSE error: ${res.status}`);

            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });

                const lines = buffer.split("\n");
                buffer = lines.pop() ?? "";

                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        const raw = line.slice(6).trim();
                        if (!raw) continue;
                        try {
                            const parsed = JSON.parse(raw) as { event: string; data: unknown };
                            if (parsed.event === "done") {
                                onDone();
                                return;
                            }
                            onEvent(parsed);
                        } catch {
                            // ignore malformed lines
                        }
                    }
                }
            }
            onDone();
        } catch (e) {
            if (e instanceof Error && e.name !== "AbortError") onError(e);
        }
    })();

    return ctrl;
}
