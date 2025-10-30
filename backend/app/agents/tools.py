from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx
from langchain_core.tools import tool

from .config import get_backend_api_base_url


def _serialize(data: Any) -> str:
    """Return a deterministic JSON string for the LLM to consume."""
    return json.dumps(data, ensure_ascii=True, separators=(",", ":"), default=str)


async def _request_json(method: str, url: str, **kwargs: Any) -> Dict[str, Any]:
    """Helper to call the backend REST API and normalise errors for the LLM."""
    base_url = get_backend_api_base_url()
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        response = await client.request(method, url, **kwargs)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        return {
            "error": "http_error",
            "status_code": exc.response.status_code,
            "detail": exc.response.text[:4000],
        }
    try:
        return response.json()
    except ValueError:
        return {
            "error": "invalid_json",
            "status_code": response.status_code,
            "detail": response.text[:4000],
        }


@tool("list_products")
async def list_products_tool(query: Optional[str] = None) -> str:
    """Search the product catalog by name or SKU. Returns up to 25 matching products with inventory per variant."""
    params = {"q": query} if query else None
    data = await _request_json("GET", "/products", params=params)
    return _serialize(data)


@tool("get_product_by_sku")
async def get_product_by_sku_tool(sku: str) -> str:
    """Retrieve a single product by SKU including price_cents and inventory information."""
    safe_sku = quote(sku, safe="")
    data = await _request_json("GET", f"/products/{safe_sku}")
    return _serialize(data)


@tool("get_store_info")
async def get_store_info_tool() -> str:
    """Fetch store profile details such as address, opening hours, phone number, and supported couriers."""
    data = await _request_json("GET", "/store/info")
    return _serialize(data)


@tool("estimate_shipping")
async def estimate_shipping_tool(dest_city_id: int, weight_grams: int = 1000, courier: str = "jne") -> str:
    """Call RajaOngkir to estimate shipping cost. Needs destination city ID, optional weight (grams) and courier code."""
    params = {
        "dest_city_id": dest_city_id,
        "weight_grams": weight_grams,
        "courier": courier,
    }
    data = await _request_json("GET", "/shipping/estimate", params=params)
    return _serialize(data)


@tool("list_shipping_destinations")
async def list_shipping_destinations_tool(query: Optional[str] = None) -> str:
    """Search available shipping destination cities (RajaOngkir). Use to fetch city IDs before estimating cost."""
    params = {"q": query} if query else None
    data = await _request_json("GET", "/shipping/destinations", params=params)
    return _serialize(data)


def get_agent_tools() -> List:
    """Return the default toolset used by the CS agent."""
    return [
        list_products_tool,
        get_product_by_sku_tool,
        get_store_info_tool,
        estimate_shipping_tool,
        list_shipping_destinations_tool,
    ]


__all__ = [
    "list_products_tool",
    "get_product_by_sku_tool",
    "get_store_info_tool",
    "estimate_shipping_tool",
    "list_shipping_destinations_tool",
    "get_agent_tools",
]
