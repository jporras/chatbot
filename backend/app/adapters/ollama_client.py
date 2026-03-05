import requests

class OllamaClient:

    def __init__(self, base_url: str, model_name: str):
        self.base_url = base_url
        self.model_name = model_name

    def generate(self, prompt: str) -> str:

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"]