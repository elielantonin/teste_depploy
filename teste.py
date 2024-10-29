from datetime import datetime
from dateutil.relativedelta import relativedelta
import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Função para calcular o status do próximo pagamento
def calcular_status_pagamento(data_pagamento_str, plano):
    if pd.isnull(data_pagamento_str):
        return "Data inválida"

    try:
        data_pagamento = pd.to_datetime(data_pagamento_str, format='%Y-%m-%d')
    except ValueError:
        return "Data inválida"

    periodicidade = {
        'mensal': 1,
        'trimestral': 3,
        'semestral': 6,
        'anual': 12
    }

    plano = plano.lower()
    
    if plano not in periodicidade:
        return None

    proximo_pagamento = data_pagamento + relativedelta(months=periodicidade[plano])
    
    return "Atrasado" if proximo_pagamento.date() < datetime.now().date() else "Em dia"

def carregar_dados(conexao):
    query = "SELECT nome, plano, data_pagamento FROM pagamentos"
    return pd.read_sql_query(query, conexao)
    

def plotar_grafico_status(dados):
    status_counts = dados['Status'].value_counts()
    fig, ax = plt.subplots()
    ax.bar(status_counts.index, status_counts.values, color=['red', 'green'])
    ax.set_title('Status dos Pagamentos')
    ax.set_xlabel('Status')
    ax.set_ylabel('Quantidade')
    st.pyplot(fig)

def main():
    
    st.title("Painel de Pagamentos de Alunos")
    st.write("Visualize o status das mensalidades dos alunos com base no plano e último pagamento registrado.")

    # Conectar ao banco de dados
    conn = sqlite3.connect('database.db')

    try:
        # Carregar dados
        dados = carregar_dados(conn)

        # Aplicar a função de status de pagamento
        dados['Status'] = dados.apply(lambda row: calcular_status_pagamento(row['data_pagamento'], row['plano']), axis=1)

        # Filtrar por status
        filtro_status = st.selectbox("Filtrar por status", ["Todos", "Atrasado", "Em dia"])
        if filtro_status != "Todos":
            dados = dados[dados["Status"] == filtro_status]

        # Exibir dados em tabela
        st.dataframe(dados[['nome', 'plano', 'Status']])

        # Plotar gráfico de status
        plotar_grafico_status(dados)

    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
