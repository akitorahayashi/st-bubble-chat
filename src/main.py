import streamlit as st
from streamlit_chat import message

st.title("Bubble Chat UI")

if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.chat_input("メッセージを入力")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # ここで自前のAIロジックを呼び出す
    ai_response = f"AIが返す: {user_input}"  # 例
    st.session_state.messages.append({"role": "ai", "content": ai_response})

for msg in st.session_state.messages:
    message(msg["content"], is_user=(msg["role"] == "user"))
