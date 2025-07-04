import sys
from pathlib import Path
import pandas as pd

from .models import Deck, Flashcard
from .anki_connector import AnkiConnector # Importar AnkiConnector

def build_deck_tree(root_path='.'):
    """
    Função principal de serialização. Caminha pela árvore de diretórios e constrói o modelo de dados.
    """
    root_path = Path(root_path).resolve()
    # Passa o próprio root_path para o construtor do Deck raiz
    root_deck = Deck(root_path, project_root=root_path)
    
    # Dicionário para manter o controle dos decks já criados
    deck_map = {root_path: root_deck}

    for csv_path in sorted(root_path.rglob('*.csv')):
        # Encontra o diretório pai do arquivo CSV
        parent_dir = csv_path.parent
        
        # Garante que todos os decks pais existam
        current_deck = root_deck
        # Itera sobre as partes do caminho relativo para construir sub-decks
        for part in parent_dir.relative_to(root_path).parts:
            sub_deck_path = current_deck.path / part
            if sub_deck_path not in deck_map:
                # Passa o project_root para os sub-decks também
                new_deck = Deck(sub_deck_path, parent_deck=current_deck, project_root=root_path)
                current_deck.sub_decks.append(new_deck)
                deck_map[sub_deck_path] = new_deck
                current_deck = new_deck
            else:
                current_deck = deck_map[sub_deck_path]
        
        # Processa o arquivo CSV
        tags = list(parent_dir.relative_to(root_path).parts) + [csv_path.stem]
        
        try:
            # Tenta ler com pandas, com parâmetros mais robustos
            df = pd.read_csv(
                csv_path, 
                encoding='utf-8', 
                on_bad_lines='warn', # Avisa sobre linhas malformadas, mas tenta continuar
                sep=',', 
                quotechar='"', 
                doublequote=True, 
                skipinitialspace=True
            )

            # Verifica se as colunas essenciais existem
            if 'pergunta' not in df.columns or 'resposta' not in df.columns:
                # Se as colunas não forem encontradas, tenta ler linha a linha como fallback
                raise ValueError("Colunas 'pergunta' ou 'resposta' ausentes após parsing com pandas.")

            for index, row in df.iterrows():
                pergunta = str(row.get('pergunta', '')).strip()
                resposta = str(row.get('resposta', '')).strip()

                # Se a pergunta ou resposta estiverem vazias ou forem NaN após o parsing do pandas,
                # significa que o pandas não conseguiu extrair os dados corretamente para esta linha.
                if not pergunta or not resposta or pd.isna(row.get('pergunta')) or pd.isna(row.get('resposta')):
                    # Cria um flashcard de problema para esta linha específica
                    problem_tags = tags + ['problema_csv', 'pandas_parsing_falha']
                    problem_pergunta = f"CSV Malformado (linha {index+2}): {csv_path.name}" # +2 para cabeçalho e 0-index
                    problem_resposta = f"Dados originais: {row.to_dict()}" # Representação da linha problemática
                    card = Flashcard(problem_pergunta, problem_resposta, problem_tags)
                    current_deck.flashcards.append(card)
                    print(f"Aviso: Linha {index+2} em '{csv_path.name}' problemática. Criado flashcard de erro.", file=sys.stderr)
                else:
                    card = Flashcard(pergunta, resposta, tags)
                    current_deck.flashcards.append(card)

        except (pd.errors.ParserError, ValueError, UnicodeDecodeError) as e:
            print(f"Erro grave ao processar '{csv_path}' com pandas ({e}). Tentando fallback linha a linha...", file=sys.stderr)
            # Fallback: ler o arquivo linha a linha para capturar o conteúdo bruto
            with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
                for i, raw_line in enumerate(f):
                    # Ignora o cabeçalho na leitura bruta se o pandas já tentou lê-lo
                    if i == 0 and 'pergunta' in raw_line.lower() and 'resposta' in raw_line.lower():
                        continue 
                    
                    problem_tags = tags + ['problema_csv', 'fallback_leitura_bruta']
                    problem_pergunta = f"CSV Malformado (bruto, linha {i+1}): {csv_path.name}"
                    problem_resposta = raw_line.strip() # Conteúdo bruto da linha
                    card = Flashcard(problem_pergunta, problem_resposta, problem_tags)
                    current_deck.flashcards.append(card)
                    print(f"Aviso: Linha {i+1} em '{csv_path.name}' adicionada como flashcard de erro bruto.", file=sys.stderr)
        except Exception as e:
            print(f"Erro inesperado ao processar '{csv_path}': {e}", file=sys.stderr)
            # Adiciona um flashcard de erro geral para o arquivo
            problem_tags = tags + ['problema_csv', 'erro_arquivo_geral']
            problem_pergunta = f"CSV Malformado (erro geral): {csv_path.name}"
            problem_resposta = f"Erro: {e}"
            card = Flashcard(problem_pergunta, problem_resposta, problem_tags)
            current_deck.flashcards.append(card)

    return root_deck



