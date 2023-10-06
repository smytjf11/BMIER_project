
import openai
import datetime
from datetime import datetime
import json
import importlib


def load_config():
    with open("config.json", "r") as f:
        config = json.load(f)
    return config

config = load_config()
chat_history_enabled = config['chat_history']
summary_enabled = config['summary']
branching_enabled = config['branching']
conversations_enabled = config['conversations']


model = config['ai_model']
model_module_name = f"{model.replace('.', '_')}_module"
ai_module = importlib.import_module(f"{model_module_name}")




gui = config['gui']
gui_module_name = f"{gui.replace('.', '_')}_gui"
gui_module = importlib.import_module(f"{gui_module_name}")
database = config['database']
database_module_name = f"{database.replace('.', '_')}_database"
database_module = importlib.import_module(f"{database_module_name}"




global conversation_id 

def summarize_chat(self, conversation_id):
    if summary_enabled == True:
        # Get the message count from the database
        message_count = database_module.count_conversation_messages(self, conversation_id)

        # If the message count is 0, warn the user and abort the summary
        if message_count == 0:
            print("Message count is 0. Summary aborted.")
            return

        # Check if the summary should be updated
        if message_count % config['summary_update_interval'] == 0:
            summary_str, messages_str = database_module.get_summary_data(self, conversation_id)

            # Create the prompt string with the summary at the beginning
            prompt = "Please provide a concise summary of the following, in about 20 words or less:" + summary_str + "\r" + messages_str + "\r"

            # Create a prompt for the OpenAI API that uses the messages
            prompt_messages = [{"role": "user", "content": prompt}]

            # Get the summary from the OpenAI API
            summary = ai_module.get_summary(prompt_messages)
            # check if the summary is empty
            if summary == "":
                print("Summary is empty. No update.")
                return

            # Update the chat summary in the mongo database
            database_module.update_summary(self, conversation_id, summary)
        else:
            print("No summary update.")
            print("Final message count is", message_count)
    else:
        print("Summary is disabled.")



def fetch_chat_history(self, conversation_id):
    # call the get document function to get the full history of the conversation
    full_history = database_module.get_document(self, conversation_id)
    
    history = ai_module._get_history(full_history) 
    return history


def send_to_api(self, input_text, conversation_id, selected_item, selected_branch_conversation_id=None):
    # Fetch the chat history lines from the parent conversation
    if chat_history_enabled == True:
        chat_history_lines = fetch_chat_history(self, conversation_id)
    else:
        chat_history_lines = []

    # Fetch the messages from the selected branch (if any) and convert them to a list of dictionaries
    if branching_enabled == True and selected_branch_conversation_id:
        branch_messages = database_module.fetch_selected_branch_messages(self, selected_item, selected_branch_conversation_id)
    
        
    else:
        branch_messages = []
        
    # Combine the chat history lines and the branch messages
    combined_messages = chat_history_lines + branch_messages
    chat_memory = ai_module.construct_chat_memory(self, input_text, combined_messages)
    response = ai_module.get_response(self, chat_memory)
    # check if the response is empty

    return response


