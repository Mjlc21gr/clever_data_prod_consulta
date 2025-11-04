#!/usr/bin/env python3
"""
API REST para consulta de clientes - Lista para GCP
Optimizada para producción con logging, validaciones y manejo de errores robusto
"""

from flask import Flask, request, jsonify
from consulta_cliente_fixed import ConsultaClienteAPI
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
api_cliente = ConsultaClienteAPI()


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


def validate_documento(tipo_documento, numero_documento):
    """
    Valida el formato del tipo y número de documento

    Args:
        tipo_documento (str): Tipo de documento a validar
        numero_documento (str): Número de documento a validar

    Returns:
        tuple: (is_valid, error_message)
    """
    if not tipo_documento:
        return False, "El tipo de documento es requerido"

    if not numero_documento:
        return False, "El número de documento es requerido"

    if not isinstance(tipo_documento, str):
        return False, "El tipo de documento debe ser una cadena de texto"

    if not isinstance(numero_documento, str):
        return False, "El número de documento debe ser una cadena de texto"

    tipo_clean = tipo_documento.strip().upper()
    numero_clean = numero_documento.strip()

    # Validar tipos de documento válidos
    tipos_validos = ['CC', 'CE', 'NIT', 'PP', 'TI', 'RC', 'CD']
    if tipo_clean not in tipos_validos:
        return False, f"Tipo de documento no válido. Tipos válidos: {', '.join(tipos_validos)}"

    if len(numero_clean) < 3:
        return False, "El número de documento debe tener al menos 3 caracteres"

    if len(numero_clean) > 20:
        return False, "El número de documento no puede tener más de 20 caracteres"

    return True, None


