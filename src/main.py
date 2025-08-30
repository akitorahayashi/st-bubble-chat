import streamlit as st
import time

st.title("Bubble Chat UI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# サイドバーに新しいチャット開始ボタンを配置
with st.sidebar:
    st.title("チャット")
    if st.button("⟲ 新しいチャットを開始", help="履歴をクリアして新しいチャットを開始", key="new_chat_btn"):
        st.session_state.messages.clear()
        if "ai_thinking" in st.session_state:
            del st.session_state.ai_thinking
        st.rerun()

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

st.markdown("""
<style>
.chat-container {
    max-width: 800px;
    margin: 0 auto;
}

.message {
    margin: 10px 0;
    display: flex;
    align-items: flex-start;
}

.user-message {
    justify-content: flex-end;
}

.ai-message {
    justify-content: flex-start;
}

.message-content {
    max-width: 70%;
    padding: 12px 16px;
    border-radius: 20px;
    word-wrap: break-word;
}

.user-message .message-content {
    background-color: #007bff;
    color: white;
    margin-left: 20px;
}

.ai-message .message-content {
    background-color: #f1f1f1;
    color: #333;
    margin-right: 20px;
}

.avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    margin: 0 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
}

.user-avatar {
    background-color: #007bff;
    color: white;
}

.ai-avatar {
    background-color: #28a745;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# メッセージ表示
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="message user-message">
            <div class="message-content">
                {msg["content"]}
            </div>
            <div class="avatar user-avatar">
                🧑
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="message ai-message">
            <div class="avatar ai-avatar">
                🤖
            </div>
            <div class="message-content">
                {msg["content"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

# AIが応答中の場合の思考中吹き出し表示
if "ai_thinking" in st.session_state and st.session_state.ai_thinking:
    st.markdown("""
    <div class="message ai-message">
        <div class="avatar ai-avatar">
            🤖
        </div>
        <div class="message-content">
            <div style="display: flex; align-items: center;">
                <div class="thinking-dots">
                    考え中...
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # AIの応答を非同期で処理
    try:
        time.sleep(3)
        ai_response = f"AIが返す: {st.session_state.messages[-1]['content']}"
        st.session_state.messages.append({"role": "ai", "content": ai_response})
        st.session_state.ai_thinking = False
        
        # 直近 10 件に制限
        MAX_MSG = 10
        if len(st.session_state.messages) > MAX_MSG:
            st.session_state.messages = st.session_state.messages[-MAX_MSG:]
            
        st.rerun()
    except Exception as e:
        st.error("応答の生成に失敗しました。しばらくしてから再試行してください。")
        st.session_state.ai_thinking = False
        st.rerun()

# ユーザーメッセージが追加されたばかりで、まだAI応答がない場合
if (len(st.session_state.messages) > 0 and 
    st.session_state.messages[-1]["role"] == "user" and
    not st.session_state.get("ai_thinking", False)):
    st.session_state.ai_thinking = True
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
