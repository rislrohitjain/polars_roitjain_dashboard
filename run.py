# run.py
import os
import sys
import signal
import subprocess
from pathlib import Path

def start_pipeline():
    print("🚀 Initializing Ultra-Fast Performance Pipelines...")
    
    # Resolve absolute paths to prevent directory execution mismatch
    root_dir = Path(__file__).parent.resolve()
    app_path = root_dir / "app.py"
    
    # Configure environment variables for optimal performance
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root_dir)
    
    # Vercel bypass: If running in a production serverless env, do not spin up local daemons
    if os.getenv("VERCEL") == "1":
        print("⚠️ Vercel environment detected. Skipping local process orchestration.")
        return

    # Fire up API and UI in concurrent subprocesses natively
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.index:app", "--port", "8000", "--host", "127.0.0.1"],
        cwd=str(root_dir),
        env=env
    )
    
    ui_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", "8501", "--server.headless", "true"],
        cwd=str(root_dir),
        env=env
    )
    
    try:
        # Keep the main process alive while children run
        api_process.wait()
        ui_process.wait()
    except KeyboardInterrupt:
        print("\nStopping analytics services gracefully...")
    finally:
        # Hard cleanup loop to prevent port allocation locking (EADDRINUSE)
        for process, name in [(api_process, "FastAPI"), (ui_process, "Streamlit")]:
            if process.poll() is None:  # If process is still active
                try:
                    if sys.platform == "win32":
                        process.terminate()
                    else:
                        os.kill(process.pid, signal.SIGTERM)
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()  # Force kill if graceful termination hangs
                    print(f"⚠️ {name} process forced to stop.")
        print("🏁 All processes terminated cleanly.")

if __name__ == "__main__":
    start_pipeline()