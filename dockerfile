# Dockerfile para ConexAI

# Imagem base oficial do Python
FROM python:3.12-slim

# Diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos necessários
COPY requirements.txt ./
COPY . /app

# Instala as dependências
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expõe a porta da API
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
