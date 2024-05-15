"""
登录验证
"""
import streamlit as st
import toml

from cookie import CookieHandler

cookie = {data: value for data, value in st.secrets.cookie.items()}
cookie_handler = CookieHandler(cookie['name'], cookie['key'], cookie['expiry_days'])

def on_change(key):
    selection = st.session_state[key]
    key += 1
    st.write(f"Selection changed to {selection}: {key}")
    
def load_user_data() -> tuple:
    """
    加载用户数据
    :return: 返回用户数据和cookie
    """
    credentials = {'usernames': {user: {} for user in st.secrets.usernames}}
    for user in st.secrets.usernames:
        credentials['usernames'][user] = dict(st.secrets.usernames[user])
    cookie = {data: value for data, value in st.secrets.cookie.items()}
    return credentials, cookie


def get_info(username):
    """
    获取用户信息存入session_state的
    :param username: 用户ID
    :return: 返回对应的值
    """
    # sql_query = f"SELECT * FROM grades_info.user_info WHERE student_id = '{username}';"
    if username is not '':
        try:
            user_infoes, _ = load_user_data()
            user_info = user_infoes['usernames'][username]
            user_info['username'] = username
            return user_info
        except:
            st.error('Incorrect username or password')
            st.stop()
    else:
        st.warning('请重新输入你的用户名和密码')
        st.stop()


def init_login():
    """
    初始化session_state
    :return: None
    """
    if 'user_info' not in st.session_state:
        st.session_state [ 'user_info' ] = None
    if 'is_register' not in st.session_state:
        st.session_state.is_register = None
    if 'logout' not in st.session_state:
        st.session_state.logout = None

def on_register():
    """
    注册状态管理
    """
    if st.session_state.is_register is None:
        st.session_state.is_register = True

def out_register():
    """
    注销状态管理
    """
    if st.session_state.is_register is True:
        st.session_state.is_register = None

# 注册页面
def register_page():
    empty = st.empty()
    with empty:
        with st.form('Register user', clear_on_submit=True):
            st.markdown('### 注册')
            new_name = st.text_input('昵称')
            new_username = st.text_input('用户名: *限制为英文字母*').lower()
            new_password = st.text_input('密码', type='password')
            new_password_repeat = st.text_input('重复密码', type='password')
            new_email = st.text_input('邮箱')
            register_btn, login_btn = st.columns([9, 1])
            register_put = register_btn.form_submit_button('注册')
            is_return = login_btn.form_submit_button('返回', on_click=out_register, 
                                                      use_container_width=True)
            if register_put:
                if new_password == new_password_repeat:
                    data = {'usernames': (load_user_data())[0]['usernames'], 'cookie': (load_user_data())[1]}
                    data['usernames'][new_username] = {'name': new_name, 'email': new_email, 'password': new_password,'logged_in': False, 'failed_login_attempts': 0, 'is_admin': False}
                    # st.write(data)
                    with open('.streamlit/secrets.toml', 'w', encoding='utf-8') as f:
                        toml.dump(data, f)
                    empty.empty()
                    out_register()
                    st.rerun()
                else:
                    st.error('Passwords do not match')
            if is_return:
                st.rerun()

def login_in():
    """
    登录注册页面 
    :return: 登录结果
    """
    global cookie_handler

    if st.session_state.is_register == True:
        register_page()
        return False

    if st.session_state ['user_info'] is not None:
        return True
    # if 'cookie_handler' in st.session_state:
    token = cookie_handler.get_cookie()
    if token is not None:
        st.session_state['user_info'] = token['user_info']
        # cookie_handler.delete_cookie()
        return True
        
    empty = st.empty()
    with empty:
        if st.session_state ['user_info'] is None:
            with st.form ("login_form", clear_on_submit=True):
                st.markdown('### 登录')
                username = st.text_input ("**用户名**")
                password = st.text_input ("**密码**", type='password')
                login_btn, register_btn = st.columns([9, 1])
                submitted = login_btn.form_submit_button ( " **登录** " )
                register = register_btn.form_submit_button("**注册**", on_click=on_register, use_container_width=True)
                # if register is True:
                #     on_register()

                try:
                    user_info = get_info(username)
                    real_password = user_info['password']

                except:
                    st.error('Unkonwn error')
                    return False

                if submitted is True and password == real_password:
                    st.session_state ['user_info'] = user_info
                    cookie_handler.set_cookie()
                    empty.empty()
                    return True
                elif submitted is True and password != real_password:
                    st.error ( "用户名或密码错误" )
                    return False


def login_out():
    """
    修改 authenticator.logout ('注销',location = 'sidebar') 退出登录选项
    :return: True表示成功退出，否则返回错误消息
    """
    global cookie_handler
    try:
        # 重置 session 状态
        st.session_state ['user_info'] = None
        st.session_state.logout = True
        cookie_handler.delete_cookie()
        # del st.session_state.cookie_handler
        # # 刷新页面
        # st.experimental_rerun ()
        return True

    except KeyError as e:
        return f"缺少配置: {e}"
    except Exception as e:
        return f"退出登录时出错: {e}"



