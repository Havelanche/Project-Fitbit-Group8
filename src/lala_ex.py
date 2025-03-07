import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import plotly.express as px

def print_random_message():
    print("lala wants to make friend with python.")


st.set_page_config(
    page_title = "lala's dashboard", 
    layout = "wide", page_icon="🚸",
    initial_sidebar_state = "expanded")

st.write("Hello, let's learn how to build a streeamlit app together")
st.title("This is the app title")
st.header("This is the header")
st.markdown("This is the markdown")
st.subheader("This is the subheader")
st.caption("This is the caption")
st.sidebar.title("Sidebar Title")
st.sidebar.markdown("This is the sidebar content")
st.sidebar.button("Click me!")
st.sidebar.radio('Pick your sidebar gender', ['Male', 'Female'])