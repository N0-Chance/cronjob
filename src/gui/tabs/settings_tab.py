import customtkinter
import os
from ..utils.config import ConfigManager

class SettingsTab(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Initialize config manager
        self.config = ConfigManager()
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        
        # Create sections
        self.setup_api_settings()
        self.setup_email_settings()
        self.setup_model_settings()
        self.setup_save_button()
        
    def setup_api_settings(self):
        # API Settings Section
        label = customtkinter.CTkLabel(self, text="API Settings", font=("Arial", 16, "bold"))
        label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 10))
        
        # OpenAI API Key
        customtkinter.CTkLabel(self, text="OpenAI API Key:").grid(
            row=1, column=0, sticky="w", padx=10, pady=5
        )
        self.openai_key = customtkinter.CTkEntry(self, width=400, show="*")
        self.openai_key.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        self.openai_key.insert(0, self.config.get("OPENAI_API_KEY", ""))
        
        # Show/Hide API Key
        self.show_api_key = customtkinter.CTkButton(
            self, text="Show", width=60,
            command=lambda: self.toggle_key_visibility(self.openai_key)
        )
        self.show_api_key.grid(row=1, column=2, padx=5, pady=5)
        
    def setup_email_settings(self):
        # Email Settings Section
        label = customtkinter.CTkLabel(self, text="Email Settings", font=("Arial", 16, "bold"))
        label.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 10))
        
        # SMTP Server
        customtkinter.CTkLabel(self, text="SMTP Server:").grid(
            row=3, column=0, sticky="w", padx=10, pady=5
        )
        self.smtp_server = customtkinter.CTkEntry(self, width=400)
        self.smtp_server.grid(row=3, column=1, sticky="ew", padx=10, pady=5)
        self.smtp_server.insert(0, self.config.get("SMTP_SERVER", ""))
        
        # SMTP Port
        customtkinter.CTkLabel(self, text="SMTP Port:").grid(
            row=4, column=0, sticky="w", padx=10, pady=5
        )
        self.smtp_port = customtkinter.CTkEntry(self, width=400)
        self.smtp_port.grid(row=4, column=1, sticky="ew", padx=10, pady=5)
        self.smtp_port.insert(0, self.config.get("SMTP_PORT", ""))
        
        # Email From
        customtkinter.CTkLabel(self, text="Email From:").grid(
            row=5, column=0, sticky="w", padx=10, pady=5
        )
        self.email_from = customtkinter.CTkEntry(self, width=400)
        self.email_from.grid(row=5, column=1, sticky="ew", padx=10, pady=5)
        self.email_from.insert(0, self.config.get("EMAIL_FROM", ""))
        
        # Email To
        customtkinter.CTkLabel(self, text="Email To:").grid(
            row=6, column=0, sticky="w", padx=10, pady=5
        )
        self.email_to = customtkinter.CTkEntry(self, width=400)
        self.email_to.grid(row=6, column=1, sticky="ew", padx=10, pady=5)
        self.email_to.insert(0, self.config.get("EMAIL_TO", ""))
        
        # SMTP Username
        customtkinter.CTkLabel(self, text="SMTP Username:").grid(
            row=7, column=0, sticky="w", padx=10, pady=5
        )
        self.smtp_username = customtkinter.CTkEntry(self, width=400)
        self.smtp_username.grid(row=7, column=1, sticky="ew", padx=10, pady=5)
        self.smtp_username.insert(0, self.config.get("SMTP_USERNAME", ""))
        
        # SMTP Password
        customtkinter.CTkLabel(self, text="SMTP Password:").grid(
            row=8, column=0, sticky="w", padx=10, pady=5
        )
        self.smtp_password = customtkinter.CTkEntry(self, width=400, show="*")
        self.smtp_password.grid(row=8, column=1, sticky="ew", padx=10, pady=5)
        self.smtp_password.insert(0, self.config.get("SMTP_PASSWORD", ""))
        
        # Show/Hide SMTP Password
        self.show_smtp_pass = customtkinter.CTkButton(
            self, text="Show", width=60,
            command=lambda: self.toggle_key_visibility(self.smtp_password)
        )
        self.show_smtp_pass.grid(row=8, column=2, padx=5, pady=5)
        
    def setup_model_settings(self):
        # Model Settings Section
        label = customtkinter.CTkLabel(self, text="Model Settings", font=("Arial", 16, "bold"))
        label.grid(row=9, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 10))
        
        # Writer Model
        customtkinter.CTkLabel(self, text="Writer Model:").grid(
            row=10, column=0, sticky="w", padx=10, pady=5
        )
        self.writer_model = customtkinter.CTkEntry(self, width=400)
        self.writer_model.grid(row=10, column=1, sticky="ew", padx=10, pady=5)
        self.writer_model.insert(0, self.config.get("WRITER_MODEL", ""))
        
        # Judge Model
        customtkinter.CTkLabel(self, text="Judge Model:").grid(
            row=11, column=0, sticky="w", padx=10, pady=5
        )
        self.judge_model = customtkinter.CTkEntry(self, width=400)
        self.judge_model.grid(row=11, column=1, sticky="ew", padx=10, pady=5)
        self.judge_model.insert(0, self.config.get("JUDGE_MODEL", ""))
        
        # Agent Model
        customtkinter.CTkLabel(self, text="Agent Model:").grid(
            row=12, column=0, sticky="w", padx=10, pady=5
        )
        self.agent_model = customtkinter.CTkEntry(self, width=400)
        self.agent_model.grid(row=12, column=1, sticky="ew", padx=10, pady=5)
        self.agent_model.insert(0, self.config.get("AGENT_MODEL", ""))
        
    def setup_save_button(self):
        # Save Button
        self.save_button = customtkinter.CTkButton(
            self, text="Save Settings", command=self.save_settings,
            width=200
        )
        self.save_button.grid(row=13, column=0, columnspan=2, pady=20)
        
    def toggle_key_visibility(self, entry_widget):
        """Toggle between showing and hiding sensitive information."""
        if entry_widget.cget("show") == "":
            entry_widget.configure(show="*")
            if entry_widget == self.openai_key:
                self.show_api_key.configure(text="Show")
            else:
                self.show_smtp_pass.configure(text="Show")
        else:
            entry_widget.configure(show="")
            if entry_widget == self.openai_key:
                self.show_api_key.configure(text="Hide")
            else:
                self.show_smtp_pass.configure(text="Hide")
                
    def save_settings(self):
        """Save all settings to config."""
        settings = {
            "OPENAI_API_KEY": self.openai_key.get(),
            "SMTP_SERVER": self.smtp_server.get(),
            "SMTP_PORT": self.smtp_port.get(),
            "EMAIL_FROM": self.email_from.get(),
            "EMAIL_TO": self.email_to.get(),
            "SMTP_USERNAME": self.smtp_username.get(),
            "SMTP_PASSWORD": self.smtp_password.get(),
            "WRITER_MODEL": self.writer_model.get(),
            "JUDGE_MODEL": self.judge_model.get(),
            "AGENT_MODEL": self.agent_model.get()
        }
        
        try:
            self.config.save_settings(settings)
            self.show_message("Success", "Settings saved successfully!")
        except Exception as e:
            self.show_message("Error", f"Failed to save settings: {str(e)}")
            
    def show_message(self, title, message):
        """Show a popup message."""
        dialog = customtkinter.CTkInputDialog(
            text=message,
            title=title,
            button_text="OK"
        )
        dialog.get_input()  # This will show the dialog and wait for OK 