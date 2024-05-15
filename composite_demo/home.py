import time

import streamlit as st

from login_utility import login_out
import demo_chat

def test():
    st.balloons()

# 登入后的页面
def user_page():
    hide_st_style = """
            <style>
            footer {visibility: hidden;}
            #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
    </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    DEFAULT_SYSTEM_PROMPT = ''

    # Set the title of the demo
    st.title("ChatGLM3 For FIS")

    # Add your custom text here, with smaller font size
    st.markdown(
        "经过ChatGLM3-6b微调的模型，能够从金融文本中快速生成摘要，帮助您迅速获取关键信息。")

    with st.sidebar:
        with st.popover(":gear: 个人信息", use_container_width=True):
            st.text('昵称：{}\n用户名：{}\n邮箱：{}'.format(st.session_state.user_info['name'], st.session_state.user_info['username'], st.session_state.user_info['email']))
            logout_click = st.button("登出", use_container_width=True)
            if logout_click:
                login_out()
        with st.expander(":hammer_and_wrench: :violet[**参数**]", expanded=False):
            top_p = st.slider(
                'top_p', 0.0, 1.0, 0.7, step=0.01
            )
            temperature = st.slider(
                'temperature', 0.0, 1.5, 0.5, step=0.01
            )
            repetition_penalty = st.slider(
                'repetition_penalty', 0.0, 2.0, 1.1, step=0.01
            )
            max_new_token = st.slider(
                'Output length', 5, 1024, 512, step=64
            )

        cols = st.columns(2)
        retry_btn = cols[0]
        clear_history = cols[1].button("清空历史", use_container_width=True)
        retry = retry_btn.button("重新生成", use_container_width=True)

        with st.expander(":ballot_box_with_ballot: :blue[**系统提示词**]", expanded=False):
            system_prompt = st.text_area(
                label="System Prompt",
                height=200,
                value=DEFAULT_SYSTEM_PROMPT,
                label_visibility="collapsed"
            )

        model_type = st.selectbox(':books: **选择模型**', ['FIS-ChatGLM3', 'Base with Prompt'], index=0, disabled=True)

    prompt_text = st.chat_input(
        '请输入文本',
        key='chat_input',
    )

    if clear_history or retry:
        prompt_text = ""

    # st.stop()
    demo_chat.main(
        retry=retry,
        top_p=top_p,
        temperature=temperature,
        prompt_text=prompt_text,
        system_prompt=system_prompt,
        repetition_penalty=repetition_penalty,
        max_new_tokens=max_new_token
    )
