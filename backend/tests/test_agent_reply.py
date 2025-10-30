import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.routers import agent as agent_module

pytestmark = pytest.mark.asyncio


class DummyConn:
    def __init__(
        self,
        store_row: Optional[Dict[str, Any]],
        catalog_rows: Iterable[Dict[str, Any]],
        execute_log: List[Tuple[str, Tuple[Any, ...]]],
    ) -> None:
        self._store_row = store_row
        self._catalog_rows = list(catalog_rows)
        self._execute_log = execute_log

    async def fetchrow(self, *args, **kwargs):
        return self._store_row

    async def fetch(self, *args, **kwargs):
        return list(self._catalog_rows)

    async def execute(self, sql: str, *params: Any):
        self._execute_log.append((sql, params))
        return "OK"


class DummyAcquire:
    def __init__(self, conn: DummyConn) -> None:
        self._conn = conn

    async def __aenter__(self) -> DummyConn:
        return self._conn

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


class DummyPool:
    def __init__(self, conn: DummyConn) -> None:
        self._conn = conn

    def acquire(self) -> DummyAcquire:
        return DummyAcquire(self._conn)


class FakeMemoryStore:
    def __init__(self, preset_turns: Optional[List[Dict[str, str]]] = None) -> None:
        self.preset_turns = preset_turns or []
        self.user_messages: List[Tuple[str, str]] = []
        self.ai_messages: List[Tuple[str, str]] = []

    def get_turns(self, session_id: str) -> List[Dict[str, str]]:
        return list(self.preset_turns)

    def append_user_message(self, session_id: str, content: str) -> None:
        self.user_messages.append((session_id, content))

    def append_ai_message(self, session_id: str, content: str) -> None:
        self.ai_messages.append((session_id, content))


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


def patch_agent_dependencies(
    monkeypatch: pytest.MonkeyPatch,
    *,
    store_row: Optional[Dict[str, Any]],
    catalog_rows: Iterable[Dict[str, Any]],
    run_agent_result: Optional[Dict[str, Any]] = None,
    memory_store: Optional[FakeMemoryStore] = None,
):
    execute_log: List[Tuple[str, Tuple[Any, ...]]] = []
    conn = DummyConn(store_row, catalog_rows, execute_log)
    pool = DummyPool(conn)

    async def fake_get_pool():
        return pool

    monkeypatch.setattr(agent_module, "get_session", fake_get_pool)

    memory = memory_store or FakeMemoryStore()
    monkeypatch.setattr(agent_module, "default_memory_store", memory)

    captured: Dict[str, Any] = {}

    async def fake_run_agent(message: str, **kwargs):
        captured["message"] = message
        captured["kwargs"] = kwargs
        return run_agent_result or {"reply": "Siap bantu! 😊", "intermediate_steps": ["noop"]}

    monkeypatch.setattr(agent_module, "run_agent", fake_run_agent)

    return execute_log, memory, captured


async def test_agent_reply_success(monkeypatch, client):
    store_row = {
        "name": "Toko Andalan",
        "address": "Jl. Merdeka No.1",
        "open_hours": "08:00-20:00",
    }
    catalog_rows = [
        {"sku": "SKU1", "name": "Kaos Oversize", "price_cents": 1750000, "description": "Bahan katun premium"},
        {"sku": "SKU2", "name": "Hoodie Hangat", "price_cents": 2150000, "description": "Nyaman dipakai malam hari"},
    ]
    run_agent_result = {"reply": "Halo! Berikut info produk kami.", "intermediate_steps": ["tool_call"]}

    execute_log, memory, captured = patch_agent_dependencies(
        monkeypatch,
        store_row=store_row,
        catalog_rows=catalog_rows,
        run_agent_result=run_agent_result,
    )

    response = await client.post("/agent/reply", json={"from": "62812", "text": "Halo, ada promo?"})
    assert response.status_code == 200
    payload = response.json()

    assert payload["reply"] == run_agent_result["reply"]
    assert payload["meta"]["intermediate_steps"] == ["tool_call"]

    assert captured["message"] == "Halo, ada promo?"
    kwargs = captured["kwargs"]
    assert kwargs["session_id"] == "62812"
    assert "Name: Toko Andalan" in kwargs["store_profile"]
    assert "Kaos Oversize (SKU: SKU1)" in kwargs["catalog_context"]
    assert "Rp17,500" in kwargs["catalog_context"]

    assert memory.user_messages == [("62812", "Halo, ada promo?")]
    assert memory.ai_messages == [("62812", run_agent_result["reply"])]

    assert len(execute_log) == 1
    sql, params = execute_log[0]
    assert "insert into chat_logs" in sql.lower()
    assert params[0] == "62812"
    assert params[1] == run_agent_result["reply"]
    assert params[2]["intermediate_steps"] == ["tool_call"]


