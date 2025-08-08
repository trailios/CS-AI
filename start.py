import subprocess
import time
import sys
import signal
import os

cores = 1500

def signal_handler(sig, frame):
    print("\nReceived interrupt signal. Stopping services...")
    os._exit(1)

signal.signal(signal.SIGINT, signal_handler)

uvicorn_cmd = ["uvicorn", "app:app", "--host", "0.0.0.0", "--workers", "16", "--port", "80"]
celery_cmd = [
    "celery",
    "-A", "src.api.tasks",
    "worker",
    "--pool=threads",
    f"--concurrency={cores}",
    "--without-gossip",      
    "--without-mingle",           
    "--without-heartbeat"         
]
print("starting Celery")
celery_process = subprocess.Popen(celery_cmd)

print("starting server")
try:
    uvicorn_process = subprocess.Popen(uvicorn_cmd)
    uvicorn_process.wait()

except KeyboardInterrupt:
    print("\nStopping services...")
    if 'uvicorn_process' in locals():
        uvicorn_process.terminate()
    celery_process.terminate()
    
    try:
        if 'uvicorn_process' in locals():
            uvicorn_process.wait(timeout=5)
        celery_process.wait(timeout=5)
        
    except subprocess.TimeoutExpired:
        if 'uvicorn_process' in locals():
            uvicorn_process.kill()
        celery_process.kill()
    
    print("all processes terminated.")
    sys.exit(0)
