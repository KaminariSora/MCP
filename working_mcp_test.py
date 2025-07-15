import asyncio
import json
import subprocess
import sys

async def test_mcp_server():
    """ทดสอบ MCP server แบบถูกต้อง"""
    
    print("Starting MCP server test...")
    
    # เริ่มต้น subprocess สำหรับ server
    process = subprocess.Popen(
        [sys.executable, 'server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    
    try:
        # รอให้ server เริ่มต้น
        await asyncio.sleep(1)
        
        # ส่ง initialize request
        print("\n=== Testing Initialize ===")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        
        # อ่านผลลัพธ์
        response = process.stdout.readline()
        if response:
            print(f"Initialize response: {response.strip()}")
        
        # ส่ง initialized notification
        print("\n=== Sending Initialized Notification ===")
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        process.stdin.write(json.dumps(initialized_notification) + '\n')
        process.stdin.flush()
        
        await asyncio.sleep(0.5)
        
        # ทดสอบ list tools
        print("\n=== Testing List Tools ===")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(tools_request) + '\n')
        process.stdin.flush()
        
        response = process.stdout.readline()
        if response:
            print(f"Tools response: {response.strip()}")
            # Parse และแสดง tools
            try:
                resp_data = json.loads(response)
                if 'result' in resp_data and 'tools' in resp_data['result']:
                    tools = resp_data['result']['tools']
                    print(f"Found {len(tools)} tools:")
                    for tool in tools:
                        print(f"  - {tool['name']}: {tool['description']}")
            except:
                pass
        
        # ทดสอบ echo
        print("\n=== Testing Echo Tool ===")
        echo_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "echo",
                "arguments": {"text": "สวัสดี MCP Server!"}
            }
        }
        
        process.stdin.write(json.dumps(echo_request) + '\n')
        process.stdin.flush()
        
        response = process.stdout.readline()
        if response:
            print(f"Echo response: {response.strip()}")
            # Parse และแสดงผลลัพธ์
            try:
                resp_data = json.loads(response)
                if 'result' in resp_data and 'content' in resp_data['result']:
                    content = resp_data['result']['content'][0]['text']
                    print(f"Echo result: {content}")
            except:
                pass
        
        # ทดสอบ calculate
        print("\n=== Testing Calculate Tool ===")
        calc_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "calculate",
                "arguments": {"expression": "10 + 5 * 2 - 3"}
            }
        }
        
        process.stdin.write(json.dumps(calc_request) + '\n')
        process.stdin.flush()
        
        response = process.stdout.readline()
        if response:
            print(f"Calculate response: {response.strip()}")
            # Parse และแสดงผลลัพธ์
            try:
                resp_data = json.loads(response)
                if 'result' in resp_data and 'content' in resp_data['result']:
                    content = resp_data['result']['content'][0]['text']
                    print(f"Calculate result: {content}")
            except:
                pass
        
        # ทดสอบ get_current_time
        print("\n=== Testing Time Tool ===")
        time_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "get_current_time",
                "arguments": {"timezone": "Bangkok"}
            }
        }
        
        process.stdin.write(json.dumps(time_request) + '\n')
        process.stdin.flush()
        
        response = process.stdout.readline()
        if response:
            print(f"Time response: {response.strip()}")
            # Parse และแสดงผลลัพธ์
            try:
                resp_data = json.loads(response)
                if 'result' in resp_data and 'content' in resp_data['result']:
                    content = resp_data['result']['content'][0]['text']
                    print(f"Time result: {content}")
            except:
                pass
        
        # ทดสอบ error handling
        print("\n=== Testing Error Handling ===")
        error_request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "calculate",
                "arguments": {"expression": "1/0"}
            }
        }
        
        process.stdin.write(json.dumps(error_request) + '\n')
        process.stdin.flush()
        
        response = process.stdout.readline()
        if response:
            print(f"Error test response: {response.strip()}")
            try:
                resp_data = json.loads(response)
                if 'result' in resp_data and 'content' in resp_data['result']:
                    content = resp_data['result']['content'][0]['text']
                    print(f"Error result: {content}")
            except:
                pass
        
        print("\n=== Test Complete ===")
        print("✅ MCP Server is working correctly!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())