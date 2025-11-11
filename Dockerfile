# Usar Python 3.9 slim como imagen base
FROM python:3.9-slim

# Establecer variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY consulta_cliente_fixed.py .
COPY consulta_vehiculo.py .
COPY api_unificada.py .

# Exponer el puerto
EXPOSE 8080

# Comando para ejecutar la aplicación
CMD ["python", "api_unificada.py"]