import streamlit as st
from groq import Groq
from supabase import create_client

st.set_page_config(page_title="AI Engineering Assistant", page_icon="⚙️", layout="wide")

# 1. KẾT NỐI SUPABASE
SUPABASE_URL = "https://dyvczgsexqhfxqeulxus.supabase.co"
SUPABASE_KEY = "sb_publishable_bIaQbxOUbAYculAfpK8Yvg_A0MJKXgf"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. GIAO DIỆN
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .stChatMessage { border-radius: 6px; padding: 20px; margin-bottom: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) { background-color: #ffffff !important; border-right: 4px solid #2ea44f; }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) { background-color: #f6f8fa !important; border-left: 4px solid #0366d6; }
    [data-testid="stSidebar"] { background-color: #f9fbfd; }
    div[role="radiogroup"] > label > div:first-of-type { display: none; }
    div[role="radiogroup"] > label { padding: 8px 10px; border-radius: 6px; margin-bottom: 2px; }
    div[role="radiogroup"] > label:hover { background-color: #e1e4e8; cursor: pointer; }
    pre { background-color: #282c34 !important; color: #abb2bf !important; border-radius: 6px; padding: 15px; }
    code { color: #e06c75; background-color: rgba(27,31,35,0.05); font-family: Consolas, monospace; }
</style>
""", unsafe_allow_html=True)

# 3. YÊU CẦU ĐĂNG NHẬP & ĐỌC FILE
file_content = ""
with st.sidebar:
    st.title("⚙️ AI Kỹ thuật Pro")
    user_id = st.text_input("👤 ID Kỹ sư:", placeholder="Nhập ID cá nhân...")
    api_key = st.text_input("🔑 Groq API Key:", type="password")
    
    st.divider()
    st.markdown("📂 **Công cụ: Đọc File Code**")
    uploaded_file = st.file_uploader("Tải file .cpp, .py, .ino", type=['cpp', 'py', 'txt', 'ino', 'h', 'c'])
    if uploaded_file:
        try:
            file_content = uploaded_file.getvalue().decode("utf-8")
            st.success("Đã nạp file vào bộ nhớ AI!")
        except Exception as e:
            st.error("Không thể đọc định dạng file này.")
            
    st.divider()

if not user_id or not api_key:
    st.info("Vui lòng nhập ID và API Key để kích hoạt.")
    st.stop()

client = Groq(api_key=api_key)

# 4. TẢI DỮ LIỆU TỪ DATABASE
if "all_chats" not in st.session_state:
    response = supabase.table("chat_history").select("*").eq("user_id", user_id).order("created_at").execute()
    st.session_state.all_chats = {"Cuộc trò chuyện 1": []}
    for row in response.data:
        c_name = row.get("chat_name", "Cuộc trò chuyện 1").replace("Workspace", "Cuộc trò chuyện") 
        if c_name not in st.session_state.all_chats:
            st.session_state.all_chats[c_name] = []
        st.session_state.all_chats[c_name].append({"role": row["role"], "content": row["content"]})

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Cuộc trò chuyện 1"

# 5. GIAO DIỆN MENU
with st.sidebar:
    if st.button("➕ Cuộc trò chuyện mới", use_container_width=True):
        new_chat_name = f"Cuộc trò chuyện {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[new_chat_name] = []
        st.session_state.current_chat = new_chat_name
    
    st.markdown("📝 **Lịch sử trò chuyện**")
    selected_chat = st.radio(
        "Danh sách:", list(st.session_state.all_chats.keys()), 
        index=list(st.session_state.all_chats.keys()).index(st.session_state.current_chat), label_visibility="collapsed"
    )
    st.session_state.current_chat = selected_chat

# 6. HIỂN THỊ TIN NHẮN
current_messages = st.session_state.all_chats[st.session_state.current_chat]
for message in current_messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 7. XỬ LÝ CHAT, ĐỌC FILE VÀ QUẢN LÝ BỘ NHỚ
if prompt := st.chat_input("Nhập yêu cầu phân tích hệ thống, thuật toán điều khiển..."):
    
    # Nếu có file, gộp ruột file vào chung với câu hỏi
    full_prompt = prompt
    if file_content:
        full_prompt = f"{prompt}\n\n[DỮ LIỆU FILE ĐÍNH KÈM BẠN CẦN PHÂN TÍCH]:\n```\n{file_content}\n```"

    with st.chat_message("user"):
        st.markdown(prompt) # Chỉ hiển thị câu hỏi ngắn cho đẹp
    
    # Lưu câu hỏi đầy đủ (kèm file) vào lịch sử
    current_messages.append({"role": "user", "content": full_prompt})
    supabase.table("chat_history").insert({
        "user_id": user_id, "role": "user", "content": prompt, "chat_name": st.session_state.current_chat
    }).execute()

    system_prompt = {
        "role": "system", 
        "content": "Bạn là Chuyên gia Kỹ sư Cơ điện tử. Trả lời bằng Tiếng Việt. Phân tích sâu kiến trúc code."
    }
    
    # THUẬT TOÁN SLIDING WINDOW: Chỉ lấy 10 tin nhắn gần nhất để chống tràn bộ nhớ API
    MAX_MEMORY = 10
    recent_messages = current_messages[-MAX_MEMORY:]
    messages_to_send = [system_prompt] + recent_messages

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile", messages=messages_to_send, stream=True, temperature=0.3
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
    supabase.table("chat_history").insert({
        "user_id": user_id, "role": "assistant", "content": full_response, "chat_name": st.session_state.current_chat
    }).execute()
