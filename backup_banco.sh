#!/bin/bash
echo "1. Backup de Segurança..."
gbak -b -user SYSDBA -password masterkey localhost:/home/bruno/inkers/data/base/BASE.FDB /home/bruno/inkers/data/backups/base_bkp.fbk

if [ $? -eq 0 ]; then
    echo "2. Gerando SQL de Diferenças..."
    python3 sync_full_inkers.py
    
    echo "3. Aplicando Atualizações..."
    isql -user SYSDBA -password masterkey base -i apply_sync.sql
    
    echo "Sucesso! Estrutura sincronizada."
else
    echo "Erro no backup. Abortando."
fi