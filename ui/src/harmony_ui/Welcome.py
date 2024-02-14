#! /usr/bin/env python3

import re
import streamlit as st

from toolkit.constants import ENVIRONMENT
from   toolkit.utils import \
     display_service

from toolkit.help import (
     summary_help, harmony_help, help_help
)


def configure(subtitle=''):
    """
    Configure main page of app
    """
    if subtitle: subtitle = ": " + subtitle
    st.set_page_config(
        page_title='Cipher Harmony' + subtitle,
        layout='wide',
        page_icon=':smiley:',
        initial_sidebar_state='auto')

    # Hide Streamlit developer-oriented menu in production, to reduce user confusion
    if 'production' == ENVIRONMENT:
        hide_streamlit_style = '''
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        '''
        st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

configure()

st.markdown({
    'production': '#  Cipher-Harmony: Comparison Apps',
    'edge': '#  Cipher-Harmony: Comparison EDGE',
    'development': '#  Cipher-Harmony: Comparison DEV'
}.get(ENVIRONMENT, '# A nice nautical name UNKNOWN'))

st.warning('Please select a sequencing exploration avenue in the sidebar.')
applications = {
    'Summary': 'Experiment re-processing status using version 7.1.0',
    "Harmony": 'Cipher comparsion of experiments',
    'Help': 'A help page to describe the plots from harmony',
}

applications.update(
    {}
    if 'edge' == ENVIRONMENT
    else {}
)
    
for app, desc in applications.items():
    print (app)
    print (desc)
    with st.expander(f'{app}: {desc}'):
        app_name = re.sub('[^0-9a-zA-Z]+', '', app).lower()
        func = eval(f'{app_name}_help')
        func()
    
with st.sidebar.container():
    display_service()