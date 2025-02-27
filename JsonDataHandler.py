"""
    >>>PARSE LIST AND REMOVE DUPLICATES<<<

    sample data structure:

    [['dogs', 'cats', 'pets'],
    ['pets', 'monkey', 'rat'],
    ['cow', 'monkey', 'rat', 'pig'],
    ['cow', 'monkey', 'rat', 'pig']]

    nested_list = JsonDataHandler.read_data('animals')
    combined_list = list(set(item for sublist in nested_list for item in sublist))
    print(combined_list)

    output : ['pets', 'monkey', 'rat', 'pig', 'cats', 'cow', 'dogs']

    =======================================================================================

    >>>PARSE MESSAGES USING USERNAME<<<

    sample data structure:

    {
        "source": "training_data",
        "data": {
            "test420": {
                "timestamp": "27-02-2025 12:06:25",
                "input": "hallooo",
                "output": "Hello.\n"
            }
        }
    }

    data = JsonDataHandler.read_data('training_data')
    username = 'test420'
    mesages = [item[username] for item in data if username in item]
    
    output : [{'timestamp': '27-02-2025 12:06:25', 'input': 'hallooo','output': 'Hello.\n'}]

    =======================================================================================
"""

import json
import os
import logging
from typing import Union
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class JsonDataHandler:
    def __init__(self, file_path: str):
        self.file_path = file_path
        if not os.path.exists(file_path):
            logging.warning(f"File {file_path} does not exist. Creating a new file.")
            open(file_path, 'w').close()

    def write_data(self, source: str, data: Union[dict, list]):
        timestamp = datetime.utcnow().isoformat()  # Current UTC time in ISO format
        with open(self.file_path, "a") as f:
            if isinstance(data, list):
                for item in data:
                    if item not in data:
                        data.append(item)
                
                # Prepare and write updated data with timestamp to JSON
                data_dict = {"timestamp": timestamp, "source": source, "data": data}
                try:
                    f.write(json.dumps(data_dict) + "\n")
                    return f"{source} data updated successfully!"
                except Exception as e:
                    logging.error(f"Error updating {source} data: {e}")
            else:
                f.write(json.dumps({"timestamp": timestamp, "source": source, "data": data}) + "\n")

    def read_data(self, source: Union[str, type]) -> Union[list, dict]:
        data = set() if source == list else []
        
        try:
            with open(self.file_path, "r") as json_lines:
                for line in json_lines:
                    try:
                        json_data = json.loads(line.strip())
                        if json_data.get("source") == source:
                            new_data = json_data.get("data", [])
                            if source == list:
                                data.update(new_data)  # Add all unique items from new_data
                            else:
                                data.append(new_data)
                    except json.JSONDecodeError as e:
                        logging.error(f"Error decoding JSON on line: {line}. Exception: {e}")
        except FileNotFoundError as e:
            logging.error(f"File not found: {e}")
        
        return list(data) if source == list else data
