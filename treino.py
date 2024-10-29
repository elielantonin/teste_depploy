import sqlite3
import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd

# Função para criar as tabelas necessárias
def criar_tabelas():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Criar tabela de alunos
    c.execute(''' 
        CREATE TABLE IF NOT EXISTS alunos (
            matricula INTEGER PRIMARY KEY AUTOINCREMENT,
            unidade TEXT NOT NULL,
            nome TEXT NOT NULL,
            cpf TEXT NOT NULL UNIQUE,
            data_nascimento DATE,
            endereco TEXT,
            telefone TEXT,
            email TEXT
        )
    ''')

    # Criar tabela de pagamentos
    c.execute(''' 
        CREATE TABLE IF NOT EXISTS pagamentos (
            codigo_pagamento INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula INTEGER,
            unidade TEXT NOT NULL,
            nome TEXT,
            cpf TEXT,
            data_pagamento DATE,
            plano TEXT,
            valor REAL,
            status TEXT,
            FOREIGN KEY (matricula) REFERENCES alunos (matricula)
        )
    ''')

    conn.commit()
    conn.close()

# Função para buscar aluno
def buscar_aluno(busca_por, valor):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if busca_por == "Matrícula":
        c.execute("SELECT * FROM alunos WHERE matricula = ?", (valor,))
    elif busca_por == "Nome":
        c.execute("SELECT * FROM alunos WHERE nome LIKE ?", ('%' + valor + '%',))
    elif busca_por == "CPF":
        c.execute("SELECT * FROM alunos WHERE cpf = ?", (valor,))
    
    aluno = c.fetchone()
    conn.close()
    return aluno

# Função para calcular o status do próximo pagamento com base no plano
def alerta_proximo_pagamento(data_pagamento, plano):
    if isinstance(data_pagamento, str):
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
            try:
                data_pagamento = datetime.strptime(data_pagamento, fmt)
                break
            except ValueError:
                continue
    elif isinstance(data_pagamento, date):
        data_pagamento = datetime.combine(data_pagamento, datetime.min.time())
    else:
        return None

    periodicidade_meses = {
        'mensal': 1,
        'trimestral': 3,
        'semestral': 6,
        'anual': 12
    }

    plano = plano.lower()
    if plano not in periodicidade_meses:
        return None

    proximo_pagamento = data_pagamento + relativedelta(months=periodicidade_meses[plano])
    hoje = datetime.now()

    return "Atrasado" if proximo_pagamento < hoje else "Em dia"

