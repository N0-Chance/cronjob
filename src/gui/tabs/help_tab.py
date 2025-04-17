import customtkinter
from markdown import markdown
from tkinterweb import HtmlFrame

class HelpTab(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)

        # Create an HTML frame to display the README content
        self.html_frame = HtmlFrame(self, messages_enabled=False)
        self.html_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Load the README.md content
        self.load_readme()

    def load_readme(self):
        try:
            with open("README.md", "r", encoding="utf-16") as readme_file:
                markdown_content = readme_file.read()
                html_content = markdown(markdown_content)
                self.html_frame.load_html(html_content)
        except Exception as e:
            self.html_frame.load_html(f"<p>Failed to load README.md: {str(e)}</p>") 