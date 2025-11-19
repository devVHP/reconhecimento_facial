import streamlit as st
from utils import listar_usuarios, buscar_usuario_por_id_e_nome, atualizar_usuario, deletar_usuario, carregar_usuarios
import sqlite3
import pandas as pd
from time import sleep

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
con = sqlite3.connect("banco_biometria.sqlite")
cur = con.cursor()

try:
    if st.session_state.permissao == "adm":
        listagem, alteracao, remocao = st.tabs(["Usuários Cadastrados", "Alterar Usuário", "Remover Usuários"])

        with listagem:
            if st.button("🔄 Atualizar página"):
                st.rerun()
            usuarios = listar_usuarios(cur)
            df_usuarios = pd.DataFrame(usuarios, columns=['ID', 'Usuário', 'Permissão'])
            st.dataframe(df_usuarios)

        with alteracao:
            if "usuario_verificado" not in st.session_state:
                st.session_state.usuario_verificado = False
            if "dados_usuario" not in st.session_state:
                st.session_state.dados_usuario = None

            id_usuario = st.text_input("ID:")
            usuario_alterar = st.text_input("Usuário:")

            # Botão de verificação
            if st.button("Verificar usuário"):
                if not id_usuario.isdigit():
                    st.error("❌ O ID deve ser um número inteiro.")
                else:
                    dados = buscar_usuario_por_id_e_nome(int(id_usuario), usuario_alterar, cur)
                    if dados:
                        st.session_state.usuario_verificado = True
                        st.session_state.dados_usuario = dados
                        st.success("✅ Usuário encontrado! Você pode alterar as informações abaixo.")
                    else:
                        st.session_state.usuario_verificado = False
                        st.session_state.dados_usuario = None
                        st.error("❌ Nenhum usuário encontrado com esse ID e nome.")

            # Se o usuário já foi verificado, mostra os campos de alteração
            if st.session_state.usuario_verificado and st.session_state.dados_usuario:
                dados = st.session_state.dados_usuario

                st.subheader("Selecione as informações que deseja alterar:")
                opcoes = ["Nome", "Senha", "Permissão"]
                campos_selecionados = st.multiselect(
                    "Escolha um ou mais campos para alterar:",
                    options=opcoes
                )

                novos_campos = {}

                if "Nome" in campos_selecionados:
                    novos_campos["nome"] = st.text_input("Novo nome:")

                if "Senha" in campos_selecionados:
                    novos_campos["senha"] = st.text_input("Nova senha:", type="password")

                if "Permissão" in campos_selecionados:
                    st.info(f"Permissão atual: {dados[3]}")
                    permissoes_disponiveis = [1, 2, 3, 4]
                    permissao_selecionada = st.selectbox(
                        options=permissoes_disponiveis,
                        label="Selecione a nova permissão"
                    )
                    if permissao_selecionada:
                        novos_campos["id_permissao"] = permissao_selecionada

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

        with remocao:
            # Carrega os dados
            usuarios_df = carregar_usuarios(con)

            if usuarios_df.empty:
                st.warning("Nenhum usuário cadastrado.")
            else:
                st.subheader("Lista de usuários:")

                # Cria colunas com espaço para botões
                for i, row in usuarios_df.iterrows():
                    col1, col2, col3, col4 = st.columns([1, 3, 3, 1])
                    col1.write(row["ID"])
                    col2.write(row["Usuário"])
                    col3.write(row["Permissão"])

                    # Botão "X" de exclusão
                    if col4.button("❌", key=f"del_{row['ID']}"):
                        st.session_state["delete_id"] = row["ID"]

                # Verifica se algum botão foi clicado
                if "delete_id" in st.session_state:
                    st.warning(f"Tem certeza que deseja excluir o usuário ID {st.session_state['delete_id']}?")
                    col_a, col_b = st.columns(2)
                    if col_a.button("✅ Sim, excluir"):
                        deletar_usuario(st.session_state["delete_id"], cur)
                        del st.session_state["delete_id"]
                        st.success("Usuário deletado com sucesso!")
                        con.commit()
                        st.rerun()
                    if col_b.button("❌ Cancelar"):
                        del st.session_state["delete_id"]
                        st.rerun()
    else:
        st.markdown("Permissão negada")
except:
    st.switch_page("app.py")

con.close()
