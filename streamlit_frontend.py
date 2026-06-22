import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage,AIMessage

CONFIG={'configurable':{'thread_id':'thread_1'}}

# streamlit has a component session state which  is a dictionary-like object that persists variables across rerun cycles for an individual user session.
if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]


for msg in st.session_state['message_history']:
    with st.chat_message(msg['role']):
        st.text(msg['content'])
    
user_input=st.chat_input('type here')

if user_input:

    # adding user msg to msg history
    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # TAKING ANSWER FROM THE AI BASED ON THE USER INPUT
    response=chatbot.invoke({'messages':[HumanMessage(content=user_input)]},config=CONFIG)
    # storing the response in variable ai_msg
    ai_msg=response['messages'][-1].content
    # adding ai_msg to msg history
    st.session_state['message_history'].append({'role':'assistant','content':ai_msg})
    with st.chat_message('assistant'):
        st.text(ai_msg)