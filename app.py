import streamlit as st
import pandas as pd
import gspread
import base64
from google.oauth2.service_account import Credentials

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(page_title="Lotação 2026", layout="wide")

SHEET_URL = "https://docs.google.com/spreadsheets/d/10nQG6fYwRKMbgxAGVOl8Ko8DHjCTt4jPnuGZ1pTqWac/edit"

COLUNAS_LOTACAO = ["PROFESSORES", "DISCIPLINA", "CARGA HORÁRIA", "TURMA", "TURNO"]

# ============================================================
# CONEXÃO COM GOOGLE SHEETS
# ============================================================
@st.cache_resource
def conectar_gsheets():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # Carrega os segredos do Streamlit Cloud
    creds_dict = dict(st.secrets["connections"]["gsheets"])

    # TRATAMENTO DO ERRO DE PADDING:
    # Garante que os \n literais no segredo virem quebras de linha reais
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=scope
    )

    client = gspread.authorize(creds)
    return client

# ============================================================
# CARREGAR DADOS
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
        df["PROFESSORES"] = df["PROFESSORES"].fillna("").astype(str).str.strip()
        df["CARGA HORÁRIA"] = pd.to_numeric(df["CARGA HORÁRIA"], errors="coerce").fillna(0)
        df = df[df["PROFESSORES"] != ""]
        return df.drop_duplicates(subset=["PROFESSORES"], keep="last").reset_index(drop=True)
    except Exception as e:
        st.error(f"Erro ao carregar a aba PROFESSORES: {e}")
        return pd.DataFrame(columns=["PROFESSORES", "CARGA HORÁRIA"])

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
        for col in COLUNAS_LOTACAO:
            if col not in df.columns: df[col] = ""
        df = df[COLUNAS_LOTACAO]
        df["CARGA HORÁRIA"] = pd.to_numeric(df["CARGA HORÁRIA"], errors="coerce").fillna(0)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a Página1: {e}")
        return pd.DataFrame(columns=COLUNAS_LOTACAO)

# ... [Mantenha aqui todas as suas listas de disciplinas, turmas e turnos anteriores] ...
lista_disciplinas = ["Apoio e Orien. de estudos", "Arte", "Biologia", "Ciências", "Ciências Human. e Socie.", "Ciências naturais na Contemporaneidade", "Desenvol. Local", "Ed. Física", "Empresa Pedagógica", "Filosofia", "Física", "Geografia", "História", "Investigação Cien. e Tec.", "Leitura (literatura) e Prod. Textual", "Letram. e rac. Matemático", "Língua Inglesa", "Língua Portuguesa", "Língua Portuguesa - RA", "Literatura Arte e Movimento", "Matemática", "Matemática Geometria", "Matemática-RA", "Química", "Sociologia", "Tecnologia e Cida Digi.", "UC PROFISSIONAL 01", "UC PROFISSIONAL 02", "UC PROFISSIONAL 03"]
lista_turmas = ["4° A", "5° A", "6° A", "6° B", "6° C", "7° A", "8° A", "9° A", "9° B", "9° C", "9° D", "1° A", "1° B", "2° A", "3° A"]
lista_turnos = ["Matutino", "Vespertino", "Noturno", "Integral"]

# Execução principal
df_professores = carregar_professores()
df_dados = carregar_lotacao()
lista_professores = df_professores["PROFESSORES"].dropna().astype(str).str.strip().tolist()

# ... [O restante do seu código de interface, botões e salvamento permanece o mesmo] ...
# Dica: O código daqui para baixo não precisa mudar, o problema era apenas a conexão!
st.title("📋 Sistema de Lotação 2026")
# ... (continue com seu código de exibição e edição)
