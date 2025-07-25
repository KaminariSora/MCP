import subprocess
import sys
import os
import time

def test_server_startup():
    """ทดสอบการเริ่มต้นของ server"""
    print("Testing MCP server startup...")
    
    # ตรวจสอบว่าไฟล์ server มีอยู่
    server_file = "server.py"  # เปลี่ยนเป็นชื่อไฟล์จริง
    
    if not os.path.exists(server_file):
        print(f"Error: Server file '{server_file}' not found!")
        print("Please make sure the server file exists and update the filename.")
        return False
    
    try:
        # รัน server และดู stderr output
        print(f"Starting server: python {server_file}")
        
        process = subprocess.Popen(
            [sys.executable, server_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0  # Unbuffered
        )
        
        # รอให้ server เริ่มต้น
        time.sleep(2)
        
        # ตรวจสอบว่า process ยังทำงานอยู่
        if process.poll() is None:
            print("✅ Server started successfully!")
            
            # อ่าน stderr เพื่อดู log
            stderr_data = ""
            try:
                stderr_data = process.stderr.read()
                if stderr_data:
                    print("Server logs:")
                    print(stderr_data)
            except:
                pass
            
            # หยุด server
            process.terminate()
            process.wait(timeout=5)
            return True
            
        else:
            print("❌ Server failed to start!")
            stdout, stderr = process.communicate()
            if stderr:
                print("Error output:")
                print(stderr)
            return False
            
    except FileNotFoundError:
        print("Error: Python interpreter not found!")
        return False
    except Exception as e:
        print(f"Error running server: {e}")
        return False

def check_dependencies():
    """ตรวจสอบ dependencies"""
    print("Checking dependencies...")
    
    required_packages = ['mcp']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nInstall missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    print("=== MCP Server Diagnostic ===\n")
    
    # ตรวจสอบ dependencies
    if not check_dependencies():
        return
    
    print()
    
    # ทดสอบ server
    test_server_startup()
    
    print("\n=== Diagnostic Complete ===")
    print("\nNext steps:")
    print("1. Make sure server file name is correct")
    print("2. Check server logs for any errors")
    print("3. Verify MCP client configuration")

if __name__ == "__main__":
    main()