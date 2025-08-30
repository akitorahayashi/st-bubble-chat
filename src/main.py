import streamlit as st
from components.chat_ui import load_css, render_chat_messages, render_thinking_bubble, render_sidebar
from services.conversation_service import handle_ai_thinking, should_start_ai_thinking
from services.ollama_api_client import get_ollama_client

st.title("Bubble Chat UI")

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# Ollama APIクライアントを初期化（リロード時に環境変数を再読み込み）
if "ollama_client" not in st.session_state:
    st.session_state.ollama_client = get_ollama_client()

# サイドバーを描画
render_sidebar()

# AI処理中はチャット入力を無効化
is_ai_thinking = st.session_state.get("ai_thinking", False)
if is_ai_thinking:
    st.chat_input("AIが応答中です...", disabled=True)
else:
    user_input = st.chat_input("メッセージを入力")
    if user_input is not None:
        user_input = user_input.strip()
        if user_input:
            # ユーザーメッセージをすぐに追加して表示
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.rerun()

# CSSを読み込み
load_css()

# チャットメッセージを描画
render_chat_messages(st.session_state.messages)

# AIが応答中の場合の思考中吹き出し表示
if st.session_state.get("ai_thinking", False):
    st.markdown(render_thinking_bubble(), unsafe_allow_html=True)
    handle_ai_thinking(st.session_state.ollama_client)

# ユーザーメッセージが追加されたばかりで、まだAI応答がない場合
if should_start_ai_thinking():
    st.session_state.ai_thinking = True
    st.rerun()
