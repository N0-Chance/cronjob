import customtkinter
import os
from ..utils.config import ConfigManager
import logging
import webbrowser

class SettingsTab(customtkinter.CTkFrame):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        
        # Store reference to main window
        self.main_window = main_window

        # Initialize config manager
        self.config = ConfigManager()
        
        # Initialize toggle variables
        self.quotes_toggle_var = customtkinter.BooleanVar()
        self.quotes_toggle_var.set(self.config.get("QUOTES_ENABLED", True))
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create scrollable frame
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Create sections inside scrollable frame
        self.setup_toggle_settings()
        self.setup_model_settings()
        self.setup_api_settings()
        self.setup_email_settings()
        self.setup_gist_settings()
        self.setup_save_button()
        
        # Add a label for messages
        self.message_label = customtkinter.CTkLabel(self.scrollable_frame, text="", font=("Arial", 12))
        self.message_label.grid(row=19, column=0, columnspan=2, pady=10)

    def setup_toggle_settings(self):
        # Toggle Settings Section
        label = customtkinter.CTkLabel(self.scrollable_frame, text="Toggle Settings", font=("Arial", 16, "bold"))
        label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 10))

        # GIST Input Toggle
        self.gist_input_var = customtkinter.BooleanVar(value=self.config.get("GIST_INPUT", False))
        self.gist_input_toggle = customtkinter.CTkCheckBox(self.scrollable_frame, text="Enable GIST Input - Requires GitHub Account (Simple)", variable=self.gist_input_var)
        self.gist_input_toggle.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        # Email Toggle
        self.email_toggle_var = customtkinter.BooleanVar(value=self.config.get("EMAIL_ENABLED", False))
        self.email_toggle = customtkinter.CTkCheckBox(self.scrollable_frame, text="Enable Email - Requires SMTP Server (Advanced)", variable=self.email_toggle_var)
        self.email_toggle.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        # Motivational Quotes Toggle
        self.quotes_toggle_var = customtkinter.BooleanVar(value=self.config.get("QUOTES_ENABLED", True))
        self.quotes_toggle = customtkinter.CTkCheckBox(self.scrollable_frame, text="Enable Motivational Quotes (Optional)", variable=self.quotes_toggle_var)
        self.quotes_toggle.grid(row=2, column=0, sticky="w", padx=10, pady=5)

        # Motivational Quotes Toggle
        self.quotes_toggle_var.trace_add('write', self.toggle_quotes_bar)

    def toggle_quotes_bar(self, *args):
        if self.quotes_toggle_var.get():
            self.main_window.display_random_quote()
        else:
            self.main_window.hide_quotes_bar()
        # Save the new state
        self.config.set("QUOTES_ENABLED", self.quotes_toggle_var.get())

    def setup_model_settings(self):
        # Model Settings Section
        label = customtkinter.CTkLabel(self.scrollable_frame, text="Model Settings", font=("Arial", 16, "bold"))
        label.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 10))
        
        # Writer Model
        customtkinter.CTkLabel(self.scrollable_frame, text="Writer Model:").grid(
            row=4, column=0, sticky="w", padx=10, pady=5
        )
        self.writer_model = customtkinter.CTkEntry(self.scrollable_frame, width=400)
        self.writer_model.grid(row=4, column=1, sticky="ew", padx=10, pady=5)
        self.writer_model.insert(0, self.config.get("WRITER_MODEL", ""))
        
        # Judge Model
        customtkinter.CTkLabel(self.scrollable_frame, text="Judge Model:").grid(
            row=5, column=0, sticky="w", padx=10, pady=5
        )
        self.judge_model = customtkinter.CTkEntry(self.scrollable_frame, width=400)
        self.judge_model.grid(row=5, column=1, sticky="ew", padx=10, pady=5)
        self.judge_model.insert(0, self.config.get("JUDGE_MODEL", ""))
        
        # For more information, visit:
        customtkinter.CTkLabel(self.scrollable_frame, text="For more information, visit:").grid(
            row=6, column=0, sticky="w", padx=10, pady=5
        )
        pricing_link_label = customtkinter.CTkLabel(self.scrollable_frame, text="Pricing", cursor="hand2")
        pricing_link_label.grid(row=6, column=1, sticky="w", padx=10, pady=5)
        pricing_link_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://platform.openai.com/docs/pricing"))

        models_link_label = customtkinter.CTkLabel(self.scrollable_frame, text="Models", cursor="hand2")
        models_link_label.grid(row=6, column=1, sticky="w", padx=60, pady=5)
        models_link_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://platform.openai.com/docs/models"))

    def setup_api_settings(self):
        # API Settings Section
        label = customtkinter.CTkLabel(self.scrollable_frame, text="API Settings", font=("Arial", 16, "bold"))
        label.grid(row=7, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 10))
        
        # OpenAI API Key
        customtkinter.CTkLabel(self.scrollable_frame, text="OpenAI API Key:").grid(
            row=8, column=0, sticky="w", padx=10, pady=5
        )
        self.openai_key = customtkinter.CTkEntry(self.scrollable_frame, width=400, show="*")
        self.openai_key.grid(row=8, column=1, sticky="ew", padx=10, pady=5)
        self.openai_key.insert(0, self.config.get("OPENAI_API_KEY", ""))
        
        # Show/Hide API Key
        self.show_api_key = customtkinter.CTkButton(
            self.scrollable_frame, text="Show", width=60,
            command=lambda: self.toggle_key_visibility(self.openai_key)
        )
        self.show_api_key.grid(row=8, column=2, padx=5, pady=5)

    def setup_email_settings(self):
        # Email Settings Section
        label = customtkinter.CTkLabel(self.scrollable_frame, text="Email Settings", font=("Arial", 16, "bold"))
        label.grid(row=9, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 10))
        
        # SMTP Server
        customtkinter.CTkLabel(self.scrollable_frame, text="SMTP Server:").grid(
            row=10, column=0, sticky="w", padx=10, pady=5
        )
        self.smtp_server = customtkinter.CTkEntry(self.scrollable_frame, width=400)
        self.smtp_server.grid(row=10, column=1, sticky="ew", padx=10, pady=5)
        self.smtp_server.insert(0, self.config.get("SMTP_SERVER", ""))
        
        # SMTP Port
        customtkinter.CTkLabel(self.scrollable_frame, text="SMTP Port:").grid(
            row=11, column=0, sticky="w", padx=10, pady=5
        )
        self.smtp_port = customtkinter.CTkEntry(self.scrollable_frame, width=400)
        self.smtp_port.grid(row=11, column=1, sticky="ew", padx=10, pady=5)
        self.smtp_port.insert(0, self.config.get("SMTP_PORT", ""))
        
        # Email From
        customtkinter.CTkLabel(self.scrollable_frame, text="Email From:").grid(
            row=12, column=0, sticky="w", padx=10, pady=5
        )
        self.email_from = customtkinter.CTkEntry(self.scrollable_frame, width=400)
        self.email_from.grid(row=12, column=1, sticky="ew", padx=10, pady=5)
        self.email_from.insert(0, self.config.get("EMAIL_FROM", ""))
        
        # Email To
        customtkinter.CTkLabel(self.scrollable_frame, text="Email To:").grid(
            row=13, column=0, sticky="w", padx=10, pady=5
        )
        self.email_to = customtkinter.CTkEntry(self.scrollable_frame, width=400)
        self.email_to.grid(row=13, column=1, sticky="ew", padx=10, pady=5)
        self.email_to.insert(0, self.config.get("EMAIL_TO", ""))
        
        # SMTP Username
        customtkinter.CTkLabel(self.scrollable_frame, text="SMTP Username:").grid(
            row=14, column=0, sticky="w", padx=10, pady=5
        )
        self.smtp_username = customtkinter.CTkEntry(self.scrollable_frame, width=400)
        self.smtp_username.grid(row=14, column=1, sticky="ew", padx=10, pady=5)
        self.smtp_username.insert(0, self.config.get("SMTP_USERNAME", ""))
        
        # SMTP Password
        customtkinter.CTkLabel(self.scrollable_frame, text="SMTP Password:").grid(
            row=15, column=0, sticky="w", padx=10, pady=5
        )
        self.smtp_password = customtkinter.CTkEntry(self.scrollable_frame, width=400, show="*")
        self.smtp_password.grid(row=15, column=1, sticky="ew", padx=10, pady=5)
        self.smtp_password.insert(0, self.config.get("SMTP_PASSWORD", ""))
        
        # Show/Hide SMTP Password
        self.show_smtp_pass = customtkinter.CTkButton(
            self.scrollable_frame, text="Show", width=60,
            command=lambda: self.toggle_key_visibility(self.smtp_password)
        )
        self.show_smtp_pass.grid(row=15, column=2, padx=5, pady=5)

    def setup_gist_settings(self):
        # GIST Settings Section
        label = customtkinter.CTkLabel(self.scrollable_frame, text="GIST Settings", font=("Arial", 16, "bold"))
        label.grid(row=16, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 10))

        # GIST ID
        customtkinter.CTkLabel(self.scrollable_frame, text="GIST ID:").grid(
            row=17, column=0, sticky="w", padx=10, pady=5
        )
        self.gist_id = customtkinter.CTkEntry(self.scrollable_frame, width=400)
        self.gist_id.grid(row=17, column=1, sticky="ew", padx=10, pady=5)
        self.gist_id.insert(0, self.config.get("GIST_ID", ""))

        # GitHub Token
        customtkinter.CTkLabel(self.scrollable_frame, text="GitHub Token:").grid(
            row=18, column=0, sticky="w", padx=10, pady=5
        )
        self.github_token = customtkinter.CTkEntry(self.scrollable_frame, width=400, show="*")
        self.github_token.grid(row=18, column=1, sticky="ew", padx=10, pady=5)
        self.github_token.insert(0, self.config.get("GITHUB_TOKEN", ""))

    def setup_save_button(self):
        # Save Button
        self.save_button = customtkinter.CTkButton(
            self.scrollable_frame, text="Save Settings", command=self.save_settings,
            width=200
        )
        self.save_button.grid(row=19, column=0, columnspan=2, pady=20)

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
            "GIST_INPUT": self.gist_input_var.get(),
            "EMAIL_ENABLED": self.email_toggle_var.get(),
            "OPENAI_API_KEY": self.openai_key.get(),
            "SMTP_SERVER": self.smtp_server.get(),
            "SMTP_PORT": self.smtp_port.get(),
            "EMAIL_FROM": self.email_from.get(),
            "EMAIL_TO": self.email_to.get(),
            "SMTP_USERNAME": self.smtp_username.get(),
            "SMTP_PASSWORD": self.smtp_password.get(),
            "WRITER_MODEL": self.writer_model.get(),
            "JUDGE_MODEL": self.judge_model.get(),
            "GIST_ID": self.gist_id.get(),
            "GITHUB_TOKEN": self.github_token.get(),
            "QUOTES_ENABLED": self.quotes_toggle_var.get()
        }
        
        try:
            self.config.save_settings(settings)
            self.show_message("Settings saved successfully!")
        except Exception as e:
            self.show_message(f"Failed to save settings: {str(e)}")
            
    def show_message(self, message):
        """Display a message on the page."""
        logging.info(f"{message}")
        self.message_label.configure(text=message)
        self.after(3000, lambda: self.message_label.configure(text=""))  # Clear message after 3 seconds 