async def test_agent_reply_missing_sender_returns_422(client):
    response = await client.post("/agent/reply", json={"text": "Halo"})
    assert response.status_code == 422


async def test_agent_reply_missing_text_returns_422(client):
    response = await client.post("/agent/reply", json={"from": "62812", "text": "   "})
    assert response.status_code == 422


async def test_agent_reply_uses_fallback_when_agent_empty(monkeypatch, client):
    store_row = {"name": "Toko Aja", "open_hours": "10:00-18:00"}
    catalog_rows = []
    run_agent_result = {"reply": "", "intermediate_steps": []}
    execute_log, memory, captured = patch_agent_dependencies(
        monkeypatch,
        store_row=store_row,
        catalog_rows=catalog_rows,
        run_agent_result=run_agent_result,
    )

    response = await client.post("/agent/reply", json={"from": "62X", "text": "Ada stok?"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["reply"].startswith("Maaf, saya belum bisa menjawab")

    # Memory still records the conversation with the fallback response.
    assert memory.user_messages == [("62X", "Ada stok?")]
    assert memory.ai_messages == [("62X", payload["reply"])]

    # Ensure log written with the fallback response.
    sql, params = execute_log[0]
    assert params[1] == payload["reply"]

    # run_agent still received context data.
    assert captured["kwargs"]["store_profile"].startswith("Name: Toko Aja")


async def test_agent_reply_passes_empty_context_when_no_data(monkeypatch, client):
    execute_log, memory, captured = patch_agent_dependencies(
        monkeypatch,
        store_row=None,
        catalog_rows=[],
        run_agent_result={"reply": "Siap bantu!", "intermediate_steps": []},
    )

    response = await client.post("/agent/reply", json={"from": "62Z", "text": "Cek harga"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["reply"] == "Siap bantu!"

    kwargs = captured["kwargs"]
    assert kwargs["store_profile"] == ""
    assert kwargs["catalog_context"] == ""

    assert memory.user_messages == [("62Z", "Cek harga")]
    assert memory.ai_messages == [("62Z", "Siap bantu!")]


async def test_agent_reply_truncates_long_descriptions(monkeypatch, client):
    long_description = "A" * 150
    execute_log, memory, captured = patch_agent_dependencies(
        monkeypatch,
        store_row={"name": "Toko B"},
        catalog_rows=[{"sku": "LONG1", "name": "Produk Panjang", "price_cents": 99900, "description": long_description}],
        run_agent_result={"reply": "Hai!", "intermediate_steps": []},
    )

    response = await client.post("/agent/reply", json={"from": "62999", "text": "Info detail"})
    assert response.status_code == 200

    snippet = captured["kwargs"]["catalog_context"]
    assert len(snippet.split("— ", 1)[1]) == 120
    assert "A" * 125 not in snippet


async def test_agent_reply_reuses_existing_history(monkeypatch, client):
    preset_history = [
        {"role": "user", "content": "Sebelumnya nanya ongkir"},
        {"role": "assistant", "content": "Ongkir ke Bandung Rp20.000"},
    ]
    memory = FakeMemoryStore(preset_history)
    execute_log, memory_store, captured = patch_agent_dependencies(
        monkeypatch,
        store_row={"name": "Toko C"},
        catalog_rows=[],
        run_agent_result={"reply": "Oke, dicatat ya.", "intermediate_steps": []},
        memory_store=memory,
    )

    response = await client.post("/agent/reply", json={"from": "62001", "text": "Pesan 2 pcs"})
    assert response.status_code == 200

    # The stored history should now include the new turn.
    assert memory.user_messages[-1] == ("62001", "Pesan 2 pcs")
    assert memory.ai_messages[-1] == ("62001", "Oke, dicatat ya.")

    # Ensure run_agent received the prior conversation turns via session_id.
    assert captured["kwargs"]["session_id"] == "62001"
