from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.list_databases import ListDatabasesTool  # 复用底层连接逻辑来验库也行
from tools.sql_execute import SQLExecuteTool  # 如果你想用更通用的，可以单独写一个

class VexDBProvider(ToolProvider):

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        简单用 SELECT 1 检查 db_uri 是否可用
        """
        db_uri = credentials.get("db_uri")
        if not db_uri:
            raise ToolProviderCredentialValidationError("db_uri is required.")

        try:
            # 用最简单的 SQL 检查连接
            for _ in SQLExecuteTool.from_credentials(credentials).invoke(
                tool_parameters={"query": "SELECT 1"}
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
