import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(page_title="Lotação 2026", layout="wide")

SHEET_URL = "https://docs.google.com/spreadsheets/d/10nQG6fYwRKMbgxAGVOl8Ko8DHjCTt4jPnuGZ1pTqWac/edit"
COLUNAS_LOTACAO = ["PROFESSORES", "DISCIPLINA", "CARGA HORÁRIA", "TURMA", "TURNO"]

# ============================================================
# CONEXÃO COM GOOGLE SHEETS (CORREÇÃO DE PADDING)
# ============================================================
@st.cache_resource
def conectar_gsheets():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # 1. Pega os segredos
    secrets_dict = dict(st.secrets["connections"]["gsheets"])
    
    # 2. Força a re-leitura do objeto para garantir que o formato JSON/TOML
    # não esteja "quebrando" a string da chave privada
    json_str = json.dumps(secrets_dict)
    fixed_dict = json.loads(json_str)
    
    # 3. Garante o formato PEM correto para o Google Auth
    if "private_key" in fixed_dict:
        fixed_dict["private_key"] = fixed_dict["private_key"].replace("\\n", "\n")

    creds = Credentials.from_service_account_info(
        fixed_dict,
        scopes=scope
    )
    
    return gspread.authorize(creds)

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
        
        df = pd.DataFrame(dados) if dados else pd.DataFrame(columns=["PROFESSORES", "CARGA HORÁRIA"])
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
        
        df = pd.DataFrame(dados) if dados else pd.DataFrame(columns=COLUNAS_LOTACAO)
        for col in COLUNAS_LOTACAO:
            if col not in df.columns: df[col] = ""
        df = df[COLUNAS_LOTACAO]
        df["CARGA HORÁRIA"] = pd.to_numeric(df["CARGA HORÁRIA"], errors="coerce").fillna(0)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a Página1: {e}")
        return pd.DataFrame(columns=COLUNAS_LOTACAO)

# ... [Mantenha aqui as suas listas de listas_disciplinas, lista_turmas, etc.] ...

# ============================================================
# INTERFACE PRINCIPAL (Exemplo de estrutura)
# ============================================================
st.title("📋 Sistema de Lotação 2026")

# Restante do seu código permanece igual (tabela, botões, salvamento, etc.)
# O ponto crítico de erro era exclusivamente a conexão.
