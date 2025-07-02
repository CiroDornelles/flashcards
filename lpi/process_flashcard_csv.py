import csv
import os
import glob
import sys

def process_csv_file(input_filepath, output_filepath):
    """
    Lê um arquivo CSV, reescreve-o garantindo o escape correto e apaga o original.

    Args:
        input_filepath (str): O caminho absoluto para o arquivo CSV de entrada (não validado).
        output_filepath (str): O caminho absoluto para o arquivo CSV de saída (validado).
    """
    print(f"Processando arquivo: {input_filepath}")
    temp_output_filepath = output_filepath + ".tmp"
    try:
        rows = []
        with open(input_filepath, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            for row in reader:
                rows.append(row)

        with open(temp_output_filepath, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)
            writer.writerows(rows)

        # Se a escrita temporária for bem-sucedida, substitui o arquivo final
        os.replace(temp_output_filepath, output_filepath)

        # Apaga o arquivo de entrada (não validado)
        os.remove(input_filepath)

        print(f"  Arquivo '{input_filepath}' processado e salvo como '{output_filepath}'. Original apagado.")
    except Exception as e:
        print(f"  ERRO ao processar o arquivo '{input_filepath}': {e}")
        if os.path.exists(temp_output_filepath):
            os.remove(temp_output_filepath) # Limpa o arquivo temporário em caso de erro

def main(topic_dir):
    # Garante que o diretório de destino exista
    os.makedirs(topic_dir, exist_ok=True)

    # Encontra todos os arquivos *-naovalidado.csv no diretório do tópico
    unvalidated_files = glob.glob(os.path.join(topic_dir, "*-naovalidado.csv"))

    if not unvalidated_files:
        print(f"Nenhum arquivo *-naovalidado.csv encontrado em {topic_dir}.")
        return

    for input_filepath in unvalidated_files:
        # Constrói o nome do arquivo de saída removendo '-naovalidado.csv'
        base_filename = os.path.basename(input_filepath)
        output_filename = base_filename.replace("-naovalidado.csv", ".csv")
        output_filepath = os.path.join(topic_dir, output_filename)

        process_csv_file(input_filepath, output_filepath)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 process_flashcard_csv.py <caminho_do_diretorio_do_topico>")
        sys.exit(1)
    
    topic_directory = sys.argv[1]
    main(topic_directory)
