import customtkinter
import os
from ..components.table_view import DatabaseTableView

class DatabaseTab(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Get database path
        self.db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "db",
            "data.db"
        )
        
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create widgets
        self.setup_tab_buttons()
        self.setup_table_views()
        
        # Show default table
        self.show_table("queue")
        
    def setup_tab_buttons(self):
        # Create button frame
        button_frame = customtkinter.CTkFrame(self)
        button_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Table selection buttons
        tables = [
            ("Queue", "queue"),
            ("Processing", "processing"),
            ("Processed", "processed"),
            ("Failed", "unable_to_scrape")
        ]
        
        self.buttons = {}
        for text, table_name in tables:
            btn = customtkinter.CTkButton(
                button_frame,
                text=text,
                command=lambda t=table_name: self.show_table(t),
                width=120
            )
            btn.pack(side="left", padx=5)
            self.buttons[table_name] = btn
            
    def setup_table_views(self):
        # Create table views
        self.tables = {
            "queue": DatabaseTableView(self, "queue", self.db_path),
            "processing": DatabaseTableView(self, "processing", self.db_path),
            "processed": DatabaseTableView(self, "processed", self.db_path),
            "unable_to_scrape": DatabaseTableView(self, "unable_to_scrape", self.db_path)
        }
        
        # Grid them all (they'll be hidden/shown as needed)
        for table in self.tables.values():
            table.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
            table.grid_remove()  # Hide all initially
            
    def show_table(self, table_name):
        # Hide all tables
        for table in self.tables.values():
            table.grid_remove()
            
        # Show selected table
        self.tables[table_name].grid()
        
        # Update button states
        for name, button in self.buttons.items():
            button.configure(state="disabled" if name == table_name else "normal") 