from langgraph.graph import StateGraph,START,END
from dotenv import load_dotenv
from typing import TypedDict,Literal,Annotated
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage,BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

load_dotenv()

model= ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.5,
)

class chatstate(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]

def chat_node(state:chatstate):
    messages=state['messages']
    response=model.invoke(messages)
    return { 'messages':[response]}

conn=sqlite3.connect(database="chatbot.db",check_same_thread=False)
checkpointer=SqliteSaver(conn=conn)

graph=StateGraph(chatstate)
graph.add_node('chat_node',chat_node)
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

chatbot=graph.compile(checkpointer=checkpointer)


def retrieve_all_threads():
    # give total no of checkpoints in the database
    all_threads = set()  # to store all unique thread ids

    for checkpoint in checkpointer.list(None):
        thread_id = checkpoint.config['configurable']['thread_id']
        all_threads.add(thread_id)
    return list(all_threads)




# # test
# CONFIG={'configurable':{'thread_id':'thread_1'}}

# response=chatbot.invoke({'messages':[HumanMessage(content='make a rhyming verse with my name')]},
#                         config=CONFIG)

# print(response)