import streamlit as st
from groq import Groq

# 1. Cấu hình giao diện
st.set_page_config(page_title="AI Engineering Assistant", page_icon="🚀")
st.title("🚀 Trợ lý AI Kỹ thuật (Cloud Version)")
st.caption("Chạy trên nền tảng Groq - Tốc độ siêu nhanh & Chia sẻ được")

# 2. Nhập API Key (Khi dùng link web, bạn sẽ nhập key này để bảo mật)
api_key = st.sidebar.text_input("Nhập Groq API Key của bạn:", type="password")

if not api_key:
    st.info("Vui lòng mở menu bên trái (dấu >) và nhập API Key từ Groq để bắt đầu chat!", icon="🔑")
    st.stop()

client = Groq(api_key=api_key)

# 3. Khởi tạo lịch sử chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Xử lý chat
if prompt := st.chat_input("Hỏi tôi về kỹ thuật, code, toán học..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Gọi AI từ Groq Cloud
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        )
        
        for chunk in completion:
            content = chunk.choices[0].delta.content
            if content:
                full_response += content
                message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
