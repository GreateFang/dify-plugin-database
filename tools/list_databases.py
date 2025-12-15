from typing import Dict, Any, Generator, List
import psycopg2
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class ListDatabases(Tool):

    def _invoke(
        self,
        tool_input: Dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Required abstract method.
        Dify calls this, not _run.
        """

        db_uri = tool_input.get("db_uri") or self.runtime.credentials.get("db_uri")
        
        # 错误处理 1：缺少 URI
        if not db_uri:
            yield self.create_text_message("Error: Database URI is not provided.")
            return

        try:
            conn = psycopg2.connect(db_uri)
        except Exception as e:
            # 错误处理 2：连接失败
            yield self.create_text_message(f"Error: Failed to connect to database: {str(e)}")
            return

        databases: List[str] = []
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT datname
                    FROM pg_database
                    WHERE datistemplate = false
                    ORDER BY datname;
                    """
                )
                databases = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            # 错误处理 3：查询失败
            yield self.create_text_message(f"Error: Failed to query databases: {str(e)}")
            return
        finally:
            if 'conn' in locals() and conn:
                conn.close()

        # ✅ 成功返回：使用 create_json_message 包装数据
        # 这样 Dify 才能正确识别这是一个 JSON 类型的响应
        yield self.create_json_message({
            "databases": databases
        })