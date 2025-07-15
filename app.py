from langchain_groq import ChatGroq
from langchain.schema.runnable import RunnableConfig
from langchain.schema.messages import HumanMessage
from operator import itemgetter
from dotenv import load_dotenv
import chainlit as cl
from typing import Dict, Optional, List, Union
from langchain_core.documents import Document
from langchain_google_community import GoogleTranslateTransformer
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import Tool
from langgraph.prebuilt import create_react_agent
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
tools = [
    Tool(
        name="Search WebMD",
        func=duck_wrapper,
        description="useful for when you need to answer medical and pharmacological questions"
    ),
    Tool(
        name="Translate to Arabic",
        func=lambda text: translate_text(text, "ar"),
        description="translate text to Arabic"
    ),
    Tool(
        name="Translate to English",
        func=lambda text: translate_text(text, "en"),
        description="translate text to English"
    ),
    Tool(
        name="Detect Language",
        func=detect_language,
        description="detect the language of the input text"
    )
]

# Define the prompt template
llm = ChatGroq(model_name="llama3-70b-8192", streaming=True, max_tokens=4000)

agent_executor = create_react_agent(llm, tools)


@cl.password_auth_callback
def auth():
    return cl.User(identifier="test")


@cl.oauth_callback
def oauth_callback(
        provider_id: str,
        token: str,
        raw_user_data: Dict[str, str],
        default_user: cl.User,
) -> Optional[cl.User]:
    return default_user


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("message_history", [])
    await cl.Avatar(
        name="MedLang",
        path="public/MedLang.png",
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append(HumanMessage(content=message.content))

    res = cl.Message(content="")
    
    async for chunk in agent_executor.astream(
        {"messages": message_history},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        if "agent" in chunk and "messages" in chunk["agent"]:
            await res.stream_token(chunk["agent"]["messages"][-1].content)

    await res.send()
    message_history.append(res.content)