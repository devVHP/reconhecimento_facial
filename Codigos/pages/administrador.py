import streamlit as st
from utils import listar_usuarios, buscar_usuario_por_id_e_nome, atualizar_usuario, deletar_usuario, carregar_usuarios
import sqlite3
import pandas as pd
from time import sleep

# Remove sidebar e ajusta layout
st.markdown("""
            <style>
            [data-testid="stSidebar"] { display: none }
            [data-testid="collapsedControl"] { display: none }
            </style>
            """, unsafe_allow_html=True)

st.set_page_config(page_title="Sistema de Biometria Facial",
                   page_icon="👤",
                   layout="centered",
                   initial_sidebar_state="collapsed")

# Conexão com banco
con = sqlite3.connect("banco_biometria.sqlite")
cur = con.cursor()

try:
    # Garante que somente administradores acessem
    if st.session_state.permissao == "adm":
        listagem, alteracao, remocao = st.tabs(["Usuários Cadastrados", "Alterar Usuário", "Remover Usuários"])

        # --------- LISTAR USUÁRIOS ---------
        with listagem:
            if st.button("🔄 Atualizar página"):
                st.rerun()

            usuarios = listar_usuarios(cur)
            df_usuarios = pd.DataFrame(usuarios, columns=['ID', 'Usuário', 'Permissão'])
            st.dataframe(df_usuarios)

        # --------- ALTERAR USUÁRIO ---------
        with alteracao:
            # Controle interno da tela
            if "usuario_verificado" not in st.session_state:
                st.session_state.usuario_verificado = False
            if "dados_usuario" not in st.session_state:
                st.session_state.dados_usuario = None

            # Entrada do ID e nome
            id_usuario = st.text_input("ID:")
            usuario_alterar = st.text_input("Usuário:")

            # Verifica no banco
            if st.button("Verificar usuário"):
                if not id_usuario.isdigit():
                    st.error("❌ O ID deve ser um número inteiro.")
                else:
                    dados = buscar_usuario_por_id_e_nome(int(id_usuario), usuario_alterar, cur)

                    # Prepara interface caso tenha encontrado
                    if dados:
                        st.session_state.usuario_verificado = True
                        st.session_state.dados_usuario = dados
                        st.success("✅ Usuário encontrado! Você pode alterar as informações abaixo.")
                    else:
                        st.session_state.usuario_verificado = False
                        st.session_state.dados_usuario = None
                        st.error("❌ Nenhum usuário encontrado com esse ID e nome.")

            # Após verificação, exibe campos editáveis
            if st.session_state.usuario_verificado and st.session_state.dados_usuario:
                dados = st.session_state.dados_usuario

                st.subheader("Selecione as informações que deseja alterar:")
                opcoes = ["Nome", "Senha", "Permissão"]

                # Admin escolhe o que deseja alterar
                campos_selecionados = st.multiselect("Escolha um ou mais campos para alterar:", options=opcoes)
                novos_campos = {}

                # Campos individuais
                if "Nome" in campos_selecionados:
                    novos_campos["nome"] = st.text_input("Novo nome:")

                if "Senha" in campos_selecionados:
                    novos_campos["senha"] = st.text_input("Nova senha:", type="password")

                if "Permissão" in campos_selecionados:
                    st.info(f"Permissão atual: {dados[3]}")
                    permissoes_disponiveis = [1, 2, 3, 4]
                    permissao_selecionada = st.selectbox("Selecione a nova permissão", options=permissoes_disponiveis)
                    novos_campos["id_permissao"] = permissao_selecionada

                # Salva no banco
                if st.button("Salvar alterações"):
                    if novos_campos:
                        atualizar_usuario(int(id_usuario), novos_campos, cur)
                        con.commit()
                        st.success("✅ Dados do usuário atualizados com sucesso!")
                        st.session_state.usuario_verificado = False
                        sleep(2.0)
                        st.rerun()
                    else:
                        st.warning("Nenhum campo selecionado para alteração.")

        # --------- REMOVER USUÁRIO ---------
        with remocao:
            usuarios_df = carregar_usuarios(con)

            if usuarios_df.empty:
                st.warning("Nenhum usuário cadastrado.")
            else:
                st.subheader("Lista de usuários:")

                # Exibe tabela com botões de exclusão por linha
                for i, row in usuarios_df.iterrows():
                    col1, col2, col3, col4 = st.columns([1, 3, 3, 1])
                    col1.write(row["ID"])
                    col2.write(row["Usuário"])
                    col3.write(row["Permissão"])

                    # Botão para marcar usuário para remoção
                    if col4.button("❌", key=f"del_{row['ID']}"):
                        st.session_state["delete_id"] = row["ID"]

                # Confirmação antes de excluir
                if "delete_id" in st.session_state:
                    st.warning(f"Tem certeza que deseja excluir o usuário ID {st.session_state['delete_id']}?")

                    col_a, col_b = st.columns(2)
                    if col_a.button("✅ Sim, excluir"):
                        deletar_usuario(st.session_state["delete_id"], cur)
                        del st.session_state["delete_id"]
                        con.commit()
                        st.success("Usuário deletado com sucesso!")
                        sleep(2.0)
                        st.rerun()

                    if col_b.button("❌ Cancelar"):
                        del st.session_state["delete_id"]
                        st.rerun()

    else:
        # Bloqueia acesso se não for administrador
        st.markdown("Permissão negada")

except Exception as e:
    # Se algo der errado, volta para o login
    st.markdown(e)
    sleep(3.0)
    st.switch_page("app.py")


# Fecha conexão
con.close()
