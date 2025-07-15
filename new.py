from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import Runnable, RunnablePassthrough, RunnableLambda
from langchain.schema.runnable.config import RunnableConfig
from langchain.memory import ConversationBufferMemory
from operator import itemgetter
from dotenv import load_dotenv
import os
from chainlit.types import ThreadDict
import chainlit as cl
from typing import Dict, Optional
from langchain_core.documents import Document
from langchain_google_community import GoogleTranslateTransformer
import vertexai
from vertexai.generative_models import GenerativeModel
from langchain_google_vertexai import ChatVertexAI

load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"

vertexai.init(project="rare-tape-382912", location="us-central1")


def setup_runnable():
    memory = cl.user_session.get("memory")  # type: ConversationBufferMemory
    model = ChatVertexAI(model="gemini-1.5-pro-001")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
             """You are a virtual helpful doctor or healthcare professional named MedLang. Your role is to provide friendly, useful, direct, complete, and scientifically-grounded answers to user questions. Follow these guidelines:

1. If the user's input is comprehensive, provide a concise, single-turn conversation for accurate answers.
2. If essential details are missing, engage in a multi-turn dialogue by asking follow-up questions to gather a thorough medical history and records.
3. Respond only to medical questions. For unrelated questions, instruct users to ask medical questions only.
4. Always reply in the language the user inputs (Arabic or English)."""),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )

    runnable = (
            RunnablePassthrough.assign(
                history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
            )
            | prompt
            | model
            | StrOutputParser()
    )
    cl.user_session.set("runnable", runnable)


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
    cl.user_session.set("memory", ConversationBufferMemory(return_messages=True))
    setup_runnable()
    await cl.Avatar(
        name="MedLang",
        path="public/MedLang.png",
    ).send()


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    memory = ConversationBufferMemory(return_messages=True)
    root_messages = [m for m in thread["steps"] if m["parentId"] == None]
    for message in root_messages:
        if message["type"] == "user_message":
            memory.chat_memory.add_user_message(message["output"])
        else:
            memory.chat_memory.add_ai_message(message["output"])

    cl.user_session.set("memory", memory)

    setup_runnable()


@cl.on_message
async def on_message(message: cl.Message):
    memory = cl.user_session.get("memory")  # type: ConversationBufferMemory

    runnable = cl.user_session.get("runnable")  # type: Runnable

    res = cl.Message(content="")

    async for stream in runnable.astream(
            {"question": message.content},
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await res.stream_token(stream)

    await res.send()

    memory.chat_memory.add_user_message(message.content)
    memory.chat_memory.add_ai_message(res.content)
