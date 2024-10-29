import streamlit as st
import sqlite3
import pandas as pd
import user

# Função para carregar a lista de usuários da tabela admin
def carregar_usuarios(tipo_user):
    conn = sqlite3.connect('novo.db')
    cursor = conn.cursor()
    if tipo_user == "Padrão":
        cursor.execute('SELECT user FROM usuarios')
        usuarios = cursor.fetchall()
    else: 
        cursor.execute('SELECT user FROM admin')
        usuarios = cursor.fetchall() 
    conn.close()
    return [user[0] for user in usuarios]

# Função para carregar os dados do usuário selecionado
def carregar_dados_usuario(usuario_selecionado, tipo_user):
    import pandas as pd
    conn = sqlite3.connect('novo.db')
    if tipo_user == "Padrão":
        query = "SELECT * FROM usuarios WHERE user = ?"
        df = pd.read_sql(query, conn, params=(usuario_selecionado,))
    else:
        query = "SELECT * FROM admin WHERE user = ?"
        df = pd.read_sql(query, conn, params=(usuario_selecionado,))
    conn.close()
    return df

# Função para criar um novo usuário
def criar_usuario(user, senha):
    conn = sqlite3.connect('novo.db')
    cursor = conn.cursor()
    
    # Verifica se o usuário já existe na tabela 'admin'
    cursor.execute('SELECT * FROM admin WHERE user = ?', (user,))
    existente = cursor.fetchone()
    
    if existente:
        st.error(f"Usuário {user} já existe!")
    else:
        cursor.execute('INSERT INTO admin (user, senha) VALUES (?, ?)', (user, senha))
        conn.commit()
        st.success(f"Usuário {user} criado com sucesso!")
    
    conn.close()

# Função para criar os usuários padrão na tabela 'usuarios'
def criar_usuario_padrao(user, senha):
    conn = sqlite3.connect('novo.db')
    cursor = conn.cursor()
    
    # Verifica se o usuário já existe na tabela 'usuarios'
    cursor.execute('SELECT * FROM usuarios WHERE user = ?', (user,))
    existente = cursor.fetchone()
    
    if existente:
        st.error(f"Usuário {user} já existe!")
    else:
        cursor.execute('INSERT INTO usuarios (user, senha) VALUES (?, ?)', (user, senha))
        conn.commit()
        st.success(f"Usuário {user} criado com sucesso!")
    
    conn.close()

# Função para a interface de criação de usuário
def criar_usuario_interface():
    
    tipo = st.selectbox("Tipo de Usuário", ["Administrador", "Padrão"])
    user = st.text_input("Usuário", placeholder="Insira um nome")
    senha = st.text_input("Senha", placeholder="Insira uma senha", type="password")
    
    if st.button("\U0001F4E5 Inserir"):
        if user and senha:
            if tipo == "Padrão":
                criar_usuario_padrao(user, senha)
            else:
                criar_usuario(user, senha)
        else:
            st.error("Preencha todos os campos!")

# Função para carregar a lista de usuários (para aba de edição e exclusão)
def carregar_usuarios(tipo_user3):
    import pandas as pd
    conn = sqlite3.connect('novo.db')
    if tipo_user3 == "Padrão":
        query = "SELECT user FROM usuarios"
    else:
        query = "SELECT user FROM admin"
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    return df['user'].tolist()

# Função para visualizar a senha do usuário selecionado
def senha_visualizar(usuario_selecionado, tipo_user3):
    import pandas as pd
    conn = sqlite3.connect('novo.db')
    if tipo_user3 == "Padrão":
        query = "SELECT senha FROM usuarios WHERE user = ?"
    else:
        query = "SELECT senha FROM admin WHERE user = ?"
    
    df = pd.read_sql(query, conn, params=(usuario_selecionado,))
    conn.close()
    
    if not df.empty:
        return df.iloc[0]['senha']
    else:
        return ""

# Função para atualizar a senha
def atualizar_senha(usuario_selecionado, nova_senha, tipo_user3):
    conn = sqlite3.connect('novo.db')
    if tipo_user3 == "Padrão":
        query = "UPDATE usuarios SET senha = ? WHERE user = ?"
    else:
        query = "UPDATE admin SET senha = ? WHERE user = ?"
    
    conn.execute(query, (nova_senha, usuario_selecionado))
    conn.commit()
    conn.close()

# Função para excluir o usuário
def excluir_usuario(usuario_selecionado, tipo_user3):
    conn = sqlite3.connect('novo.db')
    if tipo_user3 == "Padrão":
        query = "DELETE FROM usuarios WHERE user = ?"
    else:
        query = "DELETE FROM admin WHERE user = ?"
    
    conn.execute(query, (usuario_selecionado,))
    conn.commit()
    conn.close()

# Layout das abas
tab1, tab2, tab3 = st.tabs(["\U0001F4C1 Dados Gerais", "\U0001F4C1 Inserir", "\U0001F4C1 Editar/Excluir"])

# Aba 1: Dados gerais
with tab1:
    st.write('Lista de acesso')
    tipo_user = st.selectbox("Tipo Usuário", ["Administrador", "Padrão"], placeholder="Insira um usuário")
    lista_usuarios = carregar_usuarios(tipo_user)
    usuario_selecionado = st.selectbox("\U0001F50D Pesquisar", lista_usuarios)

    if usuario_selecionado:
        st.write(f"Dados do usuário: {usuario_selecionado}")
        dados_usuario = carregar_dados_usuario(usuario_selecionado, tipo_user)

        if not dados_usuario.empty:
            st.table(dados_usuario)
        else:
            st.write("Nenhum dado encontrado para o usuário selecionado.")

# Aba 2: Inserir usuário
with tab2:
    
    criar_usuario_interface()

# Aba 3: Editar/Excluir usuário
with tab3:
    tipo_user3 = st.selectbox("Tipo Acesso", ["Administrador", "Padrão"])
    list_editar = carregar_usuarios(tipo_user3)
    usuario_selecionado = st.selectbox("Nome do Usuário", list_editar)
    senha_atual = senha_visualizar(usuario_selecionado, tipo_user3)
    nova_senha = st.text_input("Senha", placeholder="Editar Senha", value=senha_atual)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("\U0001F501 Atualizar"):
            atualizar_senha(usuario_selecionado, nova_senha, tipo_user3)
            st.success(f"Senha do usuário {usuario_selecionado} atualizada com sucesso!")
    with col2:
        if st.button("\U0000274C Excluir"):
            excluir_usuario(usuario_selecionado, tipo_user3)
            st.success(f"Usuário {usuario_selecionado} excluído com sucesso!")
