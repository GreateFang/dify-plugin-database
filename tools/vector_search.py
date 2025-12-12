from dify_plugin import Tool
import psycopg2
import psycopg2.extras
import json


class VectorSearch(Tool):
    """
    Perform vector similarity search on a floatvector column.
    """

    def _invoke(self, params: dict, **kwargs):
        db_uri = params.get("db_uri")
        schema = params.get("schema", "public")
        table = params.get("table")
        vector_column = params.get("vector_column")
        query_vector = params.get("query_vector")
        distance_type = params.get("distance_type", "l2")
        top_k = params.get("top_k", 5)
        output_columns = params.get("output_columns")

        if not db_uri:
            raise Exception("db_uri is required.")
        if not table:
            raise Exception("table is required.")
        if not vector_column:
            raise Exception("vector_column is required.")
        if not isinstance(query_vector, list):
            raise Exception("query_vector must be list of floats.")

        # 输出列构建
        if output_columns:
            cols = output_columns
        else:
            cols = "*"

        # 距离函数
        # VexDB 跟 PGVector 一样支持 <->、<#>、<=> 等
        op = {
            "l2": "<->",
            "cosine": "<=>",
            "ip": "<#>"
        }.get(distance_type.lower(), "<->")

        full_table = f"{schema}.{table}"

        sql = f"""
            SELECT {cols},
                   {vector_column} {op} %s AS distance
            FROM {full_table}
            ORDER BY distance
            LIMIT {int(top_k)};
        """

        try:
            conn = psycopg2.connect(db_uri)
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(sql, (query_vector,))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows

        except Exception as e:
            raise Exception(f"Vector search error: {str(e)}")
