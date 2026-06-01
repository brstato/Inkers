#!/bin/bash

# 1. Gera o Timestamp (AnoMesDia_HoraMinutoSegundo)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Carrega as variáveis do .env se o arquivo existir
if [ -f .env ]; then
  # Filtra comentários e exporta as chaves
  export $(grep -v '^#' .env | xargs)
fi

# Configurações do Servidor
SERVER_IP="${PROD_HOST:-100.72.176.93}"
REMOTE_ALIAS="${PROD_PATH:-base}"

# 2. Caminho ONDE O ARQUIVO SERÁ SALVO (Com a data no nome)
REMOTE_BACKUP_PATH="/home/bruno/inkers/data/backups/base_bkp_${TIMESTAMP}.fbk"

# String de conexão para o Service Manager
SERVICE_STRING="${SERVER_IP}:service_mgr"

# Credenciais
DB_USER="${PROD_USER:-SYSDBA}"
DB_PASS="${PROD_PASS:-masterkey}"

echo "1. Iniciando Backup Remoto: ${REMOTE_BACKUP_PATH} ..."

# Executa o backup via Service Manager
gbak -b -user ${DB_USER} -password ${DB_PASS} -service ${SERVICE_STRING} ${REMOTE_ALIAS} ${REMOTE_BACKUP_PATH}

# Verifica o status do comando anterior ($?)
if [ $? -eq 0 ]; then
    echo "   Backup concluído com sucesso!"
    
    echo "2. Gerando SQL de Diferenças e Aplicando no PROD..."
    # O script Python compara DEV x PROD, gera o SQL e aplica automaticamente no banco de produção
    python3 sync_full_inkers.py --auto

    echo "Processo finalizado."
else
    echo "ERRO CRÍTICO no backup. O processo de sincronização foi abortado para segurança."
    exit 1
fi