import customtkinter
from .main_window import MainWindow

def run_gui():
    """Start the GUI application."""
    # Set appearance mode and default color theme
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("blue")
    
    # Create and run main window
    app = MainWindow()
    app.mainloop() 