import customtkinter
import queue
import threading
import logging
import tkinter as tk

class ConsoleWidget(customtkinter.CTkTextbox):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configure text widget
        self.configure(
            height=150,  # Fixed height for bottom panel
            wrap="word",
            font=("Courier", 12),
            state="disabled"
        )
        
        # Get the underlying tkinter Text widget
        self.text = self._textbox
        
        # Setup text tags for different message types
        self.text.tag_configure("error", foreground="red")
        self.text.tag_configure("warning", foreground="orange")
        self.text.tag_configure("info", foreground="white")
        self.text.tag_configure("success", foreground="green")
        
        # Message queue and processing
        self.msg_queue = queue.Queue()
        self.queue_processor = threading.Thread(target=self._process_queue, daemon=True)
        self.queue_processor.start()
        
        # Maximum number of lines to keep
        self.max_lines = 1000
        
    def write(self, text, level="info"):
        """Thread-safe method to write to the console."""
        self.msg_queue.put((text, level))
        
    def _process_queue(self):
        """Process messages from the queue and update the widget."""
        while True:
            try:
                text, level = self.msg_queue.get()
                self._update_widget(text, level)
                self.msg_queue.task_done()
            except queue.Empty:
                continue
                
    def _update_widget(self, text, level):
        """Update the text widget with the message."""
        self.configure(state="normal")
        
        # Add the text with appropriate tag
        self.text.insert("end", text, level)
        
        # Trim old lines if necessary
        lines = self.text.get("1.0", "end").split("\n")
        if len(lines) > self.max_lines:
            self.text.delete("1.0", f"{len(lines) - self.max_lines}.0")
        
        # Auto-scroll to the bottom
        self.text.see("end")
        self.configure(state="disabled")
        
    def flush(self):
        """Required for stdout compatibility."""
        pass
        
class ConsoleLogHandler(logging.Handler):
    """Custom logging handler that writes to our console widget."""
    def __init__(self, console_widget):
        super().__init__()
        self.console = console_widget
        
    def emit(self, record):
        msg = self.format(record)
        level = record.levelname.lower()
        self.console.write(f"{msg}\n", level) 