import json
import os
import openai
import streamlit as st
from dotenv import load_dotenv
from uuid import uuid4

load_dotenv()

sbcol1, sbcol2 = st.columns([5,1])

BASE_PROMPT = [{"role": "system", "content": "You are a helpful assistant for Tanner Phillips. He's a Data Scientist, has a wife and two kids, and a PhD in education. Mainly you help him with work / personal coding projects, but he likes help with creative ideas too."}]
DATA_FILE = "conversation.json"
openai.api_key = os.getenv("OPENAI_TOKEN")


def add_to_data_file(messages):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    title = get_summary(messages)
    data.insert(0,{"id":uuid4(),"title": title, "messages": messages})

    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def clear_text():
    st.session_state["prompt_text"] = ""

def show_messages(text):
    messages_str = [
    f"#### {'Tanner' if _['role']=='user' else 'AI'}: \n \n {_['content']}" 
    for _ in st.session_state["messages"][1:]
    ]
    text.markdown(str("\n \n  ".join(messages_str)))

def get_summary(messages, prompt = [{"role": "system", "content": "You write titles for conversation to save to a file. Do not make conversation, only write the title text. These are title meant to make them easy to select. So for a long conversation about a python app write something like 'appending items to lists in streamlit' or whatever seems most relevent."}]):
    text = "\n".join([m["content"] for m in messages if m["role"] != "system"])
    prompt += [{"role": "user", "content": f"Write a title for this conversation: \n\n{text}\n\n"}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        temperature=0.3,
        max_tokens=20,
    )
    summary = response["choices"][0]["message"]["content"]
    return summary

def load_conversation_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        return data
    else:
        return []

def show_saved_conversations():
    st.sidebar.markdown("## Saved Conversations")
    data = load_conversation_data()
    for conversation in data:
        title = conversation["title"]
        with sbcol1:
            st.sidebar.button(title, key=f"{title}_button", on_click=load_conversation, args=[conversation["messages"]])
        with sbcol2:
            st.sidebar.button("X", key = f'{title}')
def load_conversation(messages):
    st.session_state["messages"] = messages
    show_messages(text)

with st.sidebar:
    show_saved_conversations()
    st.markdown("---")

if "messages" not in st.session_state:
    st.session_state["messages"] = BASE_PROMPT

st.header("STREAMLIT GPT-3 CHATBOT")

text = st.empty()
show_messages(text)

prompt = st.text_area("Enter Message", key="prompt_text")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Send"):
        with st.spinner("Generating response..."):
            st.session_state["messages"] += [{"role": "user", "content": prompt}]
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=st.session_state["messages"]
            )
            message_response = response["choices"][0]["message"]["content"]
            st.session_state["messages"] += [
                {"role": "assistant", "content": message_response}
            ]
            show_messages(text)
with col2:
    if st.button("Save"):
        add_to_data_file(st.session_state["messages"])

with col3:
    if st.button("Clear"):
        st.session_state["messages"] = BASE_PROMPT
        show_messages(text)
