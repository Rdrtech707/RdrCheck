import smtplib
import os
from dotenv import load_dotenv  # << Importando do python-dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Carrega as variáveis definidas em .env
load_dotenv()

# Lê as variáveis de ambiente (ou usa defaults se quiser)
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
EMAIL_REMETENTE = os.environ.get("EMAIL_REMETENTE")
SENHA_REMETENTE = os.environ.get("SENHA_REMETENTE")  # Sem default aqui, pois é crucial

def enviar_email(destinatario, assunto, mensagem, arquivo_anexo):
    """Envia um e-mail com um arquivo PDF anexado."""
    try:
        if not os.path.exists(arquivo_anexo):
            print(f"❌ Arquivo não encontrado: {arquivo_anexo}")
            return False

        print(f"📤 Enviando e-mail com anexo: {arquivo_anexo}")  # Log para depuração

        # Criar a mensagem do e-mail
        msg = MIMEMultipart()
        msg["From"] = EMAIL_REMETENTE
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.attach(MIMEText(mensagem, "plain"))

        # Anexar o arquivo PDF
        with open(arquivo_anexo, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition",
                            f"attachment; filename={os.path.basename(arquivo_anexo)}")
            msg.attach(part)

        # Conectar ao servidor SMTP e enviar o e-mail
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Ativa criptografia TLS
        server.login(EMAIL_REMETENTE, SENHA_REMETENTE)
        server.sendmail(EMAIL_REMETENTE, destinatario, msg.as_string())
        server.quit()

        return True
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")
        return False
