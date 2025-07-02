# Plano de Implementação: Ferramenta de Sincronização Anki (`anki_sync.py`)

## 1. Visão Geral

O objetivo é desenvolver um script Python de linha de comando, `anki_sync.py`, que atue como uma ponte declarativa e robusta entre a estrutura de diretórios de flashcards do projeto e uma coleção Anki, através do add-on AnkiConnect.

A ferramenta irá operar com base em um sistema de configuração granular, permitindo que cada baralho (representado por uma pasta) defina seu próprio comportamento, incluindo algoritmos de agendamento (como FSRS), limites de cartões e metadados.

O fluxo principal consiste em três fases:
1.  **Inicialização (Opcional):** Criação de arquivos de configuração modelo.
2.  **Serialização:** Leitura da estrutura de arquivos e das configurações para construir um modelo de dados em memória de como a coleção Anki *deveria ser*.
3.  **Sincronização:** Aplicação das mudanças necessárias (criação/atualização/exclusão) para que a coleção Anki corresponda ao modelo de dados.

## 2. O Pilar Central: Configuração Granular com `deck_config.json`

A granularidade será alcançada através de um arquivo de configuração opcional, `deck_config.json`, que pode existir em qualquer diretório que represente um baralho.

-   **Herança:** Se um diretório não contém um `deck_config.json`, ele herda as configurações do diretório pai mais próximo que o contenha. Se nenhum for encontrado na árvore, um conjunto de configurações padrão globais será aplicado.
-   **Estrutura do `deck_config.json`:**
    ```json
    {
      "deckOptions": {
        "name": "Config_Deck_Personalizado",
        "new": { "steps": [10, 60], "perDay": 20 },
        "rev": { "perDay": 100 },
        "lapse": { "steps": [30], "leechAction": "tagOnly" }
      },
      "fsrs": {
        "enabled": true,
        "retention": 0.9
      },
      "metadata": {
        "extraTags": ["linux", "lpic-1"]
      }
    }
    ```

## 3. Arquitetura de Serialização: Classes do Modelo de Dados

O estado desejado do projeto será representado em memória usando as seguintes classes Python:

-   **`DeckConfig`:** Carrega, valida e gerencia os dados de um `deck_config.json`. Implementa a lógica para herdar configurações de um `DeckConfig` pai.
-   **`Flashcard`:** Representa uma única nota (uma linha de um arquivo `.csv`).
    -   Atributos: `pergunta`, `resposta`, `id_unico` (hash da pergunta para idempotência), `tags`.
-   **`Deck`:** Representa um diretório no sistema de arquivos.
    -   Atributos: `name`, `path`, `anki_deck_name` (nome hierárquico, ex: `lpi::05_Shells_Scripting`), `config` (objeto `DeckConfig`), `flashcards` (lista de objetos `Flashcard`), `sub_decks` (lista de objetos `Deck` filhos).

## 4. Fluxo de Trabalho Detalhado

### Fase 1: Inicialização (`init`)
-   **Comando:** `python anki_sync.py init <caminho_do_diretorio>`
-   **Ação:** Cria um arquivo `deck_config.json` bem documentado e com valores padrão no diretório especificado, facilitando a configuração pelo usuário.

### Fase 2: Serialização (Leitura)
-   **Comando:** `python anki_sync.py create [caminho_raiz]`
-   **Processo:**
    1.  Inicia uma caminhada recursiva a partir do `caminho_raiz`.
    2.  Para cada diretório, instancia um objeto `Deck`.
    3.  Carrega o `deck_config.json` local ou herda do pai, associando o objeto `DeckConfig` resultante ao `Deck`.
    4.  Lê todos os arquivos `.csv` no diretório, instanciando objetos `Flashcard` para cada linha e populando a lista `Deck.flashcards`.
    5.  O resultado final é um único objeto `Deck` raiz que contém a árvore completa do projeto.

### Fase 3: Sincronização (Escrita)
-   **Processo:**
    1.  Recebe a árvore de objetos `Deck` da fase anterior.
    2.  Percorre a árvore de forma recursiva (pós-ordem).
    3.  Para cada `Deck`:
        a. **Sincroniza Grupo de Opções:** Usa a API do AnkiConnect para criar ou atualizar o grupo de opções do baralho (`deckOptions`) conforme definido no `Deck.config`.
        b. **Sincroniza Baralho:** Garante que o baralho (`Deck.anki_deck_name`) exista.
        c. **Aplica Configuração:** Associa o baralho ao grupo de opções correto.
        d. **Sincroniza Notas:** Para cada `Flashcard` no `Deck`, usa a ação `addNote` (ou similar que suporte atualização baseada em um campo chave) para criar ou atualizar a nota no Anki, garantindo que ela esteja no baralho correto e com as tags apropriadas.

## 5. Interface de Linha de Comando (CLI)

A ferramenta será controlada via `argparse` com os seguintes comandos:

-   `anki_sync.py init <path>`: Cria um arquivo de configuração.
-   `anki_sync.py create <path>`: Cria/atualiza baralhos e cartões a partir do caminho.
-   `anki_sync.py delete <path>`: Exclui cartões com base nas tags derivadas do caminho.
-   `anki_sync.py --dry-run ...`: Simula a execução sem fazer alterações.
-   `anki_sync.py --yes ...`: Pula a confirmação interativa para ações destrutivas.

## 6. Módulos e Dependências

-   **`anki_connector.py`:** Módulo dedicado para toda a comunicação com a API AnkiConnect. Tratará da construção de requisições, envio e tratamento de erros de conexão.
-   **`serialization.py`:** Conterá as classes do modelo de dados (`Deck`, `DeckConfig`, `Flashcard`).
-   **`main.py` (ou `anki_sync.py`):** Orquestrará o fluxo, lidando com a CLI e chamando os outros módulos.
-   **Dependências Externas:** `requests`.

Este plano estabelece uma base sólida para uma ferramenta de sincronização poderosa e flexível.
