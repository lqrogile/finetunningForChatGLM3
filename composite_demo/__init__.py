import streamlit as st
from streamlit_option_menu import option_menu


st.set_page_config(
    page_title="ChatGLM3 FIX",
    page_icon=":ai:",
    layout="wide",
    initial_sidebar_state="auto"
)

import login_utility
# from home import user_page
import home


login_utility.init_login()
login_utility.login_in()


if st.session_state ['user_info']:
    # st.write(st.session_state)
    home.user_page()
