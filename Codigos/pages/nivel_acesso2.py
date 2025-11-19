import streamlit as st
import pandas as pd
import requests
from io import StringIO

# --- Download do arquivo CSV no Google Drive ---
file_id = "1_7cl9dcxwI4St3gFHKjhlv4XUFdVY4lq"
url = f"https://drive.google.com/uc?id={file_id}"
response = requests.get(url)           # Faz requisição HTTP
response.raise_for_status()            # Garante que não houve erro no download

# --- Remove a sidebar e botões da UI padrão do Streamlit ---
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

# --- Configurações da página ---
st.set_page_config(
    page_title="Sistema de Biometria Facial",
    page_icon="👤",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Converte DataFrame para CSV para permitir download ---
def convert_for_download(df):
    return df.to_csv().encode("utf-8")


try:
    # --- Verifica permissão do usuário (apenas 'diretores' podem acessar esta página) ---
    if st.session_state.permissao == "diretores":

        # Lê CSV baixado da URL
        df = pd.read_csv(StringIO(response.text), sep=';', encoding='utf-8')

        # Filtra somente registros com classificação ambiental I ou II
        df_nivel2 = df.loc[df['CLASSIFICACAO_AMBIENTAL'].isin(['I', 'II'])]

        # Converte o dataframe filtrado para CSV
        csv = convert_for_download(df_nivel2)

        # Botão para baixar o arquivo filtrado
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="df_diretores.csv",
            mime="text/csv",
            icon=":material/download:",
            width="stretch"
        )

        # Exibe a tabela filtrada na tela
        st.dataframe(df_nivel2)

    else:
        # Caso o usuário esteja logado mas não tenha a permissão necessária
        st.markdown("Permissão negada")

# Caso o usuário tente acessar a página diretamente sem login ou sem session_state configurado
except:
    st.switch_page("app.py")
