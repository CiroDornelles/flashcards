# Painel de Controle do Projeto: Flashcards LPI

*Bem-vindo(a) ao projeto! Este documento é o seu guia central. Ele rastreia nosso progresso, documenta decisões importantes e define as próximas tarefas. Comece por aqui para entender o estado atual do trabalho.*

## 1. Visão e Protocolo

- **Objetivo Principal:** Atingir o **Domínio Total** do sistema Linux através da criação de um conjunto de flashcards exaustivo para as certificações LPI (1, 2 e 3).
- **Metodologia:** Aderência estrita ao **Protocolo Universal de Acurácia e Verificação (PUAV)**. A filosofia é simples: a qualidade, precisão e verificação em fontes primárias (`man pages`, docs oficiais) têm precedência sobre a velocidade.

## 2. Legenda de Status

- **[Exaustivo] ✅:** Tópico concluído com profundidade máxima.
- **[LPI] ☑️:** Tópico concluído com foco nos requisitos do exame.
- **[Em Progresso] ⏳:** Tópico atualmente em desenvolvimento.
- **[Pendente] ⏸️:** Tópico aguardando para ser iniciado.
- **[Revisão] 🧐:** Tópico concluído, mas marcado para revisão e aprofundamento futuro.

## 3. Formato dos Flashcards

- **Formato do Arquivo:** CSV (Comma-Separated Values).
- **Codificação:** UTF-8.
- **Estrutura:**
    - **Cabeçalho:** A primeira linha de cada arquivo é sempre `pergunta,resposta`.
    - **Colunas:**
        1.  `pergunta`: Contém a pergunta do flashcard.
        2.  `resposta`: Contém a resposta correspondente.
- **Delimitador:** Os campos são separados por uma vírgula (`,`).
- **Gerenciamento de Aspas e Caracteres Especiais:** Para arquivos CSV novos, o script `process_flashcard_csv.py` garante que todos os campos sejam corretamente citados e que caracteres especiais (incluindo aspas duplas internas e vírgulas) sejam escapados de acordo com as regras do formato CSV, utilizando `csv.QUOTE_ALL`. O `convert_flashcards.py` é usado especificamente para converter arquivos legados de 4 colunas para o formato de 2 colunas (`pergunta,resposta`).

## 4. Ferramentas de Desenvolvimento

Para garantir a consistência e automação na criação dos flashcards, utilizamos a biblioteca `genanki` para Python.

### 4.1. Ambiente Virtual Python (`venv`)

É **altamente recomendado** o uso de um ambiente virtual para isolar as dependências do projeto.

-   **Criação do Ambiente Virtual:**
    ```bash
    python3 -m venv venv
    ```
-   **Ativação do Ambiente Virtual:**
    ```bash
    source venv/bin/activate
    ```
    (No Windows, use `venv\Scripts\activate`)
-   **Desativação do Ambiente Virtual:**
    ```bash
    deactivate
    ```

### 4.2. Instalação de Dependências (`genanki`)

Com o ambiente virtual ativado, instale a `genanki`:

```bash
pip install genanki
```

### 4.3. Geração de Flashcards com `genanki`

Os flashcards serão gerados a partir dos arquivos CSV usando scripts Python que utilizam a `genanki`. Isso garante que o formato final (`.apkg`) seja compatível com o Anki e que a estrutura (Model, Note, Deck) seja padronizada.

### 4.4. Processo de Criação de Flashcards

Para criar novos arquivos CSV de flashcards, siga o seguinte fluxo:

1.  **Criação do Conteúdo Bruto:** O agente deve gerar o conteúdo dos flashcards (pergunta e resposta) e salvá-lo em um arquivo temporário com o sufixo `-naovalidado.csv` (ex: `bash-naovalidado.csv`). Este arquivo pode ser criado diretamente pelo agente, sem preocupações com o escape de caracteres neste momento.

2.  **Processamento e Validação:** Utilize o script `process_flashcard_csv.py` para ler o arquivo `-naovalidado.csv`, garantir o escape correto de aspas e vírgulas, e reescrever o conteúdo no arquivo CSV final (ex: `bash.csv`). O script também é responsável por apagar o arquivo `-naovalidado.csv` após o processamento bem-sucedido.

    **Exemplo de uso do `process_flashcard_csv.py`:**
    ```bash
    python3 /home/ciro/Documentos/Projetos/lpi_1_flashcards/process_flashcard_csv.py /home/ciro/Documentos/Projetos/lpi_1_flashcards/05_Shells_Scripting
    ```
    (O script `process_flashcard_csv.py` processará todos os arquivos `*-naovalidado.csv` encontrados no diretório especificado.)

Este processo garante que todos os arquivos CSV de flashcards estejam no formato correto e prontos para serem utilizados na geração dos decks Anki.

## 5. Progresso Detalhado: LPIC-1

