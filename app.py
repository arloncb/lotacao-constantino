import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Sistema de Lotação", layout="wide")

st.title("📊 Sistema de Lotação de Professores")

# Inicializa o banco de dados temporário na sessão
if "lotacoes" not in st.session_state:
    st.session_state["lotacoes"] = pd.DataFrame(columns=[
        "Nome do Professor (a)", "Vínculo", "Licença Médica", "Estabilidade Gestante",
        "Nível de Ensino", "Turma", "Turno", "Disciplina", 
        "Carga Horária", "Vaga Pura"
    ])

# Formulário para cadastro de nova lotação
with st.form("cadastro_lotacao", clear_on_submit=True):
    st.subheader("Cadastrar Nova Lotação")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nome = st.text_input("Nome do Professor (a)")
        vinculo = st.selectbox("Vínculo", ["Efetivo", "Convocado"])
        nivel = st.selectbox("Nível de Ensino", ["Ensino Fundamental I", "Ensino Fundamental II", "Ensino Médio"])
        turno = st.selectbox("Turno", ["Matutino", "Vespertino", "Noturno", "Integral"])
        
    with col2:
        disciplina = st.selectbox("Disciplina", [
            "Arte", 
            "Ciências",
            "Educação Física",
            "Geografia",
            "História",
            "Língua Inglesa",
            "Língua Portuguesa", 
            "Matemática",
            "Multidisciplinar (Polivalente)"
        ])
        turma = st.text_input("Turma (Ex: 6º Ano A, 1º Ano B)")
        carga_horaria = st.number_input("Carga Horária Semanal", min_value=1, max_value=40, value=20)
        
    with col3:
        st.markdown("<br>", unsafe_allow_html=True) # Espaçamento
        licenca = st.checkbox("Em Licença Médica")
        gestante = st.checkbox("Estabilidade Gestante")
        vaga_pura = st.checkbox("Vaga Pura (Disponível para concurso)")
        
    submit = st.form_submit_button("Salvar Lotação")
    
    if submit:
        if nome and turma:
            nova_linha = pd.DataFrame([{
                "Nome do Professor (a)": nome,
                "Vínculo": vinculo,
                "Licença Médica": "Sim" if licenca else "Não",
                "Estabilidade Gestante": "Sim" if gestante else "Não",
                "Nível de Ensino": nivel,
                "Turma": turma,
                "Turno": turno,
                "Disciplina": disciplina,
                "Carga Horária": carga_horaria,
                "Vaga Pura": "Sim" if vaga_pura else "Não"
            }])
            st.session_state["lotacoes"] = pd.concat([st.session_state["lotacoes"], nova_linha], ignore_index=True)
            st.success("Lotação salva com sucesso!")
        else:
            st.warning("Por favor, preencha pelo menos o Nome do Professor (a) e a Turma.")

# Visualização dos dados
st.divider()
st.subheader("📋 Lotações Atuais")

if not st.session_state["lotacoes"].empty:
    # Exibe a tabela interativa
    st.dataframe(
        st.session_state["lotacoes"],
        use_container_width=True,
        hide_index=True
    )
    
    # Métricas rápidas
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Total de Lotações", len(st.session_state["lotacoes"]))
    col_m2.metric("Vagas Puras", len(st.session_state["lotacoes"][st.session_state["lotacoes"]["Vaga Pura"] == "Sim"]))
    col_m3.metric("Efetivos", len(st.session_state["lotacoes"][st.session_state["lotacoes"]["Vínculo"] == "Efetivo"]))
    col_m4.metric("Convocados", len(st.session_state["lotacoes"][st.session_state["lotacoes"]["Vínculo"] == "Convocado"]))
else:
    st.info("Nenhuma lotação cadastrada ainda.")
