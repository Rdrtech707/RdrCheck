import streamlit as st
from modules.inspection_groups import INSPECTION_GROUPS

def init_form_values():
    """Garante que o dicionário persistente 'form_values' esteja inicializado."""
    if "form_values" not in st.session_state:
        st.session_state["form_values"] = {}

def update_form_value(key, new_value):
    """Atualiza o dicionário persistente para a chave dada."""
    st.session_state["form_values"][key] = new_value

def select_first_options():
    """Marca apenas a primeira opção de cada item e desmarca as demais."""
    for group, item_dict in INSPECTION_GROUPS.items():
        for item, options in item_dict.items():
            for j, option in enumerate(options):
                key = f"{group}_{item}_{option}"
                st.session_state["form_values"][key] = (j == 0)

def deselect_all_options():
    """Desmarca todas as opções de todos os grupos/itens."""
    for group, item_dict in INSPECTION_GROUPS.items():
        for item, options in item_dict.items():
            for option in options:
                key = f"{group}_{item}_{option}"
                st.session_state["form_values"][key] = False

def render_single_item(group: str, item: str, options: list) -> list:
    """
    Renderiza um item dentro de um grupo, exibindo a label e os widgets.
    Retorna uma lista com as opções marcadas, conforme os valores persistidos.
    
    Para o caso "MOTOR" e "CORREIA ACESSÓRIOS": se "NÃO OK" estiver marcada,
    exibe um campo obrigatório para o Código da Correia.
    
    Ajusta o espaçamento:
      - Aproxima as opções (checkboxes) do label do item.
      - Afasta visualmente do próximo item.
    """
    init_form_values()  # Garante que o dicionário exista

    selected_values = []
    # Abre um contêiner HTML customizado para controlar o espaçamento
    st.markdown(
        """
        <div style="margin-bottom: 20px; padding-top: 0px; line-height: 0.5;">
        """, unsafe_allow_html=True)
    
    # Cria as colunas: a primeira (maior) para o label e as demais para as checkboxes
    col_sizes = [2] + [1] * len(options)
    cols = st.columns(col_sizes)
    
    with cols[0]:
        st.markdown(f"<span style='font-size:14px; margin-top:0px;'><b>{item}</b></span>", unsafe_allow_html=True)
    
    # Renderiza as checkboxes nos demais espaços da linha
    for i, option in enumerate(options):
        key = f"{group}_{item}_{option}"
        current_val = st.session_state["form_values"].get(key, False)
        with cols[i + 1]:
            new_val = st.checkbox(option, key=key, value=current_val)
        update_form_value(key, new_val)
        if new_val:
            selected_values.append(option)
    
    # Se for "MOTOR" e "CORREIA ACESSÓRIOS" e "NÃO OK" estiver marcada, renderiza o text_input
    if group.upper() == "MOTOR" and item.upper() == "CORREIA ACESSÓRIOS" and "NÃO OK" in selected_values:
        code_key = f"{group}_{item}_codigo"
        current_code = st.session_state["form_values"].get(code_key, "")
        codigo = st.text_input("Digite o Código da Correia", key=code_key, value=current_code)
        update_form_value(code_key, codigo)
        if not codigo:
            st.error("Campo obrigatório: Digite o Código da Correia")
            st.markdown("</div>", unsafe_allow_html=True)
            return []  # Indica que esse item está incompleto
        else:
            selected_values.append(f"Código: {codigo}")
    
    # Fecha o contêiner
    st.markdown("</div>", unsafe_allow_html=True)
    
    return selected_values

def render_inspection_groups():
    """
    Cria as abas a partir do dicionário INSPECTION_GROUPS e, para cada item, chama render_single_item.
    Retorna:
      - items: dicionário {nome_do_item: [opções marcadas (e informações extras, se houver)]}
      - itens_faltando: lista com itens que estão incompletos.
    """
    init_form_values()
    items = {}
    itens_faltando = []

    # Cria abas para cada grupo de inspeção
    abas = st.tabs(list(INSPECTION_GROUPS.keys()))
    for i, (group, item_dict) in enumerate(INSPECTION_GROUPS.items()):
        with abas[i]:
            st.subheader(f"🔍 {group}")
            # Itera em cada item do grupo na ordem de inserção
            for item in item_dict.keys():
                options = item_dict[item]
                selected_values = render_single_item(group, item, options)
                items[item] = selected_values
                if not selected_values:
                    itens_faltando.append(f"{group} ➝ {item}")
    return items, itens_faltando
