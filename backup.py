import sqlite3
import streamlit as st
from datetime import datetime

# Função para criar as tabelas necessárias
def criar_tabelas():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Criar tabela de alunos
    c.execute(''' 
        CREATE TABLE IF NOT EXISTS alunos (
            matricula INTEGER PRIMARY KEY AUTOINCREMENT,
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
            nome TEXT,
            cpf TEXT,
            data_pagamento DATE,
            plano TEXT,
            valor REAL,
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

# Função para registrar pagamento
def registrar_pagamento(matricula, nome, cpf, data_pagamento, plano, valor):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        # Inserir os dados no banco, convertendo data_pagamento para o formato correto
        data_pagamento_str = data_pagamento.strftime('%Y-%m-%d')
        c.execute(''' 
            INSERT INTO pagamentos (matricula, nome, cpf, data_pagamento, plano, valor) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (matricula, nome, cpf, data_pagamento_str, plano, valor))
        
        conn.commit()
        codigo_pagamento = c.lastrowid  # Obtém o código de pagamento auto-incrementado
        st.write(f"Dados inseridos: {codigo_pagamento}, {matricula}, {nome}, {cpf}, {data_pagamento}, {plano}, {valor}")  # Log
    except sqlite3.Error as e:
        st.write(f"Erro ao registrar pagamento: {e}")  # Log do erro
        return None
    finally:
        conn.close()
        
    return codigo_pagamento  # Retorna o código do pagamento gerado

# Interface do Streamlit
# Função para limpar os campos após registrar o pagamento
def limpar_campos():
    st.session_state.aluno_encontrado = None
    st.session_state.valor_mensalidade = 0.0
    
st.title("Registro de Pagamento de Mensalidade")

# Criar tabelas se não existirem
criar_tabelas()

# Seleção de campo para pesquisa
busca_por = st.selectbox("Buscar por", ["Matrícula", "Nome", "CPF"])
valor_busca = st.text_input("Insira o valor para buscar")

# Usar o estado da sessão para armazenar as informações do aluno
if "aluno_encontrado" not in st.session_state:
    st.session_state.aluno_encontrado = None

if st.button("Buscar Aluno"):
    if valor_busca:
        aluno = buscar_aluno(busca_por, valor_busca)
        if aluno:
            st.session_state.aluno_encontrado = aluno
            matricula, nome, cpf = aluno[0], aluno[1], aluno[2]
            st.success(f"Aluno encontrado: {nome} - CPF: {cpf}")
        else:
            st.error("Aluno não encontrado.")
    else:
        st.warning("Por favor, insira um valor para buscar.")

# Input para registrar pagamento
if st.session_state.aluno_encontrado:
    matricula, nome, cpf = st.session_state.aluno_encontrado[:3]
    
    st.text_input("Matrícula", value=matricula, disabled=True)
    st.text_input("Nome", value=nome, disabled=True)
    st.text_input("CPF", value=cpf, disabled=True)
    
    data_pagamento = st.date_input("Data de Pagamento", value=datetime.today())
    plano = st.selectbox("Plano", ["Mensal", "Trimestral", "Semestral", "Anual"])
    
    valor_mensalidade = st.number_input("Valor da Mensalidade", min_value=0.0, step=0.01)

    if st.button("Registrar Pagamento"):
        if valor_mensalidade <= 0:
            st.error("Por favor, insira um valor de mensalidade válido.")
        else:
            codigo = registrar_pagamento(matricula, nome, cpf, data_pagamento, plano, valor_mensalidade)
            if codigo:
                st.success(f"Pagamento registrado com sucesso! Código da transação: {codigo}")
                limpar_campos()
            else:
                st.error("Falha ao registrar o pagamento.")
