import streamlit as st
import pandas as pd

# Configuração da página para ocupar a tela toda
st.set_page_config(page_title="Lotação 2026", layout="wide")

st.title("📊 Matriz de Lotação de Professores")
st.markdown("Edite os dados diretamente na tabela abaixo, como se fosse uma planilha. Você pode adicionar novas linhas no final ou colar dados do Excel/Google Sheets.")

# Cria um banco de dados vazio com algumas linhas iniciais para facilitar o preenchimento
if "lotacoes" not in st.session_state:
    # Gerando 15 linhas vazias padrão para começar a edição
    df_inicial = pd.DataFrame(
        index=range(15),
        columns=[
            "Nome do Professor (a)", "Vínculo", "Licença Médica", "Estabilidade Gestante",
            "Nível de Ensino", "Turma", "Turno", "Disciplina", 
            "Carga Horária", "Vaga Pura"
        ]
    )
    # Preenchendo valores padrão para os checkboxes funcionarem bem
    df_inicial["Licença Médica"] = False
    df_inicial["Estabilidade Gestante"] = False
    df_inicial["Vaga Pura"] = False
    
    st.session_state["lotacoes"] = df_inicial

# Configuração das colunas para criar "menus suspensos" (dropdowns) e checkboxes direto na tabela
configuracao_colunas = {
    "Nome do Professor (a)": st.column_config.TextColumn("Nome do Professor (a)", required=True),
    "Vínculo": st.column_config.SelectboxColumn(
        "Vínculo", 
        options=["Efetivo", "Convocado"],
        required=True
    ),
    "Licença Médica": st.column_config.CheckboxColumn("Licença Médica", default=False),
    "Estabilidade Gestante": st.column_config.CheckboxColumn("Estabil. Gestante", default=False),
    "Nível de Ensino": st.column_config.SelectboxColumn(
        "Nível de Ensino",
        options=["Ensino Fundamental I", "Ensino Fundamental II", "Ensino Médio"],
        required=True
    ),
    "Turma": st.column_config.TextColumn("Turma (Ex: 6º A, 1º Ano A)"),
    "Turno": st.column_config.SelectboxColumn(
        "Turno",
        options=["Matutino", "Vespertino", "Noturno", "Integral"]
    ),
    "Disciplina": st.column_config.SelectboxColumn(
        "Disciplina",
        options=[
            "Arte", "Ciências", "Ciências Human. e Socie.", "Ciências naturais na Contemporaneidade", 
            "Educação Física", "Filosofia", "Física", "Geografia", "História", 
            "Leitura (literatura) e Prod. Textual", "Letram. e rac. Matemático",
            "Língua Inglesa", "Língua Portuguesa", "Matemática", "Matemática Geometria", 
            "Química", "Sociologia", "Tecnologia e Cida Digi."
        ],
        required=True
    ),
    "Carga Horária": st.column_config.NumberColumn("CH Semanal", min_value=1, max_value=40, step=1),
    "Vaga Pura": st.column_config.CheckboxColumn("Vaga Pura", default=False)
}

# Renderiza a planilha editável
dados_editados = st.data_editor(
    st.session_state["lotacoes"],
    column_config=configuracao_colunas,
    num_rows="dynamic", # Permite adicionar ou excluir linhas
    use_container_width=True,
    hide_index=True,
    height=600 # Deixa a tabela bem grande na tela
)

# Salvar o estado atualizado
st.session_state["lotacoes"] = dados_editados

# Métricas no rodapé
st.divider()
df_preenchido = dados_editados.dropna(subset=["Nome do Professor (a)"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Professores Lançados", len(df_preenchido))
col2.metric("Vagas Puras", len(df_preenchido[df_preenchido["Vaga Pura"] == True]))
col3.metric("Total CH Lançada", int(df_preenchido["Carga Horária"].sum()) if not df_preenchido.empty else 0)
col4.download_button(
    label="📥 Baixar Tabela Preenchida",
    data=df_preenchido.to_csv(index=False).encode('utf-8'),
    file_name='lotacao_2026.csv',
    mime='text/csv'
)
