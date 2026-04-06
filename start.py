# -*- coding: utf-8 -*-
"""
Beauty Salon - Development Server Launcher
Starts backend (Django) and frontend (Vite), verifies everything works.
Windows compatible.
"""

import os
import sys
import time
import signal
import socket
import subprocess
import threading
import shutil
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
VENV_DIR = PROJECT_ROOT / "venv"
VENV_PYTHON = str(VENV_DIR / "Scripts" / "python.exe")

BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000
FRONTEND_HOST = "127.0.0.1"
FRONTEND_PORT = 5173

# Colors
if sys.platform == "win32":
    os.system("color")

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

processes = []


def ok(msg):
    print(f"  {GREEN}OK{RESET} {msg}")


def fail(msg):
    print(f"  {RED}FAIL{RESET} {msg}")


def info(msg):
    print(f"  {CYAN}INFO{RESET} {msg}")


def warn(msg):
    print(f"  {YELLOW}WARN{RESET} {msg}")


def title(msg):
    print(f"\n{BOLD}{CYAN}{'=' * 50}{RESET}")
    print(f"{BOLD}{CYAN}{msg}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 50}{RESET}")


def end_msg(msg):
    print(f"\n{BOLD}{GREEN}{'=' * 50}{RESET}")
    print(f"{BOLD}{GREEN}{msg}{RESET}")
    print(f"{BOLD}{GREEN}{'=' * 50}{RESET}\n")


def kill_all(*_):
    print(f"\n{YELLOW}Stopping all servers...{RESET}")
    for p in processes:
        if p.poll() is None:
            try:
                p.terminate()
                p.wait(timeout=5)
            except Exception:
                p.kill()
    print(f"{GREEN}All processes stopped.{RESET}")
    sys.exit(0)


signal.signal(signal.SIGINT, kill_all)
signal.signal(signal.SIGTERM, kill_all)


