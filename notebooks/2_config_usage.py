# Databricks notebook source
"""
Configuration Usage Example

This notebook demonstrates:
- Loading project configuration
- Accessing environment-specific settings
- Using the configuration in Databricks context
"""

# COMMAND ----------

# Import the config loader
from loguru import logger

from supercharge_ai.config import load_config

# COMMAND ----------

# Load configuration for current environment
config = load_config("project_config.yml", env="dev")

print("Loaded Configuration:")
print(f"  Catalog: {config.catalog}")
print(f"  Schema: {config.schema_name}")
print(f"  Volume: {config.volume}")
print(f"  Full Schema Name: {config.full_schema_name}")
print(f"  Full Volume Path: {config.full_volume_path}")

# COMMAND ----------

# Log some information
logger.info(f"Using catalog: {config.catalog}")
logger.info(f"Using schema: {config.schema_name}")
logger.info(f"LLM Endpoint: {config.llm_endpoint}")

# COMMAND ----------

print("\n✓ Configuration usage example completed successfully!")
