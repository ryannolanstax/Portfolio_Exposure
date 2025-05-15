import streamlit as st
from PIL import Image


st.set_page_config(
    page_title="Welcome",
    page_icon="👋",
)

#image = Image.open('Final_Periodic_App/Stax_Banner.png')

#st.image(image)

st.write("# Welcome to Apps Data Analysis")




st.markdown(
    """
    These 3 tools allow us look at Exposure and Tariffs across the APPS portfolio

    **👈 Select an app from the sidebar** to get started

    If an app isn't working correctly, reach out to Ryan Nolan on
    Slack or email ryan.nolan@fattmerchant.com

"""
)
