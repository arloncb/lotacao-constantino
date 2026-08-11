import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Lotação 2026", layout="wide")

# Conexão com o Google Sheets usando o método nativo seguro do Streamlit
conn = st.connection("gsheets", type="GSheetsConnection")

SHEET_URL = "https://docs.google.com/spreadsheets/d/10nQG6fYwRKMbgxAGVOl8Ko8DHjCTt4jPnuGZ1pTqWac/edit?usp=sharing"

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

def criar_df_matriz(turmas):
    cols = ["Disciplina"]
    for t in turmas:
        cols.append(f"{t} - CH")
        cols.append(f"{t} - Prof (a)")
    df = pd.DataFrame(columns=cols)
    df["Disciplina"] = disciplinas
    return df

def gerar_config_colunas(turmas):
    config = {
        "Disciplina": st.column_config.TextColumn("Disciplina", disabled=True)
    }
    for t in turmas:
        config[f"{t} - CH"] = st.column_config.NumberColumn(f"{t} - CH", min_value=0, max_value=40, step=1)
        config[f"{t} - Prof (a)"] = st.column_config.TextColumn(f"{t} - Prof (a)")
    return config

# Leitura segura da aba EF1
try:
    df_carregado = conn.read(spreadsheet=SHEET_URL, worksheet="EF1", ttl=5)
    if df_carregado.empty or "Disciplina" not in df_carregado.columns:
        df_ef1 = criar_df_matriz(turmas_ef1)
    else:
        df_ef1 = df_carregado
except Exception:
    df_ef1 = criar_df_matriz(turmas_ef1)

if "matriz_ef2" not in st.session_state:
    st.session_state["matriz_ef2"] = criar_df_matriz(turmas_ef2)
if "matriz_em" not in st.session_state:
    st.session_state["matriz_em"] = criar_df_matriz(turmas_em)
if "professores" not in st.session_state:
    st.session_state["professores"] = pd.DataFrame(columns=["Professor (a)", "CH Total"])

def calcular_horas_distribuidas():
    ch_distribuida = {}
    valid_rows = df_ef1.dropna()
    for _, row in valid_rows.iterrows():
        for t in turmas_ef1:
            col_prof = f"{t} - Prof (a)"
            col_ch = f"{t} - CH"
            if col_prof in row and col_ch in row:
                prof = str(row[col_prof]).strip()
                ch = pd.to_numeric(row[col_ch], errors='coerce')
                if pd.notna(ch) and prof and prof != "None" and prof != "nan":
                    ch_distribuida[prof] = ch_distribuida.get(prof, 0) + ch
    return ch_distribuida

with st.sidebar:
    st.header("👨‍🏫 Controle de CH")
    df_profs = st.data_editor(
        st.session_state["professores"],
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Professor (a)": st.column_config.TextColumn("Professor (a)", required=True),
            "CH Total": st.column_config.NumberColumn("CH Total", min_value=1, step=1, required=True)
        }
    )
    st.session_state["professores"] = df_profs
    
    st.divider()
    st.markdown("2️⃣ **Status da Distribuição:**")
    ch_usada = calcular_horas_distribuidas()
    resumo_status = []
    
    for _, row in df_profs.dropna(subset=["Professor (a)"]).iterrows():
        prof = str(row["Professor (a)"]).strip()
        ch_total = pd.to_numeric(row["CH Total"], errors='coerce')
        if pd.isna(ch_total): ch_total = 0
        
        usada = ch_usada.get(prof, 0)
        saldo = ch_total - usada
        
        if saldo == 0:
            status = "✅ OK"
        elif saldo > 0:
            status = f"⚠️ Faltam {int(saldo)}h"
        else:
            status = f"🚨 Sobrou {int(-saldo)}h"
            
        resumo_status.append({
            "Professor (a)": prof,
            "Total": int(ch_total),
            "Distr.": int(usada),
            "Status": status
        })
        
    if resumo_status:
        st.dataframe(pd.DataFrame(resumo_status), use_container_width=True, hide_index=True)
    else:
        st.info("Cadastre um professor (a) acima.")

st.title("📊 Matriz de Lotação de Professores (as)")
st.markdown("Gerencie as turmas e disciplinas por nível de ensino. Os dados do EF1 sincronizam com o Google Sheets.")

aba1, aba2, aba3 = st.tabs(["Ensino Fundamental I", "Ensino Fundamental II", "Ensino Médio"])

with aba1:
    dados_editados_ef1 = st.data_editor(
        df_ef1,
        column_config=gerar_config_colunas(turmas_ef1),
        use_container_width=True,
        hide_index=True,
        height=1060,
        key="editor_ef1"
    )
    
    if st.button("💾 Salvar Alterações no Google Sheets (EF1)"):
        try:
            conn.update(spreadsheet=SHEET_URL, worksheet="EF1", data=dados_editados_ef1)
            st.success("Dados sincronizados com sucesso!")
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

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
