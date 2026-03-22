FROM ollama/ollama:latest

WORKDIR /app

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

ENTRYPOINT ["/app/start.sh"]