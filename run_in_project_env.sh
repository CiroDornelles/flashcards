#!/bin/bash

# Este script executa um comando dentro do ambiente do projeto flashcards.
# Ele ativa o ambiente virtual, configura o PYTHONPATH e navega para o diretório raiz do projeto.

# Define o diretório raiz do projeto como o diretório onde este script reside
PROJECT_ROOT="$(dirname "$(realpath "$0")")"

# Ativa o ambiente virtual
source "$PROJECT_ROOT/venv/bin/activate"

# Adiciona o diretório raiz do projeto ao PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Navega para o diretório raiz do projeto
cd "$PROJECT_ROOT"

# Executa o comando da CLI do anki_sync com os argumentos passados
exec python3 -m src.anki_sync.cli "$@"
