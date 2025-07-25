import asyncio
import logging
import sys
import json
from datetime import datetime
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server

# ตั้งค่า logging ที่ละเอียดขึ้น
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server_debug.log', encoding='utf-8'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("my-mcp-server")

# เพิ่ม startup messages
print("=" * 50, file=sys.stderr)
print("MCP Server Starting...", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Working directory: {sys.path[0]}", file=sys.stderr)
print("=" * 50, file=sys.stderr)

logger.info("MCP Server initializing...")

try:
    server = Server("my-mcp-server")
    logger.info("Server object created successfully")
except Exception as e:
    logger.error(f"Failed to create server: {e}")
    sys.exit(1)

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """ลิสต์ tools ที่มี"""
    logger.info("🔧 Tools list requested")
    print("📋 Listing available tools...", file=sys.stderr)
    
    tools = [
        types.Tool(
            name="get_current_time",
            description="Get the current time for any timezone",
            inputSchema={
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone (e.g., 'Asia/Bangkok', 'UTC')",
                        "default": "local"
                    }
                }
            }
        ),
        types.Tool(
            name="calculate",
            description="Perform basic mathematical calculations",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        ),
        types.Tool(
            name="echo",
            description="Echo back the input text",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to echo back"
                    }
                },
                "required": ["text"]
            }
        )
    ]
    
    logger.info(f"Returning {len(tools)} tools")
    return tools

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    """จัดการคำขอใช้ tools"""
    logger.info(f"🛠️  Tool called: {name}")
    logger.info(f"📥 Arguments: {arguments}")
    print(f"⚡ Executing tool: {name}", file=sys.stderr)
    
    try:
        if name == "get_current_time":
            timezone_name = arguments.get("timezone", "local") if arguments else "local"
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            result_text = f"Current time ({timezone_name}): {current_time}"
            
            logger.info(f"✅ Time result: {result_text}")
            return [types.TextContent(type="text", text=result_text)]
        
        elif name == "calculate":
            expression = arguments.get("expression", "") if arguments else ""
            if not expression:
                return [types.TextContent(type="text", text="No expression provided")]
            
            # Safe evaluation
            try:
                allowed_names = {
                    '__builtins__': {},
                    'abs': abs, 'round': round, 'min': min, 'max': max, 'pow': pow,
                    'pi': 3.14159, 'e': 2.71828
                }
                result = eval(expression, allowed_names)
                result_text = f"Expression: {expression}\nResult: {result}"
                
                logger.info(f"✅ Calculation result: {result}")
                return [types.TextContent(type="text", text=result_text)]
                
            except Exception as calc_error:
                error_text = f"Calculation error: {str(calc_error)}"
                logger.error(error_text)
                return [types.TextContent(type="text", text=error_text)]
        
        elif name == "echo":
            text = arguments.get("text", "") if arguments else ""
            result_text = f"Echo: {text}"
            
            logger.info(f"✅ Echo result: {result_text}")
            return [types.TextContent(type="text", text=result_text)]
        
        else:
            error_msg = f"Unknown tool: {name}"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
            
    except Exception as e:
        logger.error(f"❌ Tool execution error: {str(e)}", exc_info=True)
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    print("🔗 Attempting to connect to stdio...", file=sys.stderr)
    logger.info("Connecting to stdio transport...")
    
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            print("✅ Connected to stdio successfully!", file=sys.stderr)
            print("🚀 MCP Server is ready to serve requests", file=sys.stderr)
            logger.info("stdio connection established - server ready")
            
            # แสดงข้อมูล server
            capabilities = server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            )
            logger.info(f"Server capabilities: {capabilities}")
            
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="my-mcp-server",
                    server_version="1.0.0",
                    capabilities=capabilities,
                ),
            )
            
    except Exception as e:
        print(f"❌ Connection error: {str(e)}", file=sys.stderr)
        logger.error(f"stdio connection failed: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        print("🎯 Starting MCP server main loop...", file=sys.stderr)
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user (Ctrl+C)", file=sys.stderr)
        logger.info("Server stopped by user interrupt")
    except Exception as e:
        print(f"💥 Fatal server error: {str(e)}", file=sys.stderr)
        logger.error(f"Fatal error in main: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        print("🔚 MCP Server shutdown complete", file=sys.stderr)