import streamlit as st
import requests
import json
import os

# 配置后端 API 地址
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:9000/rag")

st.set_page_config(
    page_title="尝尝咸淡 RAG",
    page_icon="🍽️",
    layout="wide"
)

st.title("🍽️ 尝尝咸淡 - 智能食谱问答")

# 初始化 Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# 侧边栏：系统状态与管理
with st.sidebar:
    st.header("系统管理")
    
    # 检查健康状态
    try:
        health_res = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if health_res.status_code == 200:
            status = health_res.json()
            if status.get("initialized"):
                st.success("🟢 系统已就绪")
            else:
                st.warning("🟡 系统初始化中或出错")
                if status.get("error"):
                    st.error(f"错误: {status['error']}")
        else:
            st.error(f"🔴 服务状态异常: {health_res.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("🔴 无法连接到后端服务")

    st.divider()
    
    # 重建知识库按钮
    if st.button("🔄 重建知识库", help="重新加载文档并构建向量索引"):
        with st.spinner("正在构建知识库，请稍候..."):
            try:
                build_res = requests.post(f"{API_BASE_URL}/build", timeout=300)
                if build_res.status_code == 200:
                    st.success("知识库构建成功！")
                else:
                    st.error(f"构建失败: {build_res.text}")
            except Exception as e:
                st.error(f"请求失败: {e}")

# 显示聊天历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 聊天输入
if prompt := st.chat_input("今天想吃点什么？"):
    # 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 获取回答
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            with st.spinner("思考中..."):
                response = requests.post(
                    f"{API_BASE_URL}/ask",
                    json={"question": prompt, "stream": False},
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    full_response = data.get("answer", "抱歉，我没有找到答案。")
                else:
                    full_response = f"请求出错 (Status: {response.status_code}): {response.text}"
        except Exception as e:
            full_response = f"发生错误: {str(e)}"
            
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
