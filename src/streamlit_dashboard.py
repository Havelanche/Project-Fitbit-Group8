import streamlit as st
import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd

st.write("Hello, let's learn how to build a streeamlit app together")
st.title("This is the app title")
st.header("This is the header")
st.markdown("This is the markdown")
st.subheader("This is the subheader")
st.caption("This is the caption")
st.code("x = 2021")
st.latex(r''' a+a r^1+a r^2+a r^3 ''')
st.checkbox('Yes')
st.button('Click Me')
gender = st.radio('Pick your gender', ['Male', 'Female'])
if gender == "Female":
    st.selectbox('Pick a fruit', ['Apple', 'Banana', 'Orange','grapes'])
if gender == 'Male':
    st.selectbox('Pick a fruit', ['Apple', 'Banana', 'Orange'])

st.multiselect('Choose a planet', ['Jupiter', 'Mars', 'Neptune'])
st.select_slider('Pick a mark', ['Bad', 'Good', 'Excellent'])
st.slider('Pick a number', 0, 50)

st.number_input('Pick a number', 0, 10)
st.text_input('Email address')
st.date_input('Traveling date')
st.time_input('School time')
st.text_area('Description')
st.file_uploader('Upload a photo')
st.color_picker('Choose your favorite color')

st.sidebar.title("Sidebar Title")
st.sidebar.markdown("This is the sidebar content")
st.sidebar.button("Click me!")
st.sidebar.radio('Pick your sidebar gender', ['Male', 'Female'])

rand = np.random.normal(1,2,size = 200)
fig, ax = plt.subplots()
ax.hist(rand, bins = 15)
st.pyplot(fig)


df = pd.DataFrame(np.random.randn(10, 2), columns=['x', 'y'])
st.line_chart(df)

