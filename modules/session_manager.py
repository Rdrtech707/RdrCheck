# modules/session_manager.py
import requests
import streamlit as st

API_URL = "https://rdrcheck.onrender.com" # Ajuste se o backend estiver em outra porta/host

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
            resp = requests.get(f"{API_URL}/session", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                st.session_state["logged_in"] = True
                st.session_state["username"] = data.get("user", "")
                st.session_state["role"] = data.get("role", "")
                st.session_state["token"] = token_in_url
                return
            else:
                st.error("Token inválido ou expirado.")
        except Exception as e:
            st.error(f"Erro ao validar token: {e}")
    
    st.session_state["logged_in"] = False
    st.session_state["token"] = None

def login(username, password):
    """
    Faz login via backend. Se o login for bem-sucedido, atualiza a URL com o token
    usando st.query_params.from_dict() e força um rerun.
    """
    try:
        resp = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("token")
            if token:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = "admin" if username == "admin" else "user"
                st.session_state["token"] = token
                
                # Atualiza a URL para conter o token usando a nova API de query params
                st.query_params.from_dict({"token": token})
                safe_rerun()
            else:
                st.error("Token não retornado pelo servidor.")
        else:
            st.error("Usuário ou senha inválidos.")
    except Exception as e:
        st.error(f"Erro ao conectar ao servidor de autenticação: {e}")

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
