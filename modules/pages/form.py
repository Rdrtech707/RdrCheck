import streamlit as st
import os
import base64
import re
from dotenv import load_dotenv

load_dotenv()

from modules.pages.form_helpers import (
    select_first_options,
    deselect_all_options,
    render_inspection_groups,
    clear_form_session_state,
)
from modules.pdf_generator import generate_pdf
from modules.email_sender import enviar_email
from modules.database import insert_inspection, get_form_draft, set_form_draft, clear_form_draft

@st.fragment
def _form_content():
    """Conteúdo do formulário em fragment: interações só re-executam este bloco."""
    if st.session_state.pop("_form_reset_requested", None):
        clear_form_session_state()

    if "form_values" not in st.session_state:
        draft = get_form_draft(st.session_state.get("username", ""))
        st.session_state["form_values"] = draft if draft else {}

    username = st.session_state.get("username", "")

    col1, col2 = st.columns(2)
    with col1:
        placa_input = st.text_input(
            "🚗 Placa do veículo", key="placa",
            value=st.session_state["form_values"].get("placa", "")
        )
        placa = placa_input.upper().replace("-", "")
        st.session_state["form_values"]["placa"] = placa
    with col2:
        km = st.text_input(
            "📏 Quilometragem", key="km",
            value=st.session_state["form_values"].get("km", "")
        )
        st.session_state["form_values"]["km"] = km

    items, itens_faltando = render_inspection_groups()
    st.session_state["form_items"] = items
    st.session_state["form_itens_faltando"] = itens_faltando

    observacoes = st.text_area(
        "📝 Observações adicionais",
        key="observacoes",
        value=st.session_state["form_values"].get("observacoes", ""),
        placeholder="Digite qualquer observação extra sobre a revisão..."
    )
    st.session_state["form_values"]["observacoes"] = observacoes

    if st.button("Desmarcar todas as opções"):
        deselect_all_options()

    if st.session_state.role == "admin":
        st.markdown("---")
        st.markdown("### Função Extra de Administrador")
        st.button(
            label="Selecionar somente as primeiras opções",
            on_click=select_first_options
        )

    set_form_draft(username, st.session_state["form_values"])

    email_destino = os.getenv("EMAIL_DESTINATARIO") or os.getenv("EMAIL_REMETENTE", "")
    if st.button("📄 Gerar PDF"):
        # Verifica se os campos obrigatórios estão preenchidos
        if not placa or not km:
            st.error("⚠️ Preencha a Placa e a Quilometragem.")
            return

        # Validação da placa: deve seguir os padrões AAA0000 ou AAA0A00
        pattern1 = re.compile(r'^[A-Z]{3}[0-9]{4}$')
        pattern2 = re.compile(r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$')
        if not (pattern1.match(placa) or pattern2.match(placa)):
            st.error("⚠️ Placa inválida. Informe uma placa no formato AAA0000 ou AAA0A00.")
            return

        # Verifica se há itens faltando no formulário
        if st.session_state["form_itens_faltando"]:
            st.error("⚠️ Os seguintes itens precisam ser preenchidos antes de gerar o PDF:")
            for item in st.session_state["form_itens_faltando"]:
                st.write(f"🔴 {item}")
            return

        mecanico = st.session_state.username  # Usuário logado
        pdf_file_path = generate_pdf(
            placa,
            km,
            st.session_state["form_items"],
            mecanico,
            observacoes
        )
        if pdf_file_path and os.path.exists(pdf_file_path):
            st.success("✅ PDF gerado com sucesso!")
            with open(pdf_file_path, "rb") as f:
                pdf_data = f.read()
            st.download_button(
                label="📥 Baixar Relatório PDF",
                data=pdf_data,
                file_name=os.path.basename(pdf_file_path),
                mime="application/pdf",
                use_container_width=True
            )
            b64_pdf = base64.b64encode(pdf_data).decode("utf-8")
            button_style = (
                "background-color: #4CAF50; border: none; color: white; "
                "padding: 8px 16px; text-align: center; text-decoration: none; "
                "display: inline-block; font-size: 14px; margin: 4px 2px; "
                "cursor: pointer; border-radius: 4px;"
            )
            pdf_display_link = (
                f'<a href="data:application/pdf;base64,{b64_pdf}" target="_blank">'
                f'<button style="{button_style}">Visualizar Relatório PDF</button></a>'
            )
            st.markdown(pdf_display_link, unsafe_allow_html=True)

            inspection_id = insert_inspection(
                placa=placa,
                km=km,
                items=st.session_state["form_items"],
                observacoes=observacoes,
                mecanico=mecanico,
                pdf_path=pdf_file_path
            )
            st.info(f"Inspeção registrada com ID: {inspection_id}")
            clear_form_draft(username)

            assunto = f"Relatório Veicular - {placa}"
            mensagem = (
                f"Olá,\n\n"
                f"Segue em anexo o relatório da revisão veicular.\n\n"
                f"Placa: {placa}\n"
                f"KM: {km}\n\n"
                f"Att."
            )
            if email_destino:
                sucesso = enviar_email(email_destino, assunto, mensagem, pdf_file_path)
                if sucesso:
                    st.success("✅ E-mail enviado com sucesso!")
                else:
                    st.error("❌ Erro ao enviar o e-mail. Verifique logs/console.")
            else:
                st.warning("⚠️ E-mail de destino não configurado. Defina EMAIL_DESTINATARIO ou EMAIL_REMETENTE no .env")

            st.session_state["_form_reset_requested"] = True
            clear_form_session_state()
            if hasattr(st, "rerun"):
                st.rerun()
            elif hasattr(st, "experimental_rerun"):
                st.experimental_rerun()
        else:
            st.error("❌ Erro ao gerar o PDF. Tente novamente.")


def form_page():
    """Página do Formulário de Revisão Veicular"""
    st.title("📋 Formulário de Revisão Veicular")
    _form_content()
