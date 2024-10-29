import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import pandas as pd

# Função para conectar ao banco de dados SQLite
def init_db():
    conn = sqlite3.connect('gym_membership.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS alunos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cpf TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS mensalidades
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, aluno_cpf TEXT, plano TEXT, valor REAL, ultimo_pagamento DATE,
                 FOREIGN KEY(aluno_cpf) REFERENCES alunos(cpf))''')
    conn.commit()
    conn.close()

# Função para adicionar um novo aluno
def add_aluno(nome, cpf):
    conn = sqlite3.connect('gym_membership.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO alunos (nome, cpf) VALUES (?, ?)", (nome, cpf))
        conn.commit()
    except sqlite3.IntegrityError:
        st.error("CPF já cadastrado.")
    finally:
        conn.close()

# Função para buscar aluno por nome ou CPF
def get_aluno(cpf=None, nome=None):
    conn = sqlite3.connect('gym_membership.db')
    c = conn.cursor()
    if cpf:
        c.execute("SELECT nome, cpf FROM alunos WHERE cpf = ?", (cpf,))
    elif nome:
        c.execute("SELECT nome, cpf FROM alunos WHERE nome LIKE ?", (f"%{nome}%",))
    aluno = c.fetchone()
    conn.close()
    return aluno

# Inicializa o banco de dados
init_db()

st.title("Controle de Mensalidades da Academia")

tab1, tab2, tab3 = st.tabs(["📋 Dados Gerais", "➕ Inserir", "📄 Editar/Excluir"])

# Aba de Dados Gerais
with tab1:
    st.subheader("Visão Geral dos Alunos")
    members_df = pd.read_sql_query("SELECT * FROM alunos", sqlite3.connect('gym_membership.db'))
    st.dataframe(members_df)

# Aba de Inserir
with tab2:
    st.subheader("Cadastro de Aluno")
    with st.form("cadastro_aluno"):
        nome = st.text_input("Nome do Aluno")
        cpf = st.text_input("CPF do Aluno")
        submit = st.form_submit_button("Cadastrar Aluno")

        if submit:
            add_aluno(nome, cpf)
            st.success(f"Aluno {nome} cadastrado com sucesso!")

    # Pesquisa de Aluno
    st.subheader("Pesquisar Aluno")
    search_option = st.radio("Pesquisar por:", ("Nome", "CPF"))
    if search_option == "Nome":
        nome_search = st.text_input("Digite o nome do aluno:")
        if st.button("Buscar"):
            aluno = get_aluno(nome=nome_search)
            if aluno:
                st.write(f"Nome: {aluno[0]}")
                st.write(f"CPF: {aluno[1]}")
            else:
                st.error("Aluno não encontrado.")
    else:
        cpf_search = st.text_input("Digite o CPF do aluno:")
        if st.button("Buscar"):
            aluno = get_aluno(cpf=cpf_search)
            if aluno:
                st.write(f"Nome: {aluno[0]}")
                st.write(f"CPF: {aluno[1]}")
            else:
                st.error("Aluno não encontrado.")

# Aba de Editar/Excluir (exemplo simples, pode ser expandido)
with tab3:
    st.subheader("Editar/Excluir Aluno")
    # Aqui você pode adicionar lógica para editar ou excluir alunos