### **Tópico 101: Arquitetura do Sistema**
- **Status:** `[Exaustivo]` ✅
- **Sub-tópicos (12/12):**
  - `lspci.csv`, `lsusb.csv`, `lscpu.csv`, `udev.csv`, `sysfs.csv`, `grub.csv`, `systemd.csv`, `journalctl.csv`, `runlevel.csv`, `shutdown.csv`, `reboot.csv`, `wall.csv`
- **Notas:** O comando `lsdev` foi pulado por não ser padrão na distribuição base, conforme PUAV.

### **Tópico 102: Instalação e Gerenciamento de Pacotes**
- **Status:** `[Exaustivo]` ✅
- **Sub-tópicos:**
  - **102.1 - Design de Particionamento:** `[Exaustivo]` ✅
    - **Arquivos (10/10):** `fdisk.csv`, `gdisk.csv`, `parted.csv`, `mkfs.csv`, `mkswap.csv`, `swapon_off.csv`, `lsblk.csv`, `blkid.csv`, `fstab.csv`, `lvm.csv`
    - **Notas:** `gdisk` foi documentado a partir de `man pages` online devido à sua ausência no sistema.
  - **102.2 - Boot Manager:** `[Exaustivo]` ✅
    - **Arquivos (3/3):** `grub-install.csv`, `grub-mkconfig.csv`, `update-grub.csv`
  - **102.3 - Bibliotecas Compartilhadas:** `[Exaustivo]` ✅
    - **Arquivos (3/3):** `ldd.csv`, `ldconfig.csv`, `ld.so.conf.csv`
  - **102.4 - Gerenciamento de Pacotes Debian:** `[Exaustivo]` ✅
    - **Arquivos (5/5):** `dpkg.csv`, `apt.csv`, `apt-get.csv`, `apt-cache.csv`, `aptitude.csv`
  - **102.5 - Gerenciamento de Pacotes RPM e YUM:** `[Exaustivo]` ✅
    - **Arquivos (2/2):** `rpm.csv`, `yum.csv`

### **Tópico 103: Comandos GNU e Unix**
- **Status:** `[Exaustivo]` ✅
- **Sub-tópicos (21/21):** `cat.csv`, `tac.csv`, `rev.csv`, `od.csv`, `split.csv`, `csplit.csv`, `head.csv`, `tail.csv`, `sort.csv`, `uniq.csv`, `wc.csv`, `cut.csv`, `paste.csv`, `join.csv`, `comm.csv`, `diff.csv`, `patch.csv`, `grep.csv`, `sed.csv`, `awk.csv`, `tr.csv`

### **Tópico 104: Dispositivos e Sistemas de Arquivos**
- **Status:** `[Exaustivo]` ✅
- **Sub-tópicos (16/16):** `ls.csv`, `cp.csv`, `mv.csv`, `rm.csv`, `mkdir.csv`, `rmdir.csv`, `touch.csv`, `find.csv`, `xargs.csv`, `dd.csv`, `ln.csv`, `df.csv`, `du.csv`, `mount.csv`, `umount.csv`, `fdisk.csv`

### **Tópico 105: Shells e Scripting**
- **Status:** `[Exaustivo]` ✅
- **Sub-tópicos (1/X):**
  - `bash.csv`
  - `if_conditional.csv`
  - `for_loop.csv`
  - `while_until_loop.csv`
  - `redirection.csv`
  - `functions.csv`
  - `quoting.csv`
  - `shell_builtins.csv`
  - `job_control.csv`
  - `arithmetic_evaluation.csv`
  - `expansion.csv`
  - `shell_variables.csv`
  - `history.csv`

### **Tópico 106: Interfaces e Desktops**
- **Status:** `[Pendente]` ⏸️

### **Tópico 107: Tarefas Administrativas**
- **Status:** `[Pendente]` ⏸️

### **Tópico 108: Serviços Essenciais do Sistema**
- **Status:** `[Pendente]` ⏸️

### **Tópico 109: Fundamentos de Rede**
- **Status:** `[Revisão]` 🧐
- **Profundidade Atual:** `[LPI]` ☑️
- **Arquivos (16):** `dhclient.csv`, `dig.csv`, `getent.csv`, `host.csv`, `hostname.csv`, `ifconfig.csv`, `ifupdown.csv`, `ip-addr.csv`, `ip-common.csv`, `ip-link.csv`, `ip-route.csv`, `netstat.csv`, `ping.csv`, `route.csv`, `ss.csv`, `traceroute.csv`
- **Notas:** Marcado para revisão futura para expandir a cobertura de `[LPI]` para `[Exaustivo]`.

### **Tópico 110: Segurança**
- **Status:** `[Pendente]` ⏸️

## 6. Próximos Passos (Fila de Trabalho)

1.  **Tarefa Imediata:** Iniciar o **Tópico 105 (Shells e Scripting)**.
    - `bash` ⬅️ **VOCÊ ESTÁ AQUI**

---
*Este documento é dinâmico e deve ser atualizado ao final de cada sessão de trabalho.*