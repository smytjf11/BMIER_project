
$(document).ready(function () {
  // Helper function to create a paragraph element with indentation
  function createIndentedMessage(sender, text, indentLevel, conversationId) {
  const p = $('<p>');
  p.text(sender + ': ' + text);
  p.css('margin-left', indentLevel * 40 + 'px');
  p.addClass('message');

  // if the message sender is "Branches", hide the message
  if (sender === 'Branches') {
    p.hide();
  // if the sender is blank, dont add a colon after the sender name, instead just add a space
  } else if (sender === '') {
    p.text(sender + ' ' + text);

  }

  // Add a data attribute if conversationId is provided
  if (conversationId) {
    p.attr('data-conversation-id', conversationId);
  }

  return p;
}


  // Recursive function to handle branches and indentation
  async function processBranches(conversation, indentLevel) {
  const elements = [];
  let previousMessage = null;  // New variable to hold the previous message
  for (const message of conversation.messages) {
    const p = createIndentedMessage(message.sender, message.text, indentLevel);
    if (message.sender === 'Branches') {
      const branchConversationId = message.text;
      const response = await fetch('/conversation/' + branchConversationId);
      const branchData = await response.json();
      const branchElements = await processBranches(branchData, indentLevel + 1);
      for (const branchElement of branchElements) {
        branchElement.attr('data-branch-conversation-id', branchConversationId);
        elements.push(branchElement);
      }
      // Add branch conversation id to the previous message
      if (previousMessage) {
        previousMessage.attr('data-branch-conversation-id', branchConversationId);
    const iconElem = $('<img src="/static/arrow_left.png">');
    // Add the icon to the previous message at the beginning of the message with some space between the icon and the message
    previousMessage.prepend(iconElem);
    iconElem.css('margin-right', '10px');
    
        // Add click event to collapse or expand branch
        previousMessage.css('cursor', 'pointer');
        previousMessage.click(function() {
          // Toggle the display of all messages with the same branch conversation id accept the first one
          const branchId = $(this).attr('data-branch-conversation-id');
          $(`p[data-branch-conversation-id=${branchId}]:not(:first)`).toggle();
          // Toggle the display of the icon between left and down
          const icon = $(this).find('img');
          if (icon.attr('src') === '/static/arrow_left.png') {
            icon.attr('src', '/static/arrow_down.png');
          } else {
            icon.attr('src', '/static/arrow_left.png');

        }

        });
      }
    } else {
      // If it's not a "Branches" message, set it as the previous message
      previousMessage = p;
    }
    elements.push(p);
  }
  return elements;
}

  // Populate chat history when the page is loaded
  async function populateChat(conversationId) {
    const response = await fetch('/conversation/' + conversationId);
    const data = await response.json();
    $('#chat-tree').html('');
    const elements = await processBranches(data, 0);
    for (const element of elements) {
      $('#chat-tree').append(element);
    }
    //add a data attribute to the message that contains the number of the message, skip any hidden messages


    let messageNumber = 1;
    $('.message').each(function() {
      if ($(this).css('margin-left') === '0px' && $(this).css('display') !== 'none') {
        $(this).attr('data-message-id', messageNumber);
        messageNumber++;
      }
    });

    // overwrite the data attribute of messages that are not the first message in a branch with 0
    let firstBranchMessage = true;
    $('.message').each(function() {
      if ($(this).attr('data-branch-conversation-id') && firstBranchMessage) {
        firstBranchMessage = false;
      } else if ($(this).attr('data-branch-conversation-id') && !firstBranchMessage) {
        $(this).attr('data-message-id', 0);
      }
    });
      
      

    // update the conversation id global variable with the selected conversation id
    conversationId = $('#conversation').val();
    // send the conversation id to the server to update the conversation id variable there
    const response2 = await fetch('/update-selection', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        conversation_id: conversationId
      })
    });
  }
  
  

  populateChat($('#conversation').val());

  // Update chat history when conversation dropdown changes
  $('#conversation').change(async function () {
    const selectedConversationId = $(this).val();
    await populateChat(selectedConversationId);
    
    // Fetch the branch id from the last message in the conversation
    let selectedBranchId = null;
    const lastMessage = $('#chat-tree p:last-child');
    if (lastMessage.attr('data-branch-conversation-id')) {
        selectedBranchId = lastMessage.attr('data-branch-conversation-id');
    }

    // Send the selected conversation and branch ids to the server
    const response = await fetch('/update-selection', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            conversation_id: selectedConversationId,
            branch_id: selectedBranchId
        })
    });
});

let selectedItem = '';
let selectedItemId = '';

