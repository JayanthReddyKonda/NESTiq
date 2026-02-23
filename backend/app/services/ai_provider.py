"""
AI Provider abstraction layer.

Swap FakeProvider → a real provider by changing the AI_PROVIDER env var.
All real integrations are marked with # TODO: PRODUCTION
"""

from __future__ import annotations

import asyncio
import base64
import io
import logging
import random
import uuid
from abc import ABC, abstractmethod

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ── Abstract Base ─────────────────────────────────────────────────────────────

class BaseAIProvider(ABC):
    """Contract every AI provider must satisfy."""

    @abstractmethod
    async def analyze_room(self, image_bytes: bytes, filename: str) -> dict:
        """Return structured room analysis dict."""
        ...

    @abstractmethod
    async def generate_design(self, analysis: dict, style: str, preferences: dict) -> dict:
        """Return furniture layout + design dict."""
        ...

    @abstractmethod
    async def render_design(self, design: dict) -> bytes:
        """Return raw PNG bytes of the rendered design."""
        ...

    @abstractmethod
    async def procure(self, design: dict, budget: float | None, vendors: list[str]):
        """Async generator yielding procurement SSE events."""
        ...


# ── Fake Provider (default / demo) ────────────────────────────────────────────

class FakeProvider(BaseAIProvider):
    """
    Deterministic fake provider for local development and demos.
    Simulates realistic latency without any API keys.
    """

    _ROOM_TYPES = ["living_room", "bedroom", "dining_room", "home_office", "kitchen"]
    _LIGHTING = ["natural", "artificial", "mixed"]
    _FEATURES = ["window", "door", "hardwood_floor", "carpet", "fireplace", "closet", "built-in shelves"]
    _STYLES = ["modern", "scandinavian", "industrial", "bohemian", "minimalist", "traditional"]

    async def analyze_room(self, image_bytes: bytes, filename: str) -> dict:
        await asyncio.sleep(1.2)  # simulate model inference
        rng = random.Random(len(image_bytes))
        return {
            "room_type": rng.choice(self._ROOM_TYPES),
            "dimensions": {
                "width": round(rng.uniform(3.0, 6.0), 1),
                "height": round(rng.uniform(2.4, 3.5), 1),
                "depth": round(rng.uniform(4.0, 8.0), 1),
            },
            "lighting": rng.choice(self._LIGHTING),
            "existing_features": rng.sample(self._FEATURES, k=rng.randint(2, 4)),
            "style_hints": rng.sample(self._STYLES, k=2),
            "confidence": round(rng.uniform(0.82, 0.99), 2),
        }

    async def generate_design(self, analysis: dict, style: str, preferences: dict) -> dict:
        await asyncio.sleep(1.5)
        colors = {
            "modern": ["#FFFFFF", "#2C3E50", "#BDC3C7", "#E74C3C"],
            "scandinavian": ["#F5F5F0", "#8B7355", "#D4C5A9", "#4A4A4A"],
            "industrial": ["#3D3D3D", "#B87333", "#8B8680", "#F5F5DC"],
            "bohemian": ["#C19A6B", "#8B4513", "#DEB887", "#6B8E23"],
            "minimalist": ["#FAFAFA", "#E0E0E0", "#9E9E9E", "#212121"],
            "traditional": ["#8B4513", "#D2691E", "#F4A460", "#FFFAF0"],
        }.get(style, ["#FFFFFF", "#000000", "#888888", "#CCCCCC"])

        w = analysis["dimensions"]["width"]
        d = analysis["dimensions"]["depth"]

        furniture = [
            {
                "id": str(uuid.uuid4()),
                "name": "Sofa",
                "category": "seating",
                "style": style,
                "color": colors[0],
                "position": {"x": 0.0, "y": 0.0, "z": 1.0},
                "rotation": 0.0,
                "dimensions": {"w": 2.2, "h": 0.85, "d": 0.95},
                "model_url": None,
                "price_usd": 899.00,
                "vendor": "FurnitureCo",
                "sku": f"SF-{style[:3].upper()}-001",
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Coffee Table",
                "category": "table",
                "style": style,
                "color": colors[1],
                "position": {"x": 0.0, "y": 0.0, "z": 2.5},
                "rotation": 0.0,
                "dimensions": {"w": 1.2, "h": 0.45, "d": 0.6},
                "model_url": None,
                "price_usd": 299.00,
                "vendor": "FurnitureCo",
                "sku": f"CT-{style[:3].upper()}-002",
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Floor Lamp",
                "category": "lighting",
                "style": style,
                "color": colors[2],
                "position": {"x": w / 2 - 0.5, "y": 0.0, "z": 0.8},
                "rotation": 0.0,
                "dimensions": {"w": 0.35, "h": 1.8, "d": 0.35},
                "model_url": None,
                "price_usd": 149.00,
                "vendor": "LightHouse",
                "sku": f"FL-{style[:3].upper()}-003",
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Bookshelf",
                "category": "storage",
                "style": style,
                "color": colors[3],
                "position": {"x": -(w / 2 - 0.2), "y": 0.0, "z": d / 2 - 0.2},
                "rotation": 90.0,
                "dimensions": {"w": 1.0, "h": 2.0, "d": 0.3},
                "model_url": None,
                "price_usd": 399.00,
                "vendor": "WoodWorks",
                "sku": f"BS-{style[:3].upper()}-004",
            },
        ]

        total = sum(f["price_usd"] for f in furniture)

        return {
            "style": style,
            "furniture": furniture,
            "layout_notes": (
                f"Furniture arranged for a {analysis['room_type'].replace('_', ' ')} "
                f"({analysis['dimensions']['width']}m × {analysis['dimensions']['depth']}m). "
                f"Sofa faces the focal wall with coffee table centred. "
                f"Floor lamp provides ambient lighting near seating area."
            ),
            "color_palette": colors,
            "estimated_cost_usd": round(total, 2),
        }

    async def render_design(self, design: dict) -> bytes:
        """
        Simulate SDXL rendering.
        Returns a procedurally generated PNG placeholder.
        # TODO: PRODUCTION — replace with Replicate / Modal SDXL call
        """
        await asyncio.sleep(3.0)  # simulate GPU render time

        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            # Pillow not available — return a minimal 1×1 PNG
            # 1×1 white PNG (89 bytes, hardcoded)
            return base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8"
                "z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg=="
            )

        style = design.get("style", "modern")
        palette = design.get("color_palette", ["#FFFFFF", "#000000"])

        img = Image.new("RGB", (1024, 768), color=palette[0] if palette else "#F0F0F0")
        draw = ImageDraw.Draw(img)

        # Draw furniture silhouettes
        for i, piece in enumerate(design.get("furniture", [])[:6]):
            hue = palette[i % len(palette)] if palette else "#888888"
            x0 = 100 + i * 140
            y0 = 300
            x1 = x0 + 120
            y1 = y0 + 80
            try:
                draw.rectangle([x0, y0, x1, y1], fill=hue, outline="#333333", width=2)
                draw.text((x0 + 5, y0 + 30), piece["name"][:10], fill="#333333")
            except Exception:
                pass

        draw.text((20, 20), f"SpaceForge · {style.capitalize()} Design", fill="#333333")
        draw.text((20, 50), "Rendered by FakeProvider  ·  # TODO: PRODUCTION (SDXL)", fill="#999999")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    async def procure(self, design: dict, budget: float | None, vendors: list[str]):
        """
        Simulate an agentic procurement loop.
        Yields SSE-compatible dicts.
        # TODO: PRODUCTION — replace with LangGraph / AutoGen agent
        """
        furniture = design.get("furniture", [])
        currency = "USD"

        yield {"event": "thought", "data": f"Analysing {len(furniture)} furniture pieces against budget ${budget or '∞'} {currency}"}
        await asyncio.sleep(0.4)

        for piece in furniture:
            yield {"event": "action", "data": f"Searching '{piece['name']}' at {piece.get('vendor', 'any vendor')}"}
            await asyncio.sleep(0.3)
            yield {
                "event": "result",
                "data": {
                    "furniture_id": piece["id"],
                    "name": piece["name"],
                    "sku": piece.get("sku"),
                    "price_usd": piece.get("price_usd"),
                    "in_stock": True,
                    "buy_url": f"https://example.com/buy/{piece.get('sku', 'unknown')}",
                },
            }
            await asyncio.sleep(0.2)

        total = sum(p.get("price_usd", 0) for p in furniture)
        within_budget = budget is None or total <= budget
        yield {
            "event": "summary",
            "data": {
                "total_usd": round(total, 2),
                "within_budget": within_budget,
                "items": len(furniture),
            },
        }


