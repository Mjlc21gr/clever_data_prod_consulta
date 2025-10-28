#!/usr/bin/env python3
"""
API REST para consulta de placas - Lista para GCP
Optimizada para producción con logging, validaciones y manejo de errores robusto
"""

from flask import Flask, request, jsonify
from consulta_placa_fixed import ConsultaPlacaAPI
import logging
import os
from datetime import datetime
import traceback
from functools import wraps
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)

# Configuración para producción
app.config['JSON_AS_ASCII'] = False  # Soporte para caracteres UTF-8
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Instancia global de la API
api_cliente = ConsultaPlacaAPI()


def log_request(f):
    """Decorator para logging de requests"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()

        # Log del request
        logger.info(f"Request: {request.method} {request.path}")
        logger.info(f"Headers: {dict(request.headers)}")

        if request.is_json:
            logger.info(f"Body: {request.get_json()}")

        try:
            # Ejecutar función
            result = f(*args, **kwargs)

            # Log del response
            execution_time = time.time() - start_time
            logger.info(f"Response time: {execution_time:.2f}s")
            logger.info(f"Response status: {result[1] if isinstance(result, tuple) else 200}")

            return result

        except Exception as e:
            # Log del error
            execution_time = time.time() - start_time
            logger.error(f"Error after {execution_time:.2f}s: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    return decorated_function


def validate_placa(placa):
    """
    Valida el formato de la placa

    Args:
        placa (str): Placa a validar

    Returns:
        tuple: (is_valid, error_message)
    """
    if not placa:
        return False, "La placa es requerida"

    if not isinstance(placa, str):
        return False, "La placa debe ser una cadena de texto"

    placa_clean = placa.strip()

    if len(placa_clean) < 3:
        return False, "La placa debe tener al menos 3 caracteres"

    if len(placa_clean) > 10:
        return False, "La placa no puede tener más de 10 caracteres"

    return True, None


@app.route('/api/v1/vehiculos/consultar', methods=['POST'])
@log_request
def consultar_placa():
    """
    Endpoint principal para consultar datos de un vehículo por placa

    Body JSON esperado:
    {
        "placa": "ABC123"
    }

    Respuesta:
    {
        "success": true,
        "timestamp": "2025-10-28T...",
        "placa_consultada": "ABC123",
        "data": { ... },
        "errors": null,
        "execution_time_ms": 1234
    }
    """
    start_time = time.time()

    try:
        # Validar Content-Type
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type debe ser application/json",
                "timestamp": datetime.now().isoformat(),
                "placa_consultada": None,
                "data": None,
                "errors": "Invalid content type",
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }), 400

        # Obtener datos del request
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Body JSON vacío o inválido",
                "timestamp": datetime.now().isoformat(),
                "placa_consultada": None,
                "data": None,
                "errors": "Empty or invalid JSON body",
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }), 400

        # Extraer y validar la placa
        placa = data.get('placa')

        is_valid, error_message = validate_placa(placa)
        if not is_valid:
            return jsonify({
                "success": False,
                "error": error_message,
                "timestamp": datetime.now().isoformat(),
                "placa_consultada": placa,
                "data": None,
                "errors": error_message,
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }), 400

        # Limpiar y normalizar la placa
        placa_clean = str(placa).strip().upper()

        logger.info(f"Consultando placa: {placa_clean}")

        # Realizar la consulta
        resultado = api_cliente.consultar_vehiculo_por_placa(placa_clean)

        execution_time_ms = int((time.time() - start_time) * 1000)

        if resultado:
            # Éxito - agregar metadatos adicionales
            resultado.update({
                "placa_consultada": placa_clean,
                "execution_time_ms": execution_time_ms
            })

            logger.info(f"Consulta exitosa para placa: {placa_clean} en {execution_time_ms}ms")
            return jsonify(resultado), 200
        else:
            logger.error(f"Error en consulta para placa: {placa_clean}")
            return jsonify({
                "success": False,
                "error": "Error interno al consultar la placa",
                "timestamp": datetime.now().isoformat(),
                "placa_consultada": placa_clean,
                "data": None,
                "errors": "Internal server error - Unable to fetch vehicle data",
                "execution_time_ms": execution_time_ms
            }), 500

    except Exception as e:
        execution_time_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Error inesperado: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        return jsonify({
            "success": False,
            "error": f"Error inesperado del servidor: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "placa_consultada": placa if 'placa' in locals() else None,
            "data": None,
            "errors": str(e),
            "execution_time_ms": execution_time_ms
        }), 500


@app.route('/api/v1/health', methods=['GET'])
@log_request
def health_check():
    """Endpoint de verificación de salud"""
    return jsonify({
        "status": "healthy",
        "service": "Consulta Placa API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": "N/A",  # Se puede implementar si se necesita
        "environment": os.getenv('ENVIRONMENT', 'development')
    }), 200


@app.route('/api/v1/info', methods=['GET'])
@log_request
def api_info():
    """Endpoint con información de la API"""
    return jsonify({
        "name": "API de Consulta de Placas",
        "version": "1.0.0",
        "description": "API para consultar información de vehículos por placa usando Seguros Bolívar",
        "endpoints": {
            "POST /api/v1/vehiculos/consultar": "Consultar datos de un vehículo por placa",
            "GET /api/v1/health": "Verificación de salud del servicio",
            "GET /api/v1/info": "Información de la API"
        },
        "usage": {
            "method": "POST",
            "url": "/api/v1/vehiculos/consultar",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": {
                "placa": "ABC123"
            }
        },
        "example_curl": "curl -X POST http://localhost:8080/api/v1/vehiculos/consultar -H 'Content-Type: application/json' -d '{\"placa\": \"ABC123\"}'",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/', methods=['GET'])
@log_request
def root():
    """Endpoint raíz - redirige a info"""
    return jsonify({
        "message": "API de Consulta de Placas - Seguros Bolívar",
        "version": "1.0.0",
        "documentation": "/api/v1/info",
        "health_check": "/api/v1/health",
        "main_endpoint": "/api/v1/vehiculos/consultar"
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Manejador para endpoints no encontrados"""
    return jsonify({
        "success": False,
        "error": "Endpoint no encontrado",
        "timestamp": datetime.now().isoformat(),
        "available_endpoints": [
            "POST /api/v1/vehiculos/consultar",
            "GET /api/v1/health",
            "GET /api/v1/info",
            "GET /"
        ],
        "errors": "Not found"
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Manejador para métodos no permitidos"""
    return jsonify({
        "success": False,
        "error": "Método no permitido",
        "timestamp": datetime.now().isoformat(),
        "errors": "Method not allowed"
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Manejador para errores internos del servidor"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "success": False,
        "error": "Error interno del servidor",
        "timestamp": datetime.now().isoformat(),
        "errors": "Internal server error"
    }), 500


if __name__ == '__main__':
    # Configuración para desarrollo local
    port = int(os.getenv('PORT', 8080))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    print("🚀 Iniciando API de Consulta de Placas...")
    print(f"🌐 Host: {host}")
    print(f"🔌 Puerto: {port}")
    print(f"🐛 Debug: {debug}")
    print()
    print("📡 Endpoints disponibles:")
    print(f"   POST http://{host}:{port}/api/v1/vehiculos/consultar - Consultar placa")
    print(f"   GET  http://{host}:{port}/api/v1/health - Health check")
    print(f"   GET  http://{host}:{port}/api/v1/info - Información de la API")
    print(f"   GET  http://{host}:{port}/ - Endpoint raíz")
    print()
    print("📝 Ejemplo de uso con Postman:")
    print(f"   URL: http://{host}:{port}/api/v1/vehiculos/consultar")
    print("   Method: POST")
    print("   Headers: Content-Type: application/json")
    print('   Body: {"placa": "ABC123"}')
    print()

    # Ejecutar la aplicación
    app.run(
        host=host,
        port=port,
        debug=debug
    )
