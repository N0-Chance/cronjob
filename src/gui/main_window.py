import customtkinter
import sys
import threading
import asyncio
import subprocess
import os
from .tabs.settings_tab import SettingsTab
from .tabs.profile_tab import ProfileTab
from .tabs.database_tab import DatabaseTab
from .components.console import ConsoleWidget, ConsoleLogHandler
from .components.pipeline_control import PipelineControl
import logging

class MainWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Job Application Pipeline")
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)  # Main content area
        self.grid_rowconfigure(1, weight=0)  # Bottom panel
        self.grid_columnconfigure(1, weight=1)  # Main panel
        
        # Create main layout components
        self.setup_left_panel()
        self.setup_main_panel()
        self.setup_bottom_panel()
        
        # Initialize pipeline control variables
        self.pipeline_process = None
        
        # Setup logging
        self.setup_logging()

    def setup_left_panel(self):
        # Left panel for tab selection
        self.left_panel = customtkinter.CTkFrame(self, width=200)
        self.left_panel.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=5, pady=5)
        self.left_panel.grid_propagate(False)
        
        # Tab buttons
        self.settings_button = customtkinter.CTkButton(
            self.left_panel, text="Settings", command=lambda: self.show_tab("settings")
        )
        self.settings_button.pack(pady=5, padx=5, fill="x")
        
        self.profile_button = customtkinter.CTkButton(
            self.left_panel, text="Profile", command=lambda: self.show_tab("profile")
        )
        self.profile_button.pack(pady=5, padx=5, fill="x")
        
        self.database_button = customtkinter.CTkButton(
            self.left_panel, text="Database", command=lambda: self.show_tab("database")
        )
        self.database_button.pack(pady=5, padx=5, fill="x")

    def setup_main_panel(self):
        # Main content area
        self.main_panel = customtkinter.CTkFrame(self)
        self.main_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Initialize tabs
        self.tabs = {
            "settings": SettingsTab(self.main_panel),
            "profile": ProfileTab(self.main_panel),
            "database": DatabaseTab(self.main_panel)
        }
        
        # Show default tab
        self.show_tab("settings")

    def setup_bottom_panel(self):
        # Bottom panel for console and controls
        self.bottom_panel = customtkinter.CTkFrame(self)
        self.bottom_panel.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Pipeline control
        self.pipeline_control = PipelineControl(self.bottom_panel)
        self.pipeline_control.pack(side="left", padx=5, pady=5)
        
        # Console output
        self.console = ConsoleWidget(self.bottom_panel)
        self.console.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Redirect stdout to console
        sys.stdout = self.console

    def show_tab(self, tab_name):
        # Hide all tabs
        for tab in self.tabs.values():
            tab.pack_forget()
        
        # Show selected tab
        self.tabs[tab_name].pack(fill="both", expand=True)
        
        # Update button states
        self.settings_button.configure(state="disabled" if tab_name == "settings" else "normal")
        self.profile_button.configure(state="disabled" if tab_name == "profile" else "normal")
        self.database_button.configure(state="disabled" if tab_name == "database" else "normal")

    def setup_logging(self):
        """Setup logging to use our console widget."""
        handler = ConsoleLogHandler(self.console)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)

    def start_pipeline(self):
        """Start the pipeline process."""
        if self.pipeline_process is None:
            try:
                self.pipeline_process = subprocess.Popen(
                    ["python", "main.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                logging.info("Pipeline started successfully")
            except Exception as e:
                logging.error(f"Failed to start pipeline: {str(e)}")
                
    def stop_pipeline(self):
        """Stop the pipeline process."""
        if self.pipeline_process is not None:
            try:
                self.pipeline_process.terminate()
                self.pipeline_process = None
                logging.info("Pipeline stopped successfully")
            except Exception as e:
                logging.error(f"Failed to stop pipeline: {str(e)}")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop() 