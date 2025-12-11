from dify_plugin import ToolProvider
import psycopg2
import psycopg2.extras
import json


class InsertRow(ToolProvider):
    """
    Insert a single row into a table.
    Supports all standard VexDB types including floatvector.
    """

    def _invoke(self, params: dict, **kwargs):
        db_uri = params.get("db_uri")
        schema = params.get("schema", "public")
        table = params.get("table")
        row = params.get("row")

        if not db_uri:
            raise Exception("db_uri is required.")
        if not table:
            raise Exception("table is required.")
        if not isinstance(row, dict):
            raise Exception("row must be an object/dict.")

        # 构建 INSERT 语句
        columns = list(row.keys())
        values = [row[c] for c in columns]

        placeholders = ", ".join(["%s"] * len(columns))
        col_sql = ", ".join(columns)
        full_table = f"{schema}.{table}"

        sql = f"INSERT INTO {full_table} ({col_sql}) VALUES ({placeholders}) RETURNING *;"

        try:
            conn = psycopg2.connect(db_uri)
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(sql, values)
            inserted = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            return inserted
        except Exception as e:
            raise Exception(f"Insert error: {str(e)}")
