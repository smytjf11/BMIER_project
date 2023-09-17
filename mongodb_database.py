# this file holds evertyhing related to the database
import pymongo
import datetime
import ai_database
import json
import uuid

def load_config():
    with open("config.json", "r") as f:
        config = json.load(f)
    return config

config = load_config()

# a function to check if the conversation exists in the database

def conversation_exists(self, conversation_id):
    # get the conversation document from the database
    conversation = self.collection.find_one({"conversation_id": conversation_id})
    # if the conversation document is not found
    if not conversation:
        # return false
        return False
    # if the conversation document is found
    else:
    # check if the messages field in the conversation document is empty ie the conversation has no messages in it

        if "messages" in conversation and len(conversation["messages"]) > 0:
            # if the conversation has messages in it return true
            return True
        else:
            # if the conversation has no messages in it return false
            return False
    

def get_dropdown_conversation_ids(self):
    dropdown_conversation_ids = self.config_collection.find_one({"name": "dropdown_conversation_ids"})
    
    if not dropdown_conversation_ids:
        self.config_collection.insert_one({"name": "dropdown_conversation_ids", "conversation_ids": ["0"]})
        dropdown_conversation_ids = self.config_collection.find_one({"name": "dropdown_conversation_ids"})

    # Return the list of conversation IDs
    return dropdown_conversation_ids["conversation_ids"]





def add_to_database(self, conversation_id, parent_conversation_id,  user_message, model_message):
    # print the values of the parameters
    conversation = self.collection.find_one({"conversation_id": conversation_id})
    if conversation:
        # If conversation exists, append the new messages to the messages array
        self.collection.update_one(
            {"conversation_id": conversation_id},
            {"$push": {"messages": {"$each": [user_message, model_message]}}}
        )
    else:
        # If conversation doesn't exist, create a new conversation document
        conversation_doc = {
            "conversation_id": conversation_id,
            "parent_conversation_id": parent_conversation_id,
            "is_archived": 0,
            "chat_summary": "chat summary",
            "messages": [user_message, model_message]
        }
        self.collection.insert_one(conversation_doc)


def count_conversation_messages(self, conversation_id):
    # initialize the parent_conversation_id variable
    parent_conversation_id = ""
    # Find the conversation with the specified conversation_id and is_archived set to 0
    # get all of the data from the conversation document except the _id field
    # make sure to include the parent_conversation_id field in the data returned because it will be used to check if the conversation is a branch conversation
    conversation = self.collection.find_one({"conversation_id": conversation_id, "is_archived": 0}, {"parent_conversation_id": 1, "_id": 0, "messages": 1})
    # get the number of messages in the conversation document
    conversation_messages_count = len(conversation["messages"])
    
    
    if conversation:
        parent_conversation_id = conversation["parent_conversation_id"]
        # check if the conversation is a branch conversation
        if conversation["parent_conversation_id"] != conversation_id:
            # get the parent conversation document
            parent_conversation = self.collection.find_one({"conversation_id": parent_conversation_id, "is_archived": 0}, {"messages": 1, "_id": 0})
            # look for a message in the parent conversation document that has the conversation_id of the branch conversation as the value of the "text" field

            if parent_conversation == None:
                return 2

            for message in parent_conversation["messages"]:
                if message["text"] == conversation_id:
                    parent_messages_count = parent_conversation["messages"].index(message)
                    # get the number of messages in the branch conversation document
                    branch_conversation_messages_count = conversation_messages_count
                    # return the sum of the number of messages in the parent conversation document and the number of messages in the branch conversation document
                    message_count = parent_messages_count + branch_conversation_messages_count
                    
                    # get the number of messages in the parent conversation document that have Branches as the value of the "sender" field
                    # this is done to account for the messages that are to mark the location of the branch conversation in the parent conversation document
                    branches_messages_count = len([message for message in parent_conversation["messages"] if message["sender"] == "Branches"])-1
                    final_message_count = message_count - branches_messages_count
                    return final_message_count
        else:
            # if the conversation is not a branch conversation return the number of messages in the conversation document
            # get the number of messages in the conversation document that have Branches as the value of the "sender" field
            # this is done to account for the messages that are to mark the location of the branch conversation in the conversation document
            branches_messages_count = len([message for message in conversation["messages"] if message["sender"] == "Branches"])
            # the branch messages are not included in the count of the number of messages in the conversation document
            # this is because the branch messages are not displayed in the chat window
            # subtract the number of branch messages from the total number of messages in the conversation document
            return conversation_messages_count - branches_messages_count
    else:
        # Raise an error for better debugging
        raise ValueError(f"No conversation found with conversation_id: {conversation_id} and is_archived set to 0")
    



