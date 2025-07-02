#!/bin/bash

# Define o diretório raiz do projeto
PROJECT_ROOT="/home/ciro/Documentos/Projetos/flashcards"

# Ativa o ambiente virtual
echo "Ativando ambiente virtual..."
source "$PROJECT_ROOT/venv/bin/activate"

# Adiciona o diretório raiz do projeto ao PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Navega para o diretório raiz do projeto
cd "$PROJECT_ROOT"

# Executa o comando inspect
echo "Executando comando inspect..."
python3 -m src.anki_sync.cli inspect

# Desativa o ambiente virtual (opcional, mas boa prática)
deactivate

# Limpa o PYTHONPATH (opcional)
unset PYTHONPATH

echo "Comando inspect concluído."

# Auto-excluir o script
rm -- "$0"
