import customtkinter
import tkinter as tk
from tkinter import ttk
import sqlite3
import pandas as pd
import json
from datetime import datetime
import os
import logging

customtkinter.set_appearance_mode("dark")

class DatabaseTableView(customtkinter.CTkFrame):
    def __init__(self, parent, table_name, db_path):
        super().__init__(parent)
        
        self.table_name = table_name
        self.db_path = db_path
        
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create widgets
        self.setup_toolbar()
        self.setup_treeview()
        
        # Start auto-refresh
        self.after(5000, self.refresh_data)  # Refresh every 5 seconds
        
    def setup_toolbar(self):
        toolbar = customtkinter.CTkFrame(self)
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Refresh button
        refresh_btn = customtkinter.CTkButton(
            toolbar,
            text="Refresh",
            command=self.refresh_data,
            width=100
        )
        refresh_btn.pack(side="left", padx=5)
        
        # Export button
        export_btn = customtkinter.CTkButton(
            toolbar,
            text="Export CSV",
            command=self.export_csv,
            width=100
        )
        export_btn.pack(side="left", padx=5)
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.filter_data())
        search_entry = customtkinter.CTkEntry(
            toolbar,
            placeholder_text="Search...",
            textvariable=self.search_var,
            width=200
        )
        search_entry.pack(side="right", padx=5)
        
    def setup_treeview(self):
        # Create treeview with scrollbars
        container = ttk.Frame(self)
        container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure container style
        style = ttk.Style()
        style.configure("Container.TFrame", background="white")
        container.configure(style="Container.TFrame")
        
        # Configure scrollbar style
        style.configure("Vertical.TScrollbar", 
            background="white", 
            troughcolor="white",
            arrowcolor="black",
            bordercolor="white"
        )
        style.configure("Horizontal.TScrollbar",
            background="white",
            troughcolor="white",
            arrowcolor="black",
            bordercolor="white"
        )
        
        # Configure treeview style
        style.configure(
            "Treeview",
            background="white",
            foreground="black",
            fieldbackground="white",
            selectbackground="#4a4a4a",
            selectforeground="black",
            rowheight=25
        )
        
        # Configure the headings
        style.configure(
            "Treeview.Heading",
            background="white",
            foreground="black",
            relief="flat"
        )
        
        # Configure selection colors
        style.map("Treeview",
            background=[("selected", "#4a4a4a"), ("!selected", "white")],
            foreground=[("selected", "black"), ("!selected", "black")]
        )
        
        style.map("Treeview.Heading",
            background=[("active", "#3c3c3c"), ("!active", "white")],
            foreground=[("active", "black"), ("!active", "black")]
        )
        
        # Create scrollbars
        y_scroll = ttk.Scrollbar(container, orient="vertical", style="Vertical.TScrollbar")
        x_scroll = ttk.Scrollbar(container, orient="horizontal", style="Horizontal.TScrollbar")
        
        # Create treeview
        self.tree = ttk.Treeview(
            container,
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )
        
        # Configure scrollbars
        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)
        
        # Layout
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Bind double-click event
        self.tree.bind("<Double-1>", self.show_details)
        
        # Initial data load
        self.refresh_data()
        
    def refresh_data(self):
        """Fetch fresh data from database and update display."""
        try:
            conn = sqlite3.connect(self.db_path)
            query = f"SELECT * FROM {self.table_name} ORDER BY id DESC"
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Clear existing items
            self.tree.delete(*self.tree.get_children())
            
            # Configure columns
            self.tree["columns"] = list(df.columns)
            self.tree["show"] = "headings"
            
            for column in df.columns:
                self.tree.heading(column, text=column)
                # Set column width based on content
                max_width = max(
                    len(str(column)),
                    df[column].astype(str).str.len().max() if len(df) > 0 else 0
                )
                self.tree.column(column, width=min(max_width * 10, 300))
            
            # Add data
            for idx, row in df.iterrows():
                values = []
                for value in row:
                    if isinstance(value, (dict, list)):
                        values.append(json.dumps(value, indent=2))
                    else:
                        values.append(str(value))
                self.tree.insert("", "end", values=values)
                
        except Exception as e:
            print(f"Error refreshing {self.table_name} data: {str(e)}")
            
        # Schedule next refresh
        self.after(5000, self.refresh_data)
        
    def filter_data(self):
        """Filter treeview based on search text."""
        search_text = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            if not search_text:  # Show all items if search is empty
                self.tree.reattach(item, "", "end")
                continue
                
            values = [str(v).lower() for v in self.tree.item(item)["values"]]
            if any(search_text in value for value in values):
                self.tree.reattach(item, "", "end")
            else:
                self.tree.detach(item)
                
    def export_csv(self):
        """Export current view to CSV."""
        try:
            # Get current time for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.table_name}_{timestamp}.csv"
            
            # Get visible items only
            visible_items = []
            for item in self.tree.get_children():
                visible_items.append(self.tree.item(item)["values"])
                
            # Create DataFrame and save
            columns = self.tree["columns"]
            df = pd.DataFrame(visible_items, columns=columns)
            df.to_csv(filename, index=False)
            print(f"Exported to {filename}")
            
            # Create outputs directory if it doesn't exist
            outputs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "outputs")
            os.makedirs(outputs_dir, exist_ok=True)
            
            # Save to CSV
            csv_path = os.path.join(outputs_dir, f"{self.table_name}.csv")
            df.to_csv(csv_path, index=False)
            
            logging.info(f"Table exported to {csv_path}")
            
        except Exception as e:
            print(f"Error exporting CSV: {str(e)}")
            
    def show_details(self, event):
        """Show detailed view of selected row."""
        item = self.tree.selection()[0]
        values = self.tree.item(item)["values"]
        columns = self.tree["columns"]
        
        # Create details window
        details_window = tk.Toplevel(self)
        details_window.title(f"{self.table_name} Details")
        details_window.geometry("600x400")
        
        # Create text widget
        text = customtkinter.CTkTextbox(details_window)
        text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Format and display data
        text.insert("end", f"=== {self.table_name} Details ===\n\n")
        for col, val in zip(columns, values):
            # Try to pretty print JSON fields
            try:
                if isinstance(val, str) and (val.startswith("{") or val.startswith("[")):
                    val = json.dumps(json.loads(val), indent=2)
            except:
                pass
            text.insert("end", f"{col}:\n{val}\n\n")
            
        text.configure(state="disabled") 