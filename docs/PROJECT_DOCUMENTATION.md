# Documentação Abrangente do Projeto Flashcards Anki

## 1. Visão Geral do Projeto

O projeto `flashcards` é uma ferramenta de linha de comando (CLI) em Python desenvolvida para automatizar a criação, atualização e gerenciamento de flashcards. Ele atua como uma ponte declarativa e robusta entre uma estrutura de diretórios de flashcards locais (arquivos CSV) e uma coleção Anki, utilizando o add-on AnkiConnect. O objetivo principal é permitir que os usuários gerenciem seu conteúdo de flashcards localmente (em arquivos de texto versionáveis) e o reflitam de forma consistente e eficiente no Anki.

## 2. Estrutura do Projeto

A estrutura do projeto foi recentemente reorganizada para melhorar a modularidade, a clareza e a manutenibilidade.

```
flashcards/
├── src/
│   ├── anki_sync/
│   │   ├── __init__.py          # Marca o diretório como um pacote Python
│   │   ├── cli.py               # Ponto de entrada da linha de comando (CLI)
│   │   ├── core.py              # Lógica central de sincronização (build_deck_tree, sync_deck_tree)
│   │   ├── models.py            # Definições das classes de modelo de dados (Deck, Flashcard, DeckConfig)
│   │   └── anki_connector.py    # Encapsula a comunicação com a API do AnkiConnect
│   └── utils/                   # Utilitários auxiliares (ex: scripts de conversão de CSV)
│       ├── __init__.py
│       ├── convert_flashcards.py
│       └── create_flashcard_csv.py
├── data/
│   └── lpi/                     # Conteúdo dos flashcards (arquivos CSV)
│       └── ... (arquivos CSV dos flashcards)
├── docs/
│   └── PROJECT_DOCUMENTATION.md # Este arquivo (documentação abrangente)
├── tests/                       # Diretório para testes automatizados (unitários e de integração)
├── venv/                        # Ambiente virtual Python
├── .git/                        # Repositório Git
├── README.md                    # Visão geral rápida do projeto (aponta para esta documentação)
├── requirements.txt             # Dependências do projeto
├── run_in_project_env.sh        # Script para executar comandos no ambiente do projeto
└── .gitignore                   # Arquivos e diretórios a serem ignorados pelo Git
```

### 2.1. Descrição dos Componentes Principais

*   **`src/anki_sync/cli.py`**: Este é o ponto de entrada principal da aplicação. Ele utiliza o módulo `argparse` para definir os comandos da CLI (`create`, `delete`, `init`, `inspect`) e orquestra as chamadas para as funções de lógica de negócios em `core.py` e `anki_connector.py`.
*   **`src/anki_sync/core.py`**: Contém a lógica central do processo de sincronização. Inclui a função `build_deck_tree` (responsável por ler a estrutura de diretórios e arquivos CSV, construindo um modelo de dados em memória) e `sync_deck_tree` (que percorre esse modelo e interage com o Anki via `AnkiConnector`).
*   **`src/anki_sync/models.py`**: Define as classes de modelo de dados que representam a estrutura dos flashcards e decks: `DeckConfig` (configurações de baralho), `Flashcard` (um único flashcard) e `Deck` (um baralho Anki, mapeado para um diretório).
*   **`src/anki_sync/anki_connector.py`**: Uma classe que encapsula toda a comunicação com a API do AnkiConnect. Ela lida com as requisições HTTP, tratamento de erros de conexão e chamadas específicas da API (ex: `createDeck`, `addNote`, `findNotes`, `updateNoteFields`).
*   **`src/utils/`**: Contém scripts Python auxiliares que podem ser usados para tarefas de pré-processamento ou conversão de dados, como `convert_flashcards.py` e `create_flashcard_csv.py`.
*   **`data/lpi/`**: Este diretório armazena os arquivos CSV que contêm o conteúdo dos flashcards LPI. A estrutura de subdiretórios dentro de `lpi/` é mapeada diretamente para a hierarquia de baralhos no Anki.
*   **`docs/`**: Contém a documentação abrangente do projeto (`PROJECT_DOCUMENTATION.md`).
*   **`run_in_project_env.sh`**: Um script bash que simplifica a execução de comandos da CLI do projeto, ativando automaticamente o ambiente virtual e configurando o `PYTHONPATH`.

## 3. Configuração e Instalação

