"""Utility functions for Supercharge AI."""

from __future__ import annotations

from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory.

    Returns:
        Path to project root
    """
    current = Path.cwd()
    for _ in range(5):
        if (current / "databricks.yml").exists():
            return current
        current = current.parent
    return Path.cwd()


def get_notebook_path() -> str | None:
    """Get the current notebook path if running in Databricks.

    Returns:
        Notebook path or None if not in a notebook
    """
    try:
        from pyspark.sql import SparkSession

        spark = SparkSession.getActiveSession()
        if spark:
            dbutils = spark.sparkContext._jvm.com.databricks.service.DBUtils  # type: ignore
            return dbutils.notebook.getContext().notebookPath().get()  # type: ignore
    except Exception:
        pass
    return None


def ensure_dir_exists(path: Path | str) -> Path:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        Path object
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj
