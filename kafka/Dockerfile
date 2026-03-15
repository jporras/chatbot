# Usamos la imagen oficial de Apache Kafka
FROM apache/kafka:latest

# Si quisieras instalar algo adicional (como utilidades de red para debug)
# USER root
# RUN apt-get update && apt-get install -y iputils-ping && rm -rf /var/lib/apt/lists/*
# USER 1000

# Exponemos el puerto para los clientes (9092) y el controlador (9093)
EXPOSE 9092 9093

# No necesitamos un CMD porque la imagen base ya tiene el script de arranque.
# Las configuraciones pesadas se pasan por variables de entorno desde el Compose.