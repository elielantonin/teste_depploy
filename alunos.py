import sqlite3
import streamlit as st
from datetime import datetime
import pandas as pd

# Função para criar a tabela de alunos
def criar_tabela_alunos():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute(''' 
        CREATE TABLE IF NOT EXISTS alunos (
            matricula INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT NOT NULL UNIQUE,
            data_nascimento DATE,
            endereco TEXT,
            telefone TEXT,
            email TEXT,
            unidade TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Função para adicionar um aluno
def adicionar_aluno(nome, cpf, data_nascimento, endereco, telefone, email, unidade):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM alunos WHERE cpf = ?", (cpf,))
    aluno_existente = c.fetchone()
    
    if aluno_existente:
        conn.close()
        return None
    
    c.execute(''' 
        INSERT INTO alunos (nome, cpf, data_nascimento, endereco, telefone, email, unidade)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (nome, cpf, data_nascimento, endereco, telefone, email, unidade))
    
    matricula = c.lastrowid
    conn.commit()
    conn.close()
    return matricula

# Função para consultar alunos
def consultar_alunos():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT matricula, nome, cpf, data_nascimento, endereco, telefone, email, unidade FROM alunos")
    alunos = c.fetchall()
    conn.close()
    return alunos

# Função para editar aluno
def editar_aluno(matricula, nome, cpf, data_nascimento, endereco, telefone, email, unidade):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        c.execute('''
            UPDATE alunos
            SET nome = ?, cpf = ?, data_nascimento = ?, endereco = ?, telefone = ?, email = ?, unidade = ?
            WHERE matricula = ?
        ''', (nome, cpf, data_nascimento, endereco, telefone, email, unidade, matricula))

        rows_affected = c.rowcount
        conn.commit()
        conn.close()

        print(f"Linhas afetadas na atualização: {rows_affected}")
        return rows_affected
    except Exception as e:
        print(f"Erro ao atualizar cadastro: {e}")
        conn.rollback()
        conn.close()
        return 0

# Função para excluir aluno
def excluir_aluno(matricula):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM alunos WHERE matricula = ?", (matricula,))
    conn.commit()
    conn.close()

# Função para buscar aluno por matrícula, nome ou CPF
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
    print(f"Aluno encontrado: {aluno}")  # Log para depuração
    conn.close()
    return aluno

# Interface do Streamlit
st.title("\u2795Cadastros") 

criar_tabela_alunos()  # Certifique-se de que a tabela exista
tab1, tab2, tab3 = st.tabs(["\U0001F4C1 Dados Gerais", "\U0001F4C1 Inserir", "\U0001F4C1 Editar/Excluir"])

with tab1:
    st.write("\U0001F4C2Cadastros")
    alunos = consultar_alunos()
    
    if alunos:
        df_alunos = pd.DataFrame(alunos, columns=["Matrícula", "Nome", "CPF", "Data de Nascimento", "Endereço", "Telefone", "Email", "Unidade"])
        st.dataframe(df_alunos)
    else:
        st.write("Nenhum aluno cadastrado.")

with tab2:
    st.write("\U0001F4C2Inserir")
    nome = st.text_input("Nome", key="nome")
    cpf = st.text_input("CPF", key="cpf")
    data_nascimento = st.date_input("Data de Nascimento", key="data_nascimento", value=None)
    endereco = st.text_input("Endereço", key="endereco")
    telefone = st.text_input("Telefone", key="telefone")
    email = st.text_input("Email", key="email")
    unidade = st.selectbox("Unidade", ["Academia I", "Academia II"], key="unidade_input")

    if st.button("\U0001F4E5Inserir", key="botao_cadastrar"):
        if nome and cpf:
            matricula = adicionar_aluno(nome, cpf, data_nascimento, endereco, telefone, email, unidade)
            if matricula:
                st.success("Aluno cadastrado com sucesso!")
                st.info(f"Número da Matrícula: {matricula}")
            else:
                st.error("Erro: CPF já cadastrado.")
        else:
            st.warning("Preencha todos os campos obrigatórios.")

with tab3:
    st.write("\U0001F4C2Editar Cadastros")

    busca_por = st.selectbox("Buscar por:", ["Matrícula", "Nome", "CPF"], key="busca_por_input")
    valor_busca = st.text_input("Valor de busca:", key="valor_busca_input")

    if st.button("Buscar Aluno"):
        if valor_busca:
            aluno = buscar_aluno(busca_por, valor_busca)
            if aluno:
                # Carregar dados do aluno nos campos de entrada
                st.session_state['matricula'] = aluno[0]
                st.session_state['edit_nome'] = aluno[1]
                st.session_state['edit_cpf'] = aluno[2]
                st.session_state['edit_data_nascimento'] = datetime.strptime(aluno[3], '%Y-%m-%d').date() if aluno[3] else None
                st.session_state['edit_endereco'] = aluno[4]
                st.session_state['edit_telefone'] = aluno[5]
                st.session_state['edit_email'] = aluno[6]
                st.session_state['edit_unidade'] = aluno[7]
                st.session_state['editing'] = True  # Marcar que estamos editando

    # Verificar se estamos no modo de edição
    if 'editing' in st.session_state and st.session_state['editing']:
        # Criar campos de entrada para edição com valores armazenados
        nome = st.text_input("Nome", value=st.session_state['edit_nome'], key="edit_nome_input")
        cpf = st.text_input("CPF", value=st.session_state['edit_cpf'], key="edit_cpf_input")
        data_nascimento = st.date_input("Data de Nascimento", value=st.session_state['edit_data_nascimento'], key="edit_data_nascimento_input")
        endereco = st.text_input("Endereço", value=st.session_state['edit_endereco'], key="edit_endereco_input")
        telefone = st.text_input("Telefone", value=st.session_state['edit_telefone'], key="edit_telefone_input")
        email = st.text_input("Email", value=st.session_state['edit_email'], key="edit_email_input")

        unidade_opcoes = ["Academia I", "Academia II"]
        unidade = st.selectbox("Unidade", unidade_opcoes, 
            index=unidade_opcoes.index(st.session_state['edit_unidade']) if st.session_state['edit_unidade'] in unidade_opcoes else 0, 
            key="edit_unidade_input")

        # Atualizar cadastro ao clicar no botão
        if st.button("Atualizar Cadastro"):
            rows_affected = editar_aluno(st.session_state['matricula'], nome, cpf, data_nascimento, endereco, telefone, email, unidade)
            
            if rows_affected > 0:
                st.success("Cadastro atualizado com sucesso!")
                st.session_state['editing'] = False  # Desmarcar edição após atualização
            else:
                st.error("Erro: Cadastro não foi atualizado. O aluno pode não existir.")
    else:
        st.write("Faça uma busca para editar os dados de um aluno.")
