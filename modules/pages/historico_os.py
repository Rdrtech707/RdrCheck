# RdrCheck/modules/pages/historico_os.py
import streamlit as st
import os
from dotenv import load_dotenv
from modules.access_db import (
    fetch_ordems_by_modelo,
    fetch_os_pecas_by_cod,
    fetch_os_servicos_by_osnum,
)
from modules.pdf_generator import generate_os_pdf_report

# Carrega as variáveis de ambiente
load_dotenv()

def normalize_plate(plate: str) -> str:
    """
    Remove hífens e espaços e converte a placa para minúsculas.
    """
    return plate.replace('-', '').replace(' ', '').lower()

def historico_os_page():
    st.title("Histórico de OS por Placa")
    st.markdown("Esta página exibe os históricos de OS a partir do arquivo Access.")

    # Recupera as variáveis de ambiente para conexão com Access
    mdb_file = os.getenv("MDB_FILE", "data/dados.mdb")
    db_password = os.getenv("DB_PASSWORD", "")

    placa = st.text_input("Digite a placa do veículo", "")

    if placa:
        normalized_plate = normalize_plate(placa)
        try:
            df_ordens = fetch_ordems_by_modelo(mdb_file, db_password, normalized_plate)
            if df_ordens.empty:
                st.warning("Nenhuma ordem encontrada para essa placa.")
            else:
                # Filtra ordens ativas (SITUACAO == 10) e recusadas (SITUACAO == 11)
                df_ordens_ativas = df_ordens[df_ordens['SITUACAO'] == 10]
                df_ordens_recusadas = df_ordens[df_ordens['SITUACAO'] == 11]

                st.markdown("## Ordens Encerradas")
                if df_ordens_ativas.empty:
                    st.info("Nenhuma ordem ativa encontrada para essa placa.")
                else:
                    for _, ordem in df_ordens_ativas.iterrows():
                        os_num = ordem['CODIGO']
                        saida = ordem['SAIDA']
                        km = ordem['KILOMET']
                        st.subheader(f"OS: {os_num} | Saída: {saida} | Quilometragem: {km}")

                        col1, col2 = st.columns(2)
                        with col1:
                            df_pecas = fetch_os_pecas_by_cod(mdb_file, db_password, os_num)
                            if not df_pecas.empty:
                                st.markdown("### Peças")
                                st.dataframe(df_pecas[['DESCRICAO', 'QTD']])
                            else:
                                st.info("Nenhuma peça encontrada para essa OS.")
                        with col2:
                            df_servicos = fetch_os_servicos_by_osnum(mdb_file, db_password, os_num)
                            if not df_servicos.empty:
                                st.markdown("### Serviços")
                                st.dataframe(df_servicos[['DESCRICAO']])
                            else:
                                st.info("Nenhum serviço encontrado para essa OS.")

                st.markdown("## OS Recusadas")
                if df_ordens_recusadas.empty:
                    st.info("Nenhuma OS recusada encontrada para essa placa.")
                else:
                    st.dataframe(df_ordens_recusadas[['CODIGO', 'SAIDA', 'KILOMET']])

                # Botão para gerar e baixar o relatório em PDF
                if st.button("Gerar Relatório PDF"):
                    pdf_bytes = generate_os_pdf_report(placa, df_ordens_ativas, df_ordens_recusadas, mdb_file, db_password)
                    st.download_button("Baixar Relatório PDF", data=pdf_bytes, file_name=f"Relatorio_{normalized_plate}.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"Erro ao carregar os dados: {e}")

# Executa a página se o script for chamado diretamente
if __name__ == "__main__":
    historico_os_page()
