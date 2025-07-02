import argparse
import json
import requests
import sys
import time
from pathlib import Path

from serialization import build_deck_tree

class AnkiConnector:
    """
    Encapsula a comunicação com a API do AnkiConnect.
    """
    def __init__(self, host='http://localhost', port=8765, dry_run=False):
        self.url = f'{host}:{port}'
        self.session = requests.Session()
        self.dry_run = dry_run

    def _invoke(self, action, **params):
        """Método base para fazer uma chamada à API."""
        if self.dry_run and action not in ['version', 'deckNames', 'modelNames', 'findNotes', 'notesInfo']:
            print(f"[DRY RUN] Anki Action: {action} com params: {params}")
            # Para simular a criação, podemos retornar um ID falso
            if action == 'addNote':
                return 1234567890
            return None

        payload = {'action': action, 'version': 6, 'params': params}
        try:
            response = self.session.post(self.url, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            if result.get('error'):
                raise Exception(f"AnkiConnect Error: {result['error']}")
            return result.get('result')
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão com o AnkiConnect em {self.url}.", file=sys.stderr)
            print("Verifique se o Anki está em execução e o add-on AnkiConnect está instalado.", file=sys.stderr)
            sys.exit(1)

    def test_connection(self):
        """Testa a conexão com o AnkiConnect."""
        print("Testando conexão com AnkiConnect...")
        version = self._invoke('version')
        if not self.dry_run:
            print(f"Conexão bem-sucedida! Versão do AnkiConnect: {version}")
        return True

    def create_deck(self, deck_name):
        """Cria um baralho no Anki se ele não existir."""
        return self._invoke('createDeck', deck=deck_name)

    def sync_note(self, deck_name, model_name, pergunta, resposta, tags, id_unico):
        """Cria ou atualiza uma nota no Anki."""
        # Procura por uma nota existente com o mesmo ID único
        query = f'"field:ID_Unico={id_unico}"'
        existing_notes = self._invoke('findNotes', query=query)

        note_details = {
            "deckName": deck_name,
            "modelName": model_name,
            "fields": {
                "Pergunta": pergunta,
                "Resposta": resposta,
                "ID_Unico": id_unico
            },
            "tags": tags
        }

        if existing_notes:
            # Atualiza a nota existente
            note_id = existing_notes[0]
            print(f"  Atualizando nota: {pergunta[:40]}...")
            update_payload = {"id": note_id, "fields": note_details["fields"], "tags": note_details["tags"]}
            self._invoke('updateNoteFields', note=update_payload)
            self._invoke('updateNoteTags', note=note_id, tags=note_details["tags"])
        else:
            # Cria uma nova nota
            print(f"  Criando nova nota: {pergunta[:40]}...")
            self._invoke('addNote', note=note_details)

def sync_deck_tree(deck_node, connector):
    """
    Percorre a árvore de decks e sincroniza com o Anki.
    """
    # Sincroniza sub-decks primeiro (pós-ordem)
    for sub_deck in deck_node.sub_decks:
        sync_deck_tree(sub_deck, connector)

    print(f"\nSincronizando baralho: {deck_node.anki_deck_name}")
    connector.create_deck(deck_node.anki_deck_name)

    # Lógica para sincronizar grupos de opções viria aqui

    # Sincroniza os flashcards do baralho atual
    for card in deck_node.flashcards:
        # Adiciona tags extras da configuração
        all_tags = card.tags + deck_node.config.get('metadata', {}).get('extraTags', [])
        
        connector.sync_note(
            deck_name=deck_node.anki_deck_name,
            model_name="LPI-Flashcard", # Hardcoded por enquanto
            pergunta=card.pergunta,
            resposta=card.resposta,
            tags=all_tags,
            id_unico=card.id_unico
        )

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
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Simula a execução sem fazer alterações reais no Anki."
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

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
