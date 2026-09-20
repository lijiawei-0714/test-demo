import streamlit as st
import os#调用大模型
from openai import OpenAI#调用大模型
from openai.types.beta import assistant
from datetime import datetime

st.set_page_config(
    page_title="AI Partner",
    page_icon="💕",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
    }
)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("AI Partner")
    st.markdown("### 请输入访问密码")
    password = st.text_input("lft051203", type="password")
    if st.button("进入"):
        if password == "lft051203":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("密码错误，请联系管理员获取访问权限")
    st.stop()

st.title("AI Partner")

st.logo("resource/logo.jpg")

# 侧边栏设置
with st.sidebar:
    st.header("面试官设置")
    interviewer_name = st.text_input("面试官名称", value="HR小李")
    personality = st.selectbox("面试官性格", ["温和友善", "严肃认真", "幽默风趣", "专业严谨", "热情开朗"])

    st.divider()

    if "conversations" not in st.session_state:
        st.session_state.conversations = []
    if "current_index" not in st.session_state:
        st.session_state.current_index = -1
    if "is_modified" not in st.session_state:
        st.session_state.is_modified = False

    if st.button("开启一个新对话", use_container_width=True):
        if st.session_state.messages and st.session_state.is_modified:
            save_time = datetime.now().strftime("%m-%d %H:%M")
            st.session_state.conversations.append({
                "title": f"💬 {save_time}",
                "messages": st.session_state.messages.copy()
            })
            st.session_state.current_index = len(st.session_state.conversations) - 1
        st.session_state.messages = []
        st.session_state.is_modified = False
        st.rerun()

    if st.session_state.conversations:
        st.subheader("历史对话")
        for i, conv in enumerate(st.session_state.conversations):
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(conv["title"], key=f"conv_{i}", use_container_width=True):
                    st.session_state.messages = conv["messages"].copy()
                    st.session_state.current_index = i
                    st.session_state.is_modified = False
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{i}", use_container_width=True):
                    st.session_state.conversations.pop(i)
                    if st.session_state.current_index >= len(st.session_state.conversations):
                        st.session_state.current_index = len(st.session_state.conversations) - 1
                    st.rerun()

#调用api
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")

assistant_prompt = f'''
你是面试官{interviewer_name},负责面试AI应用开发的岗位,请完全带入HR的角色
规则：
1. 每次只回一条消息
2. 禁止任何场景或状态描述性文字
3. 匹配用户的语音
4. 性格{personality}，语言简洁
5. 用符合面试官的语气进行对话
6. 指出用户的问题和不足之处
'''#提示词

if "messages" not in st.session_state:
    st.session_state.messages = []#创建一个空列表,记录对话内容(初始化聊天信息)
for message in st.session_state.messages:#遍历列表中的每个元素
    st.chat_message(message["role"]).write(message["content"])#根据角色显示消息(显示对话)

prompt = st.chat_input("请输入您要问的问题")
if prompt:
    st.session_state.is_modified = True
    st.chat_message("user").write(prompt)
    #存储对话内容(user)
    st.session_state.messages.append({"role": "user", "content": prompt})
    # 调用大模型进行对话
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": "system", "content": assistant_prompt},
            *st.session_state.messages,#将对话内容传递给大模型,作为上下文,解包字典形式
        ],
        stream=True,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )
    # 流式输出大模型返回的结果
    with st.chat_message("assistant"):
        full_response = st.write_stream(response)
    #存储对话内容(ai)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
