import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Lotação 2026",
    layout="wide"
)

SHEET_URL = "https://docs.google.com/spreadsheets/d/10nQG6fYwRKMbgxAGVOl8Ko8DHjCTt4jPnuGZ1pTqWac/edit"

COLUNAS_LOTACAO = [
    "PROFESSORES",
    "DISCIPLINA",
    "CARGA HORÁRIA",
    "TURMA",
    "TURNO"
]


# ============================================================
# CONEXÃO COM GOOGLE SHEETS (BLINDADA PARA PADDING)
# ============================================================
@st.cache_resource
def conectar_gsheets():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # Pega o dicionário de conexões do secrets
    secrets_dict = dict(st.secrets["connections"]["gsheets"])

    # Normaliza via JSON para evitar problemas de parsing do TOML do Streamlit
    json_str = json.dumps(secrets_dict)
    fixed_dict = json.loads(json_str)

    # Converte explicitamente os \n literais em quebras de linha reais do PEM
    if "private_key" in fixed_dict:
        fixed_dict["private_key"] = fixed_dict["private_key"].replace("\\n", "\n")

    creds = Credentials.from_service_account_info(
        fixed_dict,
        scopes=scope
    )

    client = gspread.authorize(creds)
    return client


# ============================================================
# CARREGAR PROFESSORES DA ABA PROFESSORES
# ============================================================
@st.cache_data(ttl=10)
def carregar_professores():
    try:
        client = conectar_gsheets()
        spreadsheet = client.open_by_url(SHEET_URL)
        worksheet = spreadsheet.worksheet("PROFESSORES")
        dados = worksheet.get_all_records()

        if not dados:
            return pd.DataFrame(columns=["PROFESSORES", "CARGA HORÁRIA"])

        df = pd.DataFrame(dados)

        if "PROFESSORES" not in df.columns or "CARGA HORÁRIA" not in df.columns:
            st.error("A aba PROFESSORES precisa ter 'PROFESSORES' e 'CARGA HORÁRIA' no cabeçalho.")
            return pd.DataFrame(columns=["PROFESSORES", "CARGA HORÁRIA"])

        df["PROFESSORES"] = df["PROFESSORES"].fillna("").astype(str).str.strip()
        df["CARGA HORÁRIA"] = pd.to_numeric(df["CARGA HORÁRIA"], errors="coerce").fillna(0)
        df = df[df["PROFESSORES"] != ""]
        df = df.drop_duplicates(subset=["PROFESSORES"], keep="last")

        return df.reset_index(drop=True)

    except Exception as e:
        st.error(f"Erro ao carregar a aba PROFESSORES: {e}")
        return pd.DataFrame(columns=["PROFESSORES", "CARGA HORÁRIA"])


# ============================================================
# CARREGAR DADOS DA ABA PÁGINA1
# ============================================================
@st.cache_data(ttl=10)
def carregar_lotacao():
    try:
        client = conectar_gsheets()
        spreadsheet = client.open_by_url(SHEET_URL)
        worksheet = spreadsheet.worksheet("Página1")
        dados = worksheet.get_all_records()

        if not dados:
            return pd.DataFrame(columns=COLUNAS_LOTACAO)

        df = pd.DataFrame(dados)

        for coluna in COLUNAS_LOTACAO:
            if coluna not in df.columns:
                df[coluna] = ""

        df = df[COLUNAS_LOTACAO]
        df["CARGA HORÁRIA"] = pd.to_numeric(df["CARGA HORÁRIA"], errors="coerce").fillna(0)

        return df

    except Exception as e:
        st.error(f"Erro ao carregar a Página1: {e}")
        return pd.DataFrame(columns=COLUNAS_LOTACAO)


# ============================================================
# LISTAS DE CONFIGURAÇÃO
# ============================================================
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
    "4° A", "5° A", "6° A", "6° B", "6° C", "7° A", "8° A", 
    "9° A", "9° B", "9° C", "9° D", "1° A", "1° B", "2° A", "3° A"
]

lista_turnos = ["Matutino", "Vespertino", "Noturno", "Integral"]


# ============================================================
# CARREGAR OS DADOS NA EXECUÇÃO
# ============================================================
df_professores = carregar_professores()
df_dados = carregar_lotacao()

lista_professores = (
    df_professores["PROFESSORES"]
    .dropna()
    .astype(str)
    .str.strip()
    .tolist()
)


# ============================================================
# FUNÇÃO DE CÁLCULO DE CH
# ============================================================
def calcular_horas_atribuidas(df):
    resultado = {}
    if df.empty or "PROFESSORES" not in df.columns or "CARGA HORÁRIA" not in df.columns:
        return resultado

    for _, linha in df.iterrows():
        professor = str(linha["PROFESSORES"]).strip()
        ch = pd.to_numeric(linha["CARGA HORÁRIA"], errors="coerce")

        if professor and professor.lower() not in ["nan", "none"] and pd.notna(ch):
            resultado[professor] = resultado.get(professor, 0) + float(ch)

    return resultado


# ============================================================
# INTERFACE DA APLICAÇÃO
# ============================================================
st.title("📋 Sistema de Lotação 2026")
st.markdown("Distribua as aulas dos professores por **disciplina, turma e turno**.")

if not lista_professores:
    st.warning("Nenhum professor encontrado na aba **PROFESSORES** do Google Sheets.")

configuracao_colunas = {
    "PROFESSORES": st.column_config.SelectboxColumn("PROFESSORES", options=lista_professores, required=True),
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

horas_atribuidas = calcular_horas_atribuidas(df_editado)

# Sidebar de controle
with st.sidebar:
    st.header("👨‍🏫 Controle de CH")
    if not df_professores.empty:
        status_lista = []
        for _, r in df_professores.iterrows():
            prof = str(r["PROFESSORES"]).strip()
            ch_t = pd.to_numeric(r["CARGA HORÁRIA"], errors="coerce") or 0
            ch_a = horas_atribuidas.get(prof, 0)
            saldo = float(ch_t) - float(ch_a)
            
            if saldo == 0:
                status = "✅ COMPLETA"
            elif saldo > 0:
                status = f"⚠️ Faltam {int(saldo)}h"
            else:
                status = f"🚨 Excedeu {int(abs(saldo))}h"

            status_lista.append({"Professor": prof, "CH Total": int(ch_t), "Alocada": int(ch_a), "Saldo": int(saldo), "Status": status})
        
        st.dataframe(pd.DataFrame(status_lista), use_container_width=True, hide_index=True)

st.divider()
col_atualizar, col_salvar = st.columns(2)

with col_atualizar:
    if st.button("🔄 Atualizar dados", use_container_width=True):
        carregar_professores.clear()
        carregar_lotacao.clear()
        st.rerun()

with col_salvar:
    if st.button("💾 Salvar Lotação no Google Sheets", type="primary", use_container_width=True):
        try:
            client = conectar_gsheets()
            ws = client.open_by_url(SHEET_URL).worksheet("Página1")
            ws.clear()
            dados_salvar = [df_editado.columns.tolist()] + df_editado.fillna("").values.tolist()
            ws.update(range_name="A1", values=dados_salvar)
            st.success("✅ Salvo com sucesso!")
            carregar_lotacao.clear()
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erro ao salvar: {e}")
