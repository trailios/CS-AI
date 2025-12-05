import os
import signal
import subprocess
import sys
from typing import Dict, List, Tuple


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return max(1, int(value))
    except ValueError:
        return default


def _build_celery_cmd() -> Tuple[List[str], Dict[str, object]]:
    pool = os.getenv("CELERY_POOL") or ("threads" if os.name == "nt" else "prefork")
    cpu_count = os.cpu_count() or 1

    target = _env_int(
        "CELERY_WORKER_CONCURRENCY",
        min(32, cpu_count * (4 if pool == "threads" else 2)),
    )
    max_autoscale = _env_int("CELERY_MAX_CONCURRENCY", target)
    min_autoscale = _env_int("CELERY_MIN_CONCURRENCY", max(1, target // 2))
    if min_autoscale > max_autoscale:
        min_autoscale = max_autoscale

    log_level = os.getenv("CELERY_LOG_LEVEL", "info")
    autoscale_supported = pool != "threads" and os.getenv("CELERY_AUTOSCALE", "1") != "0"

    cmd = [
        "celery",
        "-A",
        "src.api.tasks",
        "worker",
        "-E",
        f"--pool={pool}",
        "--without-gossip",
        "--without-mingle",
        "--without-heartbeat",
        "--loglevel",
        log_level,
    ]

    if autoscale_supported:
        cmd.append(f"--autoscale={max_autoscale},{min_autoscale}")
    else:
        cmd.append(f"--concurrency={max_autoscale}")

    return cmd, {
        "pool": pool,
        "max": max_autoscale,
        "min": min_autoscale,
        "autoscale": autoscale_supported,
    }


def _stop_process(proc: subprocess.Popen, name: str) -> None:
    if proc and proc.poll() is None:
        print(f"Stopping {name}...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


processes: List[Tuple[str, subprocess.Popen]] = []


def _stop_all() -> None:
    for name, proc in reversed(processes):
        _stop_process(proc, name)


def _signal_handler(sig, frame):
    print("\nReceived interrupt signal. Stopping services...")
    _stop_all()
    sys.exit(0)


for _sig in (signal.SIGINT, signal.SIGTERM):
    try:
        signal.signal(_sig, _signal_handler)
    except Exception:
        pass


uvicorn_cmd = [
    "uvicorn",
    "app:app",
    "--host",
    "0.0.0.0",
    "--workers",
    "16",
    "--port",
    "80",
    "--log-level",
    "critical",
]

celery_cmd, celery_meta = _build_celery_cmd()
print(
    f"starting Celery (pool={celery_meta['pool']}, "
    f"autoscale={celery_meta['autoscale']}, "
    f"max={celery_meta['max']}, min={celery_meta['min']})"
)

celery_process = subprocess.Popen(celery_cmd)
processes.append(("celery", celery_process))

print("starting server")
uvicorn_process = subprocess.Popen(uvicorn_cmd)
processes.append(("uvicorn", uvicorn_process))

try:
    uvicorn_process.wait()
except KeyboardInterrupt:
    print("\nStopping services...")
finally:
    _stop_all()
