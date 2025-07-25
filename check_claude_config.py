import json
import os
import platform
import subprocess

def get_claude_config_path():
    """หา path ที่ถูกต้องของ Claude config"""
    system = platform.system()
    
    paths = []
    
    if system == "Windows":
        # Windows paths
        appdata = os.environ.get('APPDATA', '')
        localappdata = os.environ.get('LOCALAPPDATA', '')
        
        paths.extend([
            os.path.join(appdata, "Claude", "claude_desktop_config.json"),
            os.path.join(localappdata, "Claude", "claude_desktop_config.json"),
            os.path.join(appdata, "Anthropic", "Claude", "claude_desktop_config.json"),
        ])
        
    elif system == "Darwin":  # macOS
        home = os.path.expanduser("~")
        paths.extend([
            os.path.join(home, "Library", "Application Support", "Claude", "claude_desktop_config.json"),
            os.path.join(home, "Library", "Application Support", "Anthropic", "Claude", "claude_desktop_config.json"),
        ])
        
    elif system == "Linux":
        home = os.path.expanduser("~")
        paths.extend([
            os.path.join(home, ".config", "claude", "claude_desktop_config.json"),
            os.path.join(home, ".config", "anthropic", "claude", "claude_desktop_config.json"),
        ])
    
    return paths

def check_all_possible_configs():
    """ตรวจสอบ config ทุก path ที่เป็นไปได้"""
    paths = get_claude_config_path()
    found_configs = []
    
    print("🔍 Checking all possible Claude config locations...")
    print()
    
    for path in paths:
        print(f"📂 Checking: {path}")
        
        if os.path.exists(path):
            print("  ✅ File exists")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print("  ✅ Valid JSON")
                
                if 'mcpServers' in config:
                    servers = config['mcpServers']
                    print(f"  ✅ Found {len(servers)} MCP server(s)")
                    for name, settings in servers.items():
                        cmd = settings.get('command', 'N/A')
                        args = settings.get('args', [])
                        print(f"    - {name}: {cmd} {' '.join(args)}")
                else:
                    print("  ❌ No mcpServers section")
                
                found_configs.append(path)
                
            except json.JSONDecodeError as e:
                print(f"  ❌ Invalid JSON: {e}")
            except Exception as e:
                print(f"  ❌ Read error: {e}")
        else:
            print("  ❌ File not found")
        
        print()
    
    return found_configs

def create_proper_config():
    """สร้าง config ที่ถูกต้อง"""
    paths = get_claude_config_path()
    current_dir = os.getcwd()
    server_path = os.path.join(current_dir, "server.py")
    
    # ใช้ path แรกที่เหมาะสม
    target_path = paths[0] if paths else None
    
    if not target_path:
        print("❌ Cannot determine config path")
        return
    
    config = {
        "mcpServers": {
            "my-time-server": {
                "command": "python",
                "args": [server_path]
            }
        }
    }
    
    print(f"📝 Creating config at: {target_path}")
    print(f"🔧 Server path: {server_path}")
    
    # สร้าง directory ถ้าไม่มี
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    # เขียน config
    with open(target_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Config file created!")
    print()
    print("📋 Config content:")
    print(json.dumps(config, indent=2))

def verify_server_file():
    """ตรวจสอบไฟล์ server"""
    server_path = os.path.join(os.getcwd(), "server.py")
    
    print(f"🔍 Checking server file: {server_path}")
    
    if os.path.exists(server_path):
        print("✅ Server file exists")
        
        # ตรวจสอบว่าเป็น MCP server หรือไม่
        try:
            with open(server_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'mcp.server' in content and 'Server(' in content:
                print("✅ File appears to be a valid MCP server")
            else:
                print("❌ File might not be a proper MCP server")
                
        except Exception as e:
            print(f"❌ Cannot read server file: {e}")
    else:
        print("❌ Server file not found")
        print("Make sure 'server.py' is in the current directory")

def main():
    print("=== Claude Desktop MCP Configuration Diagnostic ===")
    print()
    
    # ตรวจสอบ config ที่มีอยู่
    found_configs = check_all_possible_configs()
    
    # ตรวจสอบไฟล์ server
    verify_server_file()
    print()
    
    if not found_configs:
        print("❌ No existing config found. Creating new one...")
        create_proper_config()
    else:
        print(f"✅ Found {len(found_configs)} config file(s)")
        print("If MCP tools still don't work:")
        print("1. Make sure Claude Desktop is completely restarted")
        print("2. Check if the server path in config is correct")
        print("3. Try creating a new chat in Claude Desktop")
    
    print()
    print("=== Next Steps ===")
    print("1. 🔄 Restart Claude Desktop completely (quit and reopen)")
    print("2. 🆕 Start a new chat (important!)")
    print("3. 🧪 Test: 'What time is it?'")
    print("4. 📋 Look for MCP tools in the interface")

if __name__ == "__main__":
    main()