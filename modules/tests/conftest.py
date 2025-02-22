# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def dummy_pdf(tmp_path) -> Path:
    """
    Cria um arquivo PDF fictício para teste dentro de uma pasta temporária.
    Retorna o caminho do arquivo.
    """
    pdf_path = tmp_path / "dummy.pdf"
    # Apenas gravando texto simples para simular um PDF.
    pdf_path.write_text("PDF TEST CONTENT")
    return pdf_path
