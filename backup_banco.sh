#!/bin/bash

# 1. Gera o Timestamp (AnoMesDia_HoraMinutoSegundo)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Configurações do Servidor
SERVER_IP="100.72.176.93"
REMOTE_ALIAS="base"

# 2. Caminho ONDE O ARQUIVO SERÁ SALVO (Com a data no nome)
REMOTE_BACKUP_PATH="/home/bruno/inkers/data/backups/base_bkp_${TIMESTAMP}.fbk"

# String de conexão para o Service Manager
SERVICE_STRING="${SERVER_IP}:service_mgr"

# Credenciais
DB_USER="SYSDBA"
DB_PASS="masterkey"

echo "1. Iniciando Backup Remoto: ${REMOTE_BACKUP_PATH} ..."

# Executa o backup via Service Manager
gbak -b -user ${DB_USER} -password ${DB_PASS} -service ${SERVICE_STRING} ${REMOTE_ALIAS} ${REMOTE_BACKUP_PATH}

# Verifica o status do comando anterior ($?)
if [ $? -eq 0 ]; then
    echo "   Backup concluído com sucesso!"
    
    echo "2. Gerando SQL de Diferenças..."
    # Atenção: Verifique se o seu python precisa ler ESSE backup específico.
    # Se ele precisar, teremos que criar um link simbólico ou passar o nome como parâmetro.
    python3 sync_full_inkers.py
    
    echo "3. Aplicando Atualizações..."
    isql -user SYSDBA -password masterkey localhost:base -i update_full_structure.sql
    
    echo "Processo finalizado."
else
    echo "ERRO CRÍTICO no backup. O processo de sincronização foi abortado para segurança."
    exit 1
fi