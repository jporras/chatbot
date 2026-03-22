from app.api import ask


class FakeRedisState:
    statuses: dict[str, dict] = {}

    def publish_query_event(self, query_id: str, payload: dict):
        self.statuses[query_id] = {**payload, 'query_id': query_id}

    def get_query_status(self, query_id: str):
        return self.statuses.get(query_id)


class FakeQueryService:
    def ask(self, query_id: str, question: str, **kwargs):
        state = FakeRedisState()
        state.publish_query_event(
            query_id,
            {
                'status': 'DONE',
                'progress': 100,
                'message': 'Respuesta lista',
                'answer': f'Respuesta para: {question}',
                'sources': [],
            },
        )


class InlineThread:
    def __init__(self, target, kwargs, daemon):
        self.target = target
        self.kwargs = kwargs

    def start(self):
        self.target(**self.kwargs)


def test_ask_enqueues_and_returns_query_id(client, monkeypatch):
    FakeRedisState.statuses = {}
    monkeypatch.setattr(ask, 'RedisStateService', FakeRedisState)
    monkeypatch.setattr(ask, 'QueryService', FakeQueryService)
    monkeypatch.setattr(ask, 'Thread', InlineThread)

    response = client.post(
        '/api/ask',
        json={'question': '¿Qué dice el documento?', 'user_id': 'qa-user', 'session_id': 'qa-session'},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'QUEUED'
    assert payload['query_id']


def test_query_status_404_when_missing(client, monkeypatch):
    FakeRedisState.statuses = {}
    monkeypatch.setattr(ask, 'RedisStateService', FakeRedisState)

    response = client.get('/api/queries/no-existe/status')

    assert response.status_code == 404
    assert response.json()['detail'] == 'Query not found'
