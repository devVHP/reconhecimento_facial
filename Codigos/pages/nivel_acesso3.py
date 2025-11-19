import streamlit as st
import pandas as pd
import requests
from io import StringIO

file_id = "1_7cl9dcxwI4St3gFHKjhlv4XUFdVY4lq"
url = f"https://drive.google.com/uc?id={file_id}"
response = requests.get(url)
response.raise_for_status()

st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                display: none
            }

            [data-testid="collapsedControl"] {
                display: none
            }
            </style>
            """, unsafe_allow_html=True)
st.set_page_config(page_title="Sistema de Biometria Facial", page_icon="👤", layout="centered",
                   initial_sidebar_state="collapsed")

def convert_for_download(df):
    return df.to_csv().encode("utf-8")

try:
    if st.session_state.permissao == "ministro":
        df = pd.read_csv(StringIO(response.text), sep=';', encoding='utf-8')
        df_nivel3 = df
        csv = convert_for_download(df_nivel3)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="df_ministro.csv",
            mime="text/csv",
            icon=":material/download:",
            width="stretch"
        )
        st.dataframe(df_nivel3)
    else:
        st.markdown("Permissão negada")
except:
    st.switch_page("app.py")
