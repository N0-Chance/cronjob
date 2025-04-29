#!/usr/bin/env python
import os
import sys
import subprocess
import importlib
import logging

def main():
    """
    Launcher script for the cronjob application.
    Sets up proper paths and environment variables before running the main script.
    """
    # Get base directory (where this script is located)
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Check if we're running in a packaged environment
    is_frozen = getattr(sys, 'frozen', False)
    
    # Set up environment
    env = {
        **os.environ,
        "PYTHONPATH": base_dir,
        "DB_PATH": os.path.join(base_dir, "db", "data.db"),
        "PYTHONUNBUFFERED": "1"
    }
    
    # Set environment variables for the current process too
    for key, value in env.items():
        os.environ[key] = value
    
    # Define main script path
    main_script = os.path.join(base_dir, "src", "main.py")
    
    # Print information
    print(f"Starting cronjob from {base_dir}")
    print(f"Running script at {main_script}")
    print(f"PYTHONPATH set to {env['PYTHONPATH']}")
    
    # If we're in a packaged environment OR this script is being called with a special flag
    if is_frozen or "--internal-run" in sys.argv:
        print("Running in direct mode (packaged environment or internal call)")
        try:
            # Add the base directory to the Python path
            if base_dir not in sys.path:
                sys.path.insert(0, base_dir)
            
            # Try to import and run the main function directly
            try:
                # Try importing the src.main module directly
                from src.main import main as run_main
                import asyncio
                
                # Run the main function directly
                print("Starting main function directly")
                asyncio.run(run_main())
                return 0
            except ImportError as e:
                print(f"Import error: {e}")
                # If that fails, try executing the main.py file directly
                if os.path.exists(main_script):
                    print(f"Executing {main_script} directly")
                    with open(main_script, 'r') as f:
                        # Read and modify the script to handle imports
                        script_content = f.read()
                        
                        # Execute in a namespace to isolate variables
                        namespace = {'__file__': main_script}
                        exec(script_content, namespace)
                        return 0
                else:
                    print(f"Main script not found at {main_script}")
                    return 1
        except Exception as e:
            print(f"Error running main directly: {e}")
            return 1
    else:
        # In development mode, launch as a separate process with the special flag
        cmd = [sys.executable, __file__, "--internal-run"]
        print(f"Launching in subprocess mode: {cmd}")
        return subprocess.call(cmd, env=env, cwd=base_dir)

if __name__ == "__main__":
    sys.exit(main()) 