import streamlit as st
import modules.users as users
from modules.database import (get_distinct_plates, delete_inspections_by_plate, 
                              get_all_users, update_user_credentials, log_admin_action, get_admin_logs)
from dotenv import load_dotenv
import os

# Carrega as variáveis do .env
load_dotenv()
DELETION_PASSWORD = os.getenv("DELETION_PASSWORD")

def admin_page():
    st.title("👤 Administração")
    
    # Cria abas para subdividir a página
    tabs = st.tabs(["Gerenciamento de Placas", "Gerenciamento de Usuários", "Registros"])
    
    ### Aba: Gerenciamento de Placas ###
    with tabs[0]:
        st.subheader("Gerenciamento de Placas")
        placas = get_distinct_plates()
        if placas:
            placa_selecionada = st.selectbox("Selecione a placa a excluir", placas, key="placa_exclusao")
            if st.button("❌ Excluir Placa"):
                st.session_state["excluir_placa"] = placa_selecionada
                try:
                    st.experimental_rerun()
                except Exception:
                    st.write("Atualize o Streamlit para recarregar a página automaticamente.")
            if "excluir_placa" in st.session_state:
                confirm = st.checkbox(f"Confirmar exclusão da placa {st.session_state['excluir_placa']}", key="confirm_exclusao_placa")
                if confirm:
                    deleted_count = delete_inspections_by_plate(st.session_state["excluir_placa"])
                    if deleted_count > 0:
                        st.success(f"✅ Excluídos {deleted_count} registros para a placa {st.session_state['excluir_placa']}.")
                        # Registra a ação junto com o usuário que executou (obtido de st.session_state["username"])
                        log_admin_action("Exclusão de placas", f"Placa {st.session_state['excluir_placa']} removida, {deleted_count} registros excluídos.", st.session_state["username"])
                    else:
                        st.warning(f"⚠️ Nenhum registro encontrado para a placa {st.session_state['excluir_placa']}.")
                    del st.session_state["excluir_placa"]
                    try:
                        st.experimental_rerun()
                    except Exception:
                        st.write("Atualize o Streamlit para recarregar a página automaticamente.")
        else:
            st.info("Nenhuma placa registrada para exclusão.")
    
    ### Aba: Gerenciamento de Usuários ###
    with tabs[1]:
        st.subheader("Gerenciamento de Usuários")
        st.markdown("#### Remoção de Usuários")
        users_list = users.get_users()  # Obtém todos os usuários, inclusive admin
        if users_list:
            for user, info in users_list.items():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"👤 {user} - **{info['role']}**")
                with col2:
                    if st.button(f"❌ Remover", key=f"remove_{user}", use_container_width=True):
                        st.session_state["confirm_delete_user"] = user
                        try:
                            st.experimental_rerun()
                        except Exception:
                            st.write("Atualize o Streamlit para recarregar a página automaticamente.")
        else:
            st.info("Nenhum usuário cadastrado.")
    
        if "confirm_delete_user" in st.session_state:
            user_to_delete = st.session_state["confirm_delete_user"]
            st.warning(f"⚠️ Tem certeza que deseja remover o usuário **{user_to_delete}**?")
            senha_exclusao = st.text_input("Digite a senha de exclusão", type="password", key="senha_exclusao")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirmar Remoção", use_container_width=True):
                    if senha_exclusao != DELETION_PASSWORD:
                        st.error("Senha de exclusão incorreta.")
                    else:
                        if users.remove_user(user_to_delete):
                            st.success(f"✅ Usuário {user_to_delete} removido com sucesso!")
                            log_admin_action("Exclusão de usuário", f"Usuário {user_to_delete} removido.", st.session_state["username"])
                        else:
                            st.error(f"❌ Não foi possível remover {user_to_delete}.")
                    del st.session_state["confirm_delete_user"]
                    try:
                        st.experimental_rerun()
                    except Exception:
                        st.write("Atualize o Streamlit para recarregar a página automaticamente.")
            with col2:
                if st.button("❌ Cancelar", use_container_width=True):
                    del st.session_state["confirm_delete_user"]
                    try:
                        st.experimental_rerun()
                    except Exception:
                        st.write("Atualize o Streamlit para recarregar a página automaticamente.")
    
        st.markdown("#### Adição de Usuários")
        new_username = st.text_input("Novo Usuário", key="new_username")
        new_password = st.text_input("Senha", type="password", key="new_password")
        new_role = st.selectbox("Tipo de Usuário", ["mecanico", "admin"], key="new_role")
        if st.button("➕ Adicionar Usuário"):
            if new_username and new_password:
                if users.add_user(new_username, new_password, new_role):
                    st.success("✅ Usuário adicionado com sucesso!")
                    log_admin_action("Criação de usuário", f"Usuário {new_username} adicionado com role {new_role}.", st.session_state["username"])
                    try:
                        st.experimental_rerun()
                    except Exception:
                        st.write("Atualize o Streamlit para recarregar a página automaticamente.")
                else:
                    st.error("❌ Usuário já existe ou ocorreu um erro!")
            else:
                st.error("Preencha todos os campos.")
    
        st.markdown("#### Alteração de Credenciais")
        all_users = get_all_users()
        usuarios = [user["username"] for user in all_users]  # Inclui todos os usuários, inclusive admin
        if usuarios:
            selected_user = st.selectbox("Selecione o usuário para alterar", usuarios, key="user_to_update")
            new_username_update = st.text_input("Novo Nome de Usuário", key="new_username_update")
            new_password_update = st.text_input("Nova Senha", type="password", key="new_password_update")
            if st.button("Atualizar Credenciais"):
                if not new_username_update or not new_password_update:
                    st.error("Preencha todos os campos para atualizar.")
                else:
                    updated = update_user_credentials(selected_user, new_username_update, new_password_update)
                    if updated:
                        st.success(f"✅ Credenciais atualizadas para {selected_user}!")
                        log_admin_action("Modificação de login", f"Usuário {selected_user} atualizado para {new_username_update}.", st.session_state["username"])
                        try:
                            st.experimental_rerun()
                        except Exception:
                            st.write("Atualize o Streamlit para recarregar a página automaticamente.")
                    else:
                        st.error("❌ Erro ao atualizar credenciais.")
        else:
            st.info("Nenhum usuário disponível para atualização.")
    
    ### Aba: Registros (Logs)
    with tabs[2]:
        st.subheader("Registros de Ações Administrativas")
        logs = get_admin_logs()
        if logs:
            for log in logs:
                log_dict = dict(log)  # Converte o sqlite3.Row para dicionário
                admin_user = log_dict.get("admin", "N/A")
                st.markdown(f"**{log_dict['timestamp']}** – *{log_dict['action']}* (por **{admin_user}**): {log_dict['details']}")
                st.markdown("---")
        else:
            st.info("Nenhum registro encontrado.")
