import json
import google.generativeai as ai
from time import sleep
from config import API_KEY
from Logger import Logger

class PromptHandler:
    def __init__(self):
        self.api_keys = API_KEY
        self.current_key_index = 0
        self.api_key = self.api_keys[self.current_key_index]
        self.api_keys = ai.configure(api_key=self.api_key)
        self.model = ai.GenerativeModel("gemini-2.0-flash-exp")
        self.chat = self.model.start_chat()

    def switch_api_key(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)

    def generate_message(self, prompt):
        max_retries = 3
        delay = 5

        for attempt in range(1, max_retries + 1):
            try:
                response = self.chat.send_message(prompt)
                return response.text
            except Exception as e:
                print(f"Response error (attempt {attempt}): {e}. Switching to new API key.")
                if attempt < max_retries:
                    self.switch_api_key()
                    sleep(delay)

        return False

    def load_training_data(self, control_number):
        try:
            with open('training_data.jsonl', 'r') as file:
                training_data = [
                    json.loads(line.strip())[control_number]
                    for line in file
                    if control_number in json.loads(line.strip())
                ]

            training_data.sort(key=lambda x: x['timestamp'], reverse=True)
            return training_data
        except Exception as e:
            print(f"Error loading training data for {control_number}: {e}")
            return []

    def prompt_message(self, control_number, user_input):
        training_data = self.load_training_data(control_number)

        training_context = "\n".join(
            f"{entry['input']}\n{entry['output']}" for entry in training_data
        )

        product_data = {
            "product": {
                "name": "NFC Pet Tag",
                "description": "A smart and durable NFC-enabled tag designed to Simplify pet parenting. Track, organize, and manage all in one place..",
                "features": {
                    "smart_identification": "Each tag is embedded with an NFC chip that links to your pet's unique profile.",
                    "passive_tracking" : "When someone interacts with the tag, it will store the last known location"
                },
                "benefits": {
                    "easy_recovery": "Lost pets can be quickly reunited with their owners when someone scans the tag with a smartphone.",
                    "no_batteries_needed": "Operates without requiring batteries, ensuring consistent functionality.",
                    "secure_data": "Store essential pet details such as medical history, owner contact, and care instructions securely.",
                    "set_vet_clinic_appointment": "Easily schedule vet clinic appointments through the platform."
                },
                "price": 12.99,
                "currency": "USD",
                "category": "Pet Accessories",
                "availability": "In Stock",
                "shop": "https://connecta.store",
                "demo": "https://connecta.store/demo"
            }
        }

        prompt = (
                    f"You are a persuasive and professional marketing expert focused on crafting personalized and engaging messages for Reddit DMs.\n\n"
                    f"Your task is to create a short, informative, and compelling message for a Reddit user based on:\n"
                    f"- User input: {user_input}\n"
                    f"- Product/service details: {product_data}\n"
                    f"- Context from prior interactions: {training_context}\n\n"
                    f"IMPORTANT GUIDELINES:\n"
                    f"1. DO NOT repeat or restate the user’s input in your response.\n"
                    f"   Example:\n"
                    f"   - User Input: 'How can this product help my business?'\n"
                    f"   - Incorrect: 'How can this product help my business?'\n"
                    f"   - Correct: 'This product helps streamline your workflow, saving time and improving profitability.'\n"
                    f"2. DO NOT include a subject line or introductory phrases like 'Okay, here's a persuasive and professional DM crafted based on the provided information and guidelines.'\n"
                    f"3. Keep the message short, engaging, and solution-oriented, focusing on how the product/service can address the user’s needs.\n"
                    f"4. Maintain a confident, friendly, and professional tone throughout.\n"
                    f"5. Address any potential concerns or objections in a clear and confident manner.\n"
                    f"6. Include a call to action that encourages the user to engage further."
                    f"7. If the user expresses negative sentiment or hostility (e.g., 'I will report you'), respond calmly and politely. Acknowledge their frustration and offer a respectful exit from the conversation. DO NOT push the product or continue with sales-related messages.\n"
                    f"8. If the user expresses negative sentiment or hostility, politely close the conversation without continuing with the sales pitch.\n"
                    f"9. If applicable, provide the shop link if they express interest in buying or purchasing."
                )

        try:
            response = self.generate_message(prompt)
            if not response:
                print("No valid response generated.")
            return response
        except Exception as e:
            print(f"Error generating response: {e}")
            return None

    def handle_prompt(self, control_number, user_input):
        if not user_input:
            return "Invalid or empty prompt."

        try:
            response = self.prompt_message(control_number, user_input)
            if response:
                Logger.log_for_ai_training(control_number, user_input, response)
                return str(response)
            else:
                print("Failed to generate a response.")
        except Exception as e:
            print(f"Error processing prompt for {control_number}: {e}")
