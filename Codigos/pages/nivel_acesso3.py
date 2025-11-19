import streamlit as st
import pandas as pd
import requests
from io import StringIO

# --- Download do arquivo CSV armazenado no Google Drive ---
file_id = "1_7cl9dcxwI4St3gFHKjhlv4XUFdVY4lq"
url = f"https://drive.google.com/uc?id={file_id}"

response = requests.get(url)        # Realiza o download do arquivo
response.raise_for_status()         # Garante que não ocorreu erro no download

# --- Oculta barra lateral e botões padrão do Streamlit ---
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

# --- Configurações gerais da página ---
st.set_page_config(
    page_title="Sistema de Biometria Facial",
    page_icon="👤",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Converte DataFrame para bytes CSV para permitir download ---
def convert_for_download(df):
    return df.to_csv().encode("utf-8")


try:
    # --- Verifica se o usuário logado possui permissão 'ministro' ---
    if st.session_state.permissao == "ministro":

        # Lê o CSV obtido da URL do Google Drive
        df = pd.read_csv(StringIO(response.text), sep=';', encoding='utf-8')

        # Usuários do nível "ministro" têm acesso a TODOS os dados
        df_nivel3 = df

        # Converte para CSV para download
        csv = convert_for_download(df_nivel3)

        # Botão para baixar arquivo completo
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="df_ministro.csv",
            mime="text/csv",
            icon=":material/download:",
            width="stretch"
        )

        # Exibe o DataFrame completo
        st.dataframe(df_nivel3)

    else:
        # Usuário não tem a permissão necessária
        st.markdown("Permissão negada")

# Se o usuário acessar diretamente sem estar logado ou sem session_state válido
except:
    st.switch_page("app.py")
