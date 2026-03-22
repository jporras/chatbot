#!/bin/bash
set -e

ollama serve &
OLLAMA_PID=$!

sleep 5

ollama pull llama3
ollama pull nomic-embed-text

wait $OLLAMA_PID