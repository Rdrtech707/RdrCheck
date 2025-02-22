# modules/users.py
from modules.database import get_connection

def authenticate(username, password):
    """
    Verifica se o usuário e senha são válidos, buscando no banco de dados.
    Retorna o role se autenticado ou None caso contrário.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password, role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and user["password"] == password:
        return user["role"]
    return None

def get_users():
    """
    Retorna um dicionário com os usuários cadastrados no formato:
    {username: {"password": <senha>, "role": <role>}, ...}
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, role FROM users")
    rows = cursor.fetchall()
    conn.close()
    users_dict = {}
    for row in rows:
        users_dict[row["username"]] = {"password": row["password"], "role": row["role"]}
    return users_dict

def add_user(username, password, role):
    """
    Adiciona um novo usuário no banco de dados.
    Retorna True se o usuário for adicionado com sucesso, ou False se já existir ou ocorrer erro.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
    except Exception:
        conn.rollback()
        conn.close()
        return False
    conn.close()
    return True

def remove_user(username):
    """
    Remove um usuário do banco de dados.
    Retorna True se o usuário for removido, False caso contrário.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0
