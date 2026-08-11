import streamlit as st
import pandas as pd

# Configuração da página para ocupar a tela toda
st.set_page_config(page_title="Lotação 2026", layout="wide")

# ==========================================
# 1. DADOS INICIAIS
# ==========================================
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

# ==========================================
# 2. FUNÇÕES DE APOIO
# ==========================================
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

def calcular_horas_distribuidas():
    ch_distribuida = {}
    
    # Varre todas as matrizes para somar a CH por professor
    df_list = [st.session_state["matriz_ef1"], st.session_state["matriz_ef2"], st.session_state["matriz_em"]]
    turmas_list = [turmas_ef1, turmas_ef2, turmas_em]
    
    for df, turmas in zip(df_list, turmas_list):
        for t in turmas:
            col_ch = f"{t} - CH"
            col_prof = f"{t} - Prof (a)"
            
            # Filtra linhas onde o nome do professor foi preenchido
            valid_rows = df.dropna(subset=[col_prof])
            for _, row in valid_rows.iterrows():
                prof = str(row[col_prof]).strip()
                # Pega a CH, se for inválida assume 0
                ch = pd.to_numeric(row[col_ch], errors='coerce')
                
                if pd.notna(ch) and prof and prof != "None":
                    ch_distribuida[prof] = ch_distribuida.get(prof, 0) + ch
                    
    return ch_distribuida

# ==========================================
# 3. INICIALIZAÇÃO DOS DADOS NA SESSÃO
# ==========================================
if "matriz_ef1" not in st.session_state:
    st.session_state["matriz_ef1"] = criar_df_matriz(turmas_ef1)
if "matriz_ef2" not in st.session_state:
    st.session_state["matriz_ef2"] = criar_df_matriz(turmas_ef2)
if "matriz_em" not in st.session_state:
    st.session_state["matriz_em"] = criar_df_matriz(turmas_em)
if "professores" not in st.session_state:
    st.session_state["professores"] = pd.DataFrame(columns=["Professor (a)", "CH Total"])

# ==========================================
# 4. PAINEL LATERAL (CONTROLE DE CH)
# ==========================================
with st.sidebar:
    st.header("👨‍🏫 Controle de CH")
    st.markdown("1️⃣ **Cadastre a carga total:**")
    
    # Tabela para cadastrar os professores e suas CHs totais
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
    
    # Cálculo em tempo real do status
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
        st.info("Cadastre um professor (a) acima para acompanhar o status.")

# ==========================================
# 5. ÁREA PRINCIPAL (MATRIZ DE LOTAÇÃO)
# ==========================================
st.title("📊 Matriz de Lotação de Professores (as)")
st.markdown("Preencha a Carga Horária (CH) e digite o nome do professor (a) correspondente. O painel lateral atualizará o cálculo automaticamente.")

aba1, aba2, aba3 = st.tabs(["Ensino Fundamental I", "Ensino Fundamental II", "Ensino Médio"])

with aba1:
    st.session_state["matriz_ef1"] = st.data_editor(
        st.session_state["matriz_ef1"],
        column_config=gerar_config_colunas(turmas_ef1),
        use_container_width=True,
        hide_index=True,
        height=1060
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
