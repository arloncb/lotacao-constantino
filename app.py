import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Lotação 2026",
    layout="wide"
)

SHEET_URL = "https://docs.google.com/spreadsheets/d/10nQG6fYwRKMbgxAGVOl8Ko8DHjCTt4jPnuGZ1pTqWac/edit"


# ============================================================
# COLUNAS DA ABA PÁGINA1
# ============================================================

COLUNAS_LOTACAO = [
    "PROFESSORES",
    "DISCIPLINA",
    "CARGA HORÁRIA",
    "TURMA",
    "TURNO"
]


# ============================================================
# CONEXÃO COM GOOGLE SHEETS
# ============================================================

def conectar_gsheets():

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = dict(
        st.secrets["connections"]["gsheets"]
    )

    if "private_key" in creds_dict:
        creds_dict["private_key"] = (
            creds_dict["private_key"]
            .replace("\\n", "\n")
        )

    creds = Credentials.from_service_account_info(
        creds_dict,
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

        spreadsheet = client.open_by_url(
            SHEET_URL
        )

        worksheet = spreadsheet.worksheet(
            "PROFESSORES"
        )

        # Lê os dados considerando a primeira linha
        # como cabeçalho
        dados = worksheet.get_all_records()

        if not dados:

            return pd.DataFrame(
                columns=[
                    "PROFESSORES",
                    "CARGA HORÁRIA"
                ]
            )

        df = pd.DataFrame(dados)

        # ----------------------------------------------------
        # Verifica os cabeçalhos da planilha
        # ----------------------------------------------------

        if "PROFESSORES" not in df.columns:

            st.error(
                "A aba PROFESSORES precisa ter "
                "'PROFESSORES' na célula A1."
            )

            return pd.DataFrame(
                columns=[
                    "PROFESSORES",
                    "CARGA HORÁRIA"
                ]
            )

        if "CARGA HORÁRIA" not in df.columns:

            st.error(
                "A aba PROFESSORES precisa ter "
                "'CARGA HORÁRIA' na célula B1."
            )

            return pd.DataFrame(
                columns=[
                    "PROFESSORES",
                    "CARGA HORÁRIA"
                ]
            )

        # ----------------------------------------------------
        # Limpeza dos dados
        # ----------------------------------------------------

        df["PROFESSORES"] = (
            df["PROFESSORES"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        df["CARGA HORÁRIA"] = pd.to_numeric(
            df["CARGA HORÁRIA"],
            errors="coerce"
        ).fillna(0)

        # Remove linhas sem nome
        df = df[
            df["PROFESSORES"] != ""
        ]

        # Remove possíveis duplicidades
        df = df.drop_duplicates(
            subset=["PROFESSORES"],
            keep="last"
        )

        return df.reset_index(drop=True)

    except Exception as e:

        st.error(
            f"Erro ao carregar a aba PROFESSORES: {e}"
        )

        return pd.DataFrame(
            columns=[
                "PROFESSORES",
                "CARGA HORÁRIA"
            ]
        )


# ============================================================
# CARREGAR DADOS DA ABA PÁGINA1
# ============================================================

@st.cache_data(ttl=10)
def carregar_lotacao():

    try:

        client = conectar_gsheets()

        spreadsheet = client.open_by_url(
            SHEET_URL
        )

        worksheet = spreadsheet.worksheet(
            "Página1"
        )

        dados = worksheet.get_all_records()

        if not dados:

            return pd.DataFrame(
                columns=COLUNAS_LOTACAO
            )

        df = pd.DataFrame(dados)

        # ----------------------------------------------------
        # Garante que todas as colunas existam
        # ----------------------------------------------------

        for coluna in COLUNAS_LOTACAO:

            if coluna not in df.columns:
                df[coluna] = ""

        df = df[
            COLUNAS_LOTACAO
        ]

        # ----------------------------------------------------
        # Converte carga horária
        # ----------------------------------------------------

        df["CARGA HORÁRIA"] = pd.to_numeric(
            df["CARGA HORÁRIA"],
            errors="coerce"
        )

        return df

    except Exception as e:

        st.error(
            f"Erro ao carregar a Página1: {e}"
        )

        return pd.DataFrame(
            columns=COLUNAS_LOTACAO
        )


# ============================================================
# LISTA DE DISCIPLINAS
# ============================================================

lista_disciplinas = [

    "Apoio e Orien. de estudos",
    "Arte",
    "Biologia",
    "Ciências",
    "Ciências Human. e Socie.",
    "Ciências naturais na Contemporaneidade",
    "Desenvol. Local",
    "Ed. Física",
    "Empresa Pedagógica",
    "Filosofia",
    "Física",
    "Geografia",
    "História",
    "Investigação Cien. e Tec.",
    "Leitura (literatura) e Prod. Textual",
    "Letram. e rac. Matemático",
    "Língua Inglesa",
    "Língua Portuguesa",
    "Língua Portuguesa - RA",
    "Literatura Arte e Movimento",
    "Matemática",
    "Matemática Geometria",
    "Matemática-RA",
    "Química",
    "Sociologia",
    "Tecnologia e Cida Digi.",
    "UC PROFISSIONAL 01",
    "UC PROFISSIONAL 02",
    "UC PROFISSIONAL 03"
]


# ============================================================
# LISTA DE TURMAS
# ============================================================

lista_turmas = [

    "4° A",
    "5° A",
    "6° A",
    "6° B",
    "6° C",
    "7° A",
    "8° A",
    "9° A",
    "9° B",
    "9° C",
    "9° D",
    "1° A",
    "1° B",
    "2° A",
    "3° A"
]


# ============================================================
# LISTA DE TURNOS
# ============================================================

lista_turnos = [
    "Matutino",
    "Vespertino",
    "Noturno",
    "Integral"
]


# ============================================================
# CARREGAR OS DADOS
# ============================================================

df_professores = carregar_professores()

df_dados = carregar_lotacao()


# ============================================================
# LISTA DE PROFESSORES
# ============================================================

lista_professores = (
    df_professores["PROFESSORES"]
    .dropna()
    .astype(str)
    .str.strip()
    .tolist()
)


# ============================================================
# CALCULAR CH DISTRIBUÍDA
# ============================================================

def calcular_horas_atribuidas(df):

    resultado = {}

    if df.empty:
        return resultado

    if (
        "PROFESSORES" not in df.columns
        or "CARGA HORÁRIA" not in df.columns
    ):
        return resultado

    for _, linha in df.iterrows():

        professor = str(
            linha["PROFESSORES"]
        ).strip()

        ch = pd.to_numeric(
            linha["CARGA HORÁRIA"],
            errors="coerce"
        )

        if (
            professor
            and professor.lower()
            not in ["nan", "none"]
            and pd.notna(ch)
        ):

            resultado[professor] = (
                resultado.get(
                    professor,
                    0
                )
                + float(ch)
            )

    return resultado


# ============================================================
# TÍTULO
# ============================================================

st.title(
    "📋 Sistema de Lotação 2026"
)

st.markdown(
    """
    Distribua as aulas dos professores por
    **disciplina, turma e turno**.

    Os professores e suas respectivas cargas horárias
    são carregados automaticamente da aba
    **PROFESSORES** do Google Sheets.
    """
)


# ============================================================
# INFORMAÇÃO SOBRE PROFESSORES
# ============================================================

if not lista_professores:

    st.warning(
        "Nenhum professor foi encontrado na aba "
        "**PROFESSORES** do Google Sheets."
    )

    st.info(
        "Adicione o nome do professor na coluna A "
        "e a carga horária na coluna B."
    )


# ============================================================
# CONFIGURAÇÃO DA TABELA
# ============================================================

configuracao_colunas = {

    "PROFESSORES": st.column_config.SelectboxColumn(
        "PROFESSORES",
        options=lista_professores,
        required=True,
        help=(
            "Selecione um professor cadastrado "
            "na aba PROFESSORES."
        )
    ),

    "DISCIPLINA": st.column_config.SelectboxColumn(
        "DISCIPLINA",
        options=lista_disciplinas,
        required=True
    ),

    "CARGA HORÁRIA": st.column_config.NumberColumn(
        "CARGA HORÁRIA",
        min_value=1,
        max_value=40,
        step=1,
        required=True
    ),

    "TURMA": st.column_config.SelectboxColumn(
        "TURMA",
        options=lista_turmas,
        required=True
    ),

    "TURNO": st.column_config.SelectboxColumn(
        "TURNO",
        options=lista_turnos,
        required=True
    )
}


# ============================================================
# TABELA DE LOTAÇÃO
# ============================================================

df_editado = st.data_editor(

    df_dados,

    column_config=configuracao_colunas,

    num_rows="dynamic",

    use_container_width=True,

    hide_index=True,

    height=600,

    key="editor_lotacao"
)


# ============================================================
# CH EM TEMPO REAL
# ============================================================

horas_atribuidas = calcular_horas_atribuidas(
    df_editado
)


# ============================================================
# PAINEL LATERAL
# ============================================================

with st.sidebar:

    st.header(
        "👨‍🏫 Controle de CH"
    )

    st.caption(
        "Dados carregados da aba PROFESSORES."
    )

    if not df_professores.empty:

        status_lista = []

        for _, professor_row in df_professores.iterrows():

            professor = str(
                professor_row["PROFESSORES"]
            ).strip()

            ch_total = pd.to_numeric(
                professor_row["CARGA HORÁRIA"],
                errors="coerce"
            )

            if pd.isna(ch_total):
                ch_total = 0

            ch_alocada = horas_atribuidas.get(
                professor,
                0
            )

            saldo = (
                float(ch_total)
                - float(ch_alocada)
            )

            # ------------------------------------------------
            # STATUS
            # ------------------------------------------------

            if saldo == 0:

                status = "✅ COMPLETA"

            elif saldo > 0:

                status = (
                    f"⚠️ Faltam {int(saldo)}h"
                )

            else:

                status = (
                    f"🚨 Excedeu "
                    f"{int(abs(saldo))}h"
                )

            status_lista.append({

                "Professor": professor,

                "CH Total": int(ch_total),

                "Alocada": int(ch_alocada),

                "Saldo": int(saldo),

                "Status": status
            })

        df_status = pd.DataFrame(
            status_lista
        )

        # ----------------------------------------------------
        # TABELA DE STATUS
        # ----------------------------------------------------

        st.dataframe(
            df_status,
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # RESUMO GERAL
        # ----------------------------------------------------

        st.divider()

        total_ch_professores = (
            pd.to_numeric(
                df_professores[
                    "CARGA HORÁRIA"
                ],
                errors="coerce"
            )
            .fillna(0)
            .sum()
        )

        total_ch_alocada = sum(
            horas_atribuidas.values()
        )

        saldo_geral = (
            total_ch_professores
            - total_ch_alocada
        )

        st.metric(
            "CH total a distribuir",
            f"{int(total_ch_professores)}h"
        )

        st.metric(
            "CH já distribuída",
            f"{int(total_ch_alocada)}h"
        )

        if saldo_geral >= 0:

            st.metric(
                "Saldo geral",
                f"{int(saldo_geral)}h"
            )

        else:

            st.metric(
                "Excesso geral",
                f"{int(abs(saldo_geral))}h"
            )


# ============================================================
# RESUMO PRINCIPAL
# ============================================================

st.divider()

col1, col2, col3, col4 = st.columns(4)


# Total de lançamentos

total_lancamentos = len(
    df_editado
)


# CH distribuída

total_ch_distribuida = (
    pd.to_numeric(
        df_editado["CARGA HORÁRIA"],
        errors="coerce"
    )
    .fillna(0)
    .sum()
)


# Total de professores

total_professores = len(
    df_professores
)


# Professores excedidos

professores_excedidos = 0

for _, row in df_professores.iterrows():

    professor = str(
        row["PROFESSORES"]
    ).strip()

    ch_total = pd.to_numeric(
        row["CARGA HORÁRIA"],
        errors="coerce"
    )

    if pd.isna(ch_total):
        continue

    ch_alocada = horas_atribuidas.get(
        professor,
        0
    )

    if ch_alocada > ch_total:

        professores_excedidos += 1


with col1:

    st.metric(
        "Lançamentos",
        total_lancamentos
    )


with col2:

    st.metric(
        "CH distribuída",
        f"{int(total_ch_distribuida)}h"
    )


with col3:

    st.metric(
        "Professores",
        total_professores
    )


with col4:

    st.metric(
        "Professores com excesso",
        professores_excedidos
    )


# ============================================================
# ALERTA DE EXCESSO
# ============================================================

if professores_excedidos > 0:

    st.error(
        f"🚨 Existem {professores_excedidos} professor(es) "
        "com carga horária acima do previsto."
    )


# ============================================================
# PROFESSORES COM CH PENDENTE
# ============================================================

professores_pendentes = []

for _, row in df_professores.iterrows():

    professor = str(
        row["PROFESSORES"]
    ).strip()

    ch_total = pd.to_numeric(
        row["CARGA HORÁRIA"],
        errors="coerce"
    )

    if pd.isna(ch_total):
        continue

    ch_alocada = horas_atribuidas.get(
        professor,
        0
    )

    saldo = (
        ch_total
        - ch_alocada
    )

    if saldo > 0:

        professores_pendentes.append({

            "Professor": professor,

            "CH Total": int(ch_total),

            "Alocada": int(ch_alocada),

            "Faltam": int(saldo)
        })


if professores_pendentes:

    with st.expander(
        "⚠️ Professores com CH ainda não distribuída",
        expanded=False
    ):

        st.dataframe(
            pd.DataFrame(
                professores_pendentes
            ),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# BOTÕES
# ============================================================

st.divider()

col_atualizar, col_salvar = st.columns(2)


# ============================================================
# ATUALIZAR PROFESSORES
# ============================================================

with col_atualizar:

    if st.button(
        "🔄 Atualizar professores do Google Sheets",
        use_container_width=True
    ):

        carregar_professores.clear()

        carregar_lotacao.clear()

        st.rerun()


# ============================================================
# SALVAR LOTAÇÃO
# ============================================================

with col_salvar:

    salvar = st.button(
        "💾 Salvar Lotação no Google Sheets",
        type="primary",
        use_container_width=True
    )


if salvar:

    try:

        # ----------------------------------------------------
        # Verifica professores utilizados
        # ----------------------------------------------------

        professores_digitados = set(
            df_editado[
                "PROFESSORES"
            ]
            .dropna()
            .astype(str)
            .str.strip()
        )

        professores_cadastrados = set(
            lista_professores
        )

        professores_invalidos = (
            professores_digitados
            - professores_cadastrados
        )

        if professores_invalidos:

            nomes = ", ".join(
                sorted(
                    professores_invalidos
                )
            )

            st.error(
                "Não foi possível salvar porque "
                "existem professores que não estão "
                "cadastrados na aba PROFESSORES: "
                f"{nomes}"
            )

            st.stop()


        # ----------------------------------------------------
        # Conecta ao Google Sheets
        # ----------------------------------------------------

        client = conectar_gsheets()

        spreadsheet = client.open_by_url(
            SHEET_URL
        )

        worksheet = spreadsheet.worksheet(
            "Página1"
        )


        # ----------------------------------------------------
        # Prepara os dados
        # ----------------------------------------------------

        df_salvar = df_editado.copy()

        df_salvar = df_salvar.fillna("")

        df_salvar["CARGA HORÁRIA"] = (
            pd.to_numeric(
                df_salvar["CARGA HORÁRIA"],
                errors="coerce"
            )
            .fillna("")
        )


        dados_para_salvar = (
            [
                df_salvar.columns.tolist()
            ]
            +
            df_salvar.values.tolist()
        )


        # ----------------------------------------------------
        # Limpa somente a Página1
        # ----------------------------------------------------

        worksheet.clear()


        # ----------------------------------------------------
        # Grava os dados
        # ----------------------------------------------------

        worksheet.update(
            "A1",
            dados_para_salvar
        )


        # ----------------------------------------------------
        # Limpa cache
        # ----------------------------------------------------

        carregar_lotacao.clear()

        carregar_professores.clear()


        # ----------------------------------------------------
        # Mensagem
        # ----------------------------------------------------

        st.success(
            "✅ Lotação salva com sucesso na aba Página1!"
        )


        # ----------------------------------------------------
        # Recarrega
        # ----------------------------------------------------

        st.rerun()


    except Exception as e:

        st.error(
            f"❌ Erro ao salvar a lotação: {e}"
        )
