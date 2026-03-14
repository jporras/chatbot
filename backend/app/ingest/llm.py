import os
import requests

class LLM: 
    def __init__(self): 
        self.model = os.getenv("llm_model")
        self.url = "http://localhost:11434/api/generate" 

    def generate(self, prompt: str) -> str: 
        response = requests.post( self.url, json={ "model": self.model, "prompt": prompt, "stream": False } ) 
        if response.status_code != 200: 
            raise Exception("Error calling Ollama") 
        data = response.json() 
        return data["response"]