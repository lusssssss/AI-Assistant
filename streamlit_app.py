import streamlit as st
import ollama

# 1. Cấu hình giao diện trang web
st.set_page_config(page_title="AI Agent - Automation", page_icon="🤖")
st.title("🤖 Trợ lý AI Kỹ thuật & Tự động hóa")
st.caption("Đã kết nối thành công lõi Llama 3 (Chạy Offline - Bảo mật 100%)")

# 2. Khởi tạo bộ nhớ (Session State) để lưu lịch sử đoạn chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Hiển thị lại toàn bộ lịch sử tin nhắn
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Khung nhập dữ liệu
if prompt := st.chat_input("Hỏi tôi về lập trình C/C++, lý thuyết tự động hóa..."):
    
    # In câu hỏi của bạn lên màn hình
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 5. Gọi AI trả lời
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Gửi toàn bộ lịch sử chat cho AI để nó nhớ ngữ cảnh
            stream = ollama.chat(
                model='llama3',
                messages=st.session_state.messages,
                stream=True # Kích hoạt chế độ gõ chữ từ từ
            )
            
            # Đọc từng chữ AI trả về và in ra màn hình
            for chunk in stream:
                full_response += chunk['message']['content']
                message_placeholder.markdown(full_response + "▌")
                
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            full_response = "Cảnh báo: Không thể kết nối với Ollama. Vui lòng kiểm tra xem phần mềm Ollama dưới góc phải màn hình máy tính (Taskbar) đã chạy chưa!"
            message_placeholder.error(full_response)
    
    # Lưu câu trả lời vào bộ nhớ
    st.session_state.messages.append({"role": "assistant", "content": full_response})