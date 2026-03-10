import os
import sys
import subprocess

if __name__ == "__main__":
    print("Redirecting to backend to run Sigma AI Agent...")
    
    # Resolve absolute path to backend directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, "backend")
    
    if not os.path.exists(backend_dir):
        print(f"Error: Could not find backend directory at {backend_dir}")
        sys.exit(1)
        
    print(f"Changing directory to: {backend_dir}")
    os.chdir(backend_dir)
    
    # Run uvicorn server just like the tasks and scripts do
    cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    
    print(f"Executing: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nSigma AI Agent stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
