from typing import Dict, Any, Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import psycopg2
import psycopg2.extras

class TableSchema(Tool):
    """
    Fetch table schema: columns + data types + indexes.
    """

    def _invoke(self, params: dict, **kwargs) -> Generator[ToolInvokeMessage, None, None]:
        # 1. 自动获取凭证：如果 params 里没有，尝试从环境凭证获取
        db_uri = params.get("db_uri") or self.runtime.credentials.get("db_uri")
        schema = params.get("schema")
        if not schema:
            schema = "public"  # 强制默认为 public
        tables = params.get("tables")

        # 2. 错误处理：不要 raise Exception，而是返回错误信息给 LLM
        if not db_uri:
            yield self.create_text_message("Error: db_uri is required.")
            return

        # 多表处理
        if tables:
            table_list = [t.strip() for t in tables.split(",")]
        else:
            table_list = None

        conn = None
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
                # 使用 try-except 防止因为单张表权限问题导致整体失败
                try:
                    cur.execute("""
                            SELECT attname AS column,
                                   format_type(atttypid, atttypmod) AS type
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
                except Exception as e:
                    # 记录错误但不中断循环
                    result[tb] = {"error": str(e)}

            cur.close()
            
            # ✅ 修复核心：
            # 1. 使用 create_json_message 包装结果
            # 2. 使用 yield 而不是 return
            yield self.create_json_message(result)

        except Exception as e:
            # 捕获连接级错误
            yield self.create_text_message(f"Schema fetch error: {str(e)}")
            
        finally:
            if conn:
                conn.close()