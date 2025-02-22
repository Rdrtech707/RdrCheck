from modules.users import USERS

def authenticate(username, password):
    """Verifica se o usuário e senha são válidos"""
    user = USERS.get(username)
    if user and user["password"] == password:
        return user["role"]  # Retorna a permissão do usuário
    return None
