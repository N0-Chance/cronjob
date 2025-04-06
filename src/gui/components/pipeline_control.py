import customtkinter
import subprocess
import os
import signal
import sys
import logging
import sqlite3
import time
import psutil

class PipelineControl(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create start/stop button
        self.pipeline_process = None
        self.start_stop_button = customtkinter.CTkButton(
            self,
            text="Start Pipeline",
            command=self.toggle_pipeline
        )
        self.start_stop_button.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
    def toggle_pipeline(self):
        if self.pipeline_process is None:
            self.start_pipeline()
        else:
            self.stop_pipeline()
            
    def start_pipeline(self):
        try:
            # Get the absolute path to main.py based on the GUI script location
            gui_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            main_script = os.path.join(gui_dir, "main.py")
            
            # Ensure the db directory exists
            db_dir = os.path.join(gui_dir, "db")
            os.makedirs(db_dir, exist_ok=True)
            
            # Initialize the database first
            db_path = os.path.join(gui_dir, "db", "data.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create tables if they don't exist
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    status TEXT DEFAULT 'pending',
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS processing (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    job_title TEXT,
                    job_company TEXT,
                    degree TEXT,
                    degree_reason TEXT,
                    job_data JSON,
                    resume TEXT,
                    resume_pdf TEXT,
                    cover_letter TEXT,
                    cover_letter_pdf TEXT,
                    feedback TEXT,
                    status TEXT DEFAULT 'scraping',
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS processed (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    job_title TEXT,
                    job_company TEXT,
                    degree TEXT,
                    degree_reason TEXT,
                    job_data JSON,
                    resume TEXT,
                    resume_pdf TEXT,
                    cover_letter TEXT,
                    cover_letter_pdf TEXT,
                    feedback TEXT,
                    status TEXT,
                    started_at TIMESTAMP,
                    finished_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    emailed BOOLEAN DEFAULT FALSE
                );
                CREATE TABLE IF NOT EXISTS unable_to_scrape (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    error TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    job_title TEXT,
                    job_company TEXT,
                    degree TEXT,
                    degree_reason TEXT,
                    job_data JSON,
                    resume TEXT,
                    resume_pdf TEXT,
                    cover_letter TEXT,
                    cover_letter_pdf TEXT,
                    feedback TEXT,
                    submission_status TEXT,
                    started_at TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
            """)
            conn.commit()
            conn.close()
            
            # Start the process in a new console window
            if sys.platform == "win32":
                # On Windows, start Python directly in a new console window
                self.pipeline_process = subprocess.Popen(
                    ["python", main_script],
                    cwd=gui_dir,
                    env={
                        **os.environ,
                        "PYTHONPATH": gui_dir,
                        "DB_PATH": db_path
                    },
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                
                # Store the process ID for stopping later
                self.process_id = self.pipeline_process.pid
                
                # Update button state
                self.start_stop_button.configure(text="Stop Pipeline")
                logging.info("Pipeline started successfully")
                
            else:
                # On Unix-like systems, use xterm
                self.pipeline_process = subprocess.Popen(
                    ["xterm", "-e", f"cd {gui_dir} && PYTHONPATH={gui_dir} DB_PATH={db_path} python {main_script}"]
                )
                
                # Store the process ID for stopping later
                self.process_id = self.pipeline_process.pid
                
                # Update button state
                self.start_stop_button.configure(text="Stop Pipeline")
                logging.info("Pipeline started successfully")
            
        except Exception as e:
            logging.error(f"Failed to start pipeline: {str(e)}")
            
    def stop_pipeline(self):
        if self.pipeline_process is not None:
            try:
                if sys.platform == "win32":
                    # On Windows, use taskkill to terminate the process tree
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.process_id)], 
                                 capture_output=True, 
                                 text=True)
                else:
                    # On Unix-like systems
                    self.pipeline_process.terminate()
                    self.pipeline_process.wait(timeout=5)
                
                logging.info("Pipeline stopped successfully")
            except Exception as e:
                logging.error(f"Error stopping pipeline: {str(e)}")
            finally:
                # Always reset the state
                self.pipeline_process = None
                self.process_id = None
                self.start_stop_button.configure(text="Start Pipeline") 