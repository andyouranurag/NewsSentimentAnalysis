import subprocess
import threading
import time

# Function to start FastAPI backend
def run_fastapi():
    subprocess.run(["uvicorn", "src.backend:app", "--host", "0.0.0.0", "--port", "7860"])

# Start FastAPI in a separate thread
threading.Thread(target=run_fastapi, daemon=True).start()

# Delay to allow backend to start before frontend
time.sleep(5)

# Start Streamlit frontend
subprocess.run(["streamlit", "run", "src/app.py"])