# Função para registrar pagamento
def registrar_pagamento(matricula, unidade, nome, cpf, data_pagamento, plano, valor):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        data_pagamento_str = data_pagamento.strftime('%Y-%m-%d')
        
        status = alerta_proximo_pagamento(data_pagamento, plano)
        
        if status == "Atrasado":
            status = "Pago"
        
        c.execute(''' 
            INSERT INTO pagamentos (matricula, unidade, nome, cpf, data_pagamento, plano, valor, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (matricula, unidade, nome, cpf, data_pagamento_str, plano, valor, status))

        conn.commit()
        codigo_pagamento = c.lastrowid
        st.write(f"Dados inseridos: {codigo_pagamento}, {matricula}, {unidade}, {nome}, {cpf}, {data_pagamento}, {plano}, {valor}")
    except sqlite3.Error as e:
        st.write(f"Erro ao registrar pagamento: {e}")
        return None
    finally:
        conn.close()
        
    return codigo_pagamento

# Função para limpar os campos após registrar o pagamento
def limpar_campos():
    st.session_state.aluno_encontrado = None
    st.session_state.valor_mensalidade = 0.0

# Interface do Streamlit


# Criar tabelas se não existirem
criar_tabelas()

# Definir as abas
tab1, tab2, tab3 = st.tabs(["\U0001F4C1 Dados Gerais", "\U0001F4C1 Inserir", "\U0001F4C1 Editar/Excluir"])

# Aba de dados gerais com filtro e busca específica
with tab1:
    conn = sqlite3.connect('database.db')
    
    try:
        st.write("Consulta Pagamentos")
        col1,col2 =st.columns(2)
        with col1:
         busca = st.selectbox("Buscar por", ["Matrícula", "Nome", "CPF"], key="busca_aba1")
        with col2:
         valor_busca = st.text_input("Valor",placeholder='Insira para pesquisar')

        if st.button("\U0001F50DPesquisar"):
            if valor_busca:
                if busca == "Matrícula":
                    query = "SELECT * FROM pagamentos WHERE matricula = ?"
                    pagamentos = pd.read_sql_query(query, conn, params=(valor_busca,))
                elif busca == "Nome":
                    query = "SELECT * FROM pagamentos WHERE nome LIKE ?"
                    pagamentos = pd.read_sql_query(query, conn, params=('%' + valor_busca + '%',))
                elif busca == "CPF":
                    query = "SELECT * FROM pagamentos WHERE cpf = ?"
                    pagamentos = pd.read_sql_query(query, conn, params=(valor_busca,))
                
                if not pagamentos.empty:
                    pagamentos['data_pagamento'] = pd.to_datetime(pagamentos['data_pagamento'], format='%Y-%m-%d', errors='coerce')
                    pagamentos_exibicao = pagamentos[['matricula', 'nome', 'cpf', 'plano', 'unidade', 'data_pagamento', 'valor', 'status']].rename(columns={
                        'data_pagamento': 'Data de Pagamento',
                        'valor': 'Valor da Mensalidade',
                        'status': 'Status'
                    })
                    st.dataframe(pagamentos_exibicao)
                else:
                    st.warning("Nenhum pagamento encontrado para a busca realizada.")
            else:
                st.warning("Por favor, insira um valor para busca.")
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados: {str(e)}")
    finally:
        conn.close()

# Aba de inserção de dados
with tab2:
    busca_por = st.selectbox("Buscar por", ["Matrícula", "Nome", "CPF"], key="busca_aba2")
    valor = st.text_input("Insira o valor para buscar", key="valor_busca_aba2")

    if "aluno_encontrado" not in st.session_state:
        st.session_state.aluno_encontrado = None

    if st.button("\U0001F50D Buscar", key="buscar_aba2"):
        if valor:
            aluno = buscar_aluno(busca_por, valor)
            if aluno:
                st.session_state.aluno_encontrado = aluno
                matricula, unidade, nome, cpf, *_ = aluno
                st.success(f"Aluno encontrado: {nome} - CPF: {cpf}")
            else:
                st.error("Aluno não encontrado.")
        else:
            st.warning("Por favor, insira um valor para buscar.")

    if st.session_state.aluno_encontrado:
        matricula, unidade, nome, cpf, *_ = st.session_state.aluno_encontrado

        st.text_input("Matrícula", value=matricula, disabled=True, key="matricula_aba2")
        st.text_input("Nome", value=nome, disabled=True, key="nome_aba2")
        st.text_input("CPF", value=cpf, disabled=True, key="cpf_aba2")
        st.text_input("Unidade", value=unidade, disabled=True, key="unidade_aba2")

        data_pagamento = st.date_input("Data de Pagamento", value=datetime.today(), key="data_pagamento_aba2")
        plano = st.selectbox("Plano", ["Mensal", "Trimestral", "Semestral", "Anual"], key="plano_aba2")
        valor_mensalidade = st.number_input("Valor da Mensalidade", min_value=0.0, step=0.01, key="valor_mensalidade_aba2")

        if st.button("\U0001F4E5 Registrar Pagamento", key="registrar_pagamento_aba2"):
            if valor_mensalidade <= 0:
                st.error("Por favor, insira um valor de mensalidade válido.")
            else:
                codigo = registrar_pagamento(matricula, unidade, nome, cpf, data_pagamento, plano, valor_mensalidade)
                if codigo:
                    st.success(f"Pagamento registrado com sucesso! Código de pagamento: {codigo}")
                    limpar_campos()
                else:
                    st.error("Erro ao registrar pagamento.")

# Aba de edição e exclusão
with tab3:
    st.write("Funções para edição e exclusão ainda não implementadas.")

