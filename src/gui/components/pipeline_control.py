import customtkinter
import os
import sys
import logging
import threading
import queue
import asyncio

from src import main  # This must be your async pipeline entrypoint

class PipelineControl(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.pipeline_task = None
        self.start_stop_button = customtkinter.CTkButton(
            self,
            text="Start cronjob",
            command=self.toggle_pipeline
        )
        self.start_stop_button.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        self.output_queue = queue.Queue()
        self.loop = asyncio.new_event_loop()
        self.loop_thread = None

    def toggle_pipeline(self):
        if self.pipeline_task is None:
            self.start_pipeline()
        else:
            self.stop_pipeline()

    def start_pipeline(self):
        try:
            def run_loop():
                asyncio.set_event_loop(self.loop)
                self.pipeline_task = self.loop.create_task(main.main())  # main.main() must be an async def
                try:
                    self.loop.run_until_complete(self.pipeline_task)
                except asyncio.CancelledError:
                    logging.info("Pipeline was cancelled.")

            self.loop_thread = threading.Thread(target=run_loop, daemon=True)
            self.loop_thread.start()

            self.start_stop_button.configure(text="Stop cronjob")
            logging.info("cronjob pipeline started in-thread")

        except Exception as e:
            logging.error(f"Failed to start pipeline: {str(e)}")

    def stop_pipeline(self):
        if self.pipeline_task:
            logging.info("Stopping cronjob pipeline...")

            self.pipeline_task.cancel()
            self.pipeline_task = None

            if self.loop and self.loop.is_running():
                self.loop.call_soon_threadsafe(self.loop.stop)

            self.start_stop_button.configure(text="Start cronjob")
            logging.info("cronjob stopped successfully")

    def update_console(self):
        try:
            while True:
                line, level = self.output_queue.get_nowait()
                logging.log(getattr(logging, level.upper()), line.strip())
                self.output_queue.task_done()
        except queue.Empty:
            pass