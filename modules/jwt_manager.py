import jwt
import time

# Chave secreta para assinar os tokens
SECRET_KEY = "chave_super_secreta"

# Tempo de expiração do token (60 minutos)
EXPIRATION_TIME = 60 * 60  

def generate_jwt(username, role):
    """Gera um token JWT válido por 60 minutos"""
    payload = {
        "username": username,
        "role": role,
        "exp": time.time() + EXPIRATION_TIME  # Expira em 60 minutos
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_jwt(token):
    """Verifica e decodifica um token JWT"""
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token  # Retorna os dados do usuário se válido
    except jwt.ExpiredSignatureError:
        return None  # Token expirado
    except jwt.InvalidTokenError:
        return None  # Token inválido
