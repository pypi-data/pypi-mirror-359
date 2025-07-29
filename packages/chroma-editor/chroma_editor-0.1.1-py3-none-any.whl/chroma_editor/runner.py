import os
import sys
import streamlit.web.bootstrap as st_bootstrap
import streamlit as st
from chroma_editor.app import app_run
def run_app():
    # This function is the entry point defined in pyproject.toml
    if st.runtime.exists():
        app_run()
    else:
        # Relaunch the script in a Streamlit context
        # __file__ refers to the current file (my_package/app.py)
        st_bootstrap.run(__file__, is_hello=False, args=[], flag_options={})

if __name__ == "__main__":
    run_app()