# this module is used to house any code that deals with the gpt3.5 model
# this includes the code to contact the model, and the code to parse the results
# it also includes the code to format the database specifically for the model


import openai
import datetime
from datetime import datetime
import json
import importlib
import ai_database

def load_config():
    with open("config.json", "r") as f:
        config = json.load(f)
    return config

config = load_config()


def construct_chat_memory(self, input_text, combined_messages):
        # If the combined messages exceed the maximum memory length, truncate the list
        if len(combined_messages) >= config['memory_length']:
            chat_memory = combined_messages[-config['memory_length']:]
        else:
            chat_memory = combined_messages
        
        # Remove any messages with the role "Branches" from the chat memory
        chat_memory = [message for message in chat_memory if message["role"] != "Branches"]

        # Add the user's input as a new message to the chat memory
        chat_memory.append({"role": "user", "content": input_text})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_memory,
            max_tokens=100,
            temperature=0.9,
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=["\r"]
        )

        return response["choices"][0]["message"]["content"].replace(" \r ", "")


def get_summary(prompt_messages):
        summary = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt_messages,
            max_tokens=100,
            temperature=0.7,  # Lower the temperature for more focused output
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=["\r"]
        )

        return summary["choices"][0]["message"]["content"].replace(" \r ", "")


def _clean_branch_messages(branch_messages):
    cleaned_branch_messages = [
        {"role": message["sender"], "content": message["text"]}
        for message in branch_messages["messages"]
    ]
    return cleaned_branch_messages


def _get_history(full_history):
    if full_history:
        # Separate user and model messages
        history = [
            {"role": message["sender"], "content": message["text"]}
            for message in full_history
        ]
    else:
        history = []

    return history


def prepare_user_message(self, input_text):
        user_message = {
            "sender": "user",
            "text": input_text,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        return user_message


def prepare_model_message(self, response):
    model_message = {
        "sender": "assistant",
        "text": response,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    return model_message



