import genanki
import os
import csv
import random
import html # Import the html module

# Define a base directory for the flashcards
FLASHCARDS_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
OUTPUT_DIR = os.path.join(FLASHCARDS_BASE_DIR, 'anki_decks')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Anki Model Definition (consistent across all decks)
# Using a fixed model ID for consistency. If you change the model structure, generate a new ID.
MODEL_ID = 1607392319 # A fixed ID for our basic Question/Answer model

my_model = genanki.Model(
  MODEL_ID,
  'LPI Flashcard Model',
  fields=[
    {'name': 'Question'},
    {'name': 'Answer'},
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '{{Question}}',
      'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
    },
  ],
  css='''
    .card {
      font-family: arial;
      font-size: 20px;
      text-align: center;
      color: black;
      background-color: white;
    }
  '''
)

def generate_deck_from_csv(topic_name, csv_filepath):
    deck_id = random.randrange(1 << 30, 1 << 31) # Generate a random ID for each deck
    my_deck = genanki.Deck(
      deck_id,
      f'LPI :: {topic_name}'
    )

    try:
        with open(csv_filepath, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader) # Skip header row
            
            if header != ['pergunta', 'resposta']:
                print(f"Aviso: Cabeçalho inesperado em {csv_filepath}. Esperado: ['pergunta', 'resposta'], Encontrado: {header}")
                # Attempt to proceed if it's just a case difference, otherwise might fail on next()

            for row in reader:
                if len(row) == 2:
                    # Apply html.escape to both question and answer to prevent HTML interpretation
                    question = html.escape(row[0])
                    answer = html.escape(row[1])
                    my_note = genanki.Note(
                        model=my_model,
                        fields=[question, answer]
                    )
                    my_deck.add_note(my_note)
                else:
                    print(f"Aviso: Linha ignorada em {csv_filepath} devido ao formato incorreto: {row}")

        if my_deck.notes:
            output_filename = os.path.join(OUTPUT_DIR, f'{topic_name.replace(" ", "_")}.apkg')
            genanki.Package(my_deck).write_to_file(output_filename)
            print(f"Deck gerado com sucesso: {output_filename} com {len(my_deck.notes)} flashcards.")
        else:
            print(f"Nenhum flashcard válido encontrado em {csv_filepath}. Nenhum deck gerado.")

    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em {csv_filepath}")
    except Exception as e:
        print(f"Erro ao processar {csv_filepath}: {e}")

def main():
    print("Iniciando a geração de decks Anki...")
    for root, dirs, files in os.walk(FLASHCARDS_BASE_DIR):
        # Exclude the venv and anki_decks directories from processing
        dirs[:] = [d for d in dirs if d not in ['venv', 'anki_decks', 'productivity_logs']]

        for file in files:
            if file.endswith('.csv') and file != 'dpkg.csv.bak': # Exclude backup file
                csv_filepath = os.path.join(root, file)
                # Extract topic name from the directory structure
                # Assumes topic directories are direct children of FLASHCARDS_BASE_DIR
                relative_path = os.path.relpath(root, FLASHCARDS_BASE_DIR)
                if relative_path == '.': # Files directly in the base directory (like DIRETRIZES.md)
                    topic_name = "Geral"
                else:
                    topic_name = relative_path.replace(os.sep, ' :: ')
                
                # Use the filename as part of the topic name for more specific decks
                # Or create a deck per file, depending on desired granularity
                # For now, let's create one deck per directory (topic)
                # If you want one deck per CSV file, move generate_deck_from_csv call inside this loop
                # and pass file.replace('.csv', '') as topic_name
                
                # To create one deck per CSV file:
                generate_deck_from_csv(topic_name + ' :: ' + file.replace('.csv', ''), csv_filepath)

    print("Geração de decks Anki concluída.")

if __name__ == "__main__":
    main()