import os
from fpdf import FPDF
from datetime import datetime
from modules.inspection_groups import INSPECTION_GROUPS  # Importa os grupos diretamente

# Criar a pasta de relatórios se não existir
RELATORIOS_DIR = "relatorios"
os.makedirs(RELATORIOS_DIR, exist_ok=True)

class CustomPDF(FPDF):
    def header(self):
        """Define o cabeçalho do PDF com o logo e o título centralizado."""
        logo_path = "assets/logo.png"  # Ajuste o caminho se necessário
        if os.path.exists(logo_path):
            # Adiciona o logo no canto superior esquerdo (x=10, y=8) com largura de 30mm
            self.image(logo_path, 10, 8, 30)
        # Define a fonte para o título
        self.set_font("Arial", "B", 12)
        # Move para a direita para centralizar o título (considerando a presença do logo)
        self.cell(0, 10, "OFICINA MECÂNICA - RELATÓRIO DE INSPEÇÃO", border=0, ln=1, align="C")
        # Linha horizontal abaixo do cabeçalho
        self.set_line_width(0.5)
        self.line(10, 20, self.w - 10, 20)
        self.ln(5)
    
    def footer(self):
        """Adiciona um rodapé com a numeração da página."""
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

def remove_unicode(text):
    """Remove caracteres Unicode incompatíveis com FPDF (latin-1)"""
    return text.encode("latin-1", "ignore").decode("latin-1")

def generate_pdf(placa, km, items, mecanico, observacoes):
    """Gera um PDF otimizado para modo paisagem, com logo e layout aprimorado."""
    
    pdf = CustomPDF(orientation="L", unit="mm", format="A4")  # Modo paisagem
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    pdf.set_font("Arial", size=7)  # Fonte reduzida para otimizar espaço

    # Informações gerais do veículo com fundo cinza claro para destaque
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 6, f"Placa do Veículo: {remove_unicode(placa)}", ln=True, fill=True)
    pdf.cell(0, 6, f"Quilometragem: {remove_unicode(km)}", ln=True, fill=True)
    pdf.cell(0, 6, f"Data da Revisão: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, fill=True)
    pdf.cell(0, 6, f"Mecânico Responsável: {remove_unicode(mecanico)}", ln=True, fill=True)
    pdf.ln(8)

    # Cria estrutura para os grupos reais
    grupos = {grupo: [] for grupo in INSPECTION_GROUPS.keys()}
    grupos["OUTROS"] = []  # Para itens não classificados

    # Classificar os itens dentro dos grupos corretos
    for grupo, item_dict in INSPECTION_GROUPS.items():
        for item in item_dict.keys():
            if item in items:  # Se o item foi selecionado pelo usuário
                status = ", ".join(items[item]) if items[item] else "NÃO INFORMADO"
                status = remove_unicode(status)
                grupos[grupo].append((remove_unicode(item), status))

    # Lista de status aceitáveis para não destacar em vermelho
    status_aceitaveis = ["OK", "ACEITÁVEL", "VERDE", "LIMPO","VISUALMENTE OK"]

    # Ajustar largura das colunas para caber na folha A4 em paisagem
    item_col_width = 95  # Largura da coluna para o item
    status_col_width = 40  # Largura da coluna para o status
    row_height = 4  # Altura da linha

    # Gerar as seções do PDF para cada grupo
    for grupo, itens in grupos.items():
        if itens:  # Apenas adiciona o grupo se ele tiver itens
            pdf.set_font("Arial", "B", 8)
            pdf.cell(0, 6, f"{grupo}", ln=True, align="L")
            pdf.set_font("Arial", size=7)

            # Cabeçalhos das colunas
            pdf.cell(item_col_width, row_height, "ITEM", border=1, align="C")
            pdf.cell(status_col_width, row_height, "STATUS", border=1, align="C")
            pdf.cell(item_col_width, row_height, "ITEM", border=1, align="C")
            pdf.cell(status_col_width, row_height, "STATUS", border=1, align="C")
            pdf.ln()

            # Organizar os itens em duas colunas por linha
            for i in range(0, len(itens), 2):
                for j in range(2):  # Duas colunas
                    if i + j < len(itens):
                        item, status = itens[i + j]
                        # Se houver algum status não aceitável, destaca em vermelho
                        status_list = status.split(", ")
                        if any(s not in status_aceitaveis for s in status_list):
                            pdf.set_text_color(255, 0, 0)
                        else:
                            pdf.set_text_color(0, 0, 0)
                        pdf.cell(item_col_width, row_height, item, border=1, align="L")
                        pdf.cell(status_col_width, row_height, status, border=1, align="C")
                    else:
                        # Preenche células vazias na última linha
                        pdf.cell(item_col_width, row_height, "", border=1)
                        pdf.cell(status_col_width, row_height, "", border=1)
                pdf.ln()  # Próxima linha
            pdf.set_text_color(0, 0, 0)  # Volta para a cor padrão
            pdf.ln(4)

    # Seção de observações
    pdf.ln(6)
    pdf.set_font("Arial", "B", 8)
    pdf.cell(0, 6, "OBSERVAÇÕES ADICIONAIS", ln=True, align="L")
    pdf.set_font("Arial", size=7)
    observacoes = observacoes.strip() if observacoes.strip() else "Nenhuma observação adicionada"
    pdf.multi_cell(0, 5, remove_unicode(observacoes))
    
    # Espaço para assinatura do mecânico
    pdf.ln(8)
    pdf.cell(0, 6, f"ASSINATURA DO MECÂNICO: {remove_unicode(mecanico)}", ln=True, align="L")

    # Cria o nome do arquivo com a placa e a data
    data_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    pdf_file_path = os.path.join(RELATORIOS_DIR, f"relatorio_{placa}_{data_str}.pdf")

    # Salva o PDF
    pdf.output(pdf_file_path)

    # Verifica se o arquivo foi criado e retorna seu caminho
    if not os.path.exists(pdf_file_path):
        return None
    return pdf_file_path
