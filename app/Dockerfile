# Imagem base
FROM python:3.11-slim

# Diretório dentro do container
WORKDIR /app

# Copia arquivos
COPY . .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Porta que o app usa
EXPOSE 5000

# Comando para rodar
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]