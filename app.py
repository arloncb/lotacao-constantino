import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Configuração da página
st.set_page_config(page_title="Lotação 2026", layout="wide")

SHEET_URL = "https://docs.google.com/spreadsheets/d/10nQG6fYwRKMbgxAGVOl8Ko8DHjCTt4jPnuGZ1pTqWac/edit?usp=sharing"

# Configuração da conexão com o Google Sheets via gspread usando os Secrets
def conectar_gsheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["connections"]["gsheets"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client

# Listas padrão para validação nos menus suspensos
lista_disciplinas = [
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

lista_turmas = [
    "4° A", "5° A", 
    "6° A", "6° B", "6° C", "7° A", "8° A", "9° A", "9° B", "9° C", "9° D", 
    "1° A", "1° B", "2° A", "3° A"
]

lista_turnos = ["Matutino", "Vespertino", "Noturno", "Integral"]

# Função para carregar os dados da Página1
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        client = conectar_gsheets()
        sheet = client.open_by_url(SHEET_URL)
        worksheet = sheet.worksheet("Página1")
        dados = worksheet.get_all_records()
        if not dados:
            return pd.DataFrame(columns=["PROFESSOR(A)", "DISCIPLINA", "CARGA HORÁRIA", "TURMA", "TURNO"])
        return pd.DataFrame(dados)
    except Exception as e:
        st.error(f"Erro ao carregar dados da planilha: {e}")
        return pd.DataFrame(columns=["PROFESSOR(A)", "DISCIPLINA", "CARGA HORÁRIA", "TURMA", "TURNO"])

df_dados = carregar_dados()

# Inicializa tabela de controle de CH na sessão caso não exista
if "professores_ch" not in st.session_state:
    st.session_state["professores_ch"] = pd.DataFrame(columns=["Professor (a)", "CH Total"])

# Função para calcular o total de horas alocadas por professor
def calcular_horas_atribuidas(df):
    alocadas = {}
    if not df.empty and "PROFESSOR(A)" in df.columns and "CARGA HORÁRIA" in df.columns:
        for _, row in df.dropna(subset=["PROFESSOR(A)"]).iterrows():
            prof = str(row["PROFESSOR(A)"]).strip()
            ch = pd.to_numeric(row["CARGA HORÁRIA"], errors='coerce')
            if pd.notna(ch) and prof and prof != "nan" and prof != "None":
                alocadas[prof] = alocadas.get(prof, 0) + ch
    return alocadas

# Painel Lateral para o Controle de Carga Horária Total
with st.sidebar:
    st.header("👨‍🏫 Controle de CH Total")
    st.markdown("Cadastre a carga horária total contratada de cada professor(a):")
    
    df_profs_cadastrados = st.data_editor(
        st.session_state["professores_ch"],
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Professor (a)": st.column_config.TextColumn("Professor (a)", required=True),
            "CH Total": st.column_config.NumberColumn("CH Total", min_value=1, step=1, required=True)
        },
        key="editor_profs"
    )
    st.session_state["professores_ch"] = df_profs_cadastrados
    
    st.divider()
    st.markdown("📊 **Status da Distribuição:**")
    
    horas_atribuidas = calcular_horas_atribuidas(df_dados)
    status_lista = []
    
    for _, row in df_profs_cadastrados.dropna(subset=["Professor (a)"]).iterrows():
        prof = str(row["Professor (a)"]).strip()
        ch_total = pd.to_numeric(row["CH Total"], errors='coerce')
        if pd.isna(ch_total): 
            ch_total = 0
            
        usada = horas_atribuidas.get(prof, 0)
        saldo = ch_total - usada
        
        if saldo == 0:
            st_txt = "✅ OK"
        elif saldo > 0:
            st_txt = f"⚠️ Faltam {int(saldo)}h"
        else:
            st_txt = f"🚨 Passou {int(-saldo)}h"
            
        status_lista.append({
            "Professor (a)": prof,
            "Total": int(ch_total),
            "Alocado": int(usada),
            "Status": st_txt
        })
        
    if status_lista:
        st.dataframe(pd.DataFrame(status_lista), use_container_width=True, hide_index=True)
    else:
        st.info("Cadastre os professores acima para ver o balanço.")

# Área Principal: Tabela de Lotação (Página1)
st.title("📋 Sistema de Lotação - Página1")
st.markdown("Adicione ou edite os lançamentos de lotação diretamente na tabela abaixo. Clique no botão para salvar na planilha.")

configuracao_colunas = {
    "PROFESSOR(A)": st.column_config.TextColumn("PROFESSOR(A)", required=True),
    "DISCIPLINA": st.column_config.SelectboxColumn("DISCIPLINA", options=lista_disciplinas, required=True),
    "CARGA HORÁRIA": st.column_config.NumberColumn("CARGA HORÁRIA", min_value=1, max_value=40, step=1, required=True),
    "TURMA": st.column_config.SelectboxColumn("TURMA", options=lista_turmas, required=True),
    "TURNO": st.column_config.SelectboxColumn("TURNO", options=lista_turnos, required=True)
}

df_editado = st.data_editor(
    df_dados,
    column_config=configuracao_colunas,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    height=600,
    key="editor_lotacao"
)

# Botão para salvar alterações de volta na Planilha do Google
if st.button("💾 Salvar Alterações na Planilha do Google", type="primary"):
    try:
        client = conectar_gsheets()
        sheet = client.open_by_url(SHEET_URL)
        worksheet = sheet.worksheet("Página1")
        
        worksheet.clear()
        dados_para_salvar = [df_editado.columns.values.tolist()] + df_editado.fillna("").values.tolist()
        worksheet.update(dados_para_salvar)
        
        st.cache_data.clear()
        st.success("Dados salvos e sincronizados com sucesso na Página1 do Google Sheets!")
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao salvar na planilha: {e}")
