import streamlit as st
from groq import Groq
from supabase import create_client

st.set_page_config(page_title="AI Engineering Assistant", page_icon="✨", layout="wide")

# 1. KẾT NỐI SUPABASE
SUPABASE_URL = "https://dyvczgsexqhfxqeulxus.supabase.co"
SUPABASE_KEY = "sb_publishable_bIaQbxOUbAYculAfpK8Yvg_A0MJKXgf"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. CSS "Hack" (ĐÃ XÓA DÒNG `header {visibility: hidden;}` ĐỂ TRẢ LẠI NÚT `>`)
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
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

# 3. YÊU CẦU ĐĂNG NHẬP (Để AI biết đang chat với ai mà lưu dữ liệu)
with st.sidebar:
    st.title("✨ Trợ lý AI Kỹ thuật")
    user_id = st.text_input("👤 Nhập ID cá nhân (VD: An123):", placeholder="Để nhớ bạn là ai")
    api_key = st.text_input("🔑 Nhập Groq API Key:", type="password")
    st.divider()

if not user_id or not api_key:
    st.warning("Vui lòng mở menu bên trái (nút >) nhập ID cá nhân và API Key để bắt đầu!")
    st.stop()

client = Groq(api_key=api_key)

# 4. TẢI TOÀN BỘ DỮ LIỆU TỪ DATABASE XUỐNG
if "all_chats" not in st.session_state:
    # Kéo dữ liệu của User này từ Supabase
    response = supabase.table("chat_history").select("*").eq("user_id", user_id).order("created_at").execute()
    
    st.session_state.all_chats = {"Cuộc trò chuyện 1": []}
    
    # Phân loại tin nhắn cũ vào đúng từng tab "Cuộc trò chuyện"
    for row in response.data:
        c_name = row.get("chat_name", "Cuộc trò chuyện 1")
        if c_name not in st.session_state.all_chats:
            st.session_state.all_chats[c_name] = []
        st.session_state.all_chats[c_name].append({"role": row["role"], "content": row["content"]})

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Cuộc trò chuyện 1"

# 5. GIAO DIỆN QUẢN LÝ CUỘC TRÒ CHUYỆN BÊN TRÁI
with st.sidebar:
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

# 6. HIỂN THỊ TIN NHẮN
current_messages = st.session_state.all_chats[st.session_state.current_chat]

for message in current_messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 7. XỬ LÝ CHAT & LƯU LÊN CLOUD
if prompt := st.chat_input("Nhập câu hỏi (Ví dụ: Viết code Arduino, phân tích LQR...)"):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    current_messages.append({"role": "user", "content": prompt})

    # Đẩy câu hỏi của bạn lên Database ngay lập tức
    supabase.table("chat_history").insert({
        "user_id": user_id, 
        "role": "user", 
        "content": prompt,
        "chat_name": st.session_state.current_chat
    }).execute()

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
                temperature=0.1,
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
    
    # Đẩy câu trả lời của AI lên Database ngay lập tức
    supabase.table("chat_history").insert({
        "user_id": user_id, 
        "role": "assistant", 
        "content": full_response,
        "chat_name": st.session_state.current_chat
    }).execute()
