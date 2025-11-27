"""Script to start all services for the Light AI Model Evaluation Platform."""

import os
import sys
import subprocess
import time
import signal
import threading

# Global variables to track processes
processes = []
stop_event = threading.Event()

def signal_handler(sig, frame):
    """Handle termination signals."""
    print("\nShutting down services...")
    stop_event.set()
    
    # Terminate all processes
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    
    print("All services stopped.")
    sys.exit(0)

def start_backend():
    """Start the backend service."""
    print("Starting backend service...")
    os.chdir("backend")
    backend_process = subprocess.Popen([sys.executable, "main.py"])
    os.chdir("..")
    processes.append(backend_process)
    return backend_process

def start_frontend():
    """Start the frontend service."""
    print("Starting frontend service...")
    os.chdir("eval-ui")
    frontend_process = subprocess.Popen(["npm", "run", "dev"])
    os.chdir("..")
    processes.append(frontend_process)
    return frontend_process

def wait_for_services():
    """Wait for services to be ready."""
    print("Waiting for services to start...")
    time.sleep(10)  # Give some time for services to start
    
    # Check if services are running
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✓ Backend service is running")
        else:
            print("✗ Backend service is not responding correctly")
    except Exception as e:
        print(f"✗ Backend service is not accessible: {e}")
    
    print("Services started. Visit http://localhost:5173 for the frontend and http://localhost:8000 for the backend.")

def main():
    """Main function to start all services."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Light AI Model Evaluation Platform - Start All Services")
    print("=" * 60)
    
    try:
        # Start backend service
        backend_process = start_backend()
        
        # Start frontend service
        frontend_process = start_frontend()
        
        # Wait for services to be ready
        wait_for_services()
        
        print("\nPress Ctrl+C to stop all services")
        
        # Wait indefinitely or until stop event
        while not stop_event.is_set():
            time.sleep(1)
            
    except Exception as e:
        print(f"Error starting services: {e}")
        signal_handler(None, None)

if __name__ == "__main__":
    main()