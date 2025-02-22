import streamlit as st
import os
import base64
from modules.database import get_connection

def reports_page():
    """Página de Relatórios - Agrupa e permite baixar e visualizar relatórios gerados por placa."""
    st.title("📂 Relatórios Gerados")

    # Consulta registros do banco, ordenando por placa (MAIÚSCULAS) e data (descendente)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, placa, km, pdf_path, created_at
        FROM inspections
        ORDER BY UPPER(placa) ASC, created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        st.warning("⚠️ Nenhum relatório encontrado.")
        return

    # Barra de pesquisa por placa (converte a query para MAIÚSCULAS)
    search_query = st.text_input("🔍 Buscar relatório por placa").strip().upper()

    # Se houver uma query de busca, filtra os registros comparando em MAIÚSCULAS
    if search_query:
        rows = [row for row in rows if search_query in row["placa"].upper()]

    if not rows:
        st.warning("❌ Nenhum relatório encontrado para essa placa.")
        return

    # Agrupa os registros por placa utilizando um dicionário com as placas em MAIÚSCULAS
    groups = {}
    for row in rows:
        key = row["placa"].upper()
        groups.setdefault(key, []).append(row)

    # Itera pelas placas em ordem alfabética
    for key in sorted(groups.keys()):
        reports_list = groups[key]
        # Como já trabalhamos com MAIÚSCULAS, utilizamos a própria chave para exibição
        plate_display = key

        with st.expander(f"🚗 Placa: {plate_display}"):
            # Itera sobre os relatórios associados à placa
            for i, row in enumerate(reports_list, start=1):
                file_path = row["pdf_path"]

                # Se o arquivo não existir, pula para o próximo
                if not os.path.exists(file_path):
                    continue

                st.markdown(f"**Relatório {i}**")
                st.markdown(
                    f"**ID:** {row['id']} | **KM:** {row['km']} | **Data:** {row['created_at']}"
                )

                # Leitura do arquivo PDF
                with open(file_path, "rb") as f:
                    pdf_data = f.read()

                # Cria duas colunas para os botões de baixar e visualizar
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="📥 Baixar",
                        data=pdf_data,
                        file_name=os.path.basename(file_path),
                        mime="application/pdf",
                        use_container_width=True
                    )
                with col2:
                    b64_pdf = base64.b64encode(pdf_data).decode("utf-8")
                    button_style = (
                        "background-color: #4CAF50; border: none; color: white; "
                        "padding: 8px 16px; text-align: center; text-decoration: none; "
                        "display: inline-block; font-size: 14px; margin: 4px 2px; "
                        "cursor: pointer; border-radius: 4px;"
                    )
                    pdf_display_link = (
                        f'<a href="data:application/pdf;base64,{b64_pdf}" target="_blank">'
                        f'<button style="{button_style}">Visualizar</button></a>'
                    )
                    st.markdown(pdf_display_link, unsafe_allow_html=True)

                st.markdown("---")
