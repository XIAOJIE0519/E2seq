"""Kill old server and start new one with fresh code."""
import subprocess, sys, time, os

# Kill all python processes using port 8000
result = subprocess.run(
    ["cmd", "/c", "netstat -ano | findstr :8000 | findstr LISTEN"],
    capture_output=True, text=True, timeout=5
)
for line in result.stdout.strip().split("\n"):
    parts = line.split()
    if len(parts) >= 5 and "LISTENING" in parts[3]:
        pid = parts[-1].strip()
        print(f"Killing PID {pid}...")
        subprocess.run(["cmd", "/c", f"taskkill /F /PID {pid}"],
                     capture_output=True, timeout=5)

time.sleep(3)

# Verify port is free
result2 = subprocess.run(
    ["cmd", "/c", "netstat -ano | findstr :8000 | findstr LISTEN"],
    capture_output=True, text=True, timeout=5
)
if result2.stdout.strip():
    print("WARNING: port 8000 still in use!")
else:
    print("Port 8000 is free. Starting fresh server...")

# Start server in background
env = os.environ.copy()
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "e2sc.api.server:app",
     "--host", "0.0.0.0", "--port", "8000"],
    cwd=r"f:\1a-sc-agent",
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    env=env,
)
print(f"Server PID: {proc.pid}")

# Wait for startup
import requests
for i in range(10):
    time.sleep(1)
    try:
        r = requests.get("http://localhost:8000/api/status", timeout=3)
        print(f"[{i+1}s] Server UP: {r.json()}")
        break
    except Exception as e:
        print(f"[{i+1}s] waiting... ({type(e).__name__})")
else:
    stdout, _ = proc.communicate(timeout=2)
    print("FAILED TO START:")
    print(stdout.decode("utf-8", errors="replace")[:1000])
