from dify_plugin import ToolProvider
import psycopg2
import psycopg2.extras


class TableSchema(ToolProvider):
    """
    Fetch table schema: columns + data types + indexes.
    """

    def _invoke(self, params: dict, **kwargs):
        db_uri = params.get("db_uri")
        schema = params.get("schema", "public")
        tables = params.get("tables")

        if not db_uri:
            raise Exception("db_uri is required.")

        # 多表处理
        if tables:
            table_list = [t.strip() for t in tables.split(",")]
        else:
            table_list = None

        try:
            conn = psycopg2.connect(db_uri)
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # 若未指定 tables，则列出 schema 下所有表
            if not table_list:
                cur.execute(
                    "SELECT tablename FROM pg_tables WHERE schemaname = %s;",
                    (schema,)
                )
                table_list = [r["tablename"] for r in cur.fetchall()]

            result = {}

            for tb in table_list:
                full_table = f"{schema}.{tb}"

                # 获取字段信息
                cur.execute("""
                    SELECT attname AS column,
                           atttypid::regtype::text AS type
                    FROM pg_attribute
                    WHERE attrelid = %s::regclass
                      AND attnum > 0
                      AND NOT attisdropped;
                """, (full_table,))
                columns = cur.fetchall()

                # 获取索引信息
                cur.execute("""
                    SELECT indexname, indexdef
                    FROM pg_indexes
                    WHERE schemaname = %s AND tablename = %s;
                """, (schema, tb))
                indexes = cur.fetchall()

                result[tb] = {
                    "columns": columns,
                    "indexes": indexes
                }

            cur.close()
            conn.close()
            return result

        except Exception as e:
            raise Exception(f"Schema fetch error: {str(e)}")
