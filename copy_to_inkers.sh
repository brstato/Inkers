#!/bin/bash

# Carrega as variáveis do .env se o arquivo existir
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Configurações
SOURCE="/home/bruno/Documents/caixacerto_pwa/"
REMOTE_USER="${DEPLOY_USER:-bruno}"
REMOTE_HOST="${PROD_HOST:-100.72.176.93}"
REMOTE_DIR="${DEPLOY_DIR:-/home/bruno/inkers/inkers/}"


echo "--- Iniciando Sincronização para $REMOTE_HOST ---"

# O rsync faz tudo: 
# -avz: Archive (mantém permissões), Verbose (mostra log), Compress (comprime dados)
# --update: Pula arquivos que são mais novos no destino (segurança)
# --exclude: Ignora pastas de cache do Python e Git
rsync -avz --update --progress \
    --exclude '__pycache__' \
    --exclude '.git' \
    --exclude '*.fbk' \
    --exclude 'env' \
    --exclude 'venv' \
    "$SOURCE" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}"

echo "--- Sincronização Concluída ---"