#!/bin/bash

# Script para copiar arquivos do projeto /home/bruno/Documents/caixacerto_pwa para /home/bruno/inkers/inkers
# Verifica diferenças para arquivos .py e atualiza apenas se houver mudanças

SOURCE="/home/bruno/Documents/caixacerto_pwa"
DEST="/home/bruno/inkers/inkers"

# Função para copiar arquivos não .py
copy_non_py_files() {
    echo "Copiando arquivos não .py..."
    find "$SOURCE" -type f ! -name "*.py" -exec cp --parents {} "$DEST" \;
}

# Função para verificar e copiar arquivos .py
copy_py_files() {
    echo "Verificando e copiando arquivos .py..."
    find "$SOURCE" -name "*.py" -type f | while read -r file; do
        rel_path="${file#$SOURCE/}"
        dest_file="$DEST/$rel_path"
        dest_dir="$(dirname "$dest_file")"

        # Criar diretório se não existir
        mkdir -p "$dest_dir"

        if [ -f "$dest_file" ]; then
            # Verificar diferenças
            if ! diff "$file" "$dest_file" > /dev/null 2>&1; then
                echo "Diferenças encontradas em $rel_path:"
                diff "$file" "$dest_file"
                echo "Atualizando $rel_path..."
                cp "$file" "$dest_file"
            else
                echo "Nenhuma diferença em $rel_path. Pulando..."
            fi
        else
            echo "Arquivo novo: $rel_path"
            cp "$file" "$dest_file"
        fi
    done
}

# Executar as funções
copy_non_py_files
copy_py_files

echo "Cópia concluída."