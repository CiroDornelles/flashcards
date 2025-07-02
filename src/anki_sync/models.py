import json
import hashlib
from pathlib import Path

class DeckConfig:
    """
    Representa, carrega e gerencia a configuração de um baralho a partir de um deck_config.json.
    """
    def __init__(self, config_path=None, parent_config=None):
        self.config = self._load_defaults()
        if parent_config:
            # Herda a configuração do pai
            self.config.update(parent_config.config)
        
        if config_path and config_path.exists():
            # Sobrescreve com a configuração local
            with open(config_path, 'r', encoding='utf-8') as f:
                local_config = json.load(f)
            self.config.update(local_config)

    def _load_defaults(self):
        """Retorna a configuração padrão global."""
        return {
          "deckOptions": {
            "name": "Default_Config_From_Tool",
            "new": { "steps": [10, 60], "perDay": 20 },
            "rev": { "perDay": 100 },
            "lapse": { "steps": [30], "leechAction": "tagOnly" }
          },
          "fsrs": { "enabled": True, "retention": 0.9 },
          "metadata": { "extraTags": [] }
        }

    def get(self, key, default=None):
        return self.config.get(key, default)

class Flashcard:
    """
    Representa uma única nota (uma linha de um arquivo .csv).
    """
    def __init__(self, pergunta, resposta, tags=None):
        self.pergunta = pergunta
        self.resposta = resposta
        self.tags = tags if tags is not None else []
        self.id_unico = self._generate_id()

    def _generate_id(self):
        """Gera um ID único e consistente a partir do conteúdo da pergunta."""
        return hashlib.sha256(self.pergunta.encode('utf-8')).hexdigest()

class Deck:
    """
    Representa um diretório no sistema de arquivos e, consequentemente, um baralho no Anki.
    """
    def __init__(self, path, parent_deck=None):
        self.path = Path(path)
        self.name = self.path.name
        self.parent = parent_deck
        
        self.anki_deck_name = self._build_anki_deck_name()
        self.config = DeckConfig(self.path / 'deck_config.json', self.parent.config if self.parent else None)
        
        self.flashcards = []
        self.sub_decks = []

    def _build_anki_deck_name(self):
        """Constrói o nome hierárquico do baralho para o Anki."""
        if not self.parent or not self.parent.anki_deck_name:
            return self.name
        return f"{self.parent.anki_deck_name}::{self.name}"
