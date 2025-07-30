import asyncio
import logging
import os
import sys
from mysql.connector import connect, Error
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
from pydantic import AnyUrl

# 导入标准库模块
import asyncio  # 异步IO支持
import logging  # 日志记录
import os       # 操作系统接口
import sys      # 系统特定函数

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mysql_mcp_server")

# 获取数据库配置的函数
def get_db_config():
    """
    从环境变量获取数据库配置参数
    
    Returns:
        dict: 包含数据库连接参数的字典
    
    Raises:
        ValueError: 如果缺少必要配置时抛出异常
    """
    config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", "Linsec@2018"),
        "database": os.getenv("MYSQL_DATABASE", "bladex"),
        # Add charset and collation to avoid utf8mb4_0900_ai_ci issues with older MySQL versions
        # These can be overridden via environment variables for specific MySQL versions
        "charset": os.getenv("MYSQL_CHARSET", "utf8mb4"),
        "collation": os.getenv("MYSQL_COLLATION", "utf8mb4_unicode_ci"),
        # Disable autocommit for better transaction control
        "autocommit": True,
        # Set SQL mode for better compatibility - can be overridden
        "sql_mode": os.getenv("MYSQL_SQL_MODE", "TRADITIONAL")
    }

    # Remove None values to let MySQL connector use defaults if not specified
    config = {k: v for k, v in config.items() if v is not None}

    if not all([config.get("user"), config.get("password"), config.get("database")]):
        logger.error("Missing required database configuration. Please check environment variables:")
        logger.error("MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE are required")
        raise ValueError("Missing required database configuration")

    return config

# 初始化MCP服务器
app = Server("mysql_mcp_server")  # 创建服务器实例

@app.list_resources()
async def list_resources() -> list[Resource]:
    """
    列出MySQL中的表作为资源
    
    该函数实现MCP协议的list_resources方法，将MySQL中的每个表
    转换为一个Resource对象返回给客户端。
    
    Returns:
        list[Resource]: 包含所有表信息的Resource对象列表
    """
    config = get_db_config()
    try:
        logger.info(f"Connecting to MySQL with charset: {config.get('charset')}, collation: {config.get('collation')}")
        with connect(**config) as conn:
            logger.info(f"Successfully connected to MySQL server version: {conn.get_server_info()}")
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                logger.info(f"Found tables: {tables}")

                resources = []
                for table in tables:
                    resources.append(
                        Resource(
                            uri=f"mysql://{table[0]}/data",
                            name=f"Table: {table[0]}",
                            mimeType="text/plain",
                            description=f"Data in table: {table[0]}"
                        )
                    )
                return resources
    except Error as e:
        logger.error(f"Failed to list resources: {str(e)}")
        logger.error(f"Error code: {e.errno}, SQL state: {e.sqlstate}")
        return []

@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """
    读取表内容
    
    处理read_resource请求，从指定的MySQL表中读取数据并
    返回CSV格式的结果。
    
    Args:
        uri (AnyUrl): 数据源URI，格式应为 mysql://<table_name>/data
    
    Returns:
        str: 表数据的CSV表示
    
    Raises:
        ValueError: 如果URI格式不正确
        RuntimeError: 如果数据库操作失败
    """
    config = get_db_config()
    uri_str = str(uri)
    logger.info(f"Reading resource: {uri_str}")

    if not uri_str.startswith("mysql://"):
        raise ValueError(f"Invalid URI scheme: {uri_str}")

    parts = uri_str[8:].split('/')
    table = parts[0]

    try:
        logger.info(f"Connecting to MySQL with charset: {config.get('charset')}, collation: {config.get('collation')}")
        with connect(**config) as conn:
            logger.info(f"Successfully connected to MySQL server version: {conn.get_server_info()}")
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table} LIMIT 100")
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                result = [",".join(map(str, row)) for row in rows]
                return "\n".join([",".join(columns)] + result)

    except Error as e:
        logger.error(f"Database error reading resource {uri}: {str(e)}")
        logger.error(f"Error code: {e.errno}, SQL state: {e.sqlstate}")
        raise RuntimeError(f"Database error: {str(e)}")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    列出可用工具
    
    返回当前服务器支持的所有工具。目前仅支持execute_sql工具。
    
    Returns:
        list[Tool]: 支持的工具列表
    """
    logger.info("Listing tools...")
    return [
        Tool(
            name="execute_sql",
            description="Execute an SQL query on the MySQL server",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query to execute"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    执行工具调用
    
    根据请求调用相应的工具并返回结果。目前仅支持execute_sql工具。
    
    Args:
        name (str): 工具名称
        arguments (dict): 工具调用参数
    
    Returns:
        list[TextContent]: 工具执行结果
    
    Raises:
        ValueError: 如果工具不存在或参数不完整
    """
    config = get_db_config()
    logger.info(f"Calling tool: {name} with arguments: {arguments}")

    if name != "execute_sql":
        raise ValueError(f"Unknown tool: {name}")

    query = arguments.get("query")
    if not query:
        raise ValueError("Query is required")

    try:
        logger.info(f"Connecting to MySQL with charset: {config.get('charset')}, collation: {config.get('collation')}")
        with connect(**config) as conn:
            logger.info(f"Successfully connected to MySQL server version: {conn.get_server_info()}")
            with conn.cursor() as cursor:
                cursor.execute(query)

                # Special handling for SHOW TABLES
                if query.strip().upper().startswith("SHOW TABLES"):
                    tables = cursor.fetchall()
                    result = ["Tables_in_" + config["database"]]  # Header
                    result.extend([table[0] for table in tables])
                    return [TextContent(type="text", text="\n".join(result))]

                # Handle all other queries that return result sets (SELECT, SHOW, DESCRIBE etc.)
                elif cursor.description is not None:
                    columns = [desc[0] for desc in cursor.description]
                    try:
                        rows = cursor.fetchall()
                        result = [",".join(map(str, row)) for row in rows]
                        return [TextContent(type="text", text="\n".join([",".join(columns)] + result))]
                    except Error as e:
                        logger.warning(f"Error fetching results: {str(e)}")
                        return [TextContent(type="text", text=f"Query executed but error fetching results: {str(e)}")]

                # Non-SELECT queries
                else:
                    conn.commit()
                    return [TextContent(type="text", text=f"Query executed successfully. Rows affected: {cursor.rowcount}")]

    except Error as e:
        logger.error(f"Error executing SQL '{query}': {e}")
        logger.error(f"Error code: {e.errno}, SQL state: {e.sqlstate}")
        return [TextContent(type="text", text=f"Error executing query: {str(e)}")]

async def main():
    """
    主程序入口
    
    配置并启动MCP服务器。处理服务器初始化、日志记录和错误处理。
    
    Raises:
        Exception: 如果服务器运行过程中发生错误
    """
    from mcp.server.stdio import stdio_server

    # Add additional debug output
    print("Starting MySQL MCP server with config:", file=sys.stderr)
    config = get_db_config()
    print(f"Host: {config['host']}", file=sys.stderr)
    print(f"Port: {config['port']}", file=sys.stderr)
    print(f"User: {config['user']}", file=sys.stderr)
    print(f"Database: {config['database']}", file=sys.stderr)

    logger.info("Starting MySQL MCP server...")
    logger.info(f"Database config: {config['host']}/{config['database']} as {config['user']}")

    async with stdio_server() as (read_stream, write_stream):
        try:
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
        except Exception as e:
            logger.error(f"Server error: {str(e)}", exc_info=True)
            raise

if __name__ == "__main__":
    asyncio.run(main())  # 程序入口点
