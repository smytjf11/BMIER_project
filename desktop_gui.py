from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QMainWindow, QWidget
from PyQt5.QtWidgets import QHBoxLayout, QComboBox, QTreeView
from PyQt5.QtWidgets import QComboBox
# import qicon
from PyQt5.QtGui import QIcon
import ai_database

import sys
import json
import importlib
import uuid
import datetime


conversation_id = None
selected_branch_conversation_id = None
selected_item = None

def load_config():
    with open("config.json", "r") as f:
        config = json.load(f)
    return config

config = load_config()
chat_history_enabled = config['chat_history']
branching_enabled = config['branching']
conversations_enabled = config['conversations']




model = config['ai_model']
model_module_name = f"{model.replace('.', '_')}_module"
ai_module = importlib.import_module(f"modules.ai_model.{model_module_name}")

database = config['database']
database_module_name = f"{database.replace('.', '_')}_database"
database_module = importlib.import_module(f"modules.database.{database_module_name}")







class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    
    def initUI(self):
        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle('Chat')

        layout = QVBoxLayout()
        # switch to a tree view
        self.chat_history = QTreeView()
        self.chat_history.setGeometry(QtCore.QRect(10, 40, 200, 200))
        self.chat_history.setHeaderHidden(True)

        self.chat_history_model = QtGui.QStandardItemModel()
        self.chat_history.setModel(self.chat_history_model)
        # set the selection mode to single selection
        self.chat_history.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        # connect the selection model to the on branch selected function in this file
        self.chat_history.selectionModel().selectionChanged.connect(self.on_branch_selected)
        # connect the selection model to the set selected item function in this file
        self.chat_history.selectionModel().selectionChanged.connect(self.set_selected_item)

        layout.addWidget(self.chat_history)
        # call the set up database function in the database module
        database_module.set_up_database(self)

        # add a horozontal layout to the main layout
        # call the layout user_imputs
        user_input = QHBoxLayout()
        layout.addLayout(user_input)

        # add a text input to the horizontal layout
        
        self.user_input = QLineEdit()
        user_input.addWidget(self.user_input)
        # add a branch button to the horizontal layout to branch the conversation
        # check if the config file has branching enabled
        if branching_enabled == True:
            self.branch_button = QPushButton('')
            # use an icon for the branch button
            # obtained from https://www.iconsdb.com/black-icons/fork-2-icon.html 
            # licensed under the MIT license
            self.branch_button.setIcon(QIcon('branch.png'))
            # connect the branch button to the create branch function in this file and pass the conversation id  the selected item and the selected item id
            # the selected item id is the position of the selected item in the tree view. ie the index of the selected item -1
            self.branch_button.clicked.connect(lambda: self.create_branch(conversation_id, self.chat_history.selectedIndexes()[0].row() + 1))
            user_input.addWidget(self.branch_button)


        # add a dropdown menu to the horizontal layout to select the conversation
        # check if the config file has conversations enabled
        if conversations_enabled == True:
            self.conversation = QComboBox()
            # call the set dropdown function in this file
            self.set_dropdown()
        
            user_input.addWidget(self.conversation)
            # connect the signal of the dropdown menu to the switch conversation function
            self.conversation.currentTextChanged.connect(self.switch_conversation)
        else:
            # if conversations are not enabled, but history is enabled, we need to set the conversation id to the first conversation id
            
            self.conversation = []
            # call the get_dropdown_conversation_ids function from the database file
            dropdown_conversation_ids = database_module.get_dropdown_conversation_ids(self)
            # get the conversation ids from the dropdown_conversation_ids variable
            conversation_ids = dropdown_conversation_ids
            global conversation_id
            conversation_id = conversation_ids[0]
            # set the global conversation id variable to the first conversation id
            # call the populate branch tree function with the selected_conversation_id
            

            
            
        # add the chat history to the chat history text box when the program starts
        # call populate branch tree function in this file and pass the conversation id
        # check if the config file has chat history enabled
        if chat_history_enabled == True:
            self.populate_branch_tree(conversation_id)
            history = ai_database.fetch_chat_history(self, conversation_id)
               
        
        # add a horizontal layout for the submit button and the new chat button
        buttons = QHBoxLayout()
        layout.addLayout(buttons)
        self.submit_button = QPushButton('Submit')
        # connect the submit button to the on submit button clicked function in this file

        self.submit_button.clicked.connect(self.on_submit_button_clicked)
        buttons.addWidget(self.submit_button)
        self.new_chat_button = QPushButton('New Chat')
        # connect the new chat button to the new chat function in this file
        self.new_chat_button.clicked.connect(self.new_chat)
        buttons.addWidget(self.new_chat_button)

        # add an archive button to the horizontal layout
        self.archive_button = QPushButton('Archive')
        # connect the archive button to the archive function
        self.archive_button.clicked.connect(lambda: self.archive(conversation_id=conversation_id))
        buttons.addWidget(self.archive_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    
    def create_branch(self, parent_conversation_id,  selected_item_id):
        # this function will call the create branch function in the ai_database module
        # pass the parent conversation id and the selected item id
        # and get the branch conversation id that is returned
        global conversation_id
        print(parent_conversation_id, selected_item_id)
        conversation_id = database_module.create_branch(self, parent_conversation_id, selected_item_id)
        


    def switch_conversation(self):
        global conversation_id
        # this function will switch the chat history to the selected conversation
        # get the selected conversation id from the dropdown menu in the gui.py file
        selected_conversation_id = self.conversation.currentText()
        # clear the contents of the chat history tree view
        self.chat_history_model.clear()
        
        # add the chat history to the chat history tree view
        # call the populate branch tree function with the selected_conversation_id
        if chat_history_enabled == True:
            self.populate_branch_tree(selected_conversation_id)
        # set the global conversation id variable to the selected conversation id
        conversation_id = selected_conversation_id
        
    def warn(self, message):
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            if message == "no model loaded":
                msg.setText("The request failed. this is likely due to the model not being loaded. this module requires the "
            + model + " api to be running. please check that the "+ model + " api is running and try again.")
            if message == "blank":
                msg.setText("The request failed. this is likely due an error causing the response from the model to be blank.")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
            return


    def on_submit_button_clicked(self):
        global selected_item, selected_branch_conversation_id, conversation_id
        
        input_text = self.user_input.text()
        self.user_input.clear()

        if not input_text:
            return

        if selected_branch_conversation_id is not None:
            conversation_id = selected_branch_conversation_id

        user_message = ai_module.prepare_user_message(self, input_text)
        response = ai_database.send_to_api(self, input_text, conversation_id, selected_item, selected_branch_conversation_id)
        if response == "no model loaded":
            # show a warning message to the user
            # show a warning window by calling the warn function in this file
            self.warn("no model loaded")
            return
        if response == "":
            # show a warning message to the user
            # show a warning window by calling the warn function in this file
            self.warn("blank")
            return
        model_message = ai_module.prepare_model_message(self, response)

        user_message_item = QtGui.QStandardItem(f"{user_message['text']}")
        model_message_item = QtGui.QStandardItem(f"{model_message['text']}")
        selected_index = self.chat_history.selectedIndexes()

        if selected_item:
            selected_index = self.chat_history_model.itemFromIndex(selected_index[0])
            selected_index.appendRow(user_message_item)
            selected_index.appendRow(model_message_item)
            parent_conversation_id = None
        else:
            conversation_item = QtGui.QStandardItem(f"{conversation_id}")
            conversation_item.setData(conversation_id, QtCore.Qt.UserRole + 1)
            self.chat_history_model.appendRow(conversation_item)
            conversation_item.appendRow(user_message_item)
            conversation_item.appendRow(model_message_item)
            parent_conversation_id = conversation_id
            
        if chat_history_enabled == True:
            database_module.add_to_database(self, conversation_id, parent_conversation_id,  user_message, model_message)
            


        
        # call the summarize chat function and pass the conversation id
        summary = ai_database.summarize_chat(self, conversation_id)
        if summary == "no model loaded":
            # show a warning message to the user

            # show a warning window by calling the warn function

            self.warn("no model loaded")

            return
        
        
        

    def set_selected_item(self, item):
        global selected_item
        selected_item = item
        index = self.chat_history.currentIndex()
        text = self.chat_history.model().data(index)

        if " " in text:
            selected_item = text.split(" ", 1)[1]
        else:
            selected_item = text

        return selected_item



    def add_conversation_to_tree(self, parent_item, conversation):
        if not parent_item:
            conversation_item = QtGui.QStandardItem(f"{conversation['conversation_id']}")
            conversation_item.setData(conversation["conversation_id"], QtCore.Qt.UserRole)
            self.chat_history_model.appendRow(conversation_item)
        else:
            conversation_item = parent_item
        try:
            for message in conversation['messages']:
                message_item = QtGui.QStandardItem(f"{message['sender']}: {message['text']}")
                conversation_item.appendRow(message_item)
        except TypeError:
            #   TypeError: 'NoneType' object is not subscriptable
            # this error occurs when a branch was deleted but the branch message was not deleted
            # the user should be notified that they need to delete the branch message

            # show a warning message to the user
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("there was an error loading the conversation. this is likely due to a branch being deleted but the marker for the branch not being deleted in the " + config['database'] + " database. the marker is a message that says 'Branches: <branch id>'. please delete the branch marker and try again.")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
            return

        # check if the config file has branching enabled
        if 'branches' in conversation:
            for branch_id in conversation['branches']:
                # check if the config file has branching enabled
                branch_conversation = database_module.get_conversation(self, branch_id)
                # check if the config file has branching enabled
                if branching_enabled == True:

                    for row in range(conversation_item.rowCount()):
                        item = conversation_item.child(row)
                        if item.text() == f"Branches: {branch_id}":
                            parent_item_for_branch = conversation_item.child(row - 1) if row > 0 else conversation_item

                            self.add_conversation_to_tree(parent_item_for_branch, branch_conversation)
                            conversation_item.removeRow(row)

                            parent_item_for_branch.setData(branch_id, QtCore.Qt.UserRole)
                            break
                else:
                    # do not add the branches to the tree view
                    # hide the Branches message
                    for row in range(conversation_item.rowCount()):
                        item = conversation_item.child(row)
                        if item.text() == f"Branches: {branch_id}":
                            conversation_item.removeRow(row)
                            break


    def on_branch_selected(self):
        global conversation_id
        global selected_branch_conversation_id  # Add this line

        # Get the selected item from the tree view
        selected_indexes = self.chat_history.selectedIndexes()
        if not selected_indexes:
            return

        selected_item = self.chat_history_model.itemFromIndex(selected_indexes[0])

        # Get the conversation_id of the selected item from the custom data role
        selected_conversation_id = selected_item.data(QtCore.Qt.UserRole)
        # check if the selected conversation id shorter than 24 characters
        # check if the selected conversation id is none
        if selected_conversation_id is None or len(selected_conversation_id) < 24:
            return

        # Set the global selected_branch_conversation_id variable to the selected conversation id
        selected_branch_conversation_id = selected_conversation_id  # Add this line



    def set_dropdown(self):
        global conversation_id

        # call the get_dropdown_conversation_ids function from the database file
        dropdown_conversation_ids = database_module.get_dropdown_conversation_ids(self)

        # get the conversation ids from the dropdown_conversation_ids variable
        conversation_ids = dropdown_conversation_ids
        for conversation_id in conversation_ids:
            self.conversation.addItem(conversation_id)  # Changed this line

        # set the dropdown menu and global conversation id variable to the first conversation id
        self.conversation.setCurrentText(conversation_ids[0])  # Changed this line
        conversation_id = conversation_ids[0]  # Changed this line
        
        
    
    def new_chat(self):
        # this function is called when the new chat button is clicked. it is passed the self variable and database
        global conversation_id
        new_conversation_id = database_module.new_conversation_id(self)

        # call the add_conversation_id function from the database file
        database_module.add_conversation_id(self, new_conversation_id)
        
        # add the new conversation id to the dropdown menu 
        self.conversation.addItem(new_conversation_id)
        # set the dropdown menu to the new conversation id
        self.conversation.setCurrentText(new_conversation_id)
        
        conversation_id = new_conversation_id
        # switch the chat history to the new conversation id using the switch conversation function in this file
        self.switch_conversation()
        # set the global conversation id variable to the new conversation id


    def archive(self, conversation_id):
        # call the archive function from the database file
        database_module.archive(self, conversation_id)
        # remove the conversation id from the dropdown menu
        self.conversation.removeItem(self.conversation.findText(conversation_id))


    def populate_branch_tree(self, conversation_id):
        # Fetch the root conversation from the database
        if conversation_id is None:
            conversation = database_module.get_conversation(self, conversation_id=None)
        else:
            conversation = database_module.get_conversation(self, conversation_id=conversation_id)

        if conversation is not None:
            # Add the conversation to the tree view
            
            self.add_conversation_to_tree( None, conversation)

    

def closeEvent(self, event):
    self.client.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
