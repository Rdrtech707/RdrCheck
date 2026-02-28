# RdrCheck/app.py
import os
import streamlit as st
from streamlit_theme import st_theme
from modules.session_manager import initialize_session, check_session, login, logout
from modules.pages.form import form_page
from modules.pages.reports import reports_page
from modules.pages.admin import admin_page
from modules.database import init_db
from modules.pages.historico_os import historico_os_page

st.set_page_config(page_title="Relatório de Inspeção", page_icon="🔧", layout="wide")

init_db()

LOGO_PATH = "assets/logo.png"

# 1) Inicializa sessão
initialize_session()
# 2) Checa se existe token na URL e valida
check_session()

# Exibe o logo na sidebar
if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, use_container_width=True)
else:
    st.sidebar.write("🔍 **Logo não encontrado!**")

# Tela de login se não estiver logado
if not st.session_state.logged_in:
    st.markdown(
        "<h1 style='text-align: center; color: #d63031;'>Relatório de Inspeção</h1>",
        unsafe_allow_html=True
    )
    with st.form("login_form"):
        username = st.text_input("👤 Usuário")
        password = st.text_input("🔑 Senha", type="password")
        submitted = st.form_submit_button("🔓 Entrar")
        if submitted:
            login(username, password)
            if st.session_state.logged_in:
                st.success("Login efetuado com sucesso!")
else:
    # Exibe o usuário na sidebar
    st.sidebar.markdown(f"👤 **Usuário:** {st.session_state.username} ({st.session_state.role})")
    if st.sidebar.button("🚪 Sair"):
        logout()
    
    # Integra o st_theme para obter o tema ativo
    theme_base = st.get_option("theme.base")
    if theme_base == "dark":
        header_color = "#0E1117"
    else:
        header_color = "#ffffff"

    st.markdown(
        f"""
        <div style="background-color:{header_color}; padding:10px; border-radius:5px; text-align:center;">
            <h2>Bem-vindo, {st.session_state.username}!</h2>
            <p>Função: {st.session_state.role}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Adiciona a nova opção "Histórico OS" à navegação
    aba_selecionada = st.sidebar.radio(
        "📌 Selecione a Página",
        ["📄 Formulário", "📊 Relatórios", "📝 Histórico OS"] + (["⚙️ Administração"] if st.session_state.role == "admin" else [])
    )
    if aba_selecionada == "📄 Formulário":
        form_page()
    elif aba_selecionada == "📊 Relatórios":
        reports_page()
    elif aba_selecionada == "📝 Histórico OS":
        historico_os_page()
    elif aba_selecionada == "⚙️ Administração":
        admin_page()
