import customtkinter
from src.input import insert_into_queue, is_url_processed
import webbrowser

class InputTab(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Create a text area for input
        self.text_area = customtkinter.CTkTextbox(self, width=600, height=300)
        self.text_area.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Create a submit button
        self.submit_button = customtkinter.CTkButton(self, text="Submit URL(s)", command=self.submit_urls)
        self.submit_button.pack(pady=10)

        # Add instructions with hyperlink
        self.instructions = customtkinter.CTkLabel(self, text="Enter job URL(s), one per line. Click 'Submit URL(s)' to add them to the queue.\nURLs must contain FULL job description and information.\n\nHighly recommend sourcing from hiring.cafe (click here to open).\nClick 'Apply Now' or 'Apply Directly' then copy the new tab's URL to paste here.\n\nStart cronjob to begin processing.", cursor="hand2")
        self.instructions.pack(pady=5)
        self.instructions.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://hiring.cafe"))

    def submit_urls(self):
        # Get the input from the text area
        input_text = self.text_area.get("1.0", "end-1c")
        
        # Process the input URLs
        urls = input_text.strip().split("\n")
        new_jobs = 0
        for url in urls:
            processed_info = is_url_processed(url)
            if processed_info:
                processed_id = processed_info[0]
                feedback_message = f"URL already processed with ID: {processed_id}"
                continue
            if insert_into_queue(url):
                new_jobs += 1
        
        # Provide feedback
        feedback_message = f"{new_jobs} new jobs added to the queue."
        self.instructions.configure(text=feedback_message)
        print(feedback_message)

        # Clear the text area
        self.text_area.delete("1.0", "end") 