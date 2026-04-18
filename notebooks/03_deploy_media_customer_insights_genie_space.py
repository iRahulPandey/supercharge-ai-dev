# Databricks notebook source
# MAGIC %md
# MAGIC # Deploy Media Customer Insights Genie Space
# MAGIC
# MAGIC Idempotently creates or updates a Databricks Genie Space backed by the
# MAGIC enriched insights table (`bakehouse.media_customer_review_insights`),
# MAGIC using config in `project_config.yml → genie_spaces.<space>`.
# MAGIC
# MAGIC **Per-env title suffixing:** the space title has `" (<env>)"` appended
# MAGIC (`"… (dev)"`, `"… (stg)"`, `"… (prod)"`, `"… (local)"`) so spaces from
# MAGIC different envs coexist in the same workspace.
# MAGIC
# MAGIC **Idempotency:** the deploy lists existing spaces, looks up by the
# MAGIC suffixed title, and updates in place if one is found — otherwise creates
# MAGIC new. Re-running is safe.
# MAGIC
# MAGIC **Parameters (widgets):**
# MAGIC - `env` — one of `local`, `dev`, `stg`, `prod`
# MAGIC - `space` — key under `genie_spaces:` in `project_config.yml`
# MAGIC - `config_path` — absolute workspace path to `project_config.yml`
# MAGIC - `parent_path` — workspace folder to create the space under

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from loguru import logger

from supercharge_ai.config import load_config, load_genie_space
from supercharge_ai.genie import (
    build_serialized_space,
    resolve_warehouse_id,
    space_url,
    upsert_space,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Read parameters

# COMMAND ----------

dbutils.widgets.text("env", "local", "Environment")
dbutils.widgets.text("space", "media_customer_insights", "Genie space key")
dbutils.widgets.text("config_path", "project_config.yml", "Path to project_config.yml")
dbutils.widgets.text("parent_path", "", "Workspace folder for the Genie space")

env = dbutils.widgets.get("env")
space_key = dbutils.widgets.get("space")
config_path = dbutils.widgets.get("config_path")
parent_path = dbutils.widgets.get("parent_path") or None

logger.info(
    f"env={env} space={space_key} config_path={config_path} parent_path={parent_path}"
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load config

# COMMAND ----------

project = load_config(config_path=config_path, env=env)
space_cfg = load_genie_space(space=space_key, config_path=config_path)

# Per-env title suffix so dev/stg/prod/local spaces don't collide in the
# same workspace. Source of truth for idempotent lookup.
env_title = f"{space_cfg.title} ({env})"

logger.info(f"Deploying Genie space: '{env_title}'")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Resolve table identifiers + warehouse

# COMMAND ----------

tables = [
    {
        "identifier": t.identifier(default_catalog=project.catalog),
        "description": t.description,
    }
    for t in space_cfg.tables
]
for t in tables:
    logger.info(f"Table: {t['identifier']}  — {t.get('description') or '(no desc)'}")

w = WorkspaceClient()
warehouse_id = resolve_warehouse_id(w, project.warehouse_id or None)
logger.info(f"Using warehouse_id={warehouse_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Build and upsert the space

# COMMAND ----------

serialized_space = build_serialized_space(
    tables=tables,
    sample_questions=space_cfg.sample_questions,
    instructions=space_cfg.instructions,
)

result = upsert_space(
    w,
    title=env_title,
    description=space_cfg.description,
    serialized_space=serialized_space,
    warehouse_id=warehouse_id,
    parent_path=parent_path,
)

logger.info(f"{result['action']} space_id={result['space_id']} title={result['title']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Report

# COMMAND ----------

host = w.config.host or ""
url = space_url(host, result["space_id"]) if result["space_id"] else ""
if url:
    logger.info(f"Genie space URL: {url}")

dbutils.notebook.exit(f"{result['action']}:{result['space_id']}:{result['title']}")
