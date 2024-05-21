# this module is used to house any code that deals with the oobabooga backend
# this includes the code to contact the model, and the code to parse the results
# it also includes the code to format the database specifically for the model
# oobabooga has multiple models, so this module is used to connect to oobabooga so that it can handle the different models



import datetime
from datetime import datetime
import json
import importlib
import ai_database
import requests




def load_config():
    with open("config.json", "r") as f:
        config = json.load(f)
    return config

config = load_config()


def construct_chat_memory(self, input_text, combined_messages):
        # this function is used to construct the chat memory for the model
        # it takes in the input text, and the combined messages from the database
        # it then combines them into a single list, and returns the list
        # If the combined messages exceed the maximum memory length, truncate the list
        if config['chat_history'] == True:
            if len(combined_messages) >= config['memory_length']:
                chat_memory = combined_messages[-config['memory_length']:]
            else:
                chat_memory = combined_messages
            
            # Remove any messages with the role "Branches" from the chat memory
            chat_memory = [message for message in chat_memory if message["role"] != "Branches"]

            # Add the user's input as a new message to the chat memory
            chat_memory.append({"role": "user", "content": input_text})

            # strip out everything except the text

            chat_memory = [message["content"] for message in chat_memory]
            # the format for oobabooga is "text", "text", "text"
            # so we need to add quotes around each message and then join them together with commas
            chat_memory = '", "'.join(chat_memory)

            print ("chat_memory", chat_memory)

            return chat_memory
        else:
            # if chat history is disabled, return the input text as the chat memory
            # make sure the imput is a valid list and a valid dictionary
            chat_memory = [{"role": "user", "content": input_text}]


            # strip out everything except the text
            chat_memory = [message["content"] for message in chat_memory]
            return chat_memory


def get_response(self, chat_memory):
        # this function is used to get the response from the model
        # use the oobabooga api to get the response
        # sent a post request to the oobabooga api at the generate 
        # the address is http://127.0.0.1:5000/api/v1/generate
        # the data is {"prompt": chat_memory}
        # it should be in json format
        # the response is the response from the model
        # return the response

        # Send the POST request to the oobabooga API
        # add quotes around the chat_memory
        # we just want the text and not the role
        try:



            response = requests.post(
                "http://127.0.0.1:5000/v1/completions",
                headers={"Content-Type": "application/json"}, 
                json={"prompt": chat_memory, "max_tokens": config["model_max_tokens"], "stop_sequence": config["model_stop_sequence"], 
                      }
            )
            
            print ("initial response", response)
            assistant_message = response.json()["choices"][0]["text"]

            
            print(assistant_message)
        except:
            # if the request fails, notify the user that the request failed
            print("The request failed. this is likely due to the model not being loaded. this module requires the oobabooga api to be running. please check that the oobabooga api is running, and try again.")
            # also warn using a warning message in the gui 
            # dont return an empty string because that can potentially corrupt the database
            # return an error message
            assistant_message = "no model loaded"
        
        return assistant_message
        # return the response

def get_summary(prompt_messages):
        # this function is used to get the summary from the model
        # it takes in the prompt messages, and returns the summary
        # use the oobabooga api to get the response
        # sent a post request to the oobabooga api at the generate
        # the address is http://127.0.0.1:5000/api/v1/generate
        # the data is {"prompt": prompt_messages}
        # it should be in json format\
        # the response is the response from the model
        # return the response

        # send the post request to the oobabooga api using the requests library and wait for the response
        # use the chatgpt2 model via the oobabooga api to get the response
        print("prompt_messages", prompt_messages)
        # turn the prompt messages into a string
        try:
            
            response = requests.post(
                "http://127.0.0.1:5000/v1/completions",
                headers={"Content-Type": "application/json"}, 
                json={"prompt": str(prompt_messages), "max_tokens": config["model_max_tokens"], "stop_sequence": config["model_stop_sequence"], 
                      }
            )

            
            # the response is a json object, so we need to parse it
            print ("initial response", response)
            summary_message = response.json()["choices"][0]["text"]
            return summary_message

        except:
             # if the request fails, notify the user that the summary creation failed
            print("The summary creation failed.this is likely due to the model not being loaded. this module requires the oobabooga api to be running. please check that the oobabooga api is running, and try again.")
            # return an error message
            return "no model loaded"
        

def convert_history_format(full_history):
    if full_history:
        # Separate user and model messages
        history = [
             # the database stores the messages with the role and the content named as "sender" and "text"
            # so we need to change the names to "role" and "content" to match the format of the chat memory
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
    # use a dummy response for now
    model_message = {
        "sender": "assistant",
        "text": response,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    return model_message


