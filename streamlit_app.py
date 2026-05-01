import streamlit as st
from groq import Groq

st.set_page_config(page_title="AI Engineering Assistant", page_icon="✨", layout="wide")

SUPABASE_URL = "https://dyvczgsexqhfxqeulxus.supabase.co"
SUPABASE_KEY = "sb_publishable_bIaQbxOUbAYculAfpK8Yvg_A0MJKXgf"

# CSS "Hack" để đẩy tin nhắn User sang phải và đổi màu
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stChatMessage {
        border-radius: 15px;
        padding: 10px 20px;
        margin-bottom: 10px;
    }
    
    /* Ép tin nhắn NGƯỜI DÙNG sang phải, nền xanh nhạt */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        background-color: #e3f2fd !important;
        flex-direction: row-reverse;
        text-align: right;
    }
    
    /* Tin nhắn AI bên trái, nền xám nhạt */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
        background-color: #f8f9fa !important;
        border: 1px solid #e0e4e8;
    }
    
    [data-testid="stSidebar"] {
        background-color: #f0f4f8;
    }
</style>
""", unsafe_allow_html=True)

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"Cuộc trò chuyện 1": []} 
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Cuộc trò chuyện 1"

with st.sidebar:
    st.title("✨ Trợ lý AI Kỹ thuật")
    
    if st.button("➕ Cuộc trò chuyện mới", use_container_width=True):
        new_chat_name = f"Cuộc trò chuyện {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[new_chat_name] = []
        st.session_state.current_chat = new_chat_name
    
    st.divider()
    
    selected_chat = st.radio(
        "Danh sách:", 
        list(st.session_state.all_chats.keys()), 
        index=list(st.session_state.all_chats.keys()).index(st.session_state.current_chat),
        label_visibility="collapsed"
    )
    st.session_state.current_chat = selected_chat
    
    st.divider()
    api_key = st.text_input("🔑 Nhập Groq API Key:", type="password")

if not api_key:
    st.warning("Vui lòng nhập API Key ở thanh bên trái để bắt đầu!")
    st.stop()

client = Groq(api_key=api_key)

current_messages = st.session_state.all_chats[st.session_state.current_chat]

for message in current_messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Nhập câu hỏi (Ví dụ: Viết code Arduino, phân tích LQR...)"):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    current_messages.append({"role": "user", "content": prompt})

    # LỆNH THÉP: Ép AI dùng tiếng Việt và không nói nhảm
    system_prompt = {
        "role": "system", 
        "content": "Bạn là chuyên gia kỹ thuật. TUYỆT ĐỐI KHÔNG SỬ DỤNG TIẾNG TRUNG QUỐC HOẶC KÝ TỰ LẠ. Chỉ trả lời bằng Tiếng Việt chuẩn xác. Mã nguồn C/C++ phải bọc trong ```cpp."
    }
    
    messages_to_send = [system_prompt] + current_messages

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_to_send,
                stream=True,
                temperature=0.1, # ĐẶT ĐỘ LẠNH = 0.1 ĐỂ CHỐNG "NGÁO" CHỮ TRUNG QUỐC
            )
            
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"Lỗi hệ thống: {e}")
    
    current_messages.append({"role": "assistant", "content": full_response})