Para configurar e executar o projeto, siga os passos abaixo:

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/CiroDornelles/flashcards.git
    cd flashcards
    ```

2.  **Crie e Ative o Ambiente Virtual:**
    É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    *(No Windows, use `venv\Scripts\activate`)*

3.  **Instale as Dependências:**
    Com o ambiente virtual ativado, instale as bibliotecas necessárias:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Instale o Anki e o Add-on AnkiConnect:**
    Certifique-se de ter o Anki instalado e o add-on AnkiConnect configurado e em execução. O AnkiConnect é essencial para a comunicação entre o script e o Anki.

5.  **Torne o Script de Execução Executável:**
    ```bash
    chmod +x run_in_project_env.sh
    ```

## 4. Uso da Ferramenta CLI

A ferramenta `anki_sync` é executada via linha de comando. Para simplificar, use o script `run_in_project_env.sh`. Certifique-se de que seu ambiente virtual esteja ativado antes de executar os comandos.

**Formato Geral:**
```bash
./run_in_project_env.sh <command> [arguments] [--options]
```

### 4.1. Comando `create`

Cria ou atualiza baralhos e cartões no Anki a partir da estrutura de diretórios e arquivos CSV.

```bash
./run_in_project_env.sh create [path] [--dry-run]
```

*   **`path`**: (Opcional) O caminho para o diretório raiz a ser sincronizado. Se omitido, o diretório atual (`.`) será usado.
*   **`--dry-run`**: (Opcional) Simula a execução sem fazer alterações reais no Anki. Útil para verificar o que seria sincronizado antes de aplicar as mudanças.

**Exemplo:**
```bash
./run_in_project_env.sh create data/lpi/ --dry-run
```

### 4.2. Comando `delete`

Exclui cartões do Anki com base em um caminho/tag. (Ainda não implementado)

```bash
./run_in_project_env.sh delete <path> [--dry-run] [--yes|-y]
```

*   **`path`**: O caminho que define a tag dos cartões a serem excluídos.
*   **`--dry-run`**: (Opcional) Simula a exclusão sem fazer alterações reais.
*   **`--yes` ou `-y`**: (Opcional) Pula a confirmação interativa para a exclusão.

### 4.3. Comando `init`

Cria um arquivo de configuração `deck_config.json` em um diretório especificado.

```bash
./run_in_project_env.sh init <path>
```

*   **`path`**: O caminho do diretório onde o arquivo de configuração será criado.

### 4.4. Comando `inspect`

Inspeciona baralhos e, opcionalmente, notas no Anki. Útil para verificar o estado da sua coleção após a sincronização.

```bash
./run_in_project_env.sh inspect [--details]
```

*   **`--details`**: (Opcional) Se presente, o comando listará os detalhes de cada nota dentro dos baralhos, incluindo Pergunta, Resposta, ID Único e Tags.

**Exemplos:**
```bash
# Lista todos os baralhos no Anki
./run_in_project_env.sh inspect

