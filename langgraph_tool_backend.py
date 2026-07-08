from langgraph.graph import StateGraph,START,END
from dotenv import load_dotenv
from typing import TypedDict,Literal,Annotated
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage,BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver

from langgraph.prebuilt import ToolNode,tools_condition
from langchain_core.tools import tool
from duckduckgo_search import DDGS

import requests 
import random
import sqlite3

load_dotenv()

llm= ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.5,
)

@tool
def search_tool(query: str, max_results: int = 5) -> list[dict]:
    """Search the web using DuckDuckGo."""

    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=max_results))

@tool
def calculator( num1 : float,num2 : float , operation : str)-> dict:
    """
    perofrm a basic arithmetic operation on two numbers
    supported operations:add,sub,mul,div
    """
    
    try:
        if operation=='add':
            result=num1+num2
        elif operation=='sub':
            result = num1-num2
        elif operation=='mul':
            result=num1*num2
        elif operation=='div':
            result=num1/num2
        else:
            return {'error':f'unsupported operation {operation}'}
        return {'nuum1':num1,'num2':num2,'operation':operation,'result':result}
    except Exception as e:
        return {str(e)}
    
tools=[search_tool,calculator]

llm_with_tools=llm.bind_tools(tools)

class chatstate(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]



def chat_node(state:chatstate):
    messages=state['messages']  
    response=llm_with_tools.invoke(messages)
    return {'messages':[response]}

tool_node=ToolNode(tools)

graph=StateGraph(chatstate)
graph.add_node('chat_node',chat_node)
graph.add_node('tools',tool_node)

graph.add_edge(START,'chat_node')
graph.add_conditional_edges('chat_node',tools_condition)
graph.add_edge('tools','chat_node')

conn=sqlite3.connect(database="chatbot.db",check_same_thread=False)
checkpointer=SqliteSaver(conn=conn)


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