import customtkinter
from tkinter import messagebox
from .utils.config import ConfigManager
from ..main import initialize_database

class SetupWizard(customtkinter.CTkToplevel):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.config = ConfigManager()
        self.title("Setup Wizard")
        self.geometry("600x400")
        self.steps = [self.step_api_key, self.step_profile_info]
        self.current_step = 0
        self.setup_ui()

        # Initialize the database during setup
        initialize_database()

    def setup_ui(self):
        self.step_frame = customtkinter.CTkFrame(self)
        self.step_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.show_step(self.current_step)

    def show_step(self, step_index):
        for widget in self.step_frame.winfo_children():
            widget.destroy()
        self.steps[step_index]()

    def step_api_key(self):
        label = customtkinter.CTkLabel(self.step_frame, text="Enter your API Key:")
        label.pack(pady=10)
        link_label = customtkinter.CTkLabel(self.step_frame, text="Click here to get your API key from OpenAI", cursor="hand2")
        link_label.pack(pady=5)
        link_label.bind("<Button-1>", lambda e: self.open_api_key_link())
        self.api_key_entry = customtkinter.CTkEntry(self.step_frame, width=400)
        self.api_key_entry.pack(pady=10)
        button_frame = customtkinter.CTkFrame(self.step_frame)
        button_frame.pack(pady=20)
        next_button = customtkinter.CTkButton(button_frame, text="Next", command=self.next_step)
        next_button.pack(side="left", padx=5)
        skip_button = customtkinter.CTkButton(button_frame, text="Skip", command=self.skip_step)
        skip_button.pack(side="left", padx=5)

    def open_api_key_link(self):
        import webbrowser
        webbrowser.open("https://platform.openai.com/api-keys")

    def step_profile_info(self):
        label = customtkinter.CTkLabel(self.step_frame, text="Enter your Profile Information:")
        label.pack(pady=10)
        info_label = customtkinter.CTkLabel(self.step_frame, text="Please complete your profile information in the Profile tab after setup.", wraplength=500)
        info_label.pack(pady=10)
        # Add more fields for profile information as needed
        button_frame = customtkinter.CTkFrame(self.step_frame)
        button_frame.pack(pady=20)
        finish_button = customtkinter.CTkButton(button_frame, text="Finish", command=self.finish_setup)
        finish_button.pack(side="left", padx=5)

    def next_step(self):
        if self.current_step == 0:
            api_key = self.api_key_entry.get()
            if not api_key:
                messagebox.showerror("Error", "API Key cannot be empty.")
                return
            self.config.set("OPENAI_API_KEY", api_key)
        self.current_step += 1
        if self.current_step < len(self.steps):
            self.show_step(self.current_step)

    def skip_step(self):
        self.current_step += 1
        if self.current_step < len(self.steps):
            self.show_step(self.current_step)
        else:
            self.finish_setup()

    def finish_setup(self):
        # Save profile information here
        self.config.set("SETUP_COMPLETED", True)
        messagebox.showinfo("Setup Complete", "Setup is complete. Thanks for using cronjob!")
        self.destroy() 