# Lista todos os baralhos e os detalhes das notas em cada um
./run_in_project_env.sh inspect --details
```

## 5. Progresso Detalhado do Conteúdo: LPIC-1

Este projeto também visa a criação de um conjunto exaustivo de flashcards para as certificações LPI. A metodologia segue o **Protocolo Universal de Acurácia e Verificação (PUAV)**, priorizando a qualidade e precisão.

### Legenda de Status para Tópicos LPI:

-   **[Exaustivo] ✅:** Tópico concluído com profundidade máxima.
-   **[LPI] ☑️:** Tópico concluído com foco nos requisitos do exame.
-   **[Em Progresso] ⏳:** Tópico atualmente em desenvolvimento.
-   **[Pendente] ⏸️:** Tópico aguardando para ser iniciado.
-   **[Revisão] 🧐:** Tópico concluído, mas marcado para revisão e aprofundamento futuro.

### Tópicos LPIC-1:

*   **Tópico 101: Arquitetura do Sistema** - `[Exaustivo]` ✅
*   **Tópico 102: Instalação e Gerenciamento de Pacotes** - `[Exaustivo]` ✅
*   **Tópico 103: Comandos GNU e Unix** - `[Exaustivo]` ✅
*   **Tópico 104: Dispositivos e Sistemas de Arquivos** - `[Exaustivo]` ✅
*   **Tópico 105: Shells e Scripting** - `[Em Progresso]` ⏳
*   **Tópico 106: Interfaces e Desktops** - `[Pendente]` ⏸️
*   **Tópico 107: Tarefas Administrativas** - `[Pendente]` ⏸️
*   **Tópico 108: Serviços Essenciais do Sistema** - `[Pendente]` ⏸️
*   **Tópico 109: Fundamentos de Rede** - `[Revisão]` 🧐
*   **Tópico 110: Segurança** - `[Pendente]` ⏸️

## 6. Problemas Conhecidos e Desafios Atuais

O projeto passou por várias etapas de desenvolvimento e refatoração, e alguns desafios foram encontrados:

*   **`ModuleNotFoundError`**: Problemas de localização de módulos internos após a refatoração da estrutura de diretórios. Resolvido garantindo que o diretório raiz do projeto esteja no `PYTHONPATH` e utilizando importações relativas.
*   **Problemas de Parsing de CSVs**: Arquivos CSV malformados (com vírgulas não escapadas ou aspas incorretas) causavam falhas na leitura. A solução adotada foi a integração da biblioteca `pandas` para a leitura de CSVs, que é mais robusta e tolerante a erros, com um mecanismo de fallback para linhas que o `pandas` não consegue "corrigir" completamente.
*   **Duplicatas de Notas no Anki (Ordem dos Campos)**: O Anki utiliza o primeiro campo de um modelo de nota para verificar duplicatas. A solução implementada foi a automação da exclusão e recriação do modelo "LPI-Flashcard" no Anki se sua estrutura não corresponder à esperada (garantindo que "ID_Unico" seja o primeiro campo).
*   **Tratamento de Erros do AnkiConnect**: A comunicação com o AnkiConnect pode falhar por diversos motivos (Anki não rodando, add-on desativado, requisições malformadas). O tratamento de erros atual é básico e precisa ser aprimorado para fornecer feedback mais claro e opções de recuperação.

## 7. Planos de Aprimoramento Futuros (Roadmap)

O desenvolvimento do projeto seguirá o seguinte plano de aprimoramento:

### Fase 1: Robustez na Leitura e Validação de Dados Locais

*   **Melhoria na Leitura de CSVs**:
    *   Utilização de `pandas.read_csv()` com tratamento de `on_bad_lines`.
    *   Validação de esquema básico para os CSVs (colunas "Pergunta", "Resposta", "ID_Unico").
    *   Feedback claro ao usuário sobre arquivos CSV problemáticos.
*   **Validação de Conteúdo dos Flashcards**:
    *   Validação básica para conteúdo HTML/caracteres especiais nos campos.
    *   Mecanismo para "sanitizar" o conteúdo.

### Fase 2: Gerenciamento Inteligente da Coleção Anki via AnkiConnect

*   **Gerenciamento de Modelos de Nota**:
    *   Verificar existência e estrutura de modelos de nota existentes.
    *   Oferecer opções para atualizar ou recriar modelos com estruturas diferentes.
    *   Garantir `ID_Unico` como primeiro campo para detecção de duplicatas.
*   **Tratamento de Duplicatas e Atualizações**:
    *   Utilizar `ID_Unico` para identificar notas existentes.
    *   Atualizar notas existentes (`updateNoteFields`) em vez de criar duplicatas.
    *   Implementar estratégia de "merge" ou "overwrite" para campos modificados.
*   **Sincronização de Mídia (Imagens, Áudio)**:
    *   Detectar referências a arquivos de mídia nos campos.
    *   Localizar e fazer upload de arquivos de mídia para o Anki via `storeMediaFile`.
    *   Atualizar caminhos de mídia nos campos do flashcard.
*   **Gerenciamento de Tags**:
    *   Garantir geração consistente de tags a partir da estrutura de diretórios.
    *   Permitir tags adicionais via `deck_config.json`.
    *   Atualizar tags corretamente durante a sincronização.
*   **Tratamento de Erros da API AnkiConnect**:
    *   Implementar blocos `try-except` abrangentes.
    *   Capturar exceções específicas (ex: `ConnectionRefusedError`).
    *   Fornecer mensagens de erro claras e acionáveis.
    *   Adicionar mecanismo de "retry" com backoff exponencial.

### Fase 3: Usabilidade e Desempenho

*   **Feedback Detalhado e Modo Verbose**:
    *   Adicionar um modo "verbose" (`-v` ou `--verbose`) para mais detalhes de execução.
    *   Melhorar mensagens de sucesso e falha.
*   **Otimização de Desempenho para Grandes Coleções**:
    *   Utilizar operações em lote do AnkiConnect (ex: `addNotes`, `updateNoteFields`).
    *   Minimizar o número de chamadas à API.
*   **Implementação do Comando `delete`**:
    *   Desenvolver lógica para exclusão granular de cartões.
    *   Garantir funcionalidade da flag `--yes`.

### Fase 4: Refatoração e Manutenção

*   **Modularização**:
    *   Mover `AnkiConnector` para `anki_connector.py`.
    *   Criar módulos separados para tratamento de CSVs e validação.
*   **Testes Automatizados**:
    *   Escrever testes unitários para funções críticas.
    *   Considerar testes de integração com um Anki local.

## 8. Contribuição

Contribuições são bem-vindas! Por favor, siga as diretrizes de código e o fluxo de trabalho de desenvolvimento. Para relatar bugs ou sugerir melhorias, abra uma issue no repositório.