@app.route('/api/v1/clientes/consultar', methods=['POST'])
@log_request
def consultar_cliente():
    """
    Endpoint principal para consultar datos de un cliente por tipo y número de documento

    Body JSON esperado:
    {
        "tipoDocumento": "CC",
        "numeroDocumento": "1234567890"
    }

    Respuesta:
    {
        "success": true,
        "timestamp": "2025-11-04T...",
        "tipo_documento": "CC",
        "numero_documento": "1234567890",
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
                "tipo_documento": None,
                "numero_documento": None,
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
                "tipo_documento": None,
                "numero_documento": None,
                "data": None,
                "errors": "Empty or invalid JSON body",
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }), 400

        # Extraer y validar los datos
        tipo_documento = data.get('tipoDocumento')
        numero_documento = data.get('numeroDocumento')

        is_valid, error_message = validate_documento(tipo_documento, numero_documento)
        if not is_valid:
            return jsonify({
                "success": False,
                "error": error_message,
                "timestamp": datetime.now().isoformat(),
                "tipo_documento": tipo_documento,
                "numero_documento": numero_documento,
                "data": None,
                "errors": error_message,
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }), 400

        # Limpiar y normalizar los datos
        tipo_clean = str(tipo_documento).strip().upper()
        numero_clean = str(numero_documento).strip()

        logger.info(f"Consultando cliente: {tipo_clean} {numero_clean}")

        # Realizar la consulta
        resultado = api_cliente.consultar_cliente_por_documento(tipo_clean, numero_clean)

        execution_time_ms = int((time.time() - start_time) * 1000)

        if resultado:
            # Verificar si se encontraron datos del cliente
            cliente_data = resultado.get("data", {}).get("cliente") if resultado.get("data") else None

            if not cliente_data:
                logger.info(f"No se encontraron datos para {tipo_clean} {numero_clean}")
                return jsonify({
                    "success": True,
                    "message": "No se encontraron datos para el cliente especificado",
                    "timestamp": datetime.now().isoformat(),
                    "tipo_documento": tipo_clean,
                    "numero_documento": numero_clean,
                    "data": None,
                    "errors": None,
                    "execution_time_ms": execution_time_ms
                }), 404

            # Éxito - agregar metadatos adicionales
            resultado.update({
                "tipo_documento": tipo_clean,
                "numero_documento": numero_clean,
                "execution_time_ms": execution_time_ms
            })

            logger.info(f"Consulta exitosa para cliente: {tipo_clean} {numero_clean} en {execution_time_ms}ms")
            return jsonify(resultado), 200
        else:
            logger.error(f"Error en consulta para cliente: {tipo_clean} {numero_clean}")
            return jsonify({
                "success": False,
                "error": "Error interno al consultar el cliente",
                "timestamp": datetime.now().isoformat(),
                "tipo_documento": tipo_clean,
                "numero_documento": numero_clean,
                "data": None,
                "errors": "Internal server error - Unable to fetch client data",
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
            "tipo_documento": tipo_documento if 'tipo_documento' in locals() else None,
            "numero_documento": numero_documento if 'numero_documento' in locals() else None,
            "data": None,
            "errors": str(e),
            "execution_time_ms": execution_time_ms
        }), 500


@app.route('/api/v1/clientes/consultar', methods=['GET'])
@log_request
def consultar_cliente_get():
    """
    Endpoint GET para consultar datos de un cliente por parámetros de query

    Parámetros:
    - tipoDocumento: Tipo de documento (CC, CE, NIT, etc.)
    - numeroDocumento: Número de documento
    """
    start_time = time.time()

    try:
        tipo_documento = request.args.get('tipoDocumento', '').strip().upper()
        numero_documento = request.args.get('numeroDocumento', '').strip()

        is_valid, error_message = validate_documento(tipo_documento, numero_documento)
        if not is_valid:
            return jsonify({
                "success": False,
                "error": error_message,
                "timestamp": datetime.now().isoformat(),
                "tipo_documento": tipo_documento,
                "numero_documento": numero_documento,
                "data": None,
                "errors": error_message,
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }), 400

        logger.info(f"Consultando cliente (GET): {tipo_documento} {numero_documento}")

        # Realizar la consulta
        resultado = api_cliente.consultar_cliente_por_documento(tipo_documento, numero_documento)

        execution_time_ms = int((time.time() - start_time) * 1000)

        if resultado:
            # Verificar si se encontraron datos del cliente
            cliente_data = resultado.get("data", {}).get("cliente") if resultado.get("data") else None

            if not cliente_data:
                logger.info(f"No se encontraron datos para {tipo_documento} {numero_documento}")
                return jsonify({
                    "success": True,
                    "message": "No se encontraron datos para el cliente especificado",
                    "timestamp": datetime.now().isoformat(),
                    "tipo_documento": tipo_documento,
                    "numero_documento": numero_documento,
                    "data": None,
                    "errors": None,
                    "execution_time_ms": execution_time_ms
                }), 404

            # Éxito - agregar metadatos adicionales
            resultado.update({
                "tipo_documento": tipo_documento,
                "numero_documento": numero_documento,
                "execution_time_ms": execution_time_ms
            })

            logger.info(f"Consulta exitosa para cliente: {tipo_documento} {numero_documento} en {execution_time_ms}ms")
            return jsonify(resultado), 200
        else:
            logger.error(f"Error en consulta para cliente: {tipo_documento} {numero_documento}")
            return jsonify({
                "success": False,
                "error": "Error interno al consultar el cliente",
                "timestamp": datetime.now().isoformat(),
                "tipo_documento": tipo_documento,
                "numero_documento": numero_documento,
                "data": None,
                "errors": "Internal server error - Unable to fetch client data",
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
            "tipo_documento": tipo_documento if 'tipo_documento' in locals() else None,
            "numero_documento": numero_documento if 'numero_documento' in locals() else None,
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
        "service": "Consulta Cliente API",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": "N/A",
        "environment": os.getenv('ENVIRONMENT', 'development')
    }), 200


@app.route('/api/v1/info', methods=['GET'])
@log_request
def api_info():
    """Endpoint con información de la API"""
    return jsonify({
        "name": "API de Consulta de Clientes",
        "version": "2.0.0",
        "description": "API para consultar información de clientes por tipo y número de documento usando Seguros Bolívar",
        "endpoints": {
            "POST /api/v1/clientes/consultar": "Consultar datos de un cliente por documento",
            "GET /api/v1/clientes/consultar": "Consultar datos de un cliente por parámetros",
            "GET /api/v1/health": "Verificación de salud del servicio",
            "GET /api/v1/info": "Información de la API"
        },
        "usage": {
            "method": "POST",
            "url": "/api/v1/clientes/consultar",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": {
                "tipoDocumento": "CC",
                "numeroDocumento": "1234567890"
            }
        },
        "valid_document_types": ["CC", "CE", "NIT", "PP", "TI", "RC", "CD"],
        "example_curl": "curl -X POST http://localhost:8080/api/v1/clientes/consultar -H 'Content-Type: application/json' -d '{\"tipoDocumento\": \"CC\", \"numeroDocumento\": \"1234567890\"}'",
        "example_get": "curl 'http://localhost:8080/api/v1/clientes/consultar?tipoDocumento=CC&numeroDocumento=1234567890'",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/', methods=['GET'])
@log_request
def root():
    """Endpoint raíz - redirige a info"""
    return jsonify({
        "message": "API de Consulta de Clientes - Seguros Bolívar",
        "version": "2.0.0",
        "documentation": "/api/v1/info",
        "health_check": "/api/v1/health",
        "main_endpoint": "/api/v1/clientes/consultar"
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Manejador para endpoints no encontrados"""
    return jsonify({
        "success": False,
        "error": "Endpoint no encontrado",
        "timestamp": datetime.now().isoformat(),
        "available_endpoints": [
            "POST /api/v1/clientes/consultar",
            "GET /api/v1/clientes/consultar",
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

    print("Iniciando API de Consulta de Clientes...")
    print(f"Host: {host}")
    print(f"Puerto: {port}")
    print(f"Debug: {debug}")

    # Ejecutar la aplicación
    app.run(
        host=host,
        port=port,
        debug=debug
    )