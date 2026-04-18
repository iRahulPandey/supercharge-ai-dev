# Databricks notebook source
# MAGIC %md
# MAGIC # Ingest media_customer_reviews
# MAGIC
# MAGIC Full-refresh ingestion from the `input` table to the `output` table defined in
# MAGIC `project_config.yml` under `datasets.media_customer_reviews`.
# MAGIC
# MAGIC **Config-driven:** both input and output use the same `{catalog, schema, table}`
# MAGIC shape. The output's `catalog` is optional — when omitted it inherits from the
# MAGIC current env's catalog (`dev`/`stg`/`prd`). Reuse this notebook for any other
# MAGIC full-refresh ingestion by adding a new entry under `datasets:` and pointing the
# MAGIC `dataset` parameter at its key.
# MAGIC
# MAGIC **Parameters (widgets):**
# MAGIC - `env` — one of `local`, `dev`, `stg`, `prod` (DAB target name)
# MAGIC - `dataset` — key under `datasets:` in `project_config.yml`
# MAGIC - `config_path` — absolute workspace path to `project_config.yml`

# COMMAND ----------

from loguru import logger

from supercharge_ai.config import load_config, load_dataset

# COMMAND ----------

# MAGIC %md
# MAGIC ## Read parameters

# COMMAND ----------

dbutils.widgets.text("env", "local", "Environment")
dbutils.widgets.text("dataset", "media_customer_reviews", "Dataset key")
dbutils.widgets.text("config_path", "project_config.yml", "Path to project_config.yml")

env = dbutils.widgets.get("env")
dataset_key = dbutils.widgets.get("dataset")
config_path = dbutils.widgets.get("config_path")

logger.info(f"env={env} dataset={dataset_key} config_path={config_path}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Resolve input and output

# COMMAND ----------

project = load_config(config_path=config_path, env=env)
dataset = load_dataset(dataset=dataset_key, config_path=config_path)

# Both sides accept catalog fallback to env.catalog when omitted in config.
# For this dataset input.catalog=samples is set explicitly; for datasets whose
# input lives in the env's catalog (e.g. downstream enrichment jobs), omitting
# input.catalog works too.
input_fqn = dataset.input.fqn(default_catalog=project.catalog)
output_fqn = dataset.output.fqn(default_catalog=project.catalog)

logger.info(f"Input:  {input_fqn}")
logger.info(f"Output: {output_fqn}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Ensure destination schema exists

# COMMAND ----------

output_catalog = dataset.output.catalog or project.catalog
output_schema = f"{output_catalog}.{dataset.output.schema_name}"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {output_schema}")
logger.info(f"Schema ready: {output_schema}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Full-refresh ingest (CREATE OR REPLACE TABLE)
# MAGIC
# MAGIC Idempotent — safe to re-run. For incremental loads, switch to a MERGE pattern.

# COMMAND ----------

spark.sql(f"CREATE OR REPLACE TABLE {output_fqn} AS SELECT * FROM {input_fqn}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify row count

# COMMAND ----------

row_count = spark.table(output_fqn).count()
logger.info(f"Ingested {row_count:,} rows into {output_fqn}")

dbutils.notebook.exit(f"{output_fqn}:{row_count}")
