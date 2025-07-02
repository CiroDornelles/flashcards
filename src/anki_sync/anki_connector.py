import json
import requests
import sys

class AnkiConnector:
    """
    Encapsula a comunicação com a API do AnkiConnect.
    """
    def __init__(self, host='http://localhost', port=8765, dry_run=False):
        self.url = f'{host}:{port}'
        self.session = requests.Session()
        self.dry_run = dry_run

    def _invoke(self, action, **params):
        """Método base para fazer uma chamada à API."""
        if self.dry_run and action not in ['version', 'deckNames', 'modelNames', 'findNotes', 'notesInfo']:
            print(f"[DRY RUN] Anki Action: {action} com params: {params}")
            # Para simular a criação, podemos retornar um ID falso
            if action == 'addNote':
                return 1234567890
            return None

        payload = {'action': action, 'version': 6, 'params': params}
        try:
            response = self.session.post(self.url, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            if result.get('error'):
                raise Exception(f"AnkiConnect Error: {result['error']}")
            return result.get('result')
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão com o AnkiConnect em {self.url}.", file=sys.stderr)
            print("Verifique se o Anki está em execução e o add-on AnkiConnect está instalado.", file=sys.stderr)
            sys.exit(1)

    def test_connection(self):
        """Testa a conexão com o AnkiConnect."""
        print("Testando conexão com AnkiConnect...")
        version = self._invoke('version')
        if not self.dry_run:
            print(f"Conexão bem-sucedida! Versão do AnkiConnect: {version}")
        return True

    def create_deck(self, deck_name):
        """Cria um baralho no Anki se ele não existir."""
        return self._invoke('createDeck', deck=deck_name)

    def get_model_names(self):
        """Obtém a lista de nomes de modelos de nota existentes."""
        return self._invoke('modelNames')

    def create_note_model(self, model_name, fields, card_templates, css=""):
        """Cria um novo modelo de nota no Anki, ou recria se houver conflito de campos."""
        print(f"Verificando/Criando modelo de nota: {model_name}")
        
        # Obter informações de todos os modelos para encontrar o ID do modelo
        model_info = self._invoke('modelUsages')
        model_id_to_delete = None
        
        for model_id, info in model_info.items():
            if info['name'] == model_name:
                model_id_to_delete = model_id
                break

        if model_id_to_delete:
            # Modelo existe, verificar a estrutura dos campos
            existing_fields = self._invoke('modelFieldNames', modelName=model_name)
            
            # Verificar se a ordem dos campos está correta (ID_Unico deve ser o primeiro)
            # E se todos os campos esperados estão presentes
            expected_field_names = [f['name'] for f in fields]
            
            # Simplificação: Apenas verifica se ID_Unico é o primeiro e se todos os campos esperados estão lá
            # Uma verificação mais robusta compararia a ordem exata de todos os campos
            is_correct_order = (existing_fields and existing_fields[0] == "ID_Unico")
            has_all_fields = all(field_name in existing_fields for field_name in expected_field_names)

            if is_correct_order and has_all_fields:
                print(f"Modelo '{model_name}' já existe e a estrutura dos campos está correta. Pulando criação.")
                return
            else:
                print(f"Conflito detectado no modelo '{model_name}'. Estrutura atual: {existing_fields}")
                print("Excluindo modelo existente e recriando com a estrutura correta...")
                # Excluir o modelo existente
                self._invoke('deleteModels', models=[model_id_to_delete])
                print(f"Modelo '{model_name}' existente excluído.")
        else:
            print(f"Modelo '{model_name}' não encontrado. Criando novo modelo...")

        # Criar o modelo com a estrutura correta
        model_params = {
            "modelName": model_name,
            "inOrderFields": [f['name'] for f in fields], # Usar apenas os nomes dos campos
            "cardTemplates": card_templates,
            "css": css,
            "isCloze": False
        }
        self._invoke('createModel', **model_params)
        print(f"Modelo '{model_name}' criado com sucesso.")


    def sync_note(self, deck_name, model_name, pergunta, resposta, tags, id_unico):
        """Cria ou atualiza uma nota no Anki."""
        # Procura por uma nota existente com o mesmo ID único
        query = f'"field:ID_Unico={id_unico}"'
        existing_notes = self._invoke('findNotes', query=query)

        note_details = {
            "deckName": deck_name,
            "modelName": model_name,
            "fields": {
                "Pergunta": pergunta,
                "Resposta": resposta,
                "ID_Unico": id_unico
            },
            "tags": tags
        }

        if existing_notes:
            # Atualiza a nota existente
            note_id = existing_notes[0]
            print(f"  Atualizando nota: {pergunta[:40]}...")
            update_payload = {"id": note_id, "fields": note_details["fields"], "tags": note_details["tags"]}
            self._invoke('updateNoteFields', note=update_payload)
            self._invoke('updateNoteTags', note=note_id, tags=note_details["tags"])
        else:
            # Cria uma nova nota
            print(f"  Criando nova nota: {pergunta[:40]}...")
            self._invoke('addNote', note=note_details)
