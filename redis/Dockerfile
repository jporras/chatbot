# Usamos la versión ligera de Redis
FROM redis:7.2-alpine

# Si quisieras usar un archivo de configuración personalizado, 
# descomenta la siguiente línea:
# COPY redis.conf /usr/local/etc/redis/redis.conf

# Exponemos el puerto estándar
EXPOSE 6379

# Comando para iniciar Redis con persistencia activada
# El flag --appendonly yes asegura que los datos se guarden en disco inmediatamente
CMD ["redis-server", "--appendonly", "yes"]