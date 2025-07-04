# Documentação Abrangente do Projeto Flashcards Anki

## 1. Visão Geral do Projeto

O projeto `flashcards` é uma ferramenta de linha de comando (CLI) em Python desenvolvida para automatizar a criação, atualização e gerenciamento de flashcards. Ele atua como uma ponte declarativa e robusta entre uma estrutura de diretórios de flashcards locais (arquivos CSV) e uma coleção Anki, utilizando o add-on AnkiConnect. O objetivo principal é permitir que os usuários gerenciem seu conteúdo de flashcards localmente (em arquivos de texto versionáveis) e o reflitam de forma consistente e eficiente no Anki.

## 2. Estrutura do Projeto

A estrutura do projeto foi recentemente reorganizada para melhorar a modularidade, a clareza e a manutenibilidade.

```
flashcards/
├── flashcards-cli             # Script wrapper executável para a CLI
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
│   └── lpi/                     # Conteúdo dos flashcards (arquivos CSV e configs)
│       ├── deck_config.json
│       └── ... (outros arquivos CSV e subdiretórios)
├── docs/
│   └── PROJECT_DOCUMENTATION.md # Este arquivo (documentação abrangente)
├── tests/                       # Diretório para testes automatizados (unitários e de integração)
├── venv/                        # Ambiente virtual Python
├── .git/                        # Repositório Git
├── README.md                    # Visão geral rápida do projeto (aponta para esta documentação)
├── requirements.txt             # Dependências do projeto
└── .gitignore                   # Arquivos e diretórios a serem ignorados pelo Git
```

### 2.1. Descrição dos Componentes Principais

*   **`flashcards-cli`**: O ponto de entrada executável para o usuário. Este script garante que a aplicação Python seja executada com o ambiente correto.
*   **`src/anki_sync/cli.py`**: Orquestra a aplicação. Utiliza o módulo `argparse` para definir os comandos da CLI (`create`, `delete`, `init`, `inspect`) e chama as fun��ões de lógica de negócios em `core.py`.
*   **`src/anki_sync/core.py`**: Contém a lógica central do processo de sincronização. Inclui a função `build_deck_tree` (responsável por ler a estrutura de diretórios e arquivos CSV, construindo um modelo de dados em memória) e `sync_deck_tree` (que percorre esse modelo e interage com o Anki via `AnkiConnector`).
*   **`src/anki_sync/models.py`**: Define as classes de modelo de dados que representam a estrutura dos flashcards e decks: `DeckConfig` (configurações de baralho), `Flashcard` (um único flashcard) e `Deck` (um baralho Anki, mapeado para um diretório).
*   **`src/anki_sync/anki_connector.py`**: Uma classe que encapsula toda a comunicação com a API do AnkiConnect. Ela lida com as requisições HTTP, tratamento de erros de conexão e chamadas específicas da API.
*   **`data/`**: O diretório raiz para todo o conteúdo dos flashcards. A estrutura de subdiretórios dentro de `data/` é mapeada diretamente para a hierarquia de baralhos no Anki (ex: `data/lpi/topico1` vira `flashcards::lpi::topico1`).
*   **`deck_config.json`**: Arquivos de configuração que podem existir em qualquer diretório de baralho. Eles definem o modelo de nota a ser usado, opções de baralho do Anki, e metadados como tags. As configurações são herdadas de diretórios pais.

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

5.  **Torne o Script da CLI Executável:**
    ```bash
    chmod +x flashcards-cli
    ```

## 4. Uso da Ferramenta CLI

A ferramenta é executada via linha de comando através do script `flashcards-cli`.

**Formato Geral:**
```bash
./flashcards-cli <command> [arguments] [--options]
```

### 4.1. Comando `create`

Cria ou atualiza baralhos e cartões no Anki a partir da estrutura de diretórios e arquivos CSV.

```bash
./flashcards-cli create [path] [--dry-run]
```

*   **`path`**: (Opcional) O caminho para o diretório raiz a ser sincronizado (dentro de `data/`). Se omitido, o diretório `data/` será usado.
*   **`--dry-run`**: (Opcional) Simula a execução sem fazer alterações reais no Anki. Útil para verificar o que seria sincronizado antes de aplicar as mudanças.

**Exemplo:**
```bash
# Sincroniza todo o conteúdo a partir do diretório 'data/lpi' em modo de simulação
./flashcards-cli create data/lpi --dry-run
```

### 4.2. Comando `delete`

Exclui cartões do Anki com base em um caminho/tag. (Ainda não implementado)

```bash
./flashcards-cli delete <path> [--dry-run] [--yes|-y]
```

*   **`path`**: O caminho que define a tag dos cartões a serem excluídos.
*   **`--dry-run`**: (Opcional) Simula a exclusão sem fazer alterações reais.
*   **`--yes` ou `-y`**: (Opcional) Pula a confirmação interativa para a exclusão.

### 4.3. Comando `init`

Cria um arquivo de configuração `deck_config.json` em um diretório especificado.

```bash
./flashcards-cli init <path>
```

*   **`path`**: O caminho do diretório onde o arquivo de configuração será criado.

