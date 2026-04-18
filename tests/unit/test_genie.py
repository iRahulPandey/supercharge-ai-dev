"""Tests for Genie Space deployment helpers."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from supercharge_ai.genie import (
    build_serialized_space,
    find_space_by_title,
    resolve_warehouse_id,
    space_url,
    upsert_space,
)

# --- build_serialized_space -----------------------------------------------


def test_build_serialized_space_structure():
    """Serialized space matches the Genie v1 schema.

    Critical layout:
      - `data_sources` and `instructions` are siblings of `config` (not nested)
      - `text_instructions` has AT MOST ONE entry; all user-supplied instruction
        strings go inside that entry's `content` array
    """
    s = build_serialized_space(
        tables=[
            {
                "identifier": "dev.bakehouse.media_customer_review_insights",
                "description": "Enriched reviews",
            }
        ],
        sample_questions=["Q1?", "Q2?"],
        instructions=["Rule 1", "Rule 2", "Rule 3"],
    )

    parsed = json.loads(s)
    assert parsed["version"] == 1
    assert set(parsed.keys()) == {"version", "config", "data_sources", "instructions"}

    # sample_questions under config, order preserved
    qs = parsed["config"]["sample_questions"]
    assert [q["question"] for q in qs] == [["Q1?"], ["Q2?"]]
    assert all(len(q["id"]) == 32 for q in qs)  # uuid4().hex length

    # data_sources.tables
    tbls = parsed["data_sources"]["tables"]
    assert tbls == [
        {
            "identifier": "dev.bakehouse.media_customer_review_insights",
            "description": ["Enriched reviews"],
        }
    ]

    # text_instructions: exactly ONE entry; all strings live in its `content`
    ti = parsed["instructions"]["text_instructions"]
    assert len(ti) == 1, "API limits text_instructions to at most one entry"
    assert ti[0]["content"] == ["Rule 1", "Rule 2", "Rule 3"]
    assert len(ti[0]["id"]) == 32


def test_build_serialized_space_instructions_single_entry_max():
    """Regression: API rejects >1 `text_instructions` entries.

    Even with many user-supplied instructions, the result must have exactly
    one `text_instructions` entry — all strings inside its `content` array.
    Failing this triggers:
      `instructions.text_instructions must contain at most one item`
    """
    s = build_serialized_space(
        tables=[{"identifier": "c.s.t"}],
        sample_questions=[],
        instructions=[f"I{i}" for i in range(10)],
    )
    parsed = json.loads(s)

    ti = parsed["instructions"]["text_instructions"]
    assert len(ti) == 1
    assert ti[0]["content"] == [f"I{i}" for i in range(10)]


def test_build_serialized_space_omits_empty_optional_sections():
    """Empty sample_questions → config.sample_questions absent.
    Empty instructions → instructions.text_instructions absent.
    """
    s = build_serialized_space(
        tables=[{"identifier": "dev.bakehouse.t"}],
        sample_questions=[],
        instructions=[],
    )
    parsed = json.loads(s)

    assert parsed["config"] == {}
    assert parsed["instructions"] == {}

    tbl = parsed["data_sources"]["tables"][0]
    assert "description" not in tbl
    assert tbl["identifier"] == "dev.bakehouse.t"


# --- find_space_by_title --------------------------------------------------


def test_find_space_by_title_hit():
    """Returns space_id when a matching title is present."""
    wc = MagicMock()
    wc.api_client.do.return_value = {
        "spaces": [
            {"space_id": "sp_a", "title": "Alpha"},
            {"space_id": "sp_b", "title": "Beta (dev)"},
        ]
    }
    assert find_space_by_title(wc, "Beta (dev)") == "sp_b"
    wc.api_client.do.assert_called_once_with("GET", "/api/2.0/genie/spaces")


def test_find_space_by_title_miss():
    """Returns None when no space title matches."""
    wc = MagicMock()
    wc.api_client.do.return_value = {"spaces": [{"space_id": "sp_a", "title": "Alpha"}]}
    assert find_space_by_title(wc, "Gamma") is None


def test_find_space_by_title_empty_response():
    """Handles API responses with no `spaces` field."""
    wc = MagicMock()
    wc.api_client.do.return_value = {}
    assert find_space_by_title(wc, "Whatever") is None


# --- upsert_space ---------------------------------------------------------


def test_upsert_space_creates_when_missing():
    """If no matching title, POSTs to /api/2.0/genie/spaces and returns created."""
    wc = MagicMock()
    wc.api_client.do.side_effect = [
        {"spaces": []},  # list (find_space_by_title)
        {"space_id": "sp_new"},  # create
    ]

    result = upsert_space(
        wc,
        title="Test (dev)",
        description="d",
        serialized_space="{}",
        warehouse_id="wh_1",
        parent_path="/Workspace/foo",
    )

    assert result == {"action": "created", "space_id": "sp_new", "title": "Test (dev)"}

    create_call = wc.api_client.do.call_args_list[1]
    assert create_call.args == ("POST", "/api/2.0/genie/spaces")
    body = create_call.kwargs["body"]
    assert body["title"] == "Test (dev)"
    assert body["warehouse_id"] == "wh_1"
    assert body["parent_path"] == "/Workspace/foo"


def test_upsert_space_updates_when_exists():
    """If a matching title exists, POSTs to the updatespace endpoint instead."""
    wc = MagicMock()
    wc.api_client.do.side_effect = [
        {"spaces": [{"space_id": "sp_existing", "title": "Test (dev)"}]},
        {},  # update response
    ]

    result = upsert_space(
        wc,
        title="Test (dev)",
        description="d",
        serialized_space="{}",
        warehouse_id="wh_1",
    )

    assert result == {
        "action": "updated",
        "space_id": "sp_existing",
        "title": "Test (dev)",
    }

    update_call = wc.api_client.do.call_args_list[1]
    assert update_call.args == (
        "POST",
        "/api/2.0/genie/spaces/sp_existing/updatespace",
    )


def test_upsert_space_skips_parent_path_when_not_given():
    """parent_path is omitted from the body when None."""
    wc = MagicMock()
    wc.api_client.do.side_effect = [{"spaces": []}, {"space_id": "sp_new"}]

    upsert_space(
        wc,
        title="Test",
        description="",
        serialized_space="{}",
        warehouse_id="wh_1",
    )

    body = wc.api_client.do.call_args_list[1].kwargs["body"]
    assert "parent_path" not in body


# --- resolve_warehouse_id -------------------------------------------------


def test_resolve_warehouse_id_returns_configured():
    """Configured warehouse id takes precedence over auto-detection."""
    wc = MagicMock()
    assert resolve_warehouse_id(wc, "wh_pinned") == "wh_pinned"
    wc.warehouses.list.assert_not_called()


def test_resolve_warehouse_id_autodetects_running():
    """When no id configured, picks a RUNNING warehouse over others."""
    running = MagicMock()
    running.id = "wh_run"
    running.state.value = "RUNNING"
    running.cluster_size = "Small"

    stopped = MagicMock()
    stopped.id = "wh_stop"
    stopped.state.value = "STOPPED"
    stopped.cluster_size = "2X-Small"

    wc = MagicMock()
    wc.warehouses.list.return_value = [stopped, running]

    assert resolve_warehouse_id(wc, None) == "wh_run"


def test_resolve_warehouse_id_raises_when_none_exist():
    """Empty warehouse list raises a clear error."""
    wc = MagicMock()
    wc.warehouses.list.return_value = []
    with pytest.raises(RuntimeError, match="No SQL warehouses found"):
        resolve_warehouse_id(wc, None)


# --- space_url ------------------------------------------------------------


def test_space_url_strips_trailing_slash():
    assert (
        space_url("https://x.cloud.databricks.com/", "sp_1")
        == "https://x.cloud.databricks.com/genie/rooms/sp_1"
    )
    assert (
        space_url("https://x.cloud.databricks.com", "sp_1")
        == "https://x.cloud.databricks.com/genie/rooms/sp_1"
    )
