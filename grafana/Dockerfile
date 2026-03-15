# Usamos la versión estable de Grafana
FROM grafana/grafana:latest

# Deshabilitamos el asistente de configuración inicial para ir directo al grano
ENV GF_AUTH_ANONYMOUS_ENABLED=true
ENV GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
ENV GF_SECURITY_ADMIN_PASSWORD=admin

# Copiamos la configuración de la fuente de datos (Prometheus)
COPY provisioning/ /etc/grafana/provisioning/

# Exponemos el puerto de la interfaz web
EXPOSE 3000