def fetch_selected_branch_messages(self, selected_item, selected_branch_conversation_id):
    branch_messages = self.collection.find_one({"conversation_id": selected_branch_conversation_id}, {"messages": 1, "_id": 0})

    return branch_messages


def get_document(self, conversation_id):
    # Get the conversation document from the database that has the conversation id and is not archived
    conversation = self.collection.find_one({"conversation_id": conversation_id, "is_archived": 0}, {"messages": 1, "_id": 0})

    if conversation and "messages" in conversation:
        full_history = conversation["messages"]
    else:
        full_history = []

    return full_history


def get_summary_data(self, conversation_id):
    # This function will summarize the chat history for the selected conversation id
    # It will also update the chat summary in the database
    conversation_id = conversation_id


        

    # Get the chat_summary from the mongo database for the selected conversation id
    # include the chat_summary and messages fields in the data returned
    # also get the parent_conversation_id field because it will be used to check if the conversation is a branch conversation
    conversation = self.collection.find_one({"conversation_id": conversation_id}, {"chat_summary": 1, "messages": 1, "parent_conversation_id": 1, "_id": 0})




    # Extract chat_summary
    summary_str = conversation["chat_summary"] if "chat_summary" in conversation else ""

    # Extract the messages
    messages = conversation["messages"] if "messages" in conversation else []

    # Check if the conversation is a branch conversation
    if conversation["parent_conversation_id"] != conversation_id:
        # get the parent conversation document
        parent_conversation = self.collection.find_one({"conversation_id": conversation["parent_conversation_id"]}, {"messages": 1, "_id": 0})
        # look for a message in the parent conversation document that has the conversation_id of the branch conversation as the value of the "text" field and g
        for message in parent_conversation["messages"]:
            if message["text"] == conversation_id:
                # get the index of the message in the parent conversation document
                message_index = parent_conversation["messages"].index(message)
                # get all of the messages before the message with the conversation_id of the branch conversation
                # ie every message in the parent conversation document before the message with the conversation_id of the branch conversation
                # we want the text of these messages to be included in the summary
                # the goal is to have not only the messages in the branch conversation but also the messages in the parent conversation that led to the branch conversation
                # to do this we will get the index of the message with the conversation_id of the branch conversation in the parent conversation document
                # then we will get all of the messages in the parent conversation document before the message with the conversation_id of the branch conversation
                # then we will add the messages in the branch conversation to the end of the messages in the parent conversation document before the message with the conversation_id of the branch conversation

                # get the messages in the parent conversation document before the message with the conversation_id of the branch conversation
                messages = parent_conversation["messages"][:message_index]
                # get the messages in the branch conversation
                branch_messages = conversation["messages"]
                # add the branch messages  to the end of the messages in the parent conversation document before the message with the conversation_id of the branch conversation
                messages.extend(branch_messages)
    # check if the length of the messages array is greater than the memory length
    if len(messages) > config['memory_length']:
        # if the length of the messages array is greater than the memory length then get the last n messages in the messages array
        messages = messages[-config['memory_length']:]

    # Convert the messages into a single string
    messages_str = "\r".join([message["text"] for message in messages])
    return summary_str, messages_str


def set_up_database(self):
    self.client = pymongo.MongoClient("mongodb://localhost:27017/")

    # create or get the database and collection
    self.db = self.client.get_database("chat_history")
    self.collection = self.db.get_collection("history")
    # make a new collection for the config data in the chat_history database
    self.config_collection = self.db.get_collection("config")
    return self.collection, self.config_collection


