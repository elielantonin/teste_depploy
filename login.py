import datetime 
import sqlite3
import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta


st.set_page_config(page_title="GDE ACESSO_PROD_V1.2")

# Função para verificar login no banco de dados
def login(username, password, selected_table):
    conn = sqlite3.connect('novo.db')
    cursor = conn.cursor()

    if selected_table == "USER_N1":
        cursor.execute('SELECT * FROM usuarios WHERE user=? AND senha=?', (username, password))
    elif selected_table == "USER_ADMIN":
        cursor.execute('SELECT * FROM admin WHERE user=? AND senha=?', (username, password))

    user = cursor.fetchone()
    conn.close()
    return user

# Função para atualizar o status no banco de dados
def atualizar_status(selected_id, novo_status):
    conn = sqlite3.connect('novo.db')
    cursor = conn.cursor()
    update_query = "UPDATE entrada SET Status = ? WHERE ID = ?"
    cursor.execute(update_query, (novo_status, selected_id))
    conn.commit()
    conn.close()

# Página de login
def login_page():
    st.title('Login Acesso')
    username = st.text_input('Usuário')
    password = st.text_input('Senha', type='password')
    
    selected_table = st.selectbox("USER_LEVEL:", ["USER_N1", "USER_ADMIN"])

    if st.button('Login'):
        user = login(username, password, selected_table)
        if user is not None:
            st.success('Login realizado com sucesso!')
            
            # Armazena informações de login na sessão
            st.session_state.logged_in = True
            st.session_state.user = username
            st.session_state.selected_table = selected_table  # Define o nível do usuário na sessão

        else:
            st.error('Usuário ou senha incorretos.')

# Função para exibir o menu e funcionalidades após o login
def show_menu():
    with st.sidebar:
        if st.session_state.selected_table == "USER_ADMIN":
            selected = option_menu(
                "Menu Administrador", 
                ["Entrada","Cadastro Aluno", "Gestão de Entrada", "Montar Treino", "Extrair Relatório", "Usuários", "Banco de Dados", "Usuario Administrador", "Logout"], 
                icons=['box-arrow-in-right', 'box-arrow-in-right', 'clipboard-data', 'x-circle', 'file-earmark-arrow-down', 'person', 'database', 'shield-lock', 'box-arrow-right'], 
                menu_icon="cast", 
                default_index=0
            )
        else:
            selected = option_menu(
                "Menu", 
                ["Entrada", "Cadastro Aluno", "Gestão de Entrada", "Montar Treino", "Extrair Relatório", "Logout"], 
                icons=['box-arrow-in-right', 'clipboard-data', 'x-circle', 'file-earmark-arrow-down', 'box-arrow-right'], 
                menu_icon="cast", 
                default_index=0
            )

    if selected == "Entrada":
        exec(open("entrada.py",encoding='utf-8').read(), globals())
    elif selected == "Cadastro Aluno":
        exec(open("alunos.py",encoding='utf-8').read())    
    elif selected == "Montar Treino":
        exec(open("treino.py", encoding='utf-8').read(), globals())
    elif selected == "Gestão de Entrada":
        exec(open("gestao_entrada.py").read())    
    elif selected == "Extrair Relatório":
        exec(open("relatorio.py").read())
    elif selected == "Usuários":
        exec(open("user.py", encoding='utf-8').read(), globals())
    elif selected == "Banco de Dados":
        exec(open("editar_excluir.py").read())
    elif selected == "Usuario Administrador":
        exec(open("useradmin.py").read())
    elif selected == "Logout":
        logout()

# Função para fazer logout
def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.selected_table = None  # Remove o nível do usuário da sessão
    st.experimental_rerun()  # Recarrega a página para mostrar a tela de login

# Verifica se o usuário está logado antes de exibir o conteúdo
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    login_page()
else:
    show_menu()



def carregar_css(caminho_css):
    with open(caminho_css) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Chame a função com o caminho do arquivo CSS
carregar_css("style.css")

