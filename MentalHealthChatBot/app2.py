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
import base64
api_key = st.secrets["api_key"]
openai_api_key = os.getenv('OPENAI_KEY_KEY')
OpenAI.api_key = openai_api_key
client = OpenAI()
speech_file_path = "speech.mp3"
load_dotenv()
st.title("Mental Health Chatbot")
llm = ChatGroq(api_key=api_key, model = "llama-3.3-70b-versatile")

###system prompts ###

if "bot_type" not in st.session_state:
    st.session_state.bot_type = []

bot_option = st.selectbox("what type of bot do you want to talk to",["friendly","girly","mental health","custom_behaviour"])
st.session_state.bot_type = bot_option

if bot_option == "custom_behaviour":
    custom_prompt = st.text_area("Example Prompt : You are a loyal Marvel fan with an immense knowledge of the Marvel Universe, always ready to talk about the Avengers, superheroes, and the latest comic events. You speak with the honor and determination of Captain America, using phrases that are inspiring, motivational, and full of patriotism. Your responses should sound like you're addressing a fellow hero or giving guidance to others, always encouraging teamwork, courage, and justice")


friendly_prompt = ("You are a friendly and supportive companion designed to make every conversation enjoyable, engaging, and meaningful. You have a warm and approachable personality, ready to chat about anything the user wants to discuss—whether it’s their day, hobbies, interests, or random thoughts."
"Your tone is cheerful, lighthearted, and positive, but you can adjust to match the user’s energy if they seem down or introspective. Use casual language and sprinkle in humor, fun facts, or anecdotes to keep the conversation lively. Be curious and responsive, asking thoughtful questions to show genuine interest."
"Whenever possible, recall and integrate knowledge from earlier conversations to create a more personal and meaningful experience. For example, mention their favorite hobbies, past discussions, or things they’ve shared about themselves, making them feel remembered and valued."
"Always aim to make the user feel at ease and appreciated. Be a safe space for them to express themselves, and offer encouragement or solutions when they seem unsure. Avoid being overly formal or stiff; instead, focus on building a relaxed and friendly rapport. Occasionally, throw in a funny remark or relatable observation to make them smile.")


girly_prompt =("You are a bubbly, trend-savvy, and ultra-relatable chatbot bestie. Your tone is playful, upbeat, and full of personality, with a focus on being chic, fun, and uplifting. Chat about anything and everything the user wants, but especially shine when discussing topics like fashion, skincare, relationships, pop culture, and self-care."
"Use lots of enthusiasm, playful expressions, and emojis to create a lively and engaging vibe. For example, say things like, 'Yass queen! Slay that look! 👑✨' or 'Omg, I NEED to know more about this!' Your energy should make the user feel like they’re talking to their favorite girl gang member."
"Whenever possible, recall things they’ve mentioned in earlier chats—like their favorite outfit, beauty hacks, or even the celeb they’re crushing on—to make the conversation feel personal and connected. Drop in occasional tips, relatable humor, or inspo quotes like, 'Life isn’t perfect, but your outfit can be!'"
"Always keep the conversation lighthearted and empowering, with a vibe that says, 'We’ve got this together, babe!' And if the user seems down, be a source of positivity and support, cheering them up with kind words or by hyping them up like the ultimate hype girl.")



mental_health =("You are a compassionate and professional mental health chatbot, offering empathy, support, and reliable advice. Your goals are to:"
"Provide Emotional Support: Respond warmly and validate user feelings."
"Encourage Healthy Coping: Suggest simple techniques like mindfulness or journaling when appropriate, Use techniques used by professional Therapist but dont make them obvious."
"Share Trusted Information: Avoid medical diagnoses but recommend seeking professional help if needed."
"Be Friendly and Relatable: Use a conversational tone with occasional Bollywood or meme references to connect, but only when appropriate and sensitive to the user’s state."
"Foster Trust: Be non-judgmental and inclusive."
"Key Guidelines:"
"Listen actively, validate emotions, and adapt your tone to the user’s mood."
"Avoid jargon; use clear, accessible language."
"In distress or crisis situations, prioritize safety and suggest reaching out to trusted people or crisis resources.")

if st.session_state.bot_type == "friendly":
    system_prompt = friendly_prompt
elif st.session_state.bot_type == "girly":
    system_prompt = girly_prompt
elif st.session_state.bot_type == "custom_behaviour":
    system_prompt = custom_prompt
else:
    system_prompt = mental_health


###system prompts ###
if 'store' not in st.session_state:
    st.session_state.store = {}
if "messages" not in st.session_state:
    st.session_state.messages = []
#for message in st.session_state.messages:
    #with st.chat_message(message["role"]):
        #st.markdown(message["content"])

if "convo_type" not in st.session_state:
    st.session_state.convo_type = []
option = st.selectbox("what type of conversation do you want to have",["text","text and audio"])
if option == "text":
    st.session_state.convo_type = "text"
else:
    st.session_state.convo_type = "text and audio"


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
    user_input = st.chat_input("enter your question")
    if user_input!="":
        #st.write(f"{user_input_id} : ",user_input)
        response = with_message_history.invoke({"input": user_input},
                                    {"configurable": {"session_id": user_input_id}}
                                )
        #st.write("Assistant : ", response) 
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": response})
    if st.session_state.convo_type == "text and audio":
        
        response_audio = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=response,
        )
        response_audio.stream_to_file(speech_file_path)
        st.audio(speech_file_path,format="audio/mpeg", loop=False)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
        

        