**Exemplo:**
```bash
# Cria um deck_config.json em um novo diretório de baralho
./flashcards-cli init data/meu_novo_baralho
```

### 4.4. Comando `inspect`

Inspeciona baralhos e, opcionalmente, notas no Anki. Útil para verificar o estado da sua coleção após a sincronização.

```bash
./flashcards-cli inspect [--details] [--path <local_path>]
```

*   **`--details`**: (Opcional) Mostra os detalhes de cada nota dentro dos baralhos.
*   **`--path`**: (Opcional) Filtra a inspeção para mostrar apenas os baralhos correspondentes ao caminho local especificado.

**Exemplos:**
```bash
# Lista todos os baralhos no Anki
./flashcards-cli inspect

# Lista apenas os baralhos relacionados ao diretório 'data/lpi'
./flashcards-cli inspect --path data/lpi
```

## 5. Gerenciamento de Configuração

A ferramenta agora utiliza arquivos `deck_config.json` para um controle declarativo e granular sobre os baralhos e modelos de nota.

### 5.1. Herança de Configuração
As configurações são herdadas. Um `deck_config.json` em um subdiretório sobrescreverá ou complementará as configurações de um `deck_config.json` em um diretório pai.

### 5.2. Definição de Modelo de Nota
O modelo de nota (Note Type) do Anki pode ser definido diretamente no `deck_config.json`. A ferramenta garantirá que este modelo exista no Anki antes de sincronizar as notas.

**Exemplo de `deck_config.json` com definição de modelo:**
```json
{
  "model": {
    "name": "LPI-Flashcard-Custom",
    "fields": ["ID_Unico", "Pergunta", "Resposta"],
    "templates": [
      {
        "Name": "Card 1",
        "Front": "{{Pergunta}}",
        "Back": "{{FrontSide}}<hr id=answer>{{Resposta}}"
      }
    ],
    "css": ".card { font-family: sans-serif; ... }"
  },
  "metadata": {
    "extraTags": ["linux", "lpic-1"]
  }
}
```
Se um `deck_config.json` não especificar um modelo, a ferramenta usará o modelo "Basic" padrão do Anki.

## 6. Progresso Detalhado do Conteúdo: LPIC-1
... (seção inalterada) ...

## 7. Problemas Conhecidos e Desafios Atuais

*   **[RESOLVIDO] `ModuleNotFoundError`**: Resolvido com o uso do script `flashcards-cli` e importações relativas corretas.
*   **[RESOLVIDO] Problemas de Parsing de CSVs**: Resolvido com a integração da biblioteca `pandas` e um mecanismo de fallback robusto.
*   **[RESOLVIDO] Duplicatas de Notas no Anki (Ordem dos Campos)**: Resolvido ao garantir que o `ID_Unico` (hash da pergunta) seja o identificador único para atualizações e ao permitir que a definição do modelo seja gerenciada via `deck_config.json`, garantindo consistência.
*   **Tratamento de Erros do AnkiConnect**: A comunicação com o AnkiConnect pode falhar. O tratamento de erros atual é básico e precisa ser aprimorado para fornecer feedback mais claro.

## 8. Planos de Aprimoramento Futuros (Roadmap)

O desenvolvimento do projeto seguirá o seguinte plano de aprimoramento:

### Fase 1: Refatoração e Correção de Inconsistências (Concluída)
*   **[CONCLUÍDO] ✅ Criar script de entrada `flashcards-cli`**.
*   **[CONCLUÍDO] ✅ Mover conteúdo para o diretório `data/`**.
*   **[CONCLUÍDO] ✅ Centralizar lógica de nomenclatura de baralhos**.
*   **[CONCLUÍDO] ✅ Desacoplar definição de modelo de nota do código**.

### Fase 2: Robustez e Validação
*   **Validação de Conteúdo dos Flashcards**:
    *   Validação básica para conteúdo HTML/caracteres especiais.
    *   Mecanismo para "sanitizar" o conteúdo.

### Fase 3: Gerenciamento Inteligente da Coleção Anki
*   **Sincronização de Mídia (Imagens, Áudio)**:
    *   Detectar referências a arquivos de mídia e fazer o upload.
*   **Tratamento de Erros da API AnkiConnect**:
    *   Implementar blocos `try-except` abrangentes com mensagens claras.
    *   Adicionar mecanismo de "retry" com backoff exponencial.

### Fase 4: Usabilidade e Desempenho
*   **Feedback Detalhado e Modo Verbose**:
    *   Adicionar um modo "verbose" (`-v` ou `--verbose`).
*   **Otimização de Desempenho**:
    *   Utilizar operações em lote do AnkiConnect (`addNotes`, `updateNoteFields`).
*   **Implementação do Comando `delete`**:
    *   Desenvolver lógica para exclusão granular de cartões.

### Fase 5: Manutenção
*   **Testes Automatizados**:
    *   Escrever testes unitários para funções críticas.
    *   Considerar testes de integração com um Anki local.

## 9. Contribuição

Contribuições são bem-vindas! Por favor, siga as diretrizes de código e o fluxo de trabalho de desenvolvimento. Para relatar bugs ou sugerir melhorias, abra uma issue no repositório.