
import base64
import os

import streamlit as st
from react_agent import ReactAgent
from tools.agent_tools import rag as knowledge_rag
from utils.config_handler import chroma_conf
from utils.path_tool import get_abs_path

st.set_page_config(
    page_title='山东大学智能服务助手',
    page_icon='🎓',
    layout='wide',
    initial_sidebar_state='expanded',
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 6rem;
    }
    .hero {
        padding: 1.6rem 1.8rem;
        border-radius: 1rem;
        background: white;
        color: #1f2937;
        border: 1px solid #e5e7eb;
        margin-bottom: 1.2rem;
    }
    .hero h1 {
        margin: 0;
        font-size: 2rem;
    }
    .hero p {
        margin: 0.5rem 0 0;
        color: #6b7280;
    }
        </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>🎓 山东大学智能服务助手</h1>
        <p>校园政策咨询、资料检索与图片问答，一站式解决校园问题</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if 'agent' not in st.session_state:
    st.session_state['agent'] = ReactAgent()

data_path = get_abs_path(chroma_conf['data_path'])
os.makedirs(data_path, exist_ok=True)

def knowledge_file_signature():
    return tuple(
        sorted(
            (
                file_name,
                os.path.getsize(os.path.join(data_path, file_name)),
                os.path.getmtime(os.path.join(data_path, file_name)),
            )
            for file_name in os.listdir(data_path)
            if file_name.lower().endswith(('.txt', '.pdf'))
        )
    )


current_signature = knowledge_file_signature()
if st.session_state.get('knowledge_file_signature') != current_signature:
    st.session_state['knowledge_sync_result'] = (
        knowledge_rag.vector_store.sync_documents()
    )
    st.session_state['knowledge_file_signature'] = knowledge_file_signature()

with st.sidebar:
    with st.expander('📚 知识库管理', expanded=True):
        st.caption('上传或删除资料后，系统会自动同步向量库。')
        uploaded_documents = st.file_uploader(
            '上传 TXT / PDF 资料',
            type=['txt', 'pdf'],
            accept_multiple_files=True,
            help='资料保存在本地 data 文件夹',
        )
        if st.button(
            '保存并同步资料',
            type='primary',
            use_container_width=True,
        ):
            for uploaded_document in uploaded_documents or []:
                target_name = os.path.basename(uploaded_document.name)
                target_path = os.path.join(data_path, target_name)
                with open(target_path, 'wb') as file:
                    file.write(uploaded_document.getvalue())
            st.session_state['knowledge_sync_result'] = (
                knowledge_rag.vector_store.sync_documents()
            )
            st.session_state['knowledge_file_signature'] = (
                knowledge_file_signature()
            )
            st.success('知识库同步完成')

        knowledge_files = sorted(
            file_name
            for file_name in os.listdir(data_path)
            if file_name.lower().endswith(('.txt', '.pdf'))
        )
        st.metric('本地资料数量', len(knowledge_files))
        if knowledge_files:
            for file_name in knowledge_files:
                file_path = os.path.join(data_path, file_name)
                file_col, delete_col = st.columns([4, 2])
                file_col.caption(file_name)
                pending_delete = st.session_state.get('pending_delete')
                if pending_delete == file_name:
                    delete_col.warning('确定删除？')
                    confirm_col, cancel_col = st.columns(2)
                    if confirm_col.button(
                        '确认',
                        key=f'confirm_delete_{file_name}',
                        type='primary',
                    ):
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        st.session_state.pop('pending_delete', None)
                        st.session_state['knowledge_sync_result'] = (
                            knowledge_rag.vector_store.sync_documents()
                        )
                        st.session_state['knowledge_file_signature'] = (
                            knowledge_file_signature()
                        )
                        st.rerun()
                    if cancel_col.button(
                        '取消',
                        key=f'cancel_delete_{file_name}',
                    ):
                        st.session_state.pop('pending_delete', None)
                        st.rerun()
                elif delete_col.button(
                    '删除',
                    key=f'delete_{file_name}',
                ):
                    st.session_state['pending_delete'] = file_name
                    st.rerun()
        else:
            st.info('还没有资料。上传 TXT 或 PDF 后即可建立知识库。')

        if st.button('检查并同步变更', use_container_width=True):
            st.session_state['knowledge_sync_result'] = (
                knowledge_rag.vector_store.sync_documents()
            )
            st.session_state['knowledge_file_signature'] = (
                knowledge_file_signature()
            )
            st.success('变更同步完成')

        sync_result = st.session_state.get('knowledge_sync_result')
        if sync_result:
            changed_count = sum(
                len(sync_result[key])
                for key in ('added', 'updated', 'deleted')
            )
            if changed_count:
                st.info(
                    f"新增 {len(sync_result['added'])} 个，"
                    f"更新 {len(sync_result['updated'])} 个，"
                    f"删除 {len(sync_result['deleted'])} 个"
                )
            if sync_result['failed']:
                st.error(f"处理失败：{', '.join(sync_result['failed'])}")

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if not st.session_state['messages']:
    st.subheader('你好，我可以帮你做什么？')
    st.caption('可以直接提问，也可以点击下方输入框左侧的附件按钮上传图片。')

for message in st.session_state['messages']:
    with st.chat_message(message['role']):
        st.write(message['content'])
        if message.get('image'):
            st.image(message['image'])

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = "001"

chat_input = st.chat_input(
    '请输入问题',
    accept_file=True,
    file_type=['png', 'jpg', 'jpeg', 'webp'],
    max_upload_size=10,
)

if chat_input:
    if isinstance(chat_input, str):
        prompt = chat_input.strip()
        uploaded_image = None
    else:
        prompt = chat_input.text.strip()
        uploaded_image = chat_input.files[0] if chat_input.files else None

    if not prompt and uploaded_image:
        prompt = '请描述这张图片，并回答其中与山东大学相关的问题。'
    if not prompt:
        st.warning('请输入问题，或上传图片后再提交。')
        st.stop()

    image_data_url = None

    if uploaded_image:
        image_bytes = uploaded_image.getvalue()
        image_type = uploaded_image.type or 'image/jpeg'
        image_data_url = (
            f'data:{image_type};base64,'
            f'{base64.b64encode(image_bytes).decode("ascii")}'
        )

    with st.chat_message('user'):
        st.write(prompt)
        if uploaded_image:
            st.image(image_bytes, caption=uploaded_image.name)

    st.session_state['messages'].append({
        'role': 'user',
        'content': prompt,
        'image': image_bytes if uploaded_image else None,
    })

    # AI回复
    response_mesages = []
    res_stream = st.session_state['agent'].execute_stream(
        prompt,
        st.session_state["thread_id"],
        image_data_url=image_data_url,
    )

    # 将消息保存在列表中，并且不改变原来的生成器
    def capure(generator, cache_list):

        for chunk in generator:
            cache_list.append(chunk)
            yield chunk

    st.chat_message('assistant').write_stream(capure(res_stream, response_mesages))
    st.session_state['messages'].append({
        'role': 'assistant',
        'content': ''.join(response_mesages),
    })
    st.rerun()

# cd D:\01\ai\python\rag-gsg\agent_university   切换文件夹
# streamlit run app.py  运行这个程序
# ctrl C 可以在终端退出streamlit
