# tests/test_email_sender.py
import pytest
import os
from unittest.mock import patch, MagicMock
from modules.email_sender import enviar_email

def test_enviar_email_arquivo_inexistente():
    """
    Se o arquivo não existir, enviar_email deve retornar False.
    """
    result = enviar_email(
        destinatario="teste@example.com",
        assunto="Assunto",
        mensagem="Corpo do e-mail",
        arquivo_anexo="arquivo_inexistente.pdf"
    )
    assert result is False, "Deveria retornar False quando o arquivo não existe."


@patch("smtplib.SMTP")
def test_enviar_email_sucesso(mock_smtp, dummy_pdf):
    """
    Testa envio de e-mail com sucesso, usando mock do SMTP e um PDF fictício.
    """
    # Configura o mock para não gerar erro
    instance = mock_smtp.return_value
    instance.sendmail.return_value = {}

    # Chama a função com o PDF dummy
    result = enviar_email(
        destinatario="teste@example.com",
        assunto="Assunto",
        mensagem="Corpo do e-mail",
        arquivo_anexo=str(dummy_pdf)  # Convertendo Path -> str
    )
    assert result is True, "Deveria retornar True quando tudo corre bem."

    # Verifica se sendmail foi de fato chamado
    instance.sendmail.assert_called_once()
