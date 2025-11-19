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
    verificar_acesso_biometrico,
    verificar_nivel_acesso
)

# --- Configurações de layout e aparência ---
st.markdown("""
            <style>
            [data-testid="stSidebar"] { display: none }
            [data-testid="collapsedControl"] { display: none }
            </style>
            """, unsafe_allow_html=True)
st.set_page_config(page_title="Sistema de Biometria Facial", page_icon="👤", layout="centered")

# --- Conexão com banco SQLite ---
con = sqlite3.connect("banco_biometria.sqlite")
cur = con.cursor()

# --- Controle de sessão (login, permissões e flags) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'permissao' not in st.session_state: st.session_state.permissao = ""
if 'usuario' not in st.session_state: st.session_state.usuario = ""
if 'ready_to_capture_login' not in st.session_state: st.session_state.ready_to_capture_login = False
if 'ready_to_capture_cadastro' not in st.session_state: st.session_state.ready_to_capture_cadastro = False

# --- Orientações para a captura facial ---
orientacoes = """
### 🧾 ORIENTAÇÕES
1. Ambiente bem iluminado (sem luz direta no rosto).  
2. Sem óculos, bonés, toucas ou acessórios que cubram o rosto.  
3. Rosto centralizado e posição vertical.  
4. Evite inclinar a cabeça ou se afastar da câmera.  
5. Somente o seu rosto deve aparecer na imagem.

💡 Capture a foto usando o botão abaixo.
"""

# --- Interface principal ---
st.title("👤 Sistema de Login e Cadastro Facial")
espaco_esq, meio, espaco_dir = st.columns([0.1, 0.8, 0.1])

with meio:
    # ------------------- LOGIN ------------------
    st.subheader("🔑 Login de Usuário")
    usuario = st.text_input("Usuário:")
    senha = st.text_input("Senha:", type="password")

    if meio.button("Entrar", width="stretch"):
        # Valida campos
        if usuario == "" or senha == "":
            st.warning("Preencha os campos")

        # Verifica se usuário existe no banco
        elif not verificar_usuario(usuario, cur):
            st.error("Usuário não encontrado!")
            sleep(2); st.rerun()

        # Verifica credenciais
        elif not verificar_acesso(usuario, senha, cur):
            st.error("Senha incorreta!")
            sleep(2); st.rerun()

        # Login válido
        else:
            st.success(f"✅ Usuário {usuario} autenticado!")
            st.session_state.logged_in = True
            st.session_state.usuario = usuario
            st.session_state.ready_to_capture_login = True

    else:
        # Redireciona para página de cadastro
        if meio.button("Cadastre-se", width="stretch"):
            st.switch_page("pages/cadastro.py")

    # --- Captura facial após login ---
    if st.session_state.logged_in and st.session_state.ready_to_capture_login:

        st.info(orientacoes)
        st.subheader("📸 Capture seu rosto para verificação")

        # Captura imagem da câmera
        foto = st.camera_input("Tire uma foto")

        # Ao clicar para verificar biometria
        if foto is not None and st.button("Verificar acesso", width="stretch"):
            # Converte imagem capturada
            bytes_img = foto.getvalue()
            np_arr = np.frombuffer(bytes_img, np.uint8)
            imagem = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            # Analisa rosto (iluminação, posição etc.)
            valid_face, msg_face = analyze_face_components(imagem)
            if not valid_face:
                st.error(msg_face)
            else:
                st.success(msg_face)
                try:
                    # Carrega imagem do rosto salvo no banco
                    imagem_banco = carregar_imagem_sqlite(st.session_state.usuario, cur)

                    # Compara biometria (foto atual vs foto cadastrada)
                    valid_bio, msg_bio = verificar_acesso_biometrico(imagem, imagem_banco)

                    if valid_bio:
                        st.success(msg_bio)

                        # Obtém nível de acesso e redireciona para a página correta
                        nivel_usuario = verificar_nivel_acesso(usuario, cur)
                        st.session_state.permissao = nivel_usuario

                        if nivel_usuario == "publico":
                            st.switch_page("pages/nivel_acesso1.py")
                        if nivel_usuario == "diretores":
                            st.switch_page("pages/nivel_acesso2.py")
                        if nivel_usuario == "ministro":
                            st.switch_page("pages/nivel_acesso3.py")
                        if nivel_usuario == "adm":
                            st.switch_page("pages/administrador.py")

                    else:
                        st.error(msg_bio)

                except Exception as e:
                    st.error(f"❌ Erro durante verificação biométrica: {str(e)}")

            # Reseta o estado de captura
            st.session_state.ready_to_capture_login = False

# --- Fecha a conexão com o banco ---
con.close()
