import streamlit as st
from groq import Groq
from supabase import create_client

st.set_page_config(page_title="AI Engineering Assistant", page_icon="⚙️", layout="wide")

# 1. KẾT NỐI SUPABASE (Đã dán thông tin của bạn)
SUPABASE_URL = "https://dyvczgsexqhfxqeulxus.supabase.co"
SUPABASE_KEY = "sb_publishable_bIaQbxOUbAYculAfpK8Yvg_A0MJKXgf"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. GIAO DIỆN DEVELOPER TỐI ƯU
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stChatMessage {
        border-radius: 6px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        line-height: 1.6;
    }
    
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        background-color: #ffffff !important;
        border: 1px solid #e1e4e8;
        border-right: 4px solid #2ea44f;
    }
    
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
        background-color: #f6f8fa !important;
        border: 1px solid #e1e4e8;
        border-left: 4px solid #0366d6;
    }
    
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e1e4e8;
    }
    
    /* Mở rộng khung hiển thị code và làm nổi bật */
    pre {
        background-color: #282c34 !important;
        color: #abb2bf !important;
        border-radius: 6px;
        padding: 15px;
    }
    code {
        color: #e06c75;
        background-color: rgba(27,31,35,0.05);
        border-radius: 3px;
        font-family: 'Fira Code', Consolas, monospace;
    }
</style>
""", unsafe_allow_html=True)

# 3. YÊU CẦU ĐĂNG NHẬP
with st.sidebar:
    st.title("⚙️ AI Kỹ thuật Pro")
    st.caption("Workspace Lập trình & Điều khiển Tự động")
    user_id = st.text_input("👤 ID Kỹ sư:", placeholder="Nhập ID cá nhân...")
    api_key = st.text_input("🔑 Groq API Key:", type="password")
    st.divider()

if not user_id or not api_key:
    st.info("Vui lòng mở menu bên trái (nút >) nhập ID và API Key để kích hoạt Workspace.")
    st.stop()

client = Groq(api_key=api_key)

# 4. TẢI DỮ LIỆU TỪ DATABASE
if "all_chats" not in st.session_state:
    response = supabase.table("chat_history").select("*").eq("user_id", user_id).order("created_at").execute()
    st.session_state.all_chats = {"Workspace 1": []}
    
    for row in response.data:
        c_name = row.get("chat_name", "Workspace 1")
        if c_name not in st.session_state.all_chats:
            st.session_state.all_chats[c_name] = []
        st.session_state.all_chats[c_name].append({"role": row["role"], "content": row["content"]})

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Workspace 1"

# 5. QUẢN LÝ WORKSPACE BÊN TRÁI
with st.sidebar:
    if st.button("➕ Mở Workspace mới", use_container_width=True):
        new_chat_name = f"Workspace {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[new_chat_name] = []
        st.session_state.current_chat = new_chat_name
    
    st.divider()
    selected_chat = st.radio(
        "Danh sách dự án:", 
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

# 7. XỬ LÝ CHAT VỚI BỘ TƯ DUY KỸ SƯ TRƯỞNG
if prompt := st.chat_input("Nhập yêu cầu phân tích hệ thống, thuật toán điều khiển, Code C++..."):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    current_messages.append({"role": "user", "content": prompt})

    supabase.table("chat_history").insert({
        "user_id": user_id, 
        "role": "user", 
        "content": prompt,
        "chat_name": st.session_state.current_chat
    }).execute()

    # BỘ NÃO V.3 MAX: Ép AI suy nghĩ sâu và tuân thủ chuẩn code công nghiệp
    system_prompt = {
        "role": "system", 
        "content": """Bạn là một Chuyên gia Kỹ sư Cơ điện tử & Lập trình Hệ thống nhúng cấp cao.
        Chuyên môn sâu: Vi điều khiển (đặc biệt là dòng ESP32), thuật toán điều khiển tự động (PID lồng nhau, LQR, bộ lọc dữ liệu), giao tiếp ngoại vi (I2C, SPI) và xử lý dữ liệu cảm biến thời gian thực.

        QUY TRÌNH TƯ DUY VÀ VIẾT CODE BẮT BUỘC CỦA BẠN:
        1. PHÂN TÍCH: Trình bày ngắn gọn logic toán học, sơ đồ khối, hoặc thuật toán trước khi viết code.
        2. KIẾN TRÚC CODE CHUYÊN NGHIỆP:
           - TUYỆT ĐỐI KHÔNG dùng hàm delay() gây nghẽn (blocking). Bắt buộc dùng millis(), micros() hoặc Ngắt (Interrupts / Timer) cho các tác vụ định thời.
           - Chia code thành các hàm nhỏ (modular), rành mạch. Sử dụng biến cấu trúc (struct) nếu quản lý nhiều tham số.
           - Áp dụng kỹ thuật State Machine (Máy trạng thái) cho các quy trình tuần tự.
        3. CHẤT LƯỢNG CODE: 
           - Code phải sạch, tối ưu bộ nhớ. Dùng các kiểu dữ liệu chuẩn xác (uint8_t, int16_t, float).
           - Có comment tiếng Việt chi tiết ở các phần tính toán quan trọng.
           - Xử lý các điều kiện biên (ràng buộc tín hiệu đầu ra, chống bão hòa tích phân - anti-windup cho PID).
        4. NGÔN NGỮ: Chỉ trả lời bằng Tiếng Việt chuẩn xác. Bọc mã nguồn trong ```cpp hoặc ```python.
        """
    }
    
    messages_to_send = [system_prompt] + current_messages

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Tăng nhẹ temperature để AI có thể "sáng tạo" các thuật toán tốt hơn, thay vì quá cứng nhắc
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_to_send,
                stream=True,
                temperature=0.3,
                max_tokens=4096 
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
        "user_id": user_id, 
        "role": "assistant", 
        "content": full_response,
        "chat_name": st.session_state.current_chat
    }).execute()
