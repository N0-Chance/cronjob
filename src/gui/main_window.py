import customtkinter
import sys
import threading
import asyncio
import subprocess
import os
from .tabs.settings_tab import SettingsTab
from .tabs.profile_tab import ProfileTab
from .tabs.database_tab import DatabaseTab
from .tabs.input_tab import InputTab
from .tabs.help_tab import HelpTab
from .components.console import ConsoleWidget, ConsoleLogHandler
from .components.pipeline_control import PipelineControl
import logging
from src.updater import is_update_available, perform_update
from tkinter import messagebox
from src.gui.utils.config import QUOTES, ConfigManager
from .setup_wizard import SetupWizard

customtkinter.set_appearance_mode("dark")

class MainWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Initialize config manager
        self.config = ConfigManager()

        # Load version number
        with open("version.txt", "r") as f:
            self.version = f.read().strip()

        # Check if setup is completed
        if not self.config.get("SETUP_COMPLETED", False):
            self.run_setup_wizard()

        # Set the window icon
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "cronjob.ico")
        self.iconbitmap(icon_path)
        
        # Configure window
        self.title("cronjob: Resume and Cover Letter Writer")
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # Add motivational quotes bar at the top
        self.quotes_label = customtkinter.CTkLabel(self, text="", font=("Arial", 14))
        self.quotes_label.grid(row=0, column=0, columnspan=3, sticky="ew", padx=(180, 5), pady=5)

        # Configure grid layout
        self.grid_rowconfigure(1, weight=1)  # Main content area
        self.grid_rowconfigure(2, weight=0)  # Bottom panel
        self.grid_columnconfigure(1, weight=1)  # Main panel
        
        # Create main layout components
        self.setup_left_panel()
        self.setup_main_panel()
        self.setup_bottom_panel()
        
        # Initialize pipeline control variables
        self.pipeline_process = None
        
        # Setup logging
        self.setup_logging()
        
        # Start periodic console update
        self.after(100, self.update_console)

        # Check for updates after 1500ms
        self.after(1500, self.check_for_updates)

        # Check if quotes are enabled
        if self.config.get("QUOTES_ENABLED", True):  # Default to True
            self.display_random_quote()
            self.schedule_quote_change()

    def setup_left_panel(self):
        # Left panel for tab selection
        self.left_panel = customtkinter.CTkFrame(self, width=200)
        self.left_panel.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=5, pady=5)
        self.left_panel.grid_propagate(False)

        # Tab buttons
        self.input_button = customtkinter.CTkButton(
            self.left_panel, text="Input", command=lambda: self.show_tab("input")
        )
        self.input_button.pack(pady=5, padx=5, fill="x")
        
        self.profile_button = customtkinter.CTkButton(
            self.left_panel, text="Profile", command=lambda: self.show_tab("profile")
        )
        self.profile_button.pack(pady=5, padx=5, fill="x")
        
        self.database_button = customtkinter.CTkButton(
            self.left_panel, text="Database", command=lambda: self.show_tab("database")
        )
        self.database_button.pack(pady=5, padx=5, fill="x")

        self.settings_button = customtkinter.CTkButton(
            self.left_panel, text="Settings", command=lambda: self.show_tab("settings")
        )
        self.settings_button.pack(pady=5, padx=5, fill="x")

        self.help_button = customtkinter.CTkButton(
            self.left_panel, text="Help", command=lambda: self.show_tab("help")
        )
        self.help_button.pack(pady=5, padx=5, fill="x")

        self.outputs_button = customtkinter.CTkButton(
            self.left_panel, text="Output Folder", command=self.open_outputs_folder
        )
        self.outputs_button.pack(pady=20, padx=5, fill="x", side="bottom", anchor="s")

    def setup_main_panel(self):
        # Main content area
        self.main_panel = customtkinter.CTkFrame(self)
        self.main_panel.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        # Initialize tabs
        self.tabs = {
            "input": InputTab(self.main_panel),
            "profile": ProfileTab(self.main_panel),
            "database": DatabaseTab(self.main_panel),
            "settings": SettingsTab(self.main_panel, self),
            "help": HelpTab(self.main_panel)
        }
        
        # Show default tab
        self.show_tab("input")

    def setup_bottom_panel(self):
        # Bottom panel for console and controls
        self.bottom_panel = customtkinter.CTkFrame(self)
        self.bottom_panel.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Left frame for pipeline control and version
        self.left_bottom_frame = customtkinter.CTkFrame(self.bottom_panel, fg_color="transparent")
        self.left_bottom_frame.pack(side="left", padx=5, pady=5, anchor="sw")

        # Pipeline control
        self.pipeline_control = PipelineControl(self.left_bottom_frame)
        self.pipeline_control.pack(side="top", padx=5, pady=(5, 0))

        # Version label
        self.version_label = customtkinter.CTkLabel(
            self.left_bottom_frame, 
            text=f"v {self.version}",
            font=("Arial", 10)
        )
        self.version_label.pack(side="top", padx=5, pady=(2, 5))
        
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
        self.input_button.configure(state="disabled" if tab_name == "input" else "normal")
        self.help_button.configure(state="disabled" if tab_name == "help" else "normal")

    def setup_logging(self):
        """Setup logging to use our console widget."""
        handler = ConsoleLogHandler(self.console)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)

    def update_console(self):
        """Periodically update the console with pipeline output."""
        if hasattr(self, 'pipeline_control'):
            self.pipeline_control.update_console()
        # Schedule next update
        self.after(100, self.update_console)

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

    def open_outputs_folder(self):
        outputs_path = os.path.join(os.path.dirname(__file__), "..", "..", "output")
        if not os.path.exists(outputs_path):
            os.makedirs(outputs_path)
        subprocess.Popen(f'explorer \"{outputs_path}\"')

    def check_for_updates(self):
        local, latest, is_new = is_update_available()
        if is_new:
            response = messagebox.askyesno(
                "Update Available",
                f"A new version is available.\n\nLocal: {local}\nLatest: {latest}\n\nUpdate now?"
            )
            if response:
                msg = perform_update()
                messagebox.showinfo("Updater", msg)

    def display_random_quote(self):
        import random
        quote = random.choice(QUOTES)
        self.quotes_label.configure(text=quote)
        self.quotes_label.grid()  # Ensure the label is visible

    def hide_quotes_bar(self):
        self.quotes_label.grid_remove()  # Hide the label when quotes are disabled

    def schedule_quote_change(self):
        if self.config.get("QUOTES_ENABLED", True):
            self.after(60000, self.change_quote)  # Schedule every 60 seconds

    def change_quote(self):
        self.display_random_quote()
        self.schedule_quote_change()

    def run_setup_wizard(self):
        """Run the setup wizard for first-time setup."""
        wizard = SetupWizard(self)
        self.wait_window(wizard)

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop() 