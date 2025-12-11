from dify_plugin import ToolProvider
import psycopg2
import psycopg2.extras


class SqlExecute(ToolProvider):
    """
    Execute arbitrary SQL and return results.
    """

    def _invoke(self, params: dict, **kwargs):
        db_uri = params.get("db_uri")
        query = params.get("query")

        if not db_uri:
            raise Exception("db_uri is required.")
        if not query:
            raise Exception("query is required.")

        try:
            conn = psycopg2.connect(db_uri)
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(query)

            # 可能是 SELECT 或 DML
            if cur.description:
                rows = cur.fetchall()
            else:
                conn.commit()
                rows = {"affected_rows": cur.rowcount}

            cur.close()
            conn.close()
            return rows

        except Exception as e:
            raise Exception(f"SQL execution error: {str(e)}")
