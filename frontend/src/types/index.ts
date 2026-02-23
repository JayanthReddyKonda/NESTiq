// ── Domain types (mirror backend Pydantic schemas) ────────────────────────────

export interface RoomDimensions {
    width: number;
    height: number;
    depth: number;
}

export interface RoomAnalysis {
    room_type: string;
    dimensions: RoomDimensions;
    lighting: string;
    existing_features: string[];
    style_hints: string[];
    confidence: number;
}

export interface RoomAnalyzeResponse {
    room_id: string;
    filename: string;
    file_url: string | null;
    analysis: RoomAnalysis;
    created_at: string;
}

export interface FurniturePiece {
    id: string;
    name: string;
    category: string;
    style: string;
    color: string;
    position: { x: number; y: number; z: number };
    rotation: number;
    dimensions: { w: number; h: number; d: number };
    model_url: string | null;
    price_usd: number | null;
    vendor: string | null;
    sku: string | null;
}

export interface DesignGenerateResponse {
    design_id: string;
    room_id: string;
    style: string;
    furniture: FurniturePiece[];
    layout_notes: string;
    color_palette: string[];
    estimated_cost_usd: number;
    created_at: string;
}

export interface RenderJobResponse {
    job_id: string;
    design_id: string;
    status: "pending" | "processing" | "done" | "failed";
    image_url: string | null;
    error: string | null;
    created_at: string;
}

export interface ARPosition {
    furniture_id: string;
    x: number;
    y: number;
    z: number;
    rotation_y: number;
}

export interface ARSessionResponse {
    design_id: string;
    model_url: string;
    positions: ARPosition[];
    scale_factor: number;
    ar_modes: string;
}

export interface AgentEvent {
    event: "thought" | "action" | "result" | "summary" | "error" | "done";
    data: unknown;
}
