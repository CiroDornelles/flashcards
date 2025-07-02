# Flashcards em Português do Brasil

Este repositório contém uma coleção de flashcards sobre diversos assuntos, todos em português do Brasil. O objetivo é criar um recurso comunitário para estudantes e entusiastas que desejam aprender e revisar tópicos de forma eficiente.

## Assuntos Disponíveis

Atualmente, temos os seguintes baralhos de flashcards:

*   **LPI (Linux Professional Institute):** Flashcards para ajudar nos estudos para as certificações LPI.

## Como Contribuir

Sinta-se à vontade para contribuir com novos baralhos de flashcards ou melhorar os existentes. Para contribuir:

1.  Faça um fork deste repositório.
2.  Crie uma nova branch para suas alterações (`git checkout -b meu-novo-baralho`).
3.  Adicione seus flashcards em um novo diretório com um nome descritivo.
4.  Faça o commit de suas alterações (`git commit -m 'Adiciona novo baralho sobre...'`).
5.  Envie para a sua branch (`git push origin meu-novo-baralho`).
6.  Abra um Pull Request.

Agradecemos a todos que contribuem para este projeto!

---

## 🚧 Trabalho em Progresso: Ferramenta de Sincronização com Anki (`anki_sync.py`) 🚧

Atualmente, estamos desenvolvendo uma ferramenta de linha de comando em Python para automatizar a criação, atualização e gerenciamento de flashcards diretamente do repositório para o Anki, utilizando o add-on AnkiConnect.

### **Progresso Atual (02/07/2025):**

-   **Plano de Implementação (`IMPLEMENTATION_PLAN.md`):** Um plano detalhado para a ferramenta foi criado e documentado.
-   **Estrutura do Código:**
    -   `anki_sync.py`: Ponto de entrada da CLI, com a lógica principal para os comandos `create` e `init`.
    -   `serialization.py`: Módulo contendo as classes de modelo de dados (`Deck`, `Flashcard`, `DeckConfig`) e a lógica para ler a estrutura de diretórios do projeto.
-   **Funcionalidade Implementada:**
    -   **Criação e Atualização (`create`):** A ferramenta já consegue ler recursivamente os diretórios, parsear os arquivos `.csv`, e sincronizar as notas com o Anki. A sincronização é inteligente, atualizando cartões existentes para evitar duplicatas.
    -   **Inicialização de Configuração (`init`):** O comando para criar um arquivo `deck_config.json` modelo está funcional.
    -   **Modo de Simulação (`--dry-run`):** Implementado para o comando `create`, permitindo a verificação das ações sem alterar a coleção Anki.

### **Onde o Trabalho Parou:**

O trabalho foi interrompido imediatamente antes da primeira execução de teste do comando `create --dry-run`. A estrutura de código para a criação de cartões está completa, mas ainda não foi validada em uma execução real.

### **Próximos Passos:**

1.  **Testar a Funcionalidade `create`:**
    -   Executar `python anki_sync.py create . --dry-run` para validar a lógica de serialização e a saída do modo de simulação.
    -   Corrigir eventuais bugs no parsing de arquivos ou na lógica de construção da árvore de baralhos.
    -   Executar o comando sem `--dry-run` para realizar a primeira sincronização real com o Anki.
2.  **Implementar a Sincronização de Configurações de Baralho:** Adicionar a lógica que lê o `deck_config.json` e usa a API do AnkiConnect para criar/atualizar os "Grupos de Opções" do Anki, incluindo o suporte para FSRS.
3.  **Implementar o Comando `delete`:** Desenvolver a lógica para a exclusão granular de cartões com base em tags.
4.  **Refinar e Documentar:** Melhorar a documentação interna do código e a usabilidade da ferramenta.