def archive(self, conversation_id):
    # this function will archive the selected conversation
    # set the global conversation id variable to the conversation id passed to the function
    conversation_id = conversation_id

    # this function will archive the selected conversation
    # get the selected conversation id from the global conversation id variable
    selected_conversation_id = conversation_id
    # set the selected conversation to archived in the database
    conversation = self.collection.find_one({"conversation_id": conversation_id})
    # if the conversation document is not found
    if not conversation:
        print("Conversation not found")
        return None
    # set the is_archived field to 1
    conversation["is_archived"] = 1
    # update the conversation document in the database 
    self.collection.replace_one({"conversation_id": conversation_id}, conversation)
    # get the branches of the conversation document
    branches = self.collection.find({"parent_conversation_id": conversation_id})
    # loop through the branches of the conversation document
    for branch in branches:
        # set the is_archived field to 1
        branch["is_archived"] = 1
        # update the branch document in the database
        self.collection.replace_one({"conversation_id": branch["conversation_id"]}, branch)

    # remove the selected conversation from the dropdown_conversation_ids document
    self.config_collection.update_one(
        {"name": "dropdown_conversation_ids"},
        {"$pull": {"conversation_ids":(selected_conversation_id)}},
        upsert=True
    )


def get_conversation(self, conversation_id):
    # Get the conversation document from the database that has the conversation id
    conversation = self.collection.find_one({"conversation_id": conversation_id})
    return conversation


def new_conversation_id(self):
    # get the highest conversation id and add 1 to it
    new_conversation_id = str(int(max(self.config_collection.find_one({"name": "dropdown_conversation_ids"})['conversation_ids'])) + 1)
    # check if the conversation id is already in the database and if it is, add 1 to it and check again
    while self.collection.find_one({"conversation_id": new_conversation_id}):
        new_conversation_id = str(int(new_conversation_id) + 1)
    return new_conversation_id


def add_conversation_id(self, new_conversation_id):
    # add the new conversation id to the dropdown_conversation_ids document
    self.config_collection.update_one(
            {"name": "dropdown_conversation_ids"},
            {"$push": {"conversation_ids":(new_conversation_id)}},
            upsert=True
        )

def create_branch(self, parent_conversation_id, selected_item, selected_item_id):
    global conversation_id
    # Fetch the parent conversation document from the get_conversation function in database_module.py
    parent_conversation = self.collection.find_one({"conversation_id": parent_conversation_id})

    if not parent_conversation:
        print("Parent conversation not found")
        return None

    # Generate a unique conversation ID for the new branch
    new_conversation_id = str(uuid.uuid4())

    # Create a new conversation document with the same chat summary as the parent conversation
    new_conversation = {
        "conversation_id": new_conversation_id,
        "is_archived": 0,
        "chat_summary": parent_conversation["chat_summary"],
        "messages": [],
        "branches": [],
        "parent_conversation_id": parent_conversation_id
    }

    # Save the new conversation document in the database
    self.collection.insert_one(new_conversation)
    
    # set the global conversation id variable to the new conversation id
    conversation_id = new_conversation_id

    # Append the new conversation ID to the branches array in the parent conversation document
    self.collection.update_one(
        {"conversation_id": parent_conversation_id},
        {"$push": {"branches": new_conversation_id}}
    )

    # the selected item id id the position of the selected item in the parent conversation's messages array
    # so id 4 is the 4th item in the array
    # so the new message will be inserted after the 4th item in the array
    # Find the index of the selected item in the parent conversation's messages array

    # convert the selected item id to an int
    message_index = int(selected_item_id)



    # Insert the new message into the parent conversation after the selected item
    if message_index != -1:
        new_message = {
            "sender": "Branches",
            "text": new_conversation_id,
            "timestamp": datetime.datetime.now()
        }
        self.collection.update_one(
            {"conversation_id": parent_conversation_id},
            {"$push": {"messages": {"$each": [new_message], "$position": message_index }}}
        )
    else:
        print("Selected item not found in the parent conversation's messages")

    return new_conversation_id

def update_summary(self, conversation_id, summary):
    self.collection.update_one({"conversation_id": conversation_id}, {"$set": {"chat_summary": summary}})
    print("summary updated")