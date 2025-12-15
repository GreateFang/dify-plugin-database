from typing import Dict, Any, Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import psycopg2
import psycopg2.extras
import json  # 👈 必须导入 json

class InsertRow(Tool):
    """
    Insert a single row into a table.
    Supports all standard VexDB types including floatvector.
    """

    def _invoke(self, params: dict, **kwargs) -> Generator[ToolInvokeMessage, None, None]:
        db_uri = params.get("db_uri") or self.runtime.credentials.get("db_uri")
        schema = params.get("schema", "public")
        table = params.get("table")
        row_input = params.get("row")  # 获取原始输入

        if not db_uri:
            yield self.create_text_message("Error: db_uri is required.")
            return
        if not table:
            yield self.create_text_message("Error: table is required.")
            return

        # 🔥🔥🔥 核心修复：将字符串解析为字典 🔥🔥🔥
        row = {}
        if isinstance(row_input, dict):
            # 如果系统恰好传来了字典（极少见但兼容）
            row = row_input
        elif isinstance(row_input, str):
            # 如果是字符串（通常情况），尝试解析 JSON
            try:
                row = json.loads(row_input)
            except json.JSONDecodeError:
                yield self.create_text_message("Error: 'Row Data' is not valid JSON string.")
                return
        else:
            yield self.create_text_message(f"Error: Unexpected type for row data: {type(row_input)}")
            return

        # 再次确认解析后是字典
        if not isinstance(row, dict):
            yield self.create_text_message("Error: parsed row data must be a dictionary.")
            return

        # 构建 INSERT 语句
        columns = list(row.keys())
        values = [row[c] for c in columns]

        # 简单的 SQL 构造 (注意：生产环境建议加强列名校验以防注入)
        placeholders = ", ".join(["%s"] * len(columns))
        col_sql = ", ".join(columns)
        
        # 处理 schema 为空的情况
        if not schema:
            schema = "public"
            
        full_table = f"{schema}.{table}"

        sql = f"INSERT INTO {full_table} ({col_sql}) VALUES ({placeholders}) RETURNING *;"

        conn = None
        try:
            conn = psycopg2.connect(db_uri)
            # 使用 RealDictCursor 以便返回结果为字典
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cur.execute(sql, values)
            inserted = cur.fetchone()
            conn.commit()
            
            cur.close()
            
            # 成功返回
            yield self.create_json_message({
                "inserted_row": inserted,
                "status": "success"
            })
            
        except Exception as e:
            if conn:
                conn.rollback()
            yield self.create_text_message(f"Insert error: {str(e)}")
        finally:
            if conn:
                conn.close()