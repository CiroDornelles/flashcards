import os
import csv

def convert_file(filepath):
    print(f"Convertendo arquivo: {filepath}")
    new_rows = []
    try:
        with open(filepath, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            header = next(reader) # Skip old header

            new_rows.append(['pergunta', 'resposta']) # Add new header

            for row in reader:
                if len(row) == 4:
                    comando = row[0].strip()
                    descricao = row[1].strip()
                    exemplo = row[2].strip()
                    observacoes = row[3].strip()

                    pergunta = f"Qual é o comando `{comando}` e o que ele faz?"
                    resposta = f"O comando `{comando}` {descricao}. Exemplo de uso: `{exemplo}`. Observações: `{observacoes}`."
                    new_rows.append([pergunta, resposta])
                else:
                    # If a row doesn't have 4 columns, keep it as is (assuming it's already in the correct format or an anomaly)
                    new_rows.append(row)

        with open(filepath, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile, quoting=csv.QUOTE_ALL) # Use QUOTE_ALL to ensure all fields are quoted
            writer.writerows(new_rows)
        print(f"  Conversão concluída para {filepath}")
    except Exception as e:
        print(f"  ERRO ao converter {filepath}: {e}")

def main():
    project_root = "/home/ciro/Documentos/Projetos/lpi_1_flashcards"
    files_to_convert = [
        os.path.join(project_root, "02_Gerenciamento_Pacotes", "apt-get.csv"),
        os.path.join(project_root, "02_Gerenciamento_Pacotes", "yum.csv"),
        os.path.join(project_root, "02_Gerenciamento_Pacotes", "rpm.csv"),
        os.path.join(project_root, "02_Gerenciamento_Pacotes", "apt-cache.csv"),
        os.path.join(project_root, "02_Gerenciamento_Pacotes", "aptitude.csv"),
        os.path.join(project_root, "03_Comandos_GNU_Unix", "tr.csv"),
        os.path.join(project_root, "03_Comandos_GNU_Unix", "tac.csv"),
        os.path.join(project_root, "03_Comandos_GNU_Unix", "split.csv"),
        os.path.join(project_root, "03_Comandos_GNU_Unix", "cut.csv"),
        os.path.join(project_root, "03_Comandos_GNU_Unix", "sort.csv"),
        os.path.join(project_root, "03_Comandos_GNU_Unix", "patch.csv"),
        os.path.join(project_root, "03_Comandos_GNU_Unix", "head.csv"),
        os.path.join(project_root, "03_Comandos_GNU_Unix", "cat.csv"),
        os.path.join(project_root, "03_Comandos_GNU_Unix", "uniq.csv"),
        os.path.join(project_root, "03_Comandos_GNU_Unix", "od.csv"),
        os.path.join(project_root, "03_Comandos_GNU_Unix", "diff.csv"),
        os.path.join(project_root, "03_Comandos_GNU_Unix", "paste.csv"),
        os.path.join(project_root, "03_Comandos_GNU_Unix", "rev.csv"),
        os.path.join(project_root, "03_Comandos_GNU_Unix", "csplit.csv"),
        os.path.join(project_root, "03_Comandos_GNU_Unix", "comm.csv"),
        os.path.join(project_root, "03_Comandos_GNU_Unix", "tail.csv"),
        os.path.join(project_root, "03_Comandos_GNU_Unix", "awk.csv"),
        os.path.join(project_root, "03_Comandos_GNU_Unix", "grep.csv"),
        os.path.join(project_root, "03_Comandos_GNU_Unix", "join.csv"),
        os.path.join(project_root, "04_Sistema_Arquivos_FHS", "rmdir.csv"),
        os.path.join(project_root, "04_Sistema_Arquivos_FHS", "mount.csv"),
        os.path.join(project_root, "04_Sistema_Arquivos_FHS", "rm.csv"),
        os.path.join(project_root, "04_Sistema_Arquivos_FHS", "xargs.csv"),
        os.path.join(project_root, "04_Sistema_Arquivos_FHS", "cp.csv"),
        os.path.join(project_root, "04_Sistema_Arquivos_FHS", "du.csv"),
        os.path.join(project_root, "04_Sistema_Arquivos_FHS", "df.csv"),
        os.path.join(project_root, "04_Sistema_Arquivos_FHS", "umount.csv"),
        os.path.join(project_root, "04_Sistema_Arquivos_FHS", "ls.csv"),
        os.path.join(project_root, "04_Sistema_Arquivos_FHS", "mv.csv"),
        os.path.join(project_root, "04_Sistema_Arquivos_FHS", "dd.csv"),
        os.path.join(project_root, "04_Sistema_Arquivos_FHS", "touch.csv"),
        os.path.join(project_root, "04_Sistema_Arquivos_FHS", "ln.csv"),
        os.path.join(project_root, "04_Sistema_Arquivos_FHS", "fdisk.csv"),
        os.path.join(project_root, "04_Sistema_Arquivos_FHS", "find.csv"),
        os.path.join(project_root, "04_Sistema_Arquivos_FHS", "mkdir.csv"),
    ]

    for file_path in files_to_convert:
        convert_file(file_path)

if __name__ == "__main__":
    main()
