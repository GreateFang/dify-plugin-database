from typing import Dict, Any, Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import psycopg2
import psycopg2.extras
import json  # ✅ 必须导入 json

class VectorSearch(Tool):
    """
    Perform vector similarity search on a floatvector column.
    """

    def _invoke(self, params: dict, **kwargs) -> Generator[ToolInvokeMessage, None, None]:
        db_uri = params.get("db_uri") or self.runtime.credentials.get("db_uri")
        schema = params.get("schema", "public")
        table = params.get("table")
        vector_column = params.get("vector_column")
        query_vector = params.get("query_vector")
        distance_type = params.get("distance_type", "l2")
        top_k = params.get("top_k", 5)
        output_columns = params.get("output_columns")

        if not db_uri:
            yield self.create_text_message("Error: db_uri is required.")
            return
        if not table:
            yield self.create_text_message("Error: table is required.")
            return
        if not vector_column:
            yield self.create_text_message("Error: vector_column is required.")
            return

        # 🔥【关键修复】前端传来的是字符串 "[0.1, ...]"，必须先解析为 JSON 列表
        if isinstance(query_vector, str):
            try:
                query_vector = json.loads(query_vector)
            except Exception:
                yield self.create_text_message("Error: query_vector must be a valid JSON list string.")
                return

        # 类型检查
        if not isinstance(query_vector, list):
            yield self.create_text_message("Error: query_vector must be a list of floats.")
            return

        # 输出列构建
        if output_columns:
            cols = output_columns
        else:
            cols = "*"

        # 距离函数映射
        op = {
            "l2": "<->",
            "cosine": "<=>",
            "ip": "<#>"
        }.get(str(distance_type).lower(), "<->")

        full_table = f"{schema}.{table}"

        # SQL
        sql = f"""
            SELECT {cols},
                   {vector_column} {op} %s AS distance
            FROM {full_table}
            ORDER BY distance
            LIMIT %s;
        """

        conn = None
        try:
            conn = psycopg2.connect(db_uri)
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # 执行查询
            cur.execute(sql, (query_vector, int(top_k)))
            rows = cur.fetchall()
            
            cur.close()
            
            # ✅ 返回 JSON 结果
            yield self.create_json_message({
                "results": rows,
                "count": len(rows)
            })

        except Exception as e:
            yield self.create_text_message(f"Vector search error: {str(e)}")
        finally:
            if conn:
                conn.close()