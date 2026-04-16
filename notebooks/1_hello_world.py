# Databricks notebook source
"""
Hello World Notebook

This notebook demonstrates:
- Databricks notebook format
- Cell structure (using # COMMAND ----------)
- Basic Databricks operations
"""

# COMMAND ----------

print("Welcome to Supercharge AI!")
print("This is a simple Hello World notebook running on Databricks.")

# COMMAND ----------

# Get the workspace client
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
current_user = w.current_user.me()

print(f"\nLogged in as: {current_user.display_name}")
print(f"Email: {current_user.emails[0].value if current_user.emails else 'N/A'}")

# COMMAND ----------

print("\n✓ Hello World notebook completed successfully!")