# ── Grok (xAI) Provider ──────────────────────────────────────────────────────
# Uses the standard openai SDK pointed at https://api.x.ai/v1
# Model: grok-3 (vision + text + streaming)

class GrokProvider(BaseAIProvider):
    def __init__(self) -> None:
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise RuntimeError(
                "openai package is required for GrokProvider. "
                "Add 'openai>=1.30.0' to requirements.txt"
            ) from exc

        self._client = AsyncOpenAI(
            api_key=settings.grok_api_key.get_secret_value(),
            base_url=settings.grok_base_url,   # https://api.x.ai/v1
        )
        self._model = settings.grok_model       # grok-3

    # ── Analyze ──────────────────────────────────────────────────────────────

    async def analyze_room(self, image_bytes: bytes, filename: str) -> dict:
        """
        Send the room image to Grok vision and return structured analysis.
        grok-3 accepts base64-encoded images inline.
        """
        import base64, json as _json

        b64 = base64.b64encode(image_bytes).decode()
        mime = "image/jpeg"
        if filename.lower().endswith(".png"):
            mime = "image/png"
        elif filename.lower().endswith(".webp"):
            mime = "image/webp"

        prompt = (
            "You are an expert interior designer AI. Analyze this room photograph "
            "and return ONLY a valid JSON object — no markdown, no explanation — "
            "with this exact schema:\n"
            "{\n"
            '  "room_type": string,\n'
            '  "dimensions": {"width": number, "height": number, "depth": number},\n'
            '  "lighting": string,\n'
            '  "existing_features": [string],\n'
            '  "style_hints": [string],\n'
            '  "confidence": number (0.0–1.0)\n'
            "}\n"
            "All measurements in metres. Return raw JSON only."
        )

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{b64}"},
                        },
                    ],
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=1024,
            temperature=0.2,
        )

        raw = response.choices[0].message.content
        logger.debug("Grok analyze_room response: %s", raw)
        return _json.loads(raw)

    # ── Design generation ─────────────────────────────────────────────────────

    async def generate_design(self, analysis: dict, style: str, preferences: dict) -> dict:
        """
        Ask Grok to generate a full furniture layout for the analysed room.
        """
        import json as _json

        prompt = (
            f"You are an expert interior designer AI.\n"
            f"Room analysis: {_json.dumps(analysis)}\n"
            f"Style requested: {style}\n"
            f"User preferences: {_json.dumps(preferences)}\n\n"
            "Return ONLY a valid JSON object with this exact schema:\n"
            "{\n"
            '  "style": string,\n'
            '  "furniture": [\n'
            "    {\n"
            '      "id": string (uuid),\n'
            '      "name": string,\n'
            '      "category": string,\n'
            '      "style": string,\n'
            '      "color": string (hex),\n'
            '      "position": {"x": number, "y": number, "z": number},\n'
            '      "rotation": number,\n'
            '      "dimensions": {"w": number, "h": number, "d": number},\n'
            '      "model_url": null,\n'
            '      "price_usd": number,\n'
            '      "vendor": string,\n'
            '      "sku": string\n'
            "    }\n"
            "  ],\n"
            '  "layout_notes": string,\n'
            '  "color_palette": [string (hex)],\n'
            '  "estimated_cost_usd": number\n'
            "}\n"
            "Return 4–6 furniture items. All dimensions in metres. Return raw JSON only."
        )

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=2048,
            temperature=0.4,
        )

        raw = response.choices[0].message.content
        logger.debug("Grok generate_design response: %s", raw)
        return _json.loads(raw)

    # ── Render ────────────────────────────────────────────────────────────────

    async def render_design(self, design: dict) -> bytes:
        """
        Grok is text/vision only — rendering still uses the FakeProvider placeholder.
        TODO: PRODUCTION — wire Replicate SDXL or Modal GPU for real renders.
        """
        logger.info("GrokProvider: render_design delegating to FakeProvider (no image gen)")
        return await FakeProvider().render_design(design)

    # ── Procurement stream ────────────────────────────────────────────────────

    async def procure(self, design: dict, budget: float | None, vendors: list[str]):
        """
        Stream Grok's procurement analysis as SSE events.
        Uses streaming chat completion — each chunk becomes a thought/result event.
        """
        import json as _json

        furniture = design.get("furniture", [])
        budget_str = f"${budget}" if budget else "no fixed budget"

        prompt = (
            f"You are an expert procurement specialist AI.\n"
            f"Interior design has {len(furniture)} furniture items:\n"
            f"{_json.dumps(furniture, indent=2)}\n\n"
            f"Budget: {budget_str}\n"
            f"Preferred vendors: {vendors or ['any']}\n\n"
            "For each item:\n"
            "1. Search for the best real purchase source\n"
            "2. Suggest alternatives if over budget\n"
            "3. Provide a realistic price estimate\n\n"
            "Stream your reasoning naturally — think out loud, then give results."
        )

        # Opening thought event
        yield {"event": "thought", "data": f"Analysing {len(furniture)} items with budget {budget_str}"}

        # Stream Grok's response
        stream = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            max_tokens=2048,
            temperature=0.5,
        )

        buffer = ""
        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                buffer += delta
                # Emit streamed text as thought events
                yield {"event": "thought", "data": delta}

        # Final summary — compute totals from design data
        total = sum(p.get("price_usd", 0) for p in furniture)
        within_budget = budget is None or total <= budget
        yield {
            "event": "summary",
            "data": {
                "total_usd": round(total, 2),
                "within_budget": within_budget,
                "items": len(furniture),
                "grok_analysis": buffer[-500:] if buffer else "",  # last 500 chars
            },
        }


# ── Factory ───────────────────────────────────────────────────────────────────

_PROVIDERS: dict[str, type[BaseAIProvider]] = {
    "fake": FakeProvider,
    "grok": GrokProvider,
}


def get_ai_provider() -> BaseAIProvider:
    """FastAPI dependency — returns the configured AI provider singleton."""
    provider_cls = _PROVIDERS.get(settings.ai_provider, FakeProvider)
    logger.info("AI provider: %s", settings.ai_provider)
    return provider_cls()