$(document).on('click', '.message', function() {
  // highlight the selected item 
  $('.message').css('background-color', '#fff');  // reset all items
  $(this).css('background-color', '#e5e5e5');  // highlight the selected item

  const fullText = $(this).text();
  selectedItem = fullText.substring(fullText.indexOf(':') + 2);
  // get the message id of the selected item by getting the data attribute of the selected item
  selectedItemId = $(this).attr('data-message-id');
  console.log('Selected item:', selectedItem);
  console.log('Selected item ID:', selectedItemId);
  
  const branchConversationId = $(this).attr('data-branch-conversation-id');
  const conversationId = $('#conversation').val();

  console.log('Conversation ID:', conversationId, 'Branch conversation ID:', branchConversationId);
  
  const ajaxCall = (url, data) => $.ajax({
    url: url,
    method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify(data),
    success: function(response) {
      console.log(`${url} sent to server:`, response);
    },
    error: function(err) {
      console.error(`Error sending ${url} to server:`, err);
    }
  });

  if (branchConversationId) {
    console.log('Selected branch conversation ID:', branchConversationId);
    ajaxCall('/set-branch-conversation-id', { 'branch_conversation_id': branchConversationId, 'conversation_id': conversationId });
  } else {
    console.log('No branch conversation ID selected');
    // Send the selected conversation id to the server to update the conversation id variable there
    // set the branch conversation id to null
    ajaxCall('/set-branch-conversation-id', { 'branch_conversation_id': null, 'conversation_id': conversationId });
    console.log('Branch conversation ID set to None');
  }
  console.log('Selected conversation ID:', conversationId);
  console.log('Selected branch conversation ID:', branchConversationId);
  console.log('Selected item ID:', selectedItemId);



  
  // Send the selectedItem to the server
  ajaxCall('/set-selected-item', { 'selected_item': selectedItem, 'selected_item_id': selectedItemId });
  

});




// Event handler for the "Submit" button
$('#submit').click(async function () {
  const inputText = $('#user-input').val().trim();
  $('#user-input').val('');

  if (!inputText) return;

  const selectedBranchConversationId = $('#branch-conversation-id').val();
  const conversationId = $('#conversation').val();


  const postData = {
    input_text: inputText,
    conversation_id: selectedBranchConversationId || conversationId,
  };

  const response = await fetch('/submit-message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(postData),
  });

  // get the user and model messages, and the flags from the response
  const { user_message: userMessage, model_message: modelMessage, is_branch: isBranch, conversation_exists: conversationExists } = await response.json();

  // print the flags to the console
  console.log('is_branch:', isBranch, 'conversation_exists:', conversationExists);

  function appendMessage(sender, text, indentation) {
    const msg = createIndentedMessage(sender, text, indentation);
    $('#chat-tree').append(msg);
  }

  // If the conversation exists, and is not a branch, append the user and model messages to the bottom of the chat history
  // add the data-message-id attribute to the messages to keep track of the message ids
  if (conversationExists && !isBranch) {
    console.log('This is not a branch. I repeat');
    // append the user and model messages to the bottom of the chat history
    // get the id of the last message in the chat history
    const lastMessageId = parseInt($('#chat-tree p:last-child').attr('data-message-id'));
    appendMessage(userMessage.sender, userMessage.text, 0);
    // add the data-message-id attribute to the messages to keep track of the message ids
    $('#chat-tree p:last-child').attr('data-message-id', lastMessageId + 1);
    
    appendMessage(modelMessage.sender, modelMessage.text, 0);
    $('#chat-tree p:last-child').attr('data-message-id', lastMessageId + 2);


  //if the conversation exists, and is a branch, append the user and model messages to the end of the branch 
  } else if (conversationExists && isBranch) {
    console.log('This is a branch');
    // find the selected item in the chat history
    const selectedItemParagraph = $(`p:contains(${selectedItem})`);

    // find the end of the branch by looking at the data-branch-conversation-id attribute of the next message
    // the end of the branch is last message with the same branch conversation id

    // get the branch conversation id of the selected item
    const branchConversationId = selectedItemParagraph.attr('data-branch-conversation-id');
    console.log('Branch conversation ID:', branchConversationId);

    // find the last message with the same branch conversation id
    const lastMessageWithSameBranchId = $(`p[data-branch-conversation-id=${branchConversationId}]:last`);
    console.log('Last message with same branch conversation ID:', lastMessageWithSameBranchId);

    // find the index of the last message with the same branch conversation id
    const lastMessageIndex = lastMessageWithSameBranchId.index();
    console.log('Index of last message with same branch conversation ID:', lastMessageIndex);

    // add the user and model messages after the last message with the same branch conversation id
    const indentedUserMessage = createIndentedMessage(userMessage.sender, userMessage.text, 1);
    lastMessageWithSameBranchId.after(indentedUserMessage);

    // set the selected item id data attribute of the user message to 0 because it is a branch
    indentedUserMessage.attr('data-message-id', 0);
    // set the branch conversation id data attribute of the user message to be the same as branch conversation id
    indentedUserMessage.attr('data-branch-conversation-id', branchConversationId);

    const indentedModelMessage = createIndentedMessage(modelMessage.sender, modelMessage.text, 1);
    indentedUserMessage.after(indentedModelMessage);
    // set the selected item id data attribute of the model message to 0 because it is a branch
    indentedModelMessage.attr('data-message-id', 0);
    // set the branch conversation id data attribute of the model message to be the same as branch conversation id
    indentedModelMessage.attr('data-branch-conversation-id', branchConversationId);

    
  //if the conversation does not exist, and is a branch, create a new branch conversation and append the user and model messages to the end of the branch
  } else if (!conversationExists && isBranch) {
    console.log('This branch does not exist');
    // find the selected item in the chat history using the selected item id
    //the selected paragraph is the paragraph with the same data-message-id as the selected item id
    const selectedItemParagraph = $(`p[data-message-id=${selectedItemId}]`);
    const indentedUserMessage = createIndentedMessage(userMessage.sender, userMessage.text, 1);
    selectedItemParagraph.after(indentedUserMessage);

    // set the selected item id data attribute of the user message to 0 because it is a branch
    indentedUserMessage.attr('data-message-id', 0);

    const indentedModelMessage = createIndentedMessage(modelMessage.sender, modelMessage.text, 1);
    indentedUserMessage.after(indentedModelMessage);
    // set the selected item id data attribute of the model message to 0 because it is a branch
    indentedModelMessage.attr('data-message-id', 0);
    // set the branch conversation id data attribute of the user message to be the same as the conversation id
    indentedUserMessage.attr('data-branch-conversation-id', conversationId);
  //if the conversation does not exist, and is not a branch, append the user and model messages to the bottom of the chat history
  } else if (!conversationExists && !isBranch) {
    console.log('This conversation does not exist');
    appendMessage(userMessage.sender, userMessage.text, 0);
    // set the selected item id data attribute of the user message to 1 because it this is the first message in the conversation
    $('#chat-tree p:last').attr('data-message-id', 1);
    appendMessage(modelMessage.sender, modelMessage.text, 0);
    // set the selected item id data attribute of the model message to 2 because it this is the second message in the conversation
    $('#chat-tree p:last').attr('data-message-id', 2);
  }
});













  // New event handler for the "New Chat" button
  $('#new-chat').click(async function () {
    const response = await fetch('/new-chat', {
      method: 'POST',
    });

    const data = await response.json();

    // Add the new conversation_id to the dropdown menu and select it
    const conversationId = data.conversation_id;
    const newOption = $('<option>');
    newOption.val(conversationId);
    newOption.text(conversationId);
    $('#conversation').append(newOption);
    $('#conversation').val(conversationId);

    // Clear the chat tree and reset the input field
    $('#chat-tree').html('');
    $('#user-input').val('');
    // add a blank row to the chat tree with no sender and no text
    $('#chat-tree').append(createIndentedMessage('', '', 0));
  });


  // Event handler for the "Archive" button
