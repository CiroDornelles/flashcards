#!/bin/bash

# Wrapper para executar scripts Python dentro do diretório lpi.
# Garante que todos os comandos sejam executados a partir do local correto.

# Verifica se o nome do script foi fornecido
if [ -z "$1" ]; then
    echo "Erro: Nenhum script especificado."
    echo "Uso: $0 <nome_do_script.py> [argumentos...]"
    exit 1
fi

# Navega para o diretório lpi
cd "$(dirname "$0")/lpi" || exit

# O primeiro argumento é o nome do script, o resto são os argumentos para ele.
SCRIPT_NAME="$1"
shift # Remove o nome do script da lista de argumentos

# Executa o script python com os argumentos restantes
python3 "$SCRIPT_NAME" "$@"
