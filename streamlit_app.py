import streamlit as st
from groq import Groq

# 1. Cấu hình giao diện tổng thể (Giống Gemini)
st.set_page_config(page_title="AI Engineering Assistant", page_icon="✨", layout="wide")

# Tiêm CSS để chỉnh sửa giao diện giống các AI hiện đại
st.markdown("""
<style>
    /* Ẩn menu và footer mặc định của Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Chỉnh màu nền và viền bong bóng chat */
    .stChatMessage {
        background-color: #f9fbfd;
        border-radius: 15px;
        padding: 10px 20px;
        margin-bottom: 10px;
        border: 1px solid #e0e4e8;
    }
    
    /* Tùy chỉnh thanh Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f0f4f8;
    }
</style>
""", unsafe_allow_html=True)

# 2. Khởi tạo sổ lưu trữ "Đa phiên" (Nhiều cuộc trò chuyện)
if "all_chats" not in st.session_state:
    # Sổ lưu trữ chính, bắt đầu với 1 trang
    st.session_state.all_chats = {"Cuộc trò chuyện 1": []} 
if "current_chat" not in st.session_state:
    # Đánh dấu đang ở trang nào
    st.session_state.current_chat = "Cuộc trò chuyện 1"

# 3. THIẾT KẾ THANH SIDEBAR (Menu bên trái)
with st.sidebar:
    st.title("✨ Trợ lý AI Kỹ thuật")
    st.caption("Giao diện Modern UI - Tốc độ siêu cao")
    
    # Nút tạo cuộc trò chuyện mới
    if st.button("➕ Cuộc trò chuyện mới", use_container_width=True):
        new_chat_name = f"Cuộc trò chuyện {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[new_chat_name] = []
        st.session_state.current_chat = new_chat_name
    
    st.divider()
    
    # Nơi để chọn và chuyển đổi giữa các cuộc trò chuyện cũ
    st.subheader("Lịch sử chat")
    selected_chat = st.radio(
        "Danh sách:", 
        list(st.session_state.all_chats.keys()), 
        index=list(st.session_state.all_chats.keys()).index(st.session_state.current_chat),
        label_visibility="collapsed"
    )
    st.session_state.current_chat = selected_chat
    
    st.divider()
    
    # Khung nhập API Key
    api_key = st.text_input("🔑 Nhập Groq API Key:", type="password")

# Kiểm tra API Key
if not api_key:
    st.warning("Vui lòng nhập API Key ở thanh bên trái để bắt đầu!")
    st.stop()

client = Groq(api_key=api_key)

# 4. HIỂN THỊ NỘI DUNG CUỘC TRÒ CHUYỆN HIỆN TẠI
# Lấy nội dung của cuộc trò chuyện đang được chọn
current_messages = st.session_state.all_chats[st.session_state.current_chat]

# Hiển thị lại các tin nhắn cũ trong phiên này
for message in current_messages:
    # Bỏ qua system prompt khi in ra màn hình
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 5. XỬ LÝ KHI NGƯỜI DÙNG NHẬP CÂU HỎI MỚI
if prompt := st.chat_input("Nhập câu hỏi (Ví dụ: Viết code Arduino, phân tích LQR...)"):
    
    # In câu hỏi ra màn hình
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Thêm câu hỏi vào bộ nhớ của cuộc trò chuyện hiện tại
    current_messages.append({"role": "user", "content": prompt})

    # Cài đặt System Prompt ép AI phải định dạng Code để bật nút Copy
    system_prompt = {
        "role": "system", 
        "content": "Bạn là một chuyên gia kỹ thuật. Luôn bọc các đoạn mã nguồn bằng Markdown (ví dụ ```c) để hệ thống tự động hiển thị nút sao chép code."
    }
    
    # Chuẩn bị gói dữ liệu gửi đi (kèm theo system prompt)
    messages_to_send = [system_prompt] + current_messages

    # Giao tiếp với AI
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_to_send,
                stream=True,
            )
            
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"Lỗi hệ thống: {e}")
    
    # Lưu câu trả lời vào bộ nhớ của cuộc trò chuyện hiện tại
    current_messages.append({"role": "assistant", "content": full_response})
