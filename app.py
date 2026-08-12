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

SHEET_URL = "https://docs.google.com/spreadsheets/d/10nQG6fYwRKMbgxAGVOl8Ko8DHjCTt4jPnuGZ1pTqWac/edit?usp=sharing"


# ============================================================
# CONEXÃO COM GOOGLE SHEETS
# ============================================================

def conectar_gsheets():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = dict(st.secrets["connections"]["gsheets"])

    # Corrige as quebras de linha da chave privada
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace(
            "\\n",
            "\n"
        )

    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=scope
    )

    client = gspread.authorize(creds)

    return client


# ============================================================
# LISTAS PARA OS MENUS SUSPENSOS
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

lista_turnos = [
    "Matutino",
    "Vespertino",
    "Noturno",
    "Integral"
]


# ============================================================
# CARREGAR DADOS DA PÁGINA 1
# ============================================================

@st.cache_data(ttl=5)
def carregar_dados():

    colunas_padrao = [
        "PROFESSOR(A)",
        "DISCIPLINA",
        "CARGA HORÁRIA",
        "TURMA",
        "TURNO"
    ]

    try:

        client = conectar_gsheets()

        sheet = client.open_by_url(SHEET_URL)

        worksheet = sheet.worksheet("Página1")

        dados = worksheet.get_all_records()

        if not dados:
            return pd.DataFrame(columns=colunas_padrao)

        df = pd.DataFrame(dados)

        # Garante que as colunas principais existam
        for coluna in colunas_padrao:
            if coluna not in df.columns:
                df[coluna] = ""

        # Mantém somente as colunas esperadas
        df = df[colunas_padrao]

        return df

    except Exception as e:

        st.error(
            f"Erro ao carregar dados da planilha: {e}"
        )

        return pd.DataFrame(columns=colunas_padrao)


# Carrega os dados
df_dados = carregar_dados()


# ============================================================
# INICIALIZA CONTROLE DE CH DOS PROFESSORES
# ============================================================

if "professores_ch" not in st.session_state:

    st.session_state["professores_ch"] = pd.DataFrame(
        columns=[
            "Professor (a)",
            "CH Total"
        ]
    )


# ============================================================
# FUNÇÃO PARA CALCULAR CH ATRIBUÍDA
# ============================================================

def calcular_horas_atribuidas(df):

    alocadas = {}

    if df.empty:
        return alocadas

    if (
        "PROFESSOR(A)" not in df.columns
        or "CARGA HORÁRIA" not in df.columns
    ):
        return alocadas

    for _, row in df.iterrows():

        professor = str(
            row["PROFESSOR(A)"]
        ).strip()

        carga = pd.to_numeric(
            row["CARGA HORÁRIA"],
            errors="coerce"
        )

        if (
            professor
            and professor.lower() not in ["nan", "none"]
            and pd.notna(carga)
        ):

            alocadas[professor] = (
                alocadas.get(professor, 0)
                + float(carga)
            )

    return alocadas


# ============================================================
# CONFIGURAÇÃO DA TABELA PRINCIPAL
# ============================================================

