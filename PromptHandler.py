import json
from datetime import datetime
from time import sleep
import google.generativeai as ai

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PromptHandler:
    def __init__(self, path: str):
        self.path = path
        self.api_keys = self.load_api_keys()
        self.current_key_index = 0
        self.api_key = self.api_keys[self.current_key_index]
        ai.configure(api_key=self.api_key)
        self.model = ai.GenerativeModel("gemini-2.0-flash-exp")
        self.chat = self.model.start_chat()

    def switch_api_key(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self.api_key = self.api_keys[self.current_key_index]
        ai.configure(api_key=self.api_key)
        logging.error("Switched API key due to failure.")

    def load_api_keys(self):
        data = []
        try:
            with open(self.path, "r") as f:
                lines = f.readlines()
                for line in reversed(lines):
                    entry = json.loads(line.strip())
                    if entry.get("source") == 'api_keys':
                        data = entry.get("data")
                        break
        except Exception as e:
            logging.error(f"Error loading JSON: {e}")
        return data

    def generate_message(self, prompt):
        max_retries = 3
        delay = 1 

        for attempt in range(max_retries):
            try:
                response = self.chat.send_message(prompt)
                return response.text
            except Exception as e:
                logging.error(f"Response error (attempt {attempt + 1}): {e}.")
                if attempt < max_retries - 1:
                    self.switch_api_key()
                    sleep(delay)
                    delay *= 2  # Exponential backoff

        logging.error("Max retries reached. No valid response.")
        return None

    def load_training_data(self, control_number):
        try:
            with open(self.path, 'r') as file:
                training_data = [
                                    json.loads(line.strip())["data"][control_number]
                                    for line in file
                                    if json.loads(line.strip()).get("source") == "training_data"
                                    and control_number in json.loads(line.strip())["data"]
                                ]
            training_data.sort(key=lambda x: x['timestamp'], reverse=True)
            return training_data
        except Exception as e:
            logging.error(f"Error loading training data: {e}")
            return []

    def log_for_ai_training(self, control_number, user_input, ai_response):
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        if isinstance(ai_response, dict):
            ai_response = json.dumps(ai_response)

        return {control_number: {"timestamp": now, "input": user_input, "output": ai_response}}

    def prompt_message(self, control_number, user_input, role="general", additional_context="", additional_data=""):
        training_data = self.load_training_data(control_number)

        # Compile past training data if available
        training_context = "\n".join(
            f"User: {entry['input']}\nAI: {entry['output']}" for entry in training_data
        )

        prompt = (
                    f"You are an AI assistant specializing in {role}.\n\n"
                    f"User Input: {user_input}\n"
                    + (f"Additional Context: {additional_data}\n" if additional_data else "")
                    + (f"Additional Context: {additional_context}\n" if additional_context else "")
                    + (f"Past Training Data:\n{training_context}\n" if training_context else "")
                    + "\nRespond concisely, ensuring clarity and relevance."
                )

        return self.generate_message(prompt)

    def handle_prompt(self, control_number, user_input, role="general", additional_context="", additional_data=""):
        if not user_input:
            logging.error("Invalid or empty input.")
            return "Invalid or empty input."

        try:
            response = self.prompt_message(control_number, user_input, role, additional_context, additional_data)
            if response:
                return self.log_for_ai_training(control_number, user_input, response)
        
            else:
                logging.error("Failed to generate a response.")
                return "Failed to generate a response."
        except Exception as e:
            logging.error(f"Error processing prompt: {e}")
            return "An error occurred while processing the request."
