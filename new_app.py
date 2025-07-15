from langchain_groq import ChatGroq
from langchain.schema.runnable import RunnableConfig
from langchain.schema.messages import HumanMessage, SystemMessage, BaseMessage
from operator import itemgetter
from dotenv import load_dotenv
import chainlit as cl
from typing import Dict, Optional, List, Union, Literal
from langchain_core.documents import Document
from langchain_google_community import GoogleTranslateTransformer
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import MessagesState
import re

# Load environment variables
load_dotenv()

# Initialize Google Translate client
translator = GoogleTranslateTransformer(project_id="rare-tape-382912")


# Function to detect language
def detect_language(text):
    from google.cloud import translate_v2 as translate
    translate_client = translate.Client()
    result = translate_client.detect_language([text])
    return result[0]['language']


# Function to translate text
def translate_text(text, target_language):
    document = Document(page_content=text)
    translated_documents = translator.transform_documents([document], target_language_code=target_language)
    return translated_documents[0].page_content


# DuckDuckGo search setup
search = DuckDuckGoSearchRun()


# Wrapper function for search results
def duck_wrapper(input_text):
    try:
        search_results = search.run(f"site:webmd.com {input_text}")
        return search_results
    except Exception as e:
        return f"Error during search: {str(e)}"


# Define tools
@tool
def search_webmd(query: str):
    """useful for when you need to answer medical and pharmacological questions"""
    return duck_wrapper(query)

@tool
def translate_to_arabic(text: str):
    """translate text to Arabic"""
    return translate_text(text, "ar")

@tool
def translate_to_english(text: str):
    """translate text to English"""
    return translate_text(text, "en")

@tool
def detect_language_tool(text: str):
    """detect the language of the input text"""
    return detect_language(text)

tools = [search_webmd, translate_to_arabic, translate_to_english, detect_language_tool]

# Define the models
model = ChatGroq(model_name="llama3-70b-8192", streaming=True, max_tokens=4000)
model = model.bind_tools(tools)
final_model = ChatGroq(model_name="llama3-70b-8192", streaming=True, max_tokens=4000)
final_model = final_model.with_config(tags=["final_node"])

tool_node = ToolNode(tools=tools)

def should_continue(state: MessagesState) -> Literal["tools", "final"]:
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return "final"

def call_model(state: MessagesState):
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}

def call_final_model(state: MessagesState):
    messages = state["messages"]
    last_ai_message = messages[-1]
    
    # The system prompt is now more explicit
    system_prompt = SystemMessage(
        content="You are a helpful medical assistant. Your goal is to provide accurate and safe medical and pharmacological information. You can search WebMD, translate text between English and Arabic, and detect the language of a given text. Always prioritize user safety and provide clear, concise, and easy-to-understand information. If you are unsure about a topic, state that you are not a medical professional and advise the user to consult with a doctor."
    )
    
    # We construct a new list of messages for the final invocation
    final_messages = [system_prompt, HumanMessage(content=last_ai_message.content)]
    
    response = final_model.invoke(final_messages)
    response.id = last_ai_message.id
    return {"messages": [response]}

# Define the graph
builder = StateGraph(MessagesState)
builder.add_node("agent", call_model)
builder.add_node("tools", tool_node)
builder.add_node("final", call_final_model)
builder.add_edge(START, "agent")
builder.add_conditional_edges(
    "agent",
    should_continue,
)
builder.add_edge("tools", "agent")
builder.add_edge("final", END)
graph = builder.compile()

@cl.on_chat_start
async def on_chat_start():
    await cl.Avatar(
        name="MedLang",
        path="public/MedLang.png",
    ).send()

@cl.on_message
async def on_message(msg: cl.Message):
    config = {"configurable": {"thread_id": cl.context.session.id}}
    cb = cl.LangchainCallbackHandler()
    final_answer = cl.Message(content="")

    # The initial message to the graph now includes the system prompt
    system_prompt = SystemMessage(
        content="You are a helpful medical assistant. Your goal is to provide accurate and safe medical and pharmacological information. You can search WebMD, translate text between English and Arabic, and detect the language of a given text. Always prioritize user safety and provide clear, concise, and easy-to-understand information. If you are unsure about a topic, state that you are not a medical professional and advise the user to consult with a doctor."
    )
    
    initial_messages = [system_prompt, HumanMessage(content=msg.content)]
    
    async for output in graph.astream_events(
        {"messages": initial_messages},
        config=RunnableConfig(callbacks=[cb]),
        version="v1"
    ):
        kind = output["event"]
        if kind == "on_chat_model_stream":
            if "final_node" in output["tags"]:
                if content := output["data"]["chunk"].content:
                    await final_answer.stream_token(content)

    await final_answer.send()