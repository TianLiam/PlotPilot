import subprocess
import sys
import os
import time
import signal
import threading

BACKEND_PORT = 8005
FRONTEND_PORT = 3000
BACKEND_HOST = "127.0.0.1"

def print_banner():
    print("")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    Narra · 叙界                            ║")
    print("║              让每一个故事，都拥有自己的世界。                ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print(f"║  后端服务: http://{BACKEND_HOST}:{BACKEND_PORT}          ║")
    print(f"║  前端服务: http://{BACKEND_HOST}:{FRONTEND_PORT}          ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print("")

def start_backend():
    print("🚀 启动后端服务...")
    backend_cmd = [
        sys.executable, "-m", "uvicorn",
        "interfaces.main:app",
        "--host", BACKEND_HOST,
        "--port", str(BACKEND_PORT),
        "--reload"
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(".")
    return subprocess.Popen(backend_cmd, env=env)

def start_frontend():
    print("🚀 启动前端服务...")
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    frontend_dir = os.path.join(script_dir, "frontend")
    frontend_cmd = "D:\\nodejs\\npm.cmd run dev"
    return subprocess.Popen(frontend_cmd, cwd=frontend_dir, shell=True)

def main():
    print_banner()

    print("📦 启动服务...")
    backend_process = start_backend()
    frontend_process = start_frontend()

    print("")
    print("🎉 服务启动完成！")
    print(f"   后端 API: http://{BACKEND_HOST}:{BACKEND_PORT}")
    print(f"   前端页面: http://{BACKEND_HOST}:{FRONTEND_PORT}")
    print("")
    print("按 Ctrl+C 停止所有服务...")

    def signal_handler(sig, frame):
        print("")
        print("🛑 正在停止服务...")
        try:
            backend_process.terminate()
            print("  ✓ 后端服务已停止")
        except:
            pass
        try:
            frontend_process.terminate()
            print("  ✓ 前端服务已停止")
        except:
            pass
        print("")
        print("👋 再见！")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
