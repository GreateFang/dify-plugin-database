from typing import Dict, Any, Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import psycopg2
import psycopg2.extras
import json

class SQLExecuteTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        db_uri = tool_parameters.get("db_uri") or self.runtime.credentials.get("db_uri")
        if not db_uri:
            yield self.create_text_message("Error: Database URI is not provided.")
            return
        
        query = tool_parameters.get("query", "").strip()
        if not query:
            yield self.create_text_message("Error: Query is empty.")
            return

        conn = None
        try:
            conn = psycopg2.connect(db_uri)
            # 自动提交模式，或者手动管理事务
            conn.autocommit = True 
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            is_select = query.strip().upper().startswith(("SELECT", "WITH", "EXPLAIN"))

            cur.execute(query)
            
            if is_select:
                rows = cur.fetchall()
                # ✅ 修复：返回 JSON 格式
                yield self.create_json_message({
                    "result": rows,
                    "count": len(rows)
                })
            else:
                # 非查询语句（UPDATE/INSERT/DELETE）
                affected = cur.rowcount
                yield self.create_text_message(f"Query executed successfully. Affected rows: {affected}")

            cur.close()

        except Exception as e:
            yield self.create_text_message(f"SQL Execution Error: {str(e)}")
        finally:
            if conn:
                conn.close()