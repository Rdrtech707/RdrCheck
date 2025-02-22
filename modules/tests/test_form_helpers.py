# tests/test_form_helpers.py
import pytest
from unittest.mock import patch, MagicMock
from modules.pages.form_helpers import render_inspection_groups, render_single_item
from modules.inspection_groups import INSPECTION_GROUPS

@patch("modules.pages.form_helpers.st")
def test_render_single_item(mock_streamlit):
    """
    Testa se render_single_item retorna opções selecionadas corretamente.
    """
    # Mock do st.columns(...) -> devolve colunas falsas
    mock_streamlit.columns.return_value = [MagicMock() for _ in range(3)]

    # Simulando 2 opções
    group = "MOTOR"
    item = "Óleo"
    options = ["OK", "Ruim"]

    # Precisamos que st.checkbox retorne True ou False de acordo com algo
    # Vamos criar side effects
    checkboxes = [False, True]  # signfica 1ª false, 2ª true
    def checkbox_side_effect(label, key=None):
        # cada vez que chama, retorna o próximo valor
        return checkboxes.pop(0)

    mock_streamlit.checkbox.side_effect = checkbox_side_effect

    # Agora chamamos a função
    selected = render_single_item(group, item, options)
    assert selected == ["Ruim"], "Deveria retornar apenas a opção marcada (Ruim)."

@patch("modules.pages.form_helpers.st")
def test_render_inspection_groups(mock_streamlit):
    """
    Testa se render_inspection_groups percorre adequadamente o INSPECTION_GROUPS.
    Faremos um mock básico do st.tabs() e st.subheader() etc.
    """
    # Mock do st.tabs -> devolve lista "mágica" simulando blocos
    mock_tab = MagicMock()
    mock_streamlit.tabs.return_value = [mock_tab] * len(INSPECTION_GROUPS)

    # Agora dentro de cada tab, também chamamos subheader e processamos items
    # Precisaríamos mockar render_single_item ou st.checkbox de forma mais ampla
    with patch("modules.pages.form_helpers.render_single_item") as mock_rsi:
        # Suppose each call to render_single_item returns ["OK"] pra simplificar
        mock_rsi.return_value = ["OK"]

        items, itens_faltando = render_inspection_groups()
        # Checa se 'items' tem a mesma quantidade de chaves do total
        num_items = sum(len(d.items()) for d in INSPECTION_GROUPS.values())
        assert len(items) == num_items
        assert len(itens_faltando) == 0, "Se sempre retornamos ['OK'], não deve faltar nada."
