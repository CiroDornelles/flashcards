import argparse
import json
import sys
import time
from pathlib import Path

from .core import build_deck_tree, sync_deck_tree, get_anki_deck_name_from_path, compare_flashcards_with_anki
from .anki_connector import AnkiConnector

def handle_create(args):
    """Função que lida com o comando 'create'."""
    print(f"Iniciando processo de criação para o caminho: '{args.path}'")
    if args.dry_run:
        print("--- MODO DE SIMULAÇÃO (DRY RUN) ATIVADO ---")

    connector = AnkiConnector(dry_run=args.dry_run)
    connector.test_connection()

    

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

    if args.compare_local:
        if not args.path:
            print("Erro: O argumento --compare-local requer que --path seja especificado para o diretório raiz dos flashcards locais.", file=sys.stderr)
            return
        
        comparison_results = compare_flashcards_with_anki(Path(args.path), connector)

        print("\n--- Relatório de Comparação (Anki vs. Local) ---")
        
        if comparison_results['only_local']:
            print("\nCartões APENAS NO REPOSITÓRIO LOCAL (precisam ser criados no Anki):")
            for card in comparison_results['only_local']:
                print(f"  - Pergunta: {card.pergunta[:70]}... (ID: {card.id_unico})")
        else:
            print("\nNenhum cartão encontrado APENAS NO REPOSITÓRIO LOCAL.")

        if comparison_results['only_anki']:
            print("\nCartões APENAS NO ANKI (não estão no repositório local):")
            for note in comparison_results['only_anki']:
                pergunta = note['fields']['Pergunta']['value'] if 'Pergunta' in note['fields'] else 'N/A'
                print(f"  - Pergunta: {pergunta[:70]}... (ID: {note['fields']['ID_Unico']['value']})")
        else:
            print("\nNenhum cartão encontrado APENAS NO ANKI.")

        if comparison_results['different']:
            print("\nCartões DIFERENTES (existem em ambos, mas com conteúdo divergente):")
            for diff in comparison_results['different']:
                local_card = diff['local']
                anki_note = diff['anki']
                print(f"  - Pergunta: {local_card.pergunta[:70]}... (ID: {local_card.id_unico})")
                print(f"    Local: Pergunta='{local_card.pergunta[:50]}...', Resposta='{local_card.resposta[:50]}...', Tags={local_card.tags}")
                print(f"    Anki:  Pergunta='{anki_note['fields']['Pergunta']['value'][:50]}...', Resposta='{anki_note['fields']['Resposta']['value'][:50]}...', Tags={anki_note['tags']}")
        else:
            print("\nNenhum cartão encontrado com CONTEÚDO DIVERGENTE.")

        if comparison_results['synced']:
            print("\nCartões SINCRONIZADOS (existem em ambos e são idênticos):")
            for card in comparison_results['synced']:
                print(f"  - Pergunta: {card.pergunta[:70]}... (ID: {card.id_unico})")
        else:
            print("\nNenhum cartão SINCRONIZADO encontrado.")

        print("\n--- Fim do Relatório de Comparação ---")
        return

    deck_names = connector._invoke('deckNames')
    if not deck_names:
        print("Nenhum baralho encontrado no Anki.")
        return

    print("\nBaralhos encontrados:")
    for deck_name in sorted(deck_names):
        # Filtrar por caminho se args.path for fornecido
        if args.path:
            # Converte o caminho local para o nome esperado do baralho Anki
            # Assume que o diretório raiz do projeto é o CWD
            expected_anki_deck_prefix = get_anki_deck_name_from_path(Path(args.path), Path('.'))
            
            # Verifica se o nome do baralho Anki começa com o prefixo esperado
            if not deck_name.startswith(expected_anki_deck_prefix):
                continue

        print(f"- {deck_name}")
        if not args.decks_only and args.details:
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
    parser_inspect.add_argument(
        '--decks-only',
        action='store_true',
        help="Mostra apenas os nomes dos baralhos, sem detalhes das notas."
    )
    parser_inspect.add_argument(
        '--path',
        type=str,
        help="Caminho para um diretório local para inspecionar baralhos e notas correspondentes."
    )
    parser_inspect.add_argument(
        '--compare-local',
        action='store_true',
        help="Compara os flashcards do Anki com os do repositório local."
    )
    parser_inspect.set_defaults(func=handle_inspect)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
