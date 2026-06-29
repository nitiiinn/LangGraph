import streamlit as st
from langgraph_tool_backend import chatbot,retrieve_all_threads
from langchain_core.messages import HumanMessage,AIMessage
import uuid


# *****************UTILITY FUNCTIONS********************
def generate_thread_id():
    thread_id = uuid.uuid4()
    return str(thread_id)

def reset_chat():
    thread_id=generate_thread_id()
    st.session_state['thread_id']=thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history']=[]

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])



# ******************************SESSION SETUP********************************
# streamlit has a component session state which  is a dictionary-like object that persists variables across rerun cycles for an individual user session.
if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]
if 'thread_id' not in st.session_state or not isinstance(st.session_state['thread_id'], str):
    st.session_state['thread_id']=generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads']=retrieve_all_threads()

add_thread(st.session_state['thread_id'])


# ******************************SIDEBAR UI****************************

st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()


st.sidebar.button('My Conversations')

for thread_id in st.session_state['chat_threads'][::-1]:
 if st.sidebar.button(str(thread_id)):
     st.session_state['thread_id']=thread_id
     messages=load_conversation(thread_id)
     temp_messages = []
     for msg in messages:
         if isinstance(msg, HumanMessage):
                role = 'user'
         else:
             role = 'assistant'
         temp_messages.append({'role': role, 'content': msg.content})

     st.session_state['message_history'] = temp_messages



# ********************************MAIN UI*****************************
for msg in st.session_state['message_history']:
    with st.chat_message(msg['role']):
        st.text(msg['content'])
    
user_input=st.chat_input('type here')

if user_input:

    # adding user msg to msg history
    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # CONFIG={'configurable':{'thread_id':st.session_state['thread_id']}}
    
    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {
            "thread_id": st.session_state["thread_id"]
        },
        'run_name': 'chat_turn',
    }

    # TAKING ANSWER FROM THE AI BASED ON THE USER INPUT and displaying it using streaming too
    with st.chat_message('assistant'):
        ai_msg=st.write_stream(message_chunk.content for message_chunk,metadata in  chatbot.stream(
            {'messages': [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode='messages'
            )
        )
    st.session_state['message_history'].append({'role':'assistant','content':ai_msg})
