import streamlit as st
from groq import Groq

# 1. Cấu hình giao diện
st.set_page_config(page_title="AI Engineering Assistant", page_icon="🚀")
st.title("🚀 Trợ lý AI Kỹ thuật (Cloud Version)")
st.caption("Chạy trên nền tảng Groq - Tốc độ siêu nhanh & Chia sẻ được")

# 2. Nhập API Key (Mở thanh menu bên trái để nhập)
api_key = st.sidebar.text_input("Nhập Groq API Key của bạn:", type="password")

if not api_key:
    st.info("Vui lòng mở menu bên trái (biểu tượng >) và nhập API Key từ Groq để bắt đầu chat!", icon="🔑")
    st.stop()

# Khởi tạo kết nối với Groq
client = Groq(api_key=api_key)

# 3. Khởi tạo bộ nhớ lưu lịch sử chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lại lịch sử tin nhắn
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Xử lý khi người dùng nhập câu hỏi
if prompt := st.chat_input("Hỏi tôi về kỹ thuật, code C/C++, tự động hóa..."):
    # Lưu tin nhắn người dùng và in ra màn hình
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Khung hiển thị tin nhắn của AI
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Gọi AI từ Groq Cloud với Model mới nhất hiện tại
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            )
            
            # Tạo hiệu ứng chữ chạy ra từ từ
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")
            
            # Xóa dấu nhấp nháy khi gõ xong
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            # Thông báo lỗi trực tiếp trên giao diện nếu có sự cố
            st.error(f"Đã xảy ra lỗi kết nối: {e}")
    
    # Lưu câu trả lời của AI vào bộ nhớ
    st.session_state.messages.append({"role": "assistant", "content": full_response})
