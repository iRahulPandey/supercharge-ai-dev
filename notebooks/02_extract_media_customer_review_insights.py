# Databricks notebook source
# MAGIC %md
# MAGIC # Extract media_customer_review_insights
# MAGIC
# MAGIC Reads `media_customer_reviews` and enriches each row with three insight
# MAGIC columns derived from the review text using Databricks **task-specific AI
# MAGIC functions** (no endpoint setup, no API keys):
# MAGIC
# MAGIC | Column | Function | Values |
# MAGIC |---|---|---|
# MAGIC | `sentiment` | `ai_analyze_sentiment` | `positive` / `negative` / `neutral` / `mixed` |
# MAGIC | `nps_category` | `ai_classify` | `promoter` / `passive` / `detractor` |
# MAGIC | `topics` | `ai_extract` | STRUCT<taste, quality, service, price, ambience, variety> |
# MAGIC
# MAGIC **NPS caveat:** true NPS requires a 0–10 rating, which the source text does
# MAGIC not have. `ai_classify` maps the review tone to the three NPS buckets so an
# MAGIC aggregate NPS (`%promoters − %detractors`) can be computed downstream.
# MAGIC
# MAGIC **Parameters (widgets):**
# MAGIC - `env` — one of `local`, `dev`, `stg`, `prod`
# MAGIC - `dataset` — key under `datasets:` in `project_config.yml` (default: `media_customer_review_insights`)
# MAGIC - `config_path` — absolute workspace path to `project_config.yml`

# COMMAND ----------

from loguru import logger

from supercharge_ai.config import load_config, load_dataset

# COMMAND ----------

# MAGIC %md
# MAGIC ## Read parameters

# COMMAND ----------

dbutils.widgets.text("env", "local", "Environment")
dbutils.widgets.text("dataset", "media_customer_review_insights", "Dataset key")
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

# Input catalog inherits from env — the ingestion job writes
# media_customer_reviews to {env.catalog}.bakehouse.media_customer_reviews.
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
# MAGIC ## Extract insights with AI functions
# MAGIC
# MAGIC Full-refresh CTAS — idempotent, safe to re-run. For incremental enrichment,
# MAGIC switch to a MERGE pattern keyed on `new_id` and only process rows where
# MAGIC `processed_at` is null or older than the source's latest `review_date`.

# COMMAND ----------

NPS_LABELS = ["promoter", "passive", "detractor"]
TOPIC_LABELS = ["taste", "quality", "service", "price", "ambience", "variety"]

nps_array_sql = "ARRAY(" + ", ".join(f"'{label}'" for label in NPS_LABELS) + ")"
topic_array_sql = "ARRAY(" + ", ".join(f"'{label}'" for label in TOPIC_LABELS) + ")"

spark.sql(f"""
    CREATE OR REPLACE TABLE {output_fqn} AS
    SELECT
        new_id,
        franchiseID                                              AS franchise_id,
        review_date,
        review,
        ai_analyze_sentiment(review)                             AS sentiment,
        ai_classify(review, {nps_array_sql})                     AS nps_category,
        ai_extract(review, {topic_array_sql})                    AS topics,
        current_timestamp()                                      AS processed_at
    FROM {input_fqn}
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify row count and sample

# COMMAND ----------

row_count = spark.table(output_fqn).count()
logger.info(f"Enriched {row_count:,} rows into {output_fqn}")

# Sample a few rows so the job log shows a quick sanity check of the AI outputs
spark.sql(f"""
    SELECT new_id, sentiment, nps_category, topics
    FROM {output_fqn}
    LIMIT 5
""").show(truncate=False)

dbutils.notebook.exit(f"{output_fqn}:{row_count}")
