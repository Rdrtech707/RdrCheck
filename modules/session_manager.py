# modules/session_manager.py
import os
import requests
import streamlit as st
from modules.users import authenticate

# URL do backend: use API_URL no .env para produção (ex: https://rdrcheck.onrender.com)
API_URL = os.getenv("API_URL", "http://localhost:5000")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "3"))  # segundos; se o backend não responder, usa autenticação local

def initialize_session():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["role"] = ""
        st.session_state["token"] = None

def safe_rerun():
    """Tenta forçar a reexecução do script usando a função disponível."""
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()
    else:
        st.write("Por favor, atualize o Streamlit para forçar um rerun.")

def check_session():
    """
    Verifica se existe um 'token' na URL (usando st.query_params) e valida-o no backend.
    Se o token for válido, o usuário permanece logado mesmo após reload.
    """


    # Ajuste na extração do token (supondo que já seja uma string)
    token_in_url = st.query_params.get("token")
    
    if token_in_url:
        headers = {"Authorization": f"Bearer {token_in_url}"}
        try:
            resp = requests.get(f"{API_URL}/session", headers=headers, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                st.session_state["logged_in"] = True
                st.session_state["username"] = data.get("user", "")
                st.session_state["role"] = data.get("role", "")
                st.session_state["token"] = token_in_url
                return
            else:
                st.error("Token inválido ou expirado.")
        except Exception:
            st.error("Servidor de autenticação indisponível. Faça login novamente.")

    st.session_state["logged_in"] = False
    st.session_state["token"] = None

def login(username, password):
    """
    Tenta login via backend. Se o backend não estiver disponível, usa autenticação
    local (SQLite). Com backend: token na URL e login persiste ao recarregar.
    Sem backend: login só vale na sessão atual.
    """
    try:
        resp = requests.post(
            f"{API_URL}/login",
            json={"username": username, "password": password},
            timeout=REQUEST_TIMEOUT
        )
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("token")
            if token:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = data.get("role", "user")
                st.session_state["token"] = token
                st.query_params.from_dict({"token": token})
                safe_rerun()
                return
            st.error("Token não retornado pelo servidor.")
            return
        if resp.status_code == 401:
            st.error("Usuário ou senha inválidos.")
            return
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, Exception):
        pass

    role = authenticate(username, password)
    if role:
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["role"] = role
        st.session_state["token"] = None
        st.info("Backend indisponível: você está logado localmente. O login não persiste ao recarregar a página.")
        safe_rerun()
    else:
        st.error("Usuário ou senha inválidos.")

def logout():
    """
    Efetua logout: limpa o token da URL e reseta o st.session_state.
    Após limpar, força um rerun para atualizar a interface.
    """
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = ""
    st.session_state["token"] = None
    
    # Limpa os parâmetros da URL usando a API de query params
    st.query_params.clear()
    safe_rerun()
