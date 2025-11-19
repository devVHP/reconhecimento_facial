import streamlit as st
import sqlite3
import cv2
import numpy as np
from time import sleep
from utils import (
    carregar_imagem_sqlite,
    verificar_acesso,
    verificar_usuario,
    criar_usuario,
    analyze_face_components,
    verificar_acesso_biometrico
)

# --- Configurações de layout e estilo ---
# Remove a sidebar e controles de colapso do Streamlit
st.markdown("""
            <style>
            [data-testid="stSidebar"] { display: none }
            [data-testid="collapsedControl"] { display: none }
            </style>
            """, unsafe_allow_html=True)

# Define título, ícone e layout da página
st.set_page_config(page_title="Sistema de Biometria Facial", page_icon="👤", layout="centered", initial_sidebar_state="collapsed")

# Conexão com o banco de dados SQLite
con = sqlite3.connect("./banco_biometria.sqlite")
cur = con.cursor()

# --- Session state ---
# Guarda informações entre interações da interface
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'usuario' not in st.session_state:
    st.session_state.usuario = ""
if 'ready_to_capture_login' not in st.session_state:
    st.session_state.ready_to_capture_login = False
if 'ready_to_capture_cadastro' not in st.session_state:
    st.session_state.ready_to_capture_cadastro = False

# Texto com instruções antes da captura facial
orientacoes = """
### 🧾 ORIENTAÇÕES
1. Ambiente bem iluminado (sem luz direta no rosto).  
2. Sem óculos, bonés, toucas ou acessórios que cubram o rosto.  
3. Rosto centralizado e posição vertical.  
4. Evite inclinar a cabeça ou se afastar da câmera.  
5. Somente o seu rosto deve aparecer na imagem.

💡 Capture a foto usando o botão abaixo.
"""

# --- Layout principal ---
st.title("Cadastro")
espaco_esq, meio, espaco_dir = st.columns([0.1, 0.8, 0.1])

with meio:

    # ------------------- CADASTRO DE USUÁRIO -------------------
    st.subheader("🧍 Cadastro de Novo Usuário")

    # Campos de entrada
    usuario = st.text_input("Crie um nome de usuário:")
    senha = st.text_input("Crie uma senha:", type="password")

    # Botão para voltar para a tela de login
    if meio.button("Voltar para Login", width="stretch"):
        st.switch_page("app.py")

    # Botão de criar usuário
    if st.button("Cadastrar", width="stretch"):
        # Verifica campos vazios
        if usuario == "" or senha == "":
            st.warning("⚠️ Preencha os campos")
        else:
            # Verifica se o usuário já existe no banco
            if verificar_usuario(usuario, cur):
                st.warning("⚠️ Nome de usuário indisponível.")
            else:
                st.success(f"✅ Usuário {usuario} disponível!")
                st.session_state.usuario = usuario
                st.session_state.ready_to_capture_cadastro = True
                st.info(orientacoes)

    # --- Captura da foto para cadastro ---
    if st.session_state.ready_to_capture_cadastro:
        st.subheader("📸 Capture seu rosto para cadastro")
        foto = st.camera_input("Tire uma foto")

        # Botão finaliza cadastro após capturar foto
        if foto is not None and st.button("Finalizar cadastro", width="stretch"):

            # Converte imagem capturada para array OpenCV
            bytes_img = foto.getvalue()
            np_arr = np.frombuffer(bytes_img, np.uint8)
            imagem = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            # Valida qualidade e posicionamento do rosto
            valid_face, msg_face = analyze_face_components(imagem)

            if not valid_face:
                st.error(msg_face)  # Erro caso o rosto não seja aceito
                st.error("Tente novamente")
                sleep(2.0)
                st.session_state.clear()
                st.rerun()
            else:
                st.success(msg_face)

                # Cria usuário e salva biometria no banco
                criar_usuario(usuario, senha, imagem, cur)
                con.commit()

                st.success("✅ Usuário criado com sucesso!")
                st.session_state.ready_to_capture_cadastro = False

                sleep(2.0)
                st.switch_page("app.py")

# --- Fechar conexão ---
con.close()