def is_port_free(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def wait_for_port(host, port, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((host, port))
                return True
            except OSError:
                time.sleep(0.5)
    return False


def run_cmd(cmd, cwd=None, capture_output=False, shell=False):
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else str(PROJECT_ROOT),
        capture_output=capture_output,
        text=True,
        shell=shell,
    )
    return result


def run_bg(cmd, cwd=None, env_extra=None):
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
    if sys.platform == "win32":
        creation_flags |= subprocess.CREATE_NO_WINDOW
    # Use shell=True on Windows so commands like "npx" are found via PATH
    p = subprocess.Popen(
        cmd,
        cwd=str(cwd) if cwd else str(PROJECT_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=creation_flags,
        shell=True,
    )
    processes.append(p)
    return p


def stream_output(proc, label):
    for line in iter(proc.stdout.readline, ""):
        line = line.rstrip()
        if line:
            try:
                print(f"  [{label}] {line}")
            except UnicodeEncodeError:
                safe_line = line.encode("cp1251", errors="replace").decode("cp1251")
                print(f"  [{label}] {safe_line}")


def kill_port_process(port):
    result = run_cmd(
        f'netstat -ano | findstr :{port}', capture_output=True, shell=True
    )
    if result.stdout:
        for line in result.stdout.strip().split("\n"):
            parts = line.strip().split()
            if len(parts) >= 5:
                pid = parts[-1]
                try:
                    run_cmd(f"taskkill /PID {pid} /F", shell=True)
                except Exception:
                    pass


def check_prerequisites():
    title("1. Checking prerequisites")
    all_ok = True

    if not Path(VENV_PYTHON).exists():
        fail(f"Python venv not found: {VENV_PYTHON}")
        info("Creating venv...")
        subprocess.run(
            [sys.executable, "-m", "venv", str(VENV_DIR)],
            cwd=str(PROJECT_ROOT),
        )
        if Path(VENV_PYTHON).exists():
            ok("venv created")
        else:
            fail("Failed to create venv")
            all_ok = False
    else:
        ok("Python venv found")

    r = run_cmd("node --version", capture_output=True, shell=True)
    if r.returncode == 0:
        ok(f"Node.js: {r.stdout.strip()}")
    else:
        fail("Node.js not found. Install from https://nodejs.org/")
        all_ok = False

    r = run_cmd("npm --version", capture_output=True, shell=True)
    if r.returncode == 0:
        ok(f"npm: {r.stdout.strip()}")
    else:
        fail("npm not found")
        all_ok = False

    return all_ok


def install_deps():
    title("2. Installing dependencies")

    info("Checking backend dependencies...")
    r = run_cmd(f'"{VENV_PYTHON}" -m pip show django', capture_output=True, shell=True, cwd=BACKEND_DIR)
    if r.returncode != 0:
        warn("Installing backend dependencies...")
        r = run_cmd(
            f'"{VENV_PYTHON}" -m pip install -r requirements/dev.txt',
            cwd=BACKEND_DIR, capture_output=False, shell=True,
        )
        if r.returncode == 0:
            ok("Backend dependencies installed")
        else:
            fail("Failed to install backend dependencies")
            return False
    else:
        ok("Backend dependencies already installed")

    info("Checking frontend dependencies...")
    if not (FRONTEND_DIR / "node_modules").exists():
        warn("Installing frontend dependencies...")
        r = run_cmd("npm install", cwd=FRONTEND_DIR)
        if r.returncode == 0:
            ok("Frontend dependencies installed")
        else:
            fail("Failed to install frontend dependencies")
            return False
    else:
        ok("Frontend dependencies already installed")

    return True


def setup_backend():
    title("3. Setting up backend")

    env_file = BACKEND_DIR / ".env"
    if not env_file.exists():
        warn("Creating .env from example...")
        example = BACKEND_DIR / ".env.example"
        if example.exists():
            shutil.copy(str(example), str(env_file))
            ok(".env created")
        else:
            fail(".env.example not found")
            return False
    else:
        ok(".env found")

    info("Running migrations...")
    r = run_cmd(f'"{VENV_PYTHON}" manage.py migrate', cwd=BACKEND_DIR, shell=True)
    if r.returncode == 0:
        ok("Migrations applied")
    else:
        fail("Migration error")
        return False

    info("Loading initial data...")
    r = run_cmd(
        f'"{VENV_PYTHON}" manage.py loaddata fixtures/initial_data.json',
        cwd=BACKEND_DIR, shell=True,
    )
    if r.returncode == 0:
        ok("Initial data loaded")
    else:
        warn("Data already loaded or error (non-critical)")

    return True


def setup_frontend():
    title("4. Setting up frontend")

    env_file = FRONTEND_DIR / ".env"
    if not env_file.exists():
        warn("Creating frontend/.env...")
        example = FRONTEND_DIR / ".env.example"
        if example.exists():
            shutil.copy(str(example), str(env_file))
            ok("frontend/.env created")
        else:
            env_file.write_text("VITE_API_URL=http://localhost:8000/api/v1\n")
            ok("frontend/.env created")
    else:
        ok("frontend/.env found")

    return True


def check_ports():
    title("5. Checking ports")

    if not is_port_free(BACKEND_HOST, BACKEND_PORT):
        warn(f"Port {BACKEND_PORT} is busy. Killing process...")
        kill_port_process(BACKEND_PORT)
        time.sleep(1)

    if not is_port_free(FRONTEND_HOST, FRONTEND_PORT):
        warn(f"Port {FRONTEND_PORT} is busy. Killing process...")
        kill_port_process(FRONTEND_PORT)
        time.sleep(1)

    ok(f"Port {BACKEND_PORT} is free")
    ok(f"Port {FRONTEND_PORT} is free")
    return True


def start_servers():
    title("6. Starting servers")

    info("Starting Django backend...")
    backend_env = os.environ.copy()
    backend_env["PYTHONUNBUFFERED"] = "1"
    backend_cmd = f'"{VENV_PYTHON}" manage.py runserver {BACKEND_HOST}:{BACKEND_PORT}'
    backend = run_bg(backend_cmd, cwd=BACKEND_DIR, env_extra=backend_env)
    threading.Thread(target=stream_output, args=(backend, "Backend"), daemon=True).start()

    if wait_for_port(BACKEND_HOST, BACKEND_PORT, timeout=20):
        ok(f"Backend running: http://{BACKEND_HOST}:{BACKEND_PORT}")
    else:
        fail("Backend did not start within 20 seconds")
        return False

    info("Starting Vite frontend...")
    frontend_cmd = "npx vite --port " + str(FRONTEND_PORT) + " --host " + FRONTEND_HOST
    frontend = run_bg(frontend_cmd, cwd=FRONTEND_DIR)
    threading.Thread(target=stream_output, args=(frontend, "Frontend"), daemon=True).start()

    if wait_for_port(FRONTEND_HOST, FRONTEND_PORT, timeout=20):
        ok(f"Frontend running: http://{FRONTEND_HOST}:{FRONTEND_PORT}")
    else:
        fail("Frontend did not start within 20 seconds")
        return False

    return True


def verify():
    title("7. Verifying services")

    import urllib.request

    try:
        resp = urllib.request.urlopen(
            f"http://{BACKEND_HOST}:{BACKEND_PORT}/api/v1/services/service-categories/",
            timeout=5,
        )
        if resp.status == 200:
            ok("API /api/v1/services/service-categories/ - OK")
        else:
            fail(f"API returned status {resp.status}")
    except Exception as e:
        fail(f"API not accessible: {e}")

    try:
        resp = urllib.request.urlopen(
            f"http://{FRONTEND_HOST}:{FRONTEND_PORT}/",
            timeout=5,
        )
        if resp.status == 200:
            ok("Frontend / - OK")
        else:
            fail(f"Frontend returned status {resp.status}")
    except Exception as e:
        fail(f"Frontend not accessible: {e}")

    return True


def main():
    title("Beauty Salon - Development Server")
    print(f"  Project: {PROJECT_ROOT}")
    print(f"  Backend: http://{BACKEND_HOST}:{BACKEND_PORT}")
    print(f"  Frontend: http://{FRONTEND_HOST}:{FRONTEND_PORT}")

    steps = [
        ("Prerequisites", check_prerequisites),
        ("Dependencies", install_deps),
        ("Backend setup", setup_backend),
        ("Frontend setup", setup_frontend),
        ("Port check", check_ports),
        ("Start servers", start_servers),
        ("Verification", verify),
    ]

    for name, fn in steps:
        if not fn():
            fail(f"Step '{name}' failed. Aborting.")
            kill_all()
            return

    end_msg("All services started successfully!")
    print(f"  {CYAN}Frontend:{RESET}  http://{FRONTEND_HOST}:{FRONTEND_PORT}")
    print(f"  {CYAN}API:{RESET}       http://{BACKEND_HOST}:{BACKEND_PORT}/api/v1/")
    print(f"  {CYAN}Swagger:{RESET}   http://{BACKEND_HOST}:{BACKEND_PORT}/api/docs/swagger/")
    print(f"  {CYAN}Admin:{RESET}     http://{BACKEND_HOST}:{BACKEND_PORT}/admin/")
    print(f"\n  Press {YELLOW}Ctrl+C{RESET} to stop.\n")

    try:
        while True:
            time.sleep(1)
            for p in processes:
                if p.poll() is not None:
                    fail(f"Process exited with code {p.returncode}")
                    kill_all()
    except KeyboardInterrupt:
        kill_all()


if __name__ == "__main__":
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    main()
