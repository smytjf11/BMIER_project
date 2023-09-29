# this module is used to house any code that deals with the kobold backend
# this includes the code to contact the model, and the code to parse the results
# it also includes the code to format the database specifically for the model
# kobold has multiple models, so this module is used to connect to kobold so that it can handle the different models



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
        return 


def get_summary(prompt_messages):
        return 



def _get_history(full_history):
    return 


def prepare_user_message(self, input_text):
    return 


def prepare_model_message(self, response):

    return 


