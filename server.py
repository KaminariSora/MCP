import asyncio
import logging
import sys
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log', encoding='utf-8'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("my-mcp-server")

logger.info("Starting MCP Server...")
print("MCP Server is starting...", file=sys.stderr)

server = Server("my-mcp-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """ลิสต์ tools ที่มี"""
    logger.info("Tools requested")
    return [
        types.Tool(
            name="get_current_time",
            description="Get the current time",
            inputSchema={
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone (optional)"
                    }
                }
            }
        ),
        types.Tool(
            name="calculate",
            description="Perform basic calculations",
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

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    """จัดการคำขอใช้ tools"""
    logger.info(f"Tool called: {name} with args: {arguments}")
    
    if name == "get_current_time":
        from datetime import datetime
        timezone = arguments.get("timezone", "local") if arguments else "local"
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"Returning time: {current_time}")
        return [
            types.TextContent(
                type="text",
                text=f"Current time ({timezone}): {current_time}"
            )
        ]
    
    elif name == "calculate":
        try:
            expression = arguments.get("expression", "") if arguments else ""
            logger.info(f"Calculating: {expression}")
            
            # ใช้ eval อย่างปลอดภัยสำหรับ demo
            allowed_names = {
                k: v for k, v in __builtins__.items() 
                if k in ('abs', 'round', 'min', 'max', 'pow', 'sum')
            }
            allowed_names.update({
                '__builtins__': {},
                'pi': 3.14159,
                'e': 2.71828
            })
            
            result = eval(expression, allowed_names)
            logger.info(f"Result: {result}")
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Expression: {expression}\nResult: {result}"
                )
            ]
        except Exception as e:
            logger.error(f"Calculation error: {str(e)}")
            return [
                types.TextContent(
                    type="text",
                    text=f"Error calculating '{expression}': {str(e)}"
                )
            ]
    
    elif name == "echo":
        text = arguments.get("text", "") if arguments else ""
        logger.info(f"Echoing: {text}")
        return [
            types.TextContent(
                type="text",
                text=f"Echo: {text}"
            )
        ]
    
    else:
        logger.error(f"Unknown tool: {name}")
        raise ValueError(f"Unknown tool: {name}")

async def main():
    logger.info("Connecting to stdio...")
    print("Connecting to stdio...", file=sys.stderr)
    
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("Connected! Ready to serve...")
            print("Connected! Ready to serve...", file=sys.stderr)
            
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="my-mcp-server",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        print(f"Server error: {str(e)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        print("Server stopped by user", file=sys.stderr)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"Fatal error: {str(e)}", file=sys.stderr)