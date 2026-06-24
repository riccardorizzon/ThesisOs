import pytest
from app.graph.checkpointer import _psycopg_conn_string, LANGGRAPH_SCHEMA


def test_conn_string_strips_sqlalchemy_driver_and_sets_search_path():
    dsn = "postgresql+psycopg://u:p@/db?host=/cloudsql/x"
    out = _psycopg_conn_string(dsn)
    assert out.startswith("postgresql://")          # psycopg wants the bare scheme
    assert "+psycopg" not in out
    assert f"options=-csearch_path%3D{LANGGRAPH_SCHEMA}" in out or "search_path" in out
