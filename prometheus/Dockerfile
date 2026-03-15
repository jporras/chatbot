# Usamos la imagen oficial estable
FROM prom/prometheus:latest

# Copiamos nuestro archivo de configuración al contenedor
COPY prometheus.yml /etc/prometheus/prometheus.yml

# Exponemos el puerto de la interfaz web de Prometheus
EXPOSE 9090

# El punto de entrada ya viene definido en la imagen base, 
# pero le pasamos parámetros para habilitar el almacenamiento persistente
CMD [ "--config.file=/etc/prometheus/prometheus.yml", \
      "--storage.tsdb.path=/prometheus", \
      "--web.console.libraries=/usr/share/prometheus/console_libraries", \
      "--web.console.templates=/usr/share/prometheus/consoles" ]