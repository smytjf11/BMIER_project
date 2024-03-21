import ai_database
import sys
import json
import importlib
import uuid
import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask.views import MethodView
from flask import jsonify
import re


conversation_id = None
selected_branch_conversation_id = None
selected_item = None


# specify the template folder and static folder

termplate_folder = 'modules/gui/browser_gui/templates'
static_folder = 'modules/gui/browser_gui/static'

app = Flask(__name__, template_folder=termplate_folder, static_folder=static_folder)


def load_config():
    with open("config.json", "r") as f:
        config = json.load(f)
    return config

config = load_config()
print(" memory length is ", config['memory_length'])
print(" summary update interval is ", config['summary_update_interval'])

model = config['ai_model']
model_module_name = f"{model.replace('.', '_')}_module"
ai_module = importlib.import_module(f"modules.ai_model.{model_module_name}")

database = config['database']
database_module_name = f"{database.replace('.', '_')}_database"
database_module = importlib.import_module(f"modules.database.{database_module_name}")

class FlaskGui(MethodView):
    def __init__(self):
        super().__init__()
        self.app = app
        database_module.set_up_database(self)
        history = ai_database.fetch_chat_history(self, conversation_id)
        self.selected_branch_conversation_id = None
        self.parent_conversation_id_for_branch = None
        
        
    def post(self):
        if request.path == '/submit-message':
            return self.submit_message()
        elif request.path == '/new-chat':  # Add this line
            return self.new_chat()  # Add this line
        elif request.path == '/archive':
            return self.archive()
        elif request.path == '/set-selected-item':
            return self.set_selected_item()
        elif request.path == '/create-branch':
            return self.create_branch()
        elif request.path == '/set-branch-conversation-id':
            return self.set_branch_conversation_id()
        
        elif  request.path == '/update-selection':
            return self.update_selection()
        else:
            # Return an appropriate response for other POST routes if any
            pass

        

    def get(self, conversation_id=None):
        print("requested URL:", request.url)
        if request.path == '/':
            return self.index()
        elif request.path == '/chat':
            return self.chat()
        elif conversation_id is not None:
            database_conversation = database_module.get_conversation(self, conversation_id)
            conversation = {}
            # if the conversation exists in the database
            if database_conversation is not None:

                for message in database_conversation['messages']:
                    sender = message['sender']
                    text = message['text']
                    # add a new row to the conversation dictionary with the sender and text
                    # make sure not to overwrite the previous row
                    conversation['messages'] = conversation.get('messages', []) + [{'sender': sender, 'text': text}]
                # return the conversation
                return jsonify(conversation)
                
            else:
                # if the conversation does not exist in the database, return the conversation with a blank row with no content
                conversation = {'messages':[{'sender': '', 'text': ''}]}
                




                return jsonify(conversation)
        else:
            return redirect(url_for('index'))
        
        
        
    def set_branch_conversation_id(self):
        global selected_branch_conversation_id
        global conversation_id
        data = request.get_json()
        if data is not None and 'branch_conversation_id' in data:
            selected_branch_conversation_id = data['branch_conversation_id']
            # After setting selected_branch_conversation_id
            conversation_id = data['conversation_id']
            print ("set_branch_conversation_id has been called")
            print("conversation id is ", conversation_id)
            print("selected branch conversation id is ", selected_branch_conversation_id)
            return {'status': 'success'}
        elif data is not None and 'selected_branch_conversation_id' not in data:
            selected_branch_conversation_id = None
            return {'status': 'success'}
    
    def update_selection(self):
        data = request.get_json()
        global conversation_id
        global selected_branch_conversation_id

        conversation_id = data.get('conversation_id', conversation_id)  # update the conversation_id if it is provided
        selected_branch_conversation_id = data.get('branch_id', selected_branch_conversation_id)  # update the branch_id if it is provided
        
        print ("updated conversation id is ", conversation_id)
        print ("updated branch conversation id is ", selected_branch_conversation_id)

        return jsonify({'message': 'Selection updated'}), 200

        
    def set_selected_item(self):
        data = request.get_json()
        global selected_item
        global selected_item_id
        selected_item = data['selected_item']
        selected_item_id = data['selected_item_id']
        # Do something with the selected item or store it as needed
        # set the selected item to the global variable
        print("Selected item:", selected_item)
        print("Selected item id:", selected_item_id)
        return jsonify({"status": "success"})


    def index(self):
        return render_template('index.html')
    
    def conversation(self, conversation_id):
        # call the get_conversation function from the database file
        conversation = database_module.get_conversation(self, conversation_id)
        # pass the conversation to the conversation.html file and the conversation id
        return render_template('conversation.html', conversation=conversation, conversation_id=conversation_id)
    
    def submit_message(self):
        data = request.get_json()

        input_text = data['input_text']

        global conversation_id
        global selected_item
        global selected_branch_conversation_id

        print("Initial conversation_id:", conversation_id)  # Debug print statement

        
        # check if the current conversation is already in the database
        if conversation_id is None or not database_module.conversation_exists(self, conversation_id):
            # if the conversation does not exist, set the conversation_exists variable to false
            conversation_exists = False
        else:
            conversation_exists = True

        print ("conversation exists is ", conversation_exists)
        if selected_branch_conversation_id is not None:
            conversation_id = selected_branch_conversation_id

        if conversation_id is not None and re.match(r'^[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}$', conversation_id):
            is_branch = True
        else:
            is_branch = False

        print("is_branch:", is_branch)  # Debug print statement

        

        print("Updated conversation_id:", conversation_id)  # Debug print statement

        if not input_text:
            return
        
        if is_branch == False:
            parent_conversation_id = ''
        else:
            parent_conversation_id = conversation_id

        user_message = ai_module.prepare_user_message(self, input_text)
        
        response = ai_database.send_to_api(self, input_text, conversation_id, selected_item, selected_branch_conversation_id)
        model_message = ai_module.prepare_model_message(self, response)
        
        database_module.add_to_database(self, conversation_id, parent_conversation_id,  user_message, model_message)

        response_data = {
            'user_message': user_message,
            'model_message': model_message,
            'is_branch': is_branch,
            'conversation_exists': conversation_exists
        }   
        
        # call the summarize_chat function from the database file
        ai_database.summarize_chat(self, conversation_id)


        return jsonify(response_data)
    
    
    def load_chat_history(self, conversation_id):
        conversation = database_module.get_conversation(self, conversation_id)
        chat_history = []
        for message in conversation['messages']:
            sender = message['sender']
            text = message['text']
            chat_history.append({'sender': sender, 'text': text})
        return chat_history

    def chat(self):
        conversation_ids = self.set_dropdown()
        chat_history = self.load_chat_history(conversation_id)
        return render_template('chat.html', config=config, conversation_ids=conversation_ids, chat_history=chat_history)
    
    def switch_conversation(self):
        global conversation_id
        conversation_id = request.form.get('conversation_id')
        print ("conversation switched to ", conversation_id)
        return redirect(url_for('chat'))


    def new_chat(self):
        global conversation_id
        conversation_id = database_module.new_conversation_id(self)
        database_module.add_conversation_id(self,conversation_id)
        
        return jsonify({"conversation_id": conversation_id})
    

    def create_branch(self):
        global conversation_id
        data = request.get_json()
        parent_conversation_id = data['parent_conversation_id']
        selected_item = data['selected_item']
        selected_item_id = data['selected_item_id']

        conversation_id = database_module.create_branch(self, parent_conversation_id,  selected_item_id)

        return jsonify({"conversation_id": conversation_id})


    def set_dropdown(self):
        print ("set_dropdown function called")
        # this function is called when the set dropdown button is clicked. it is passed the self variable and database
        # convert to use flask instead of qt
        global conversation_id

        # call the get_dropdown_conversation_ids function from the database file
        dropdown_conversation_ids = database_module.get_dropdown_conversation_ids(self)
        print ("dropdown_conversation_ids is ", dropdown_conversation_ids)

        # get the conversation ids from the dropdown_conversation_ids variable
        conversation_ids = dropdown_conversation_ids
        # set the global conversation id variable to the first conversation id
        conversation_id = conversation_ids[0][0]
        print ("conversation_id is ", conversation_ids)
        return conversation_ids
    

    def archive(self):
        data = request.json
        if data is None:
            return jsonify({"error": "Invalid JSON payload"}), 400
        conversation_id = data.get('conversation_id')
        if conversation_id is None:
            return jsonify({"error": "Missing conversation_id parameter"}), 400
        database_module.archive(self, conversation_id)
        return jsonify({"message": "Conversation archived"})

