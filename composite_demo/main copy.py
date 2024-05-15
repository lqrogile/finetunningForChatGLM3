import time

import streamlit as st
import streamlit_authenticator as stauth
import toml

st.set_page_config(
    page_title="ChatGLM3 FTX",
    page_icon=":ai:",
    layout="wide",
    initial_sidebar_state="auto"
)

import demo_chat

# 载入用户数据
def load_user_data() -> tuple:
    credentials = {'usernames': {user: {} for user in st.secrets.usernames}}
    for user in st.secrets.usernames:
        credentials['usernames'][user] = dict(st.secrets.usernames[user])
    cookie = {data: value for data, value in st.secrets.cookie.items()}
    return credentials, cookie


def session_start_register():
    st.session_state.is_register = True


def session_end_register():
    del st.session_state.is_register


def first_login():
    st.session_state.is_first_login = True


def no_login():
    del st.session_state.is_first_login



# 定义用户登录界面
def user_login() -> stauth.Authenticate:
    if 'is_register' in st.session_state and st.session_state.is_register:
        register_page()
    login_dict = {'Form name': 'ChatGLM3 FTX Login', 'Username': 'Username', 'Password': 'Password', 'Login': 'Login'}
    credentials, cookie = load_user_data()
    authenticator = stauth.Authenticate(credentials, cookie_name=cookie['name'], cookie_key=cookie['key'],
                                        cookie_expiry_days=cookie['expiry_days'])
    # 首次登录路径
    if 'is_first_login' in st.session_state and st.session_state.is_first_login:
        st.balloons()
        no_login()
        return authenticator
    # rerun路径
    if 'authentication_status' in st.session_state and st.session_state['authentication_status']:
        authenticator.login(location='main', fields=login_dict, max_login_attempts=3, max_concurrent_users=5)
        return authenticator
    # 刷新有cookie
    if authenticator.cookie_handler.get_cookie():
        authenticator.login(location='main', fields=login_dict, max_login_attempts=3, max_concurrent_users=5)
        first_login()
        st.rerun()
    # 无cookie登录路径
    if 'authentication_status' not in st.session_state or st.session_state['authentication_status'] == False:
        placeholder = st.empty()
        with placeholder.container():
            title_text, register_btn = placeholder.columns([4, 1])
            title_text.title("ChatGLM3 For FTS")
            register_btn.button('Register', on_click=session_start_register)
    authenticator.login(location='main', fields=login_dict, max_login_attempts=3, max_concurrent_users=5)
    if st.session_state['authentication_status']:
        if 'is_first_login' not in st.session_state:
            placeholder.empty()
            first_login()
            st.rerun()
    elif st.session_state['authentication_status'] == False:
        st.error('Username/password is incorrect')
        st.stop()
    elif st.session_state['authentication_status'] is None:
        st.warning('Please enter your username and password')
        st.stop()


# 注册页面
def register_page():
    title_text, return_btn = st.columns([4, 1])
    return_btn.button('Return', on_click=session_end_register)
    title_text.title("ChatGLM3 For FTS")
    register_user_form = st.form('Register user')
    register_user_form.subheader('Register User')
    new_name = register_user_form.text_input('Name')
    new_email = register_user_form.text_input('Email')
    new_username = register_user_form.text_input('Username: *only english letters are supported*').lower()
    new_password = register_user_form.text_input('Password', type='password')
    new_password_repeat = register_user_form.text_input('Repeat password', type='password')
    if register_user_form.form_submit_button('Register'):
        if new_password == new_password_repeat:
            data = {'usernames': (load_user_data())[0]['usernames'], 'cookie': (load_user_data())[1]}
            data['usernames'][new_username] = {'name': new_name, 'email': new_email, 'password': new_password,
                                               'logged_in': False, 'failed_login_attempts': 0}
            # st.write(data)
            with open('.streamlit/secrets.toml', 'w', encoding='utf-8') as f:
                toml.dump(data, f)
            st.success('User registered')
            session_end_register()
        else:
            st.error('Passwords do not match')
            st.stop()
    else:
        st.stop()


# # 登入后的页面
# def user_page(authenticator: stauth.Authenticate):
if user_login():
    hide_st_style = """
            <style>
            footer {visibility: hidden;}
            #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
    </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    DEFAULT_SYSTEM_PROMPT = ''

    # Set the title of the demo
    st.title("ChatGLM3 For FTS")

    # Add your custom text here, with smaller font size
    st.markdown(
        "经过ChatGLM3-6b微调的模型，能够从金融文本中快速生成精炼的标题级摘要，帮助您迅速获取关键信息。")

    with st.sidebar:
        logout_btn, profile_btn = st.columns([1, 1])
        if logout_btn.button("Logout", on_click=lambda: authenticator.logout('Logout', 'unrendered'),
                             use_container_width=True):
            placeholder = st.empty()
            with placeholder.container():
                with st.spinner('Logouting...'):
                    # time.sleep(2)
                    st.success('Done!')
            placeholder.empty()
        with profile_btn.popover("Profile", use_container_width=True):
            st.text('昵称：{}\n用户名：{}\nemail：{}'.format(st.session_state['name'], st.session_state['username'],
                                                          st.secrets.usernames[st.session_state['username']][
                                                              'email'] if 'email' in st.secrets.usernames[
                                                              st.session_state['username']] else 'null'))
        with st.expander(":hammer_and_wrench: :violet[**Paramaters**]", expanded=False):
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
                'Output length', 5, 32000, 300, step=64
            )

        cols = st.columns(2)
        retry_btn = cols[0]
        clear_history = cols[1].button("Clear History", use_container_width=True)
        retry = retry_btn.button("Retry", use_container_width=True)

        model_type = st.selectbox(':books: **Choosing Model Type**', ['ChatGLM3-FTS', 'Base with Prompt'], index=0, disabled=True)
        if model_type == 'Base with Prompt':
            DEFAULT_SYSTEM_PROMPT = "# CONTEXT #\n你将得到一篇金融方面的文本，你需要从中得到一篇简短精炼的摘要，以便于金融从业者迅速从大量文本中获取关键信息。\n # " \
                                    "OBJECTIVE #\n生成一篇有助于金融从业者进行分析的摘要。\n# TONE #\n严谨\n# AUDIENCE " \
                                    "#\n这个项目的主要对象是需要从海量金融文本中迅速得到专业且精炼的摘要\n# RESPONSE #\n摘要, " \
                                    "保持简洁但全面.\n#Example#\n<text>:用户发送的原始文本\n<summary>:你总结得到的摘要\nSummarize the review " \
                                    "below,in at most 50 words."

        with st.expander(":ballot_box_with_ballot: :blue[**System Prompt**]", expanded=False):
            system_prompt = st.text_area(
                label="System Prompt",
                height=270,
                value=DEFAULT_SYSTEM_PROMPT,
                label_visibility="collapsed"
            )
    model_type = ''

    prompt_text = st.chat_input(
        '请输入文本',
        key='chat_input',
    )
    # st.stop()

    if clear_history or retry:
        prompt_text = ""

    demo_chat.main(
        retry=retry,
        top_p=top_p,
        temperature=temperature,
        prompt_text=prompt_text,
        system_prompt=system_prompt,
        repetition_penalty=repetition_penalty,
        max_new_tokens=max_new_token
    )


# def main():
#     authenticator = user_login()
#     if authenticator:
#         user_page(authenticator)


# if __name__ == "__main__":
#     # 运行主函数
#     main()
