
import streamlit as  st
from react_agent import ReactAgent

st.title('山东大学智能服务助手')
st.divider()

if 'agent' not in st.session_state:
    st.session_state['agent'] = ReactAgent()


if 'messages' not in st.session_state:
    st.session_state['messages'] = []

for message in st.session_state['messages']:
    st.chat_message(message['role']).write(message['content'])

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = "001"

# 用户输入提示词
prompt = st.chat_input()

if prompt:
    st.chat_message('user').write(prompt)
    st.session_state['messages'].append({'role': 'user', 'content': prompt})

    # AI回复
    response_mesages = []
    res_stream = st.session_state['agent'].execute_stream(
        prompt, 
        st.session_state["thread_id"],)

    # 将消息保存在列表中，并且不改变原来的生成器
    def capure(generator, cache_list):

        for chunk in generator:
            cache_list.append(chunk)
            yield chunk

    st.chat_message('assistant').write_stream(capure(res_stream, response_mesages))
    st.session_state['messages'].append({'role': 'assistant', 'content': response_mesages[-1]})
    st.rerun()

# cd D:\01\ai\python\rag-gsg\agent_university   切换文件夹
# streamlit run app.py  运行这个程序
# ctrl C 可以在终端退出streamlit

