#!/bin/bash
set -e

ollama serve &
OLLAMA_PID=$!

sleep 5

if [ -n "$LLM_MODEL" ]; then
  ollama pull $LLM_MODEL
fi

wait $OLLAMA_PID