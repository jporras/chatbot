from app.api import ask, documents, upload


class InMemoryState:
    documents_by_id: dict[str, dict] = {}
    batches: dict[str, list[str]] = {}
    queries: dict[str, dict] = {}

    def set_document_status(self, document_id: str, **kwargs):
        payload = {'document_id': document_id, **kwargs}
        self.documents_by_id[document_id] = payload
        self.batches.setdefault(kwargs['batch_id'], []).append(document_id)

    def get_document_status(self, document_id: str):
        return self.documents_by_id.get(document_id)

    def get_batch_status(self, batch_id: str):
        return [self.documents_by_id[doc] for doc in self.batches.get(batch_id, [])]

    def publish_query_event(self, query_id: str, payload: dict):
        self.queries[query_id] = {'query_id': query_id, **payload}

    def get_query_status(self, query_id: str):
        return self.queries.get(query_id)


class FakeStorage:
    async def save_upload(self, file):
        return file.filename, f'/tmp/{file.filename}', f'hash-{file.filename}'


class FakeRegistry:
    def reserve_next_version(self, logical_document_id: str) -> int:
        return 1

    def set_current_hash(self, logical_document_id: str, file_version: int, content_hash: str) -> None:
        return None


class FakeProducer:
    def publish(self, *args, **kwargs):
        return None


class FakeQueryService:
    def ask(self, query_id: str, question: str, **kwargs):
        InMemoryState().publish_query_event(
            query_id,
            {
                'status': 'DONE',
                'progress': 100,
                'message': 'Respuesta lista',
                'answer': f'OK: {question}',
                'sources': [{'filename': 'manual.pdf', 'file_version': 1}],
            },
        )


class InlineThread:
    def __init__(self, target, kwargs, daemon):
        self.target = target
        self.kwargs = kwargs

    def start(self):
        self.target(**self.kwargs)


def test_e2e_mocked_upload_and_ask(client, monkeypatch):
    InMemoryState.documents_by_id = {}
    InMemoryState.batches = {}
    InMemoryState.queries = {}

    monkeypatch.setattr(upload, 'FileStorageService', FakeStorage)
    monkeypatch.setattr(upload, 'DocumentRegistryService', FakeRegistry)
    monkeypatch.setattr(upload, 'RedisStateService', InMemoryState)
    monkeypatch.setattr(upload, 'KafkaProducerService', FakeProducer)

    monkeypatch.setattr(documents, 'RedisStateService', InMemoryState)

    monkeypatch.setattr(ask, 'RedisStateService', InMemoryState)
    monkeypatch.setattr(ask, 'QueryService', FakeQueryService)
    monkeypatch.setattr(ask, 'Thread', InlineThread)

    upload_response = client.post(
        '/api/upload',
        files=[('files', ('manual.pdf', b'pdf', 'application/pdf'))],
        data={'document_ids': 'doc-qa'},
    )
    assert upload_response.status_code == 200
    batch_id = upload_response.json()['batch_id']

    batch_status = client.get(f'/api/uploads/{batch_id}/status')
    assert batch_status.status_code == 200
    assert batch_status.json()['items'][0]['document_id'] == 'doc-qa'

    ask_response = client.post('/api/ask', json={'question': 'Resumen del manual'})
    assert ask_response.status_code == 200
    query_id = ask_response.json()['query_id']

    query_status = client.get(f'/api/queries/{query_id}/status')
    assert query_status.status_code == 200
    assert query_status.json()['status'] == 'DONE'
    assert query_status.json()['answer'] == 'OK: Resumen del manual'
