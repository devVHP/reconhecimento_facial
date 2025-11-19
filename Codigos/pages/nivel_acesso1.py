import streamlit as st
import pandas as pd
import requests
from io import StringIO

# --- Baixa arquivo CSV diretamente do Google Drive ---
file_id = "1_7cl9dcxwI4St3gFHKjhlv4XUFdVY4lq"
url = f"https://drive.google.com/uc?id={file_id}"
response = requests.get(url)
response.raise_for_status()  # Garante que o download foi bem-sucedido

# --- Remove sidebar e configura layout da página ---
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

st.set_page_config(
    page_title="Sistema de Biometria Facial",
    page_icon="👤",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Função para converter dataframe para CSV e permitir download
def convert_for_download(df):
    return df.to_csv().encode("utf-8")


try:
    # --- Controle de permissão via session_state ---
    if st.session_state.permissao == "publico":

        # Lê CSV vindo do Google Drive
        df = pd.read_csv(StringIO(response.text), sep=';', encoding='utf-8')

        # Filtra apenas registros com classificação ambiental "I"
        df_nivel1 = df.loc[df['CLASSIFICACAO_AMBIENTAL'] == 'I']

        # Prepara CSV para download
        csv = convert_for_download(df_nivel1)

        # Botão para baixar o arquivo filtrado
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="df_publico.csv",
            mime="text/csv",
            icon=":material/download:",
            width="stretch"
        )

        # Exibe dataframe na tela
        st.dataframe(df_nivel1)

    else:
        # Usuário logado mas sem permissão
        st.markdown("Permissão negada")

# Caso não exista session_state.permissao → usuário não logado
except:
    st.switch_page("app.py")