app.add_url_rule('/', view_func=FlaskGui.as_view('index'))
app.add_url_rule('/chat', view_func=FlaskGui.as_view('chat'))
app.add_url_rule('/create-branch', view_func=FlaskGui.as_view('create_branch'), methods=['POST'])
app.add_url_rule('/switch-conversation', view_func=FlaskGui.as_view('switch_conversation'), methods=['POST'])
app.add_url_rule('/submit-message', view_func=FlaskGui.as_view('submit_message'), methods=['POST'])
app.add_url_rule('/new-chat', view_func=FlaskGui.as_view('new_chat'), methods=['POST'])
app.add_url_rule('/archive', view_func=FlaskGui.as_view('archive'), methods=['POST'])
app.add_url_rule('/conversation/<conversation_id>', view_func=FlaskGui.as_view('get_conversation'))
app.add_url_rule('/set-selected-item', view_func=FlaskGui.as_view('set_selected_item'), methods=['POST'])
app.add_url_rule('/set-branch-conversation-id', view_func=FlaskGui.as_view('set_branch_conversation_id'), methods=['POST'])
app.add_url_rule('/update-selection', view_func=FlaskGui.as_view('update_selection'), methods=['POST'])
def closeEvent(self, event):
    self.client.close()

if __name__ == '__main__':
    # run the server on port 5001 due to the fact that the oobabooga api runs on port 5000
    
    app.run(debug=True, port=5001)