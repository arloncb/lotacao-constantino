import streamlit as st
import pandas as pd

st.set_page_config(page_title="Lotação 2026", layout="wide")

st.title("📊 Matriz de Lotação de Professores (as)")
st.markdown("Preencha a Carga Horária (CH) e digite ou selecione o nome do Professor (a) correspondente para cada disciplina.")

# 1. Definição das Disciplinas e Turmas
disciplinas = [
    "Apoio e Orien. de estudos", "Arte", "Biologia", "Ciências", 
    "Ciências Human. e Socie.", "Ciências naturais na Contemporaneidade", 
    "Desenvol. Local", "Ed. Física", "Empresa Pedagógica", "Filosofia", 
    "Física", "Geografia", "História", "Investigação Cien. e Tec.", 
    "Leitura (literatura) e Prod. Textual", "Letram. e rac. Matemático", 
    "Língua Inglesa", "Língua Portuguesa", "Língua Portuguesa - RA", 
    "Literatura Arte e Movimento", "Matemática", "Matemática Geometria", 
    "Matemática-RA", "Química", "Sociologia", "Tecnologia e Cida Digi.", 
    "UC PROFISSIONAL 01", "UC PROFISSIONAL 02", "UC PROFISSIONAL 03"
]

turmas_ef1 = ["4° A", "5° A"]
turmas_ef2 = ["6° A", "6° B", "6° C", "7° A", "8° A", "9° A", "9° B", "9° C", "9° D"]
turmas_em = ["1° A", "1° B", "2° A", "3° A"]

# 2. Função para criar a estrutura da tabela vazia
def criar_df_matriz(turmas):
    cols = ["Disciplina"]
    for t in turmas:
        cols.append(f"{t} - CH")
        cols.append(f"{t} - Prof (a)")
    
    df = pd.DataFrame(columns=cols)
    df["Disciplina"] = disciplinas
    return df

# 3. Inicializando as tabelas na memória do aplicativo
if "matriz_ef1" not in st.session_state:
    st.session_state["matriz_ef1"] = criar_df_matriz(turmas_ef1)
if "matriz_ef2" not in st.session_state:
    st.session_state["matriz_ef2"] = criar_df_matriz(turmas_ef2)
if "matriz_em" not in st.session_state:
    st.session_state["matriz_em"] = criar_df_matriz(turmas_em)

# 4. Configuração visual e regras das colunas
def gerar_config_colunas(turmas):
    config = {
        # Trava a edição da coluna de disciplinas
        "Disciplina": st.column_config.TextColumn("Disciplina", disabled=True)
    }
    for t in turmas:
        # Configura as colunas de CH para aceitarem apenas números
        config[f"{t} - CH"] = st.column_config.NumberColumn("CH", min_value=0, max_value=40, step=1)
        # Configura as colunas de Professores (as) para texto livre
        config[f"{t} - Prof (a)"] = st.column_config.TextColumn("Professor (a)")
    return config

# 5. Interface com Abas (Tabs) para separar os níveis de ensino
aba1, aba2, aba3 = st.tabs(["Ensino Fundamental I", "Ensino Fundamental II", "Ensino Médio"])

with aba1:
    st.session_state["matriz_ef1"] = st.data_editor(
        st.session_state["matriz_ef1"],
        column_config=gerar_config_colunas(turmas_ef1),
        use_container_width=True,
        hide_index=True,
        height=1060 # Altura ajustada para caber todas as disciplinas sem rolagem vertical
    )

with aba2:
    st.session_state["matriz_ef2"] = st.data_editor(
        st.session_state["matriz_ef2"],
        column_config=gerar_config_colunas(turmas_ef2),
        use_container_width=True,
        hide_index=True,
        height=1060
    )

with aba3:
    st.session_state["matriz_em"] = st.data_editor(
        st.session_state["matriz_em"],
        column_config=gerar_config_colunas(turmas_em),
        use_container_width=True,
        hide_index=True,
        height=1060
    )
