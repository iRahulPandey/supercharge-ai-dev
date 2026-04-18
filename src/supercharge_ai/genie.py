"""Genie Space deployment helpers — idempotent create/update via REST API.

The Databricks SDK does not expose a `create_space` method; we use the raw
`POST /api/2.0/genie/spaces` (and `…/updatespace`) endpoints via
`WorkspaceClient.api_client.do()`, which handles auth transparently.

Idempotency is by **title match**: list existing spaces, look for one whose
title equals the target title, update it if found, otherwise create new.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, cast
from uuid import uuid4

if TYPE_CHECKING:
    from databricks.sdk import WorkspaceClient


def build_serialized_space(
    tables: list[dict[str, Any]],
    sample_questions: list[str],
    instructions: list[str],
) -> str:
    """Build the `serialized_space` JSON string expected by the Genie API.

    Structure (matches the Databricks working example):
        {
          "version": 1,
          "config": {"sample_questions": [...]?},
          "data_sources": {"tables": [...]},
          "instructions": {"text_instructions": [...]?}
        }

    Constraints learned the hard way:
    1. `data_sources` and `instructions` are **siblings** of `config`, not
       nested inside it. Nesting triggers
       `InvalidParameterValue: Cannot find field: data_sources`.
    2. `instructions.text_instructions` can contain **at most ONE entry**.
       That entry's `content` field is itself an array of strings — all
       user-supplied instructions go inside one entry's `content`. Using
       multiple entries triggers
       `text_instructions must contain at most one item`.

    Args:
        tables: list of {"identifier": "catalog.schema.table",
            "description": "..."} dicts. `description` is optional.
        sample_questions: UI-facing example questions.
        instructions: free-text guidance strings Genie uses when generating SQL.

    Returns:
        JSON-encoded string (the API expects a string, not a nested object).
    """
    data_sources_tables: list[dict[str, Any]] = []
    for t in tables:
        entry: dict[str, Any] = {"identifier": t["identifier"]}
        if t.get("description"):
            entry["description"] = [t["description"]]
        data_sources_tables.append(entry)

    space: dict[str, Any] = {
        "version": 1,
        "config": {},
        "data_sources": {"tables": data_sources_tables},
        "instructions": {},
    }

    if sample_questions:
        # Note: sample_questions don't require sort-by-id; preserve config order.
        space["config"]["sample_questions"] = [
            {"id": uuid4().hex, "question": [q]} for q in sample_questions
        ]

    if instructions:
        # The Genie API limits `text_instructions` to AT MOST ONE entry
        # (`Invalid export proto: instructions.text_instructions must contain
        # at most one item`). But that single entry's `content` field is
        # itself an array of strings — so all user-supplied instruction
        # strings go inside one text_instruction's `content`.
        space["instructions"]["text_instructions"] = [
            {"id": uuid4().hex, "content": list(instructions)}
        ]

    return json.dumps(space)


def resolve_warehouse_id(wc: WorkspaceClient, configured_id: str | None) -> str:
    """Return a usable warehouse id — either the configured one or the best
    running warehouse in the workspace.

    Selection priority for auto-detection: RUNNING > STARTING > STOPPED,
    then smaller size first (cheaper).
    """
    if configured_id:
        return configured_id

    warehouses = list(wc.warehouses.list())
    if not warehouses:
        raise RuntimeError(
            "No SQL warehouses found in the workspace. "
            "Set project_config.yml → <env>.warehouse_id explicitly."
        )

    state_order = {"RUNNING": 0, "STARTING": 1, "STOPPED": 2}
    size_order = {
        "2X-Small": 0,
        "X-Small": 1,
        "Small": 2,
        "Medium": 3,
        "Large": 4,
        "X-Large": 5,
        "2X-Large": 6,
        "3X-Large": 7,
        "4X-Large": 8,
    }

    def sort_key(w: object) -> tuple[int, int]:
        state_attr = getattr(w, "state", None)
        state = getattr(state_attr, "value", str(state_attr))
        size = getattr(w, "cluster_size", "") or ""
        return (state_order.get(state, 99), size_order.get(size, 99))

    warehouses.sort(key=sort_key)
    chosen_id = warehouses[0].id
    if not chosen_id:
        raise RuntimeError("Selected warehouse has no id")
    return chosen_id


def find_space_by_title(wc: WorkspaceClient, title: str) -> str | None:
    """Return the space_id whose title matches, or None.

    Uses `GET /api/2.0/genie/spaces`. Title comparison is exact.
    """
    # api_client.do returns dict | list | BinaryIO; Genie GET returns a dict.
    resp = cast(dict[str, Any], wc.api_client.do("GET", "/api/2.0/genie/spaces") or {})
    spaces: list[dict[str, Any]] = resp.get("spaces") or []
    for s in spaces:
        if s.get("title") == title:
            return s.get("space_id")
    return None


def upsert_space(
    wc: WorkspaceClient,
    *,
    title: str,
    description: str,
    serialized_space: str,
    warehouse_id: str,
    parent_path: str | None = None,
) -> dict[str, Any]:
    """Create or update a Genie space idempotently by title match.

    Args:
        wc: databricks.sdk.WorkspaceClient instance
        title: Display title; used for idempotency lookup
        description: Space description
        serialized_space: JSON-encoded space config (see build_serialized_space)
        warehouse_id: SQL warehouse backing the space
        parent_path: Optional workspace folder; when None the API defaults to
            the deploying user's home folder

    Returns:
        dict with keys: action ("created" or "updated"), space_id, title.
    """
    existing_id = find_space_by_title(wc, title)

    body: dict[str, Any] = {
        "title": title,
        "description": description,
        "serialized_space": serialized_space,
        "warehouse_id": warehouse_id,
    }
    if parent_path:
        body["parent_path"] = parent_path

    if existing_id:
        wc.api_client.do(
            "POST",
            f"/api/2.0/genie/spaces/{existing_id}/updatespace",
            body=body,
        )
        return {"action": "updated", "space_id": existing_id, "title": title}

    # api_client.do returns dict | list | BinaryIO; the create response is a dict.
    resp = cast(
        dict[str, Any],
        wc.api_client.do("POST", "/api/2.0/genie/spaces", body=body) or {},
    )
    return {
        "action": "created",
        "space_id": resp.get("space_id"),
        "title": title,
    }


def space_url(host: str, space_id: str) -> str:
    """Build the browser URL for a Genie space given its id."""
    host = host.rstrip("/")
    return f"{host}/genie/rooms/{space_id}"
