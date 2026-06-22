from langgraph.graph import StateGraph,START,END
from dotenv import load_dotenv
from typing import TypedDict,Literal,Annotated
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage,BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

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

checkpointer=InMemorySaver()

graph=StateGraph(chatstate)
graph.add_node('chat_node',chat_node)
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

chatbot=graph.compile(checkpointer=checkpointer)

 # streaming 
# for message_chunk,metadata in chatbot.stream(
#     {'messages':[HumanMessage(content='whats the recipe for alfredo pasta')]},
#     config={'configurable':{'thread_id':'thread_1'}},
#     stream_mode='messages'):

#     if message_chunk.content:
#         print(message_chunk.content,end=" ",flush=True)

## print(type(stream))

