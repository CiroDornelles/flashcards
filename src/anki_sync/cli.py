import argparse
import json
import sys
import time
from pathlib import Path

from .core import build_deck_tree, sync_deck_tree
from .anki_connector import AnkiConnector

def handle_create(args):
    """Função que lida com o comando 'create'."""
    print(f"Iniciando processo de criação para o caminho: '{args.path}'")
    if args.dry_run:
        print("--- MODO DE SIMULAÇÃO (DRY RUN) ATIVADO ---")

    connector = AnkiConnector(dry_run=args.dry_run)
    connector.test_connection()

    # Definir o modelo de nota LPI-Flashcard
    lpi_flashcard_fields = ["ID_Unico", "Pergunta", "Resposta"]
    lpi_flashcard_templates = [
        {
            "Name": "Card 1",
            "Front": "{{Pergunta}}",
            "Back": "{{FrontSide}}<hr id=answer>{{Resposta}}"
        }
    ]
    lpi_flashcard_css = ".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; }"

    connector.create_note_model("LPI-Flashcard", lpi_flashcard_fields, lpi_flashcard_templates, lpi_flashcard_css)

    # Passo 1: Serialização
    print("\nFase 1: Lendo a estrutura de diretórios e arquivos .csv...")
    root_deck = build_deck_tree(args.path)
    print("Estrutura lida com sucesso.")

    # Passo 2: Sincronização
    print("\nFase 2: Sincronizando com o Anki...")
    sync_deck_tree(root_deck, connector)
    
    print("\nSincronização concluída!")
    if not args.dry_run:
        print("Disparando sincronização em segundo plano no Anki...")
        connector._invoke('sync')

def handle_inspect(args):
    """Função que lida com o comando 'inspect'."""
    print("Iniciando inspeção do Anki...")
    connector = AnkiConnector()
    connector.test_connection()

    deck_names = connector._invoke('deckNames')
    if not deck_names:
        print("Nenhum baralho encontrado no Anki.")
        return

    print("\nBaralhos encontrados:")
    for deck_name in sorted(deck_names):
        print(f"- {deck_name}")
        if args.details:
            # Obter notas para o baralho atual
            query = f'deck:"{deck_name}"'
            note_ids = connector._invoke('findNotes', query=query)
            if note_ids:
                notes_info = connector._invoke('notesInfo', notes=note_ids)
                for note in notes_info:
                    pergunta = note['fields']['Pergunta']['value'] if 'Pergunta' in note['fields'] else 'N/A'
                    resposta = note['fields']['Resposta']['value'] if 'Resposta' in note['fields'] else 'N/A'
                    id_unico = note['fields']['ID_Unico']['value'] if 'ID_Unico' in note['fields'] else 'N/A'
                    tags = ", ".join(note['tags']) if note['tags'] else 'Nenhuma'
                    print(f"  - Nota ID: {note['noteId']}")
                    print(f"    Pergunta: {pergunta[:70]}...")
                    print(f"    Resposta: {resposta[:70]}...")
                    print(f"    ID Único: {id_unico}")
                    print(f"    Tags: {tags}")
            else:
                print("  (Nenhuma nota neste baralho)")
    print("\nInspeção concluída.")

def handle_delete(args):
    print(f"Ação 'delete' chamada para o caminho: {args.path}")
    print(f"Dry Run: {args.dry_run}")
    print(f"Confirmado: {args.yes}")
    # Lógica de exclusão virá aqui

def handle_init(args):
    print(f"Ação 'init' chamada para o caminho: {args.path}")
    config_path = Path(args.path) / 'deck_config.json'
    
    if config_path.exists():
        print(f"O arquivo de configuração '{config_path}' já existe.")
        return

    default_config = {
      "deckOptions": {
        "name": "Default_Config_From_Tool",
        "new": { "steps": [10, 60], "perDay": 20 },
        "rev": { "perDay": 100 },
        "lapse": { "steps": [30], "leechAction": "tagOnly" }
      },
      "fsrs": { "enabled": True, "retention": 0.9 },
      "metadata": { "extraTags": [] }
    }
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        print(f"Arquivo de configuração criado com sucesso em: '{config_path}'")
    except IOError as e:
        print(f"Erro ao criar o arquivo de configuração: {e}", file=sys.stderr)

def main():
    """Função principal que orquestra a CLI."""
    parser = argparse.ArgumentParser(
        description="Ferramenta para sincronizar flashcards de um repositório para o Anki."
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Comando 'create'
    parser_create = subparsers.add_parser(
        'create',
        help="Cria ou atualiza baralhos e cartões no Anki a partir de um caminho."
    )
    parser_create.add_argument(
        'path',
        nargs='?',
        default='.',
        help="Caminho para o diretório raiz a ser sincronizado (padrão: diretório atual)."
    )
    parser_create.add_argument(
        '--dry-run',
        action='store_true',
        help="Simula a execução sem fazer alterações reais no Anki."
    )
    parser_create.set_defaults(func=handle_create)

    # Comando 'delete'
    parser_delete = subparsers.add_parser(
        'delete',
        help="Exclui cartões do Anki com base em um caminho/tag."
    )
    parser_delete.add_argument(
        'path',
        help="Caminho que define a tag dos cartões a serem excluídos."
    )
    parser_delete.add_argument(
        '--dry-run',
        action='store_true',
        help="Simula a execução sem fazer alterações reais no Anki."
    )
    parser_delete.add_argument(
        '--yes',
        '-y',
        action='store_true',
        help="Pula a confirmação interativa para a exclusão."
    )
    parser_delete.set_defaults(func=handle_delete)

    # Comando 'init'
    parser_init = subparsers.add_parser(
        'init',
        help="Cria um arquivo de configuração 'deck_config.json' em um diretório."
    )
    parser_init.add_argument(
        'path',
        help="Caminho do diretório onde o arquivo de configuração será criado."
    )
    parser_init.set_defaults(func=handle_init)

    # Comando 'inspect'
    parser_inspect = subparsers.add_parser(
        'inspect',
        help="Inspeciona baralhos e notas no Anki."
    )
    parser_inspect.add_argument(
        '--details',
        action='store_true',
        help="Mostra detalhes das notas em cada baralho."
    )
    parser_inspect.set_defaults(func=handle_inspect)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
