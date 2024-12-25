import streamlit as st
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import HumanMessage, SystemMessage
from openai import OpenAI
api_key = st.secrets["api_key"]
openai_api_key = st.secrets["openai_api_key"]
OpenAI.api_key = openai_api_key
client = OpenAI(api_key=openai_api_key)
speech_file_path = "speech.mp3"
load_dotenv()
st.title("Mental Health Chatbot")
llm = ChatGroq(api_key=api_key, model = "llama-3.3-70b-versatile")
system_prompt = ("You are a mental health chatbot . Your role is to provide empathetic, expert-level emotional support in a way that feels approachable, relatable, and comforting and you should feel more like a friend than a therapist"
"Be deeply empathetic, validating emotions while offering practical guidance grounded in proven mental health techniques."
"Keep your responses concise yet impactful, using Gen Z slang, Gen X references, and internet humor effectively to make conversations engaging and approachable. NEVER STOP BEING A GENZ YOU ALWAYS SPEAK WITH SLANGS"
"Adapt your tone based on the user's emotional state—be gentle and supportive during serious moments, and light-hearted or funny when appropriate."
"Prioritize clarity, authenticity, and professionalism in all therapeutic advice."
"Strike a balance between therapy-level expertise and casual, friendly vibes. Match the user's conversational energy while maintaining a safe, judgment-free space for them to express themselves.")
if 'store' not in st.session_state:
    st.session_state.store = {}

user_input_id = st.text_input("enter your name")
def get_session_history(session_id : str)->BaseChatMessageHistory:
    if session_id not in st.session_state.store:
        st.session_state.store[session_id] = ChatMessageHistory()
    return st.session_state.store[session_id]
if user_input_id:
    chat_history = get_session_history(user_input_id)
    prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}")
    ])

    parser = StrOutputParser()
    with_message_history = RunnableWithMessageHistory(
        prompt | llm | parser,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )
    user_input = st.text_input("enter your question")
    if user_input:
        response = with_message_history.invoke({"input": user_input},
                                {"configurable": {"session_id": user_input_id}}
                            )
        response_audio = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=response,
        )
        response_audio.stream_to_file(speech_file_path)
        st.write("assistant", response) 
        st.audio(speech_file_path,format="audio/mpeg", loop=True)
        
