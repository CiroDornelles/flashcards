import csv
import os

def create_csv_file(filepath, flashcards_data):
    """
    Cria um arquivo CSV no formato 'pergunta,resposta' com o escape correto.

    Args:
        filepath (str): O caminho absoluto para o arquivo CSV a ser criado.
        flashcards_data (list): Uma lista de tuplas, onde cada tupla é (pergunta, resposta).
    """
    print(f"Criando arquivo CSV: {filepath}")
    try:
        # Garante que o diretório de destino exista
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)
            writer.writerow(['pergunta', 'resposta']) # Escreve o cabeçalho
            writer.writerows(flashcards_data) # Escreve os dados

        print(f"  Arquivo CSV '{filepath}' criado com sucesso.")
    except Exception as e:
        print(f"  ERRO ao criar o arquivo CSV '{filepath}': {e}")

if __name__ == "__main__":
    # Exemplo de uso (pode ser removido ou modificado para testes)
    project_root = "/home/ciro/Documentos/Projetos/lpi_1_flashcards"
    output_dir = os.path.join(project_root, "05_Shells_Scripting")
    output_filepath = os.path.join(output_dir, "exemplo_bash.csv")

    sample_flashcards = [
        ("Qual é o comando `echo`?", "O comando `echo` exibe uma linha de texto/string na saída padrão."),
        ("Como usar `ls` para listar arquivos ocultos?", "Use `ls -a` para listar todos os arquivos, incluindo os ocultos (que começam com ponto)."),
        ("O que faz o comando `grep -r 'padrao' .`?", "O comando `grep -r 'padrao' .` busca recursivamente pelo 'padrao' em todos os arquivos no diretório atual e subdiretórios.")
    ]

    create_csv_file(output_filepath, sample_flashcards)
