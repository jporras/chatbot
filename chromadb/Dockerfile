# Usa la imagen oficial de Chroma como base
FROM chromadb/chroma:latest

# (Opcional) Si necesitas instalar algo extra como curl para healthchecks
# USER root
# RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
# USER chromadb

# Exponemos el puerto por defecto
EXPOSE 8000

# Definimos variables de entorno por defecto
ENV IS_PERSISTENT=TRUE
ENV ANONYMIZED_TELEMETRY=FALSE
ENV PERSIST_DIRECTORY=/chroma/chroma

# El comando de inicio ya viene definido en la imagen base, 
# pero aquí podrías personalizar cómo arranca si fuera necesario.