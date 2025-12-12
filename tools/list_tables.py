from dify_plugin import Tool
import psycopg2
import psycopg2.extras


class ListTables(Tool):
    """
    List all tables in a schema, optionally filtering only those with vector columns.
    """

    def _invoke(self, params: dict, **kwargs):
        db_uri = params.get("db_uri")
        schema = params.get("schema", "public")
        only_vector = params.get("only_vector_tables", False)

        if not db_uri:
            raise Exception("db_uri is required.")

        try:
            conn = psycopg2.connect(db_uri)
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # 查询当前 schema 下所有表
            cur.execute("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = %s;
            """, (schema,))
            tables = [row["tablename"] for row in cur.fetchall()]

            # 如果不需要过滤 vector 列，直接返回
            if not only_vector:
                cur.close()
                conn.close()
                return tables

            # 否则检查每张表是否包含 floatvector 字段
            vector_tables = []
            for tb in tables:
                cur.execute("""
                    SELECT attname, atttypid::regtype::text AS type
                    FROM pg_attribute
                    WHERE attrelid = %s::regclass
                      AND attnum > 0
                      AND NOT attisdropped;
                """, (f"{schema}.{tb}",))
                cols = cur.fetchall()

                for c in cols:
                    # VexDB 类型 name: floatvector(D)
                    if c["type"].startswith("floatvector"):
                        vector_tables.append(tb)
                        break  # 已匹配到向量字段，跳过该表

            cur.close()
            conn.close()
            return vector_tables

        except Exception as e:
            raise Exception(f"Database error: {str(e)}")
