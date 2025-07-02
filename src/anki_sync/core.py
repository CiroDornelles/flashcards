import sys
from pathlib import Path
import pandas as pd

from .models import Deck, Flashcard

def build_deck_tree(root_path='.'):
    """
    Função principal de serialização. Caminha pela árvore de diretórios e constrói o modelo de dados.
    """
    root_path = Path(root_path)
    root_deck = Deck(root_path)
    
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
                new_deck = Deck(sub_deck_path, parent_deck=current_deck)
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