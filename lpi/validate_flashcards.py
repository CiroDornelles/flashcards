import os
import csv

def validate_flashcards(root_dir):
    inconsistencies_found = False
    print(f"Iniciando validação dos flashcards em: {root_dir}\n")

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".csv"):
                filepath = os.path.join(dirpath, filename)
                print(f"Validando arquivo: {filepath}")
                
                try:
                    with open(filepath, 'r', newline='', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        
                        # Check header
                        try:
                            header = next(reader)
                            if header != ['pergunta', 'resposta']:
                                print(f"  ERRO: Cabeçalho incorreto em '{filepath}'. Esperado: ['pergunta', 'resposta'], Encontrado: {header}")
                                inconsistencies_found = True
                        except StopIteration:
                            print(f"  ERRO: Arquivo vazio ou sem cabeçalho em '{filepath}'.")
                            inconsistencies_found = True
                            continue

                        # Check content lines
                        line_num = 1
                        for row in reader:
                            line_num += 1
                            if len(row) != 2:
                                print(f"  ERRO: Linha {line_num} em '{filepath}' tem número incorreto de colunas. Esperado 2, Encontrado {len(row)}: {row}")
                                inconsistencies_found = True
                            
                except Exception as e:
                    print(f"  ERRO: Não foi possível ler ou processar '{filepath}': {e}")
                    inconsistencies_found = True
                print("-" * 30) # Separator for readability

    if not inconsistencies_found:
        print("\nValidação concluída: Nenhum problema de formato encontrado em nenhum flashcard.")
    else:
        print("\nValidação concluída: Foram encontradas inconsistências. Por favor, revise os erros acima.")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.abspath(__file__))
    validate_flashcards(project_root)