from dify_plugin import ToolProvider
import psycopg2

class ListDatabases(ToolProvider):
    """
    List all databases in VexDB (Postgres-compatible).
    """

    def _invoke(self, params: dict, **kwargs):
        db_uri = params.get("db_uri")
        if not db_uri:
            raise Exception("db_uri is required.")

        try:
            conn = psycopg2.connect(db_uri)
            cur = conn.cursor()
            cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
            rows = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")

        return [r[0] for r in rows]
