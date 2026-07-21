import streamlit as st
from contextlib import contextmanager


@contextmanager
def loading(message="Loading..."):

    with st.spinner(message):
        yield