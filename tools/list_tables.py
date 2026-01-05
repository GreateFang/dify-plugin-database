from typing import Dict, Any, Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import psycopg2
import psycopg2.extras

class ListTables(Tool):
    """
    List all tables in a schema, optionally filtering only those with vector columns.
    """

    def _invoke(self, params: dict, **kwargs) -> Generator[ToolInvokeMessage, None, None]:
        db_uri = params.get("db_uri") or self.runtime.credentials.get("db_uri")
        schema = params.get("schema", "public")
        if not schema:
            schema = "public"  # 强制默认为 public
        only_vector = params.get("only_vector_tables", False)

        # 1. 错误处理：使用 yield 发送消息，然后 return 结束函数
        if not db_uri:
            yield self.create_text_message("Error: db_uri is required.")
            return

        conn = None
        try:
            conn = psycopg2.connect(db_uri)
            # 使用 RealDictCursor 以便按字典访问列名
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # 查询当前 schema 下所有表
            cur.execute("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = %s;
            """, (schema,))
            
            # 获取所有表名列表
            all_tables = [row["tablename"] for row in cur.fetchall()]

            final_tables = []

            # 逻辑分支
            if not only_vector:
                final_tables = all_tables
            else:
                # 过滤逻辑：检查每张表是否包含 floatvector 字段
                for tb in all_tables:
                    try:
                        cur.execute("""
                            SELECT attname, atttypid::regtype::text AS type
                            FROM pg_attribute
                            WHERE attrelid = %s::regclass
                              AND attnum > 0
                              AND NOT attisdropped;
                        """, (f"{schema}.{tb}",))
                        cols = cur.fetchall()

                        for c in cols:
                            # 兼容不同版本的 pgvector，通常类型名为 'vector' 或包含 'vector'
                            type_name = c.get("type", "").lower()
                            if "vector" in type_name: 
                                final_tables.append(tb)
                                break
                    except Exception as e:
                        # 忽略单个表的权限或查询错误，继续检查下一个
                        print(f"Warning checking table {tb}: {e}")
                        continue

            cur.close()
            
            # ✅ 核心修复点：使用 yield 而不是 return
            yield self.create_json_message({
                "tables": final_tables,
                "count": len(final_tables)
            })

        except Exception as e:
            # 捕获数据库连接级错误
            yield self.create_text_message(f"Database Error: {str(e)}")
            
        finally:
            if conn:
                conn.close()