$('#archive').click(async function () {
    const conversationId = $('#conversation').val();
    const postData = {
        'conversation_id': conversationId,
    };

    const response = await fetch('/archive', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData),
    });

    const data = await response.json();
    alert(data.message);


    // Update the chat history to display either the next conversation, or if the current conversation was the last one, display the one before it in the dropdown menu
    // get the values of all the options in the dropdown menu
    const conversationIds = $('#conversation option').map(function () {
        return $(this).val();
    }).get();

    // get the value of the currently selected option
    const selectedConversationId = $('#conversation').val();
    // get the index of the currently selected option
    const selectedConversationIndex = conversationIds.indexOf(selectedConversationId);
    // check if the selected conversation is the last one in the dropdown menu
    const isLastConversation = conversationIds.indexOf(selectedConversationId) === conversationIds.length - 1;
    // if the selected conversation is the last one, select the previous conversation
    if (isLastConversation) {
        const previousConversationId = conversationIds[conversationIds.length - 2];
        $('#conversation').val(previousConversationId);
    } else {
        // if the selected conversation is not the last one, select the next conversation
        const nextConversationId = conversationIds[conversationIds.indexOf(selectedConversationId) + 1];
        $('#conversation').val(nextConversationId);
    }
    // trigger the change event on the dropdown menu to update the chat history
    $('#conversation').trigger('change');

    // remove the archived conversation from the dropdown menu
    $(`#conversation option[value=${conversationId}]`).remove();
});


$('#branch-button').click(async function () {
    console.log('Branching');
    const parent_conversation_id = $('#conversation').val();
    const postData = {
        'parent_conversation_id': parent_conversation_id,
        'selected_item': selectedItem,
        'selected_item_id': selectedItemId,
    };

    const response = await fetch('/create-branch', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData),
    });

    const data = await response.json();
    const conversation_id = data.conversation_id;  // Get the new conversation_id
    console.log('New conversation_id:', conversation_id);


});
  // Add your other event handlers (archive, etc.) here
});