def sync_deck_tree(deck_node, connector):
    """
    Percorre a árvore de decks e sincroniza com o Anki.
    """
    # Sincroniza sub-decks primeiro (pós-ordem)
    for sub_deck in deck_node.sub_decks:
        sync_deck_tree(sub_deck, connector)

    print(f"\nSincronizando baralho: {deck_node.anki_deck_name}")
    connector.create_deck(deck_node.anki_deck_name)

    # Lógica para sincronizar o modelo de nota, se definido no config
    model_config = deck_node.config.get('model')
    if model_config and model_config.get('name'):
        print(f"  - Garantindo que o modelo de nota '{model_config['name']}' exista...")
        connector.create_note_model(
            model_name=model_config['name'],
            field_names=model_config.get('fields', []),
            templates=model_config.get('templates', []),
            css=model_config.get('css', '')
        )

    # Sincroniza os flashcards do baralho atual
    model_name_to_use = deck_node.config.get('model', {}).get('name', 'Basic') # Fallback para 'Basic'
    for card in deck_node.flashcards:
        # Adiciona tags extras da configuração
        all_tags = card.tags + deck_node.config.get('metadata', {}).get('extraTags', [])
        
        connector.sync_note(
            deck_name=deck_node.anki_deck_name,
            model_name=model_name_to_use,
            pergunta=card.pergunta,
            resposta=card.resposta,
            tags=all_tags,
            id_unico=card.id_unico
        )

def compare_flashcards_with_anki(root_path: Path, connector: AnkiConnector):
    """
    Compara flashcards locais com flashcards do Anki e retorna um relatório detalhado.
    """
    print("Construindo árvore de flashcards local...")
    local_root_deck = build_deck_tree(root_path)

    local_flashcards_map = {}
    def flatten_deck(deck):
        for card in deck.flashcards:
            local_flashcards_map[card.id_unico] = card
        for sub_deck in deck.sub_decks:
            flatten_deck(sub_deck)
    flatten_deck(local_root_deck)

    print("Buscando todos os flashcards do Anki...")
    all_anki_note_ids = connector._invoke('findNotes', query='')
    anki_notes_info = {}
    if all_anki_note_ids:
        batch_size = 1000
        for i in range(0, len(all_anki_note_ids), batch_size):
            batch_ids = all_anki_note_ids[i:i + batch_size]
            batch_info = connector._invoke('notesInfo', notes=batch_ids)
            for note in batch_info:
                if 'ID_Unico' in note['fields'] and note['fields']['ID_Unico']['value']:
                    anki_notes_info[note['fields']['ID_Unico']['value']] = note
                else:
                    print(f"Aviso: Nota Anki {note.get('noteId')} não possui campo ID_Unico. Ignorando para comparação.", file=sys.stderr)

    only_local = []
    only_anki = []
    different = []
    synced = []

    for local_id, local_card in local_flashcards_map.items():
        if local_id in anki_notes_info:
            anki_note = anki_notes_info[local_id]
            anki_pergunta = anki_note['fields']['Pergunta']['value']
            anki_resposta = anki_note['fields']['Resposta']['value']
            anki_tags = set(anki_note['tags'])

            is_different = False
            if local_card.pergunta != anki_pergunta or \
               local_card.resposta != anki_resposta or \
               set(local_card.tags) != anki_tags:
                is_different = True

            if is_different:
                different.append({
                    'local': local_card,
                    'anki': anki_note
                })
            else:
                synced.append(local_card)
        else:
            only_local.append(local_card)

    # A lista 'synced' deve conter todos os cartões que existem em ambos e não são diferentes
    # A forma atual já faz isso, mas vamos garantir que a lógica esteja clara.
    # O problema é que 'synced' só é preenchido se o cartão não for 'different'.
    # A lista 'only_anki' já está correta.

    # Vamos reconstruir as listas para maior clareza e correção
    final_only_local = []
    final_only_anki = []
    final_different = []
    final_synced = []

    # Iterar sobre os cartões locais
    for local_id, local_card in local_flashcards_map.items():
        if local_id in anki_notes_info:
            anki_note = anki_notes_info[local_id]
            anki_pergunta = anki_note['fields']['Pergunta']['value']
            anki_resposta = anki_note['fields']['Resposta']['value']
            anki_tags = set(anki_note['tags'])

            is_different = False
            if local_card.pergunta != anki_pergunta or \
               local_card.resposta != anki_resposta or \
               set(local_card.tags) != anki_tags:
                is_different = True

            if is_different:
                final_different.append({
                    'local': local_card,
                    'anki': anki_note
                })
            else:
                final_synced.append(local_card)
        else:
            final_only_local.append(local_card)

    # Iterar sobre os cartões do Anki para encontrar os que só existem no Anki
    for anki_id, anki_note in anki_notes_info.items():
        if anki_id not in local_flashcards_map:
            final_only_anki.append(anki_note)

    return {
        'only_local': final_only_local,
        'only_anki': final_only_anki,
        'different': final_different,
        'synced': final_synced
    }