configuracao_colunas = {

    "PROFESSOR(A)": st.column_config.TextColumn(
        "PROFESSOR(A)",
        required=True
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
# TÍTULO
# ============================================================

st.title("📋 Sistema de Lotação - 2026")

st.markdown(
    "Adicione ou edite os lançamentos de lotação diretamente "
    "na tabela abaixo. Depois clique em **Salvar Alterações** "
    "para sincronizar com o Google Sheets."
)


# ============================================================
# TABELA PRINCIPAL
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
# CALCULA CH EM TEMPO REAL
# ============================================================

horas_atribuidas = calcular_horas_atribuidas(
    df_editado
)


# ============================================================
# PAINEL LATERAL
# ============================================================

with st.sidebar:

    st.header("👨‍🏫 Controle de CH Total")

    st.markdown(
        "Cadastre a carga horária total contratada "
        "de cada professor(a):"
    )

    df_profs_cadastrados = st.data_editor(
        st.session_state["professores_ch"],
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,

        column_config={

            "Professor (a)": st.column_config.TextColumn(
                "Professor (a)",
                required=True
            ),

            "CH Total": st.column_config.NumberColumn(
                "CH Total",
                min_value=1,
                max_value=60,
                step=1,
                required=True
            )
        },

        key="editor_profs"
    )

    # Atualiza os dados da sessão
    st.session_state["professores_ch"] = (
        df_profs_cadastrados
    )

    st.divider()

    st.markdown(
        "📊 **Status da Distribuição:**"
    )


    # ========================================================
    # STATUS DA CH
    # ========================================================

    status_lista = []

    for _, row in df_profs_cadastrados.iterrows():

        professor = str(
            row["Professor (a)"]
        ).strip()

        if (
            not professor
            or professor.lower() in ["nan", "none"]
        ):
            continue

        ch_total = pd.to_numeric(
            row["CH Total"],
            errors="coerce"
        )

        if pd.isna(ch_total):
            ch_total = 0

        usada = horas_atribuidas.get(
            professor,
            0
        )

        saldo = ch_total - usada


        # Define o status
        if saldo == 0:

            status = "✅ OK"

        elif saldo > 0:

            status = f"⚠️ Faltam {int(saldo)}h"

        else:

            status = f"🚨 Passou {int(abs(saldo))}h"


        status_lista.append({

            "Professor (a)": professor,

            "Total": int(ch_total),

            "Alocado": int(usada),

            "Saldo": int(saldo),

            "Status": status
        })


    # ========================================================
    # EXIBE STATUS
    # ========================================================

    if status_lista:

        df_status = pd.DataFrame(
            status_lista
        )

        st.dataframe(
            df_status,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Cadastre os professores acima "
            "para ver o balanço."
        )


# ============================================================
# RESUMO GERAL
# ============================================================

st.divider()

col1, col2, col3, col4 = st.columns(4)


# Total de lançamentos
total_lancamentos = len(
    df_editado
)


# Total de CH distribuída
total_ch_distribuida = pd.to_numeric(
    df_editado["CARGA HORÁRIA"],
    errors="coerce"
).fillna(0).sum()


# Professores cadastrados
total_professores = len(
    df_profs_cadastrados.dropna(
        subset=["Professor (a)"]
    )
)


# Professores com CH excedida
professores_excedidos = 0

for _, row in df_profs_cadastrados.iterrows():

    professor = str(
        row["Professor (a)"]
    ).strip()

    if (
        not professor
        or professor.lower() in ["nan", "none"]
    ):
        continue

    ch_total = pd.to_numeric(
        row["CH Total"],
        errors="coerce"
    )

    if pd.isna(ch_total):
        continue

    ch_usada = horas_atribuidas.get(
        professor,
        0
    )

    if ch_usada > ch_total:
        professores_excedidos += 1


with col1:

    st.metric(
        "Lançamentos",
        total_lancamentos
    )


with col2:

    st.metric(
        "CH Distribuída",
        f"{int(total_ch_distribuida)}h"
    )


with col3:

    st.metric(
        "Professores",
        total_professores
    )


with col4:

    st.metric(
        "CH Excedida",
        professores_excedidos
    )


# ============================================================
# ALERTA DE PROFESSORES COM CH EXCEDIDA
# ============================================================

if professores_excedidos > 0:

    st.warning(
        f"⚠️ Existem **{professores_excedidos} "
        "professor(es)** com carga horária acima "
        "do total cadastrado."
    )


# ============================================================
# BOTÃO PARA SALVAR NO GOOGLE SHEETS
# ============================================================

st.divider()

if st.button(
    "💾 Salvar Alterações na Planilha do Google",
    type="primary",
    use_container_width=True
):

    try:

        # Conecta ao Google Sheets
        client = conectar_gsheets()

        sheet = client.open_by_url(
            SHEET_URL
        )

        worksheet = sheet.worksheet(
            "Página1"
        )


        # ----------------------------------------------------
        # Limpa a página atual
        # ----------------------------------------------------

        worksheet.clear()


        # ----------------------------------------------------
        # Prepara os dados
        # ----------------------------------------------------

        df_salvar = df_editado.copy()

        # Converte valores vazios
        df_salvar = df_salvar.fillna("")


        dados_para_salvar = [
            df_salvar.columns.tolist()
        ] + df_salvar.values.tolist()


        # ----------------------------------------------------
        # Atualiza a planilha
        # ----------------------------------------------------

        worksheet.update(
            dados_para_salvar,
            "A1"
        )


        # ----------------------------------------------------
        # Limpa o cache
        # ----------------------------------------------------

        st.cache_data.clear()


        # ----------------------------------------------------
        # Mensagem de sucesso
        # ----------------------------------------------------

        st.success(
            "✅ Dados salvos e sincronizados "
            "com sucesso na Página1 do Google Sheets!"
        )


        # ----------------------------------------------------
        # Recarrega a página
        # ----------------------------------------------------

        st.rerun()


    except Exception as e:

        st.error(
            f"❌ Erro ao salvar na planilha: {e}"
        )
