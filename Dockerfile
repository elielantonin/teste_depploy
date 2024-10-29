# Use a imagem base Python
FROM python:3.9

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos necessários para o diretório de trabalho
COPY . /app

# Instale as dependências do Streamlit
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exponha a porta que o Streamlit usará
EXPOSE 8501

# Defina o comando de inicialização do Streamlit
CMD ["streamlit", "run", "login.py", "--server.port=8501", "--server.enableCORS=false"]
