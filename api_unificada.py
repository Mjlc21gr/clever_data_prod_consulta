#!/usr/bin/env python3
"""
API REST unificada para consulta de clientes y vehículos - Seguros Bolívar
Optimizada para producción con detección automática de tipo de consulta
"""

from flask import Flask, request, jsonify
from consulta_cliente_fixed import ConsultaClienteAPI
from consulta_vehiculo import ConsultaVehiculoAPI
import logging
import os
import re
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

# Instancias globales de las APIs
api_cliente = ConsultaClienteAPI()
api_vehiculo = ConsultaVehiculoAPI()


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


def detectar_tipo_consulta(data):
    """
    Detecta automáticamente si la consulta es por documento de cliente o placa de vehículo.

    Args:
        data (dict): Datos del request

    Returns:
        tuple: (tipo, parametros_normalizados)
        - tipo: 'cliente' o 'vehiculo'
        - parametros_normalizados: dict con los parámetros listos para usar
    """
    # Verificar si es consulta por placa
    if 'placa' in data:
        placa = str(data['placa']).strip().upper()
        return 'vehiculo', {'placa': placa}

    # Verificar si es consulta por documento de cliente
    if 'tipoDocumento' in data and 'numeroDocumento' in data:
        tipo_documento = str(data['tipoDocumento']).strip().upper()
        numero_documento = str(data['numeroDocumento']).strip()
        return 'cliente', {
            'tipoDocumento': tipo_documento,
            'numeroDocumento': numero_documento
        }

    # Intento de detección automática por patrones
    # Si solo hay un campo de texto, intentar detectar si es placa o documento
    if len(data) == 1:
        key, value = next(iter(data.items()))
        value_str = str(value).strip().upper()

        # Patrón típico de placa colombiana (3 letras + 3 números, o variantes)
        placa_pattern = re.compile(r'^[A-Z]{3}\d{2,3}[A-Z]?$|^[A-Z]{2,3}\d{2,4}$')

        if placa_pattern.match(value_str):
            return 'vehiculo', {'placa': value_str}
        elif value_str.isdigit() and len(value_str) >= 6:
            # Probablemente un número de documento
            return 'cliente', {
                'tipoDocumento': 'CC',  # Asumir CC por defecto
                'numeroDocumento': value_str
            }

    return None, None


def validate_parametros_cliente(tipo_documento, numero_documento):
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

    tipo_clean = tipo_documento.strip().upper()
    numero_clean = numero_documento.strip()

    # Validar tipos de documento válidos
    tipos_validos = ['CC', 'CE', 'NT', 'PP', 'TI', 'RC', 'CD']
    if tipo_clean not in tipos_validos:
        return False, f"Tipo de documento no válido. Tipos válidos: {', '.join(tipos_validos)}"

    if len(numero_clean) < 3:
        return False, "El número de documento debe tener al menos 3 caracteres"

    if len(numero_clean) > 20:
        return False, "El número de documento no puede tener más de 20 caracteres"

    return True, None


def validate_parametros_vehiculo(placa):
    """
    Valida el formato de la placa

    Args:
        placa (str): Placa a validar

    Returns:
        tuple: (is_valid, error_message)
    """
    if not placa:
        return False, "La placa es requerida"

    placa_clean = placa.strip().upper()

    if len(placa_clean) < 6 or len(placa_clean) > 7:
        return False, "La placa debe tener entre 6 y 7 caracteres"

    # Validación básica de formato de placa
    placa_pattern = re.compile(r'^[A-Z0-9]{6,7}$')
    if not placa_pattern.match(placa_clean):
        return False, "La placa debe contener solo letras y números"

    return True, None


@app.route('/api/v1/clientes/consultar', methods=['POST'])
@log_request
def consultar_unificado():
    """
    Endpoint unificado para consultar datos por documento de cliente o placa de vehículo.
    Detecta automáticamente el tipo de consulta basado en los parámetros enviados.

    Body JSON esperado (cliente):
    {
        "tipoDocumento": "CC",
        "numeroDocumento": "1234567890"
    }

    Body JSON esperado (vehículo):
    {
        "placa": "ABC123"
    }

    Body JSON esperado (detección automática):
    {
        "consulta": "ABC123"  // Se detecta automáticamente si es placa o documento
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
                "data": None,
                "errors": "Empty or invalid JSON body",
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }), 400

        # Detectar tipo de consulta
        tipo_consulta, parametros = detectar_tipo_consulta(data)

        if not tipo_consulta:
            return jsonify({
                "success": False,
                "error": "No se pudo detectar el tipo de consulta. Envíe 'tipoDocumento' y 'numeroDocumento' para cliente, o 'placa' para vehículo",
                "timestamp": datetime.now().isoformat(),
                "data": None,
                "errors": "Unable to detect query type",
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }), 400

        logger.info(f"Tipo de consulta detectado: {tipo_consulta}")
        logger.info(f"Parámetros: {parametros}")

        # Procesar según el tipo de consulta
        if tipo_consulta == 'cliente':
            return procesar_consulta_cliente(parametros, start_time)
        elif tipo_consulta == 'vehiculo':
            return procesar_consulta_vehiculo(parametros, start_time)
        else:
            return jsonify({
                "success": False,
                "error": "Tipo de consulta no válido",
                "timestamp": datetime.now().isoformat(),
                "data": None,
                "errors": "Invalid query type",
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }), 400

    except Exception as e:
        execution_time_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Error inesperado: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        return jsonify({
            "success": False,
            "error": f"Error inesperado del servidor: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "data": None,
            "errors": str(e),
            "execution_time_ms": execution_time_ms
        }), 500


def procesar_consulta_cliente(parametros, start_time):
    """Procesa una consulta de cliente"""
    tipo_documento = parametros['tipoDocumento']
    numero_documento = parametros['numeroDocumento']

    # Validar parámetros
    is_valid, error_message = validate_parametros_cliente(tipo_documento, numero_documento)
    if not is_valid:
        return jsonify({
            "success": False,
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
            "tipo_consulta": "cliente",
            "tipo_documento": tipo_documento,
            "numero_documento": numero_documento,
            "data": None,
            "errors": error_message,
            "execution_time_ms": int((time.time() - start_time) * 1000)
        }), 400

    logger.info(f"Consultando cliente: {tipo_documento} {numero_documento}")

    # Realizar la consulta
    resultado = api_cliente.consultar_cliente_por_documento(tipo_documento, numero_documento)

    execution_time_ms = int((time.time() - start_time) * 1000)

    if resultado:
        # Verificar si se encontraron datos del cliente
        cliente_data = resultado.get("data", {}).get("cliente") if resultado.get("data") else None

        if not cliente_data:
            logger.info(f"No se encontraron datos para cliente {tipo_documento} {numero_documento}")
            return jsonify({
                "success": True,
                "message": "No se encontraron datos para el cliente especificado",
                "timestamp": datetime.now().isoformat(),
                "tipo_consulta": "cliente",
                "tipo_documento": tipo_documento,
                "numero_documento": numero_documento,
                "data": None,
                "errors": None,
                "execution_time_ms": execution_time_ms
            }), 404

        # Éxito - agregar metadatos adicionales
        resultado.update({
            "tipo_consulta": "cliente",
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
            "tipo_consulta": "cliente",
            "tipo_documento": tipo_documento,
            "numero_documento": numero_documento,
            "data": None,
            "errors": "Internal server error - Unable to fetch client data",
            "execution_time_ms": execution_time_ms
        }), 500


def procesar_consulta_vehiculo(parametros, start_time):
    """Procesa una consulta de vehículo"""
    placa = parametros['placa']

    # Validar parámetros
    is_valid, error_message = validate_parametros_vehiculo(placa)
    if not is_valid:
        return jsonify({
            "success": False,
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
            "tipo_consulta": "vehiculo",
            "placa": placa,
            "data": None,
            "errors": error_message,
            "execution_time_ms": int((time.time() - start_time) * 1000)
        }), 400

    logger.info(f"Consultando vehículo: {placa}")

    # Realizar la consulta
    resultado = api_vehiculo.consultar_vehiculo_por_placa(placa)

    execution_time_ms = int((time.time() - start_time) * 1000)

    if resultado:
        # Verificar si se encontraron datos del vehículo
        vehiculo_data = resultado.get("data", {}).get("vehiculos") if resultado.get("data") else None

        if not vehiculo_data:
            logger.info(f"No se encontraron datos para vehículo {placa}")
            return jsonify({
                "success": True,
                "message": "No se encontraron datos para el vehículo especificado",
                "timestamp": datetime.now().isoformat(),
                "tipo_consulta": "vehiculo",
                "placa": placa,
                "data": None,
                "errors": None,
                "execution_time_ms": execution_time_ms
            }), 404

        # Éxito - agregar metadatos adicionales
        resultado.update({
            "tipo_consulta": "vehiculo",
            "placa": placa,
            "execution_time_ms": execution_time_ms
        })

        logger.info(f"Consulta exitosa para vehículo: {placa} en {execution_time_ms}ms")
        return jsonify(resultado), 200
    else:
        logger.error(f"Error en consulta para vehículo: {placa}")
        return jsonify({
            "success": False,
            "error": "Error interno al consultar el vehículo",
            "timestamp": datetime.now().isoformat(),
            "tipo_consulta": "vehiculo",
            "placa": placa,
            "data": None,
            "errors": "Internal server error - Unable to fetch vehicle data",
            "execution_time_ms": execution_time_ms
        }), 500


@app.route('/api/v1/clientes/consultar', methods=['GET'])
@log_request
def consultar_unificado_get():
    """
    Endpoint GET unificado para consultar por parámetros de query

    Parámetros para cliente:
    - tipoDocumento: Tipo de documento (CC, CE, NIT, etc.)
    - numeroDocumento: Número de documento

    Parámetros para vehículo:
    - placa: Placa del vehículo
    """
    start_time = time.time()

    try:
        # Obtener todos los parámetros
        params = dict(request.args)

        # Detectar tipo de consulta
        tipo_consulta, parametros = detectar_tipo_consulta(params)

        if not tipo_consulta:
            return jsonify({
                "success": False,
                "error": "Parámetros inválidos. Use 'tipoDocumento' y 'numeroDocumento' para cliente, o 'placa' para vehículo",
                "timestamp": datetime.now().isoformat(),
                "data": None,
                "errors": "Invalid parameters",
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }), 400

        logger.info(f"Tipo de consulta GET detectado: {tipo_consulta}")

        # Procesar según el tipo de consulta
        if tipo_consulta == 'cliente':
            return procesar_consulta_cliente(parametros, start_time)
        elif tipo_consulta == 'vehiculo':
            return procesar_consulta_vehiculo(parametros, start_time)
        else:
            return jsonify({
                "success": False,
                "error": "Tipo de consulta no válido",
                "timestamp": datetime.now().isoformat(),
                "data": None,
                "errors": "Invalid query type",
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }), 400

    except Exception as e:
        execution_time_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Error inesperado: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        return jsonify({
            "success": False,
            "error": f"Error inesperado del servidor: {str(e)}",
            "timestamp": datetime.now().isoformat(),
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
        "service": "Consulta Unificada API",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": "N/A",
        "environment": os.getenv('ENVIRONMENT', 'development'),
        "features": ["consulta_clientes", "consulta_vehiculos", "deteccion_automatica"]
    }), 200


@app.route('/api/v1/info', methods=['GET'])
@log_request
def api_info():
    """Endpoint con información de la API"""
    return jsonify({
        "name": "API Unificada de Consultas - Seguros Bolívar",
        "version": "3.0.0",
        "description": "API unificada para consultar información de clientes por documento y vehículos por placa con detección automática",
        "endpoints": {
            "POST /api/v1/clientes/consultar": "Consultar datos con detección automática",
            "GET /api/v1/clientes/consultar": "Consultar datos por parámetros",
            "GET /api/v1/health": "Verificación de salud del servicio",
            "GET /api/v1/info": "Información de la API"
        },
        "usage": {
            "cliente": {
                "method": "POST",
                "url": "/api/v1/clientes/consultar",
                "headers": {"Content-Type": "application/json"},
                "body": {
                    "tipoDocumento": "CC",
                    "numeroDocumento": "1234567890"
                }
            },
            "vehiculo": {
                "method": "POST",
                "url": "/api/v1/clientes/consultar",
                "headers": {"Content-Type": "application/json"},
                "body": {
                    "placa": "ABC123"
                }
            }
        },
        "valid_document_types": ["CC", "CE", "NIT", "PP", "TI", "RC", "CD"],
        "examples": {
            "curl_cliente": "curl -X POST https://tu-api.com/api/v1/clientes/consultar -H 'Content-Type: application/json' -d '{\"tipoDocumento\": \"CC\", \"numeroDocumento\": \"1234567890\"}'",
            "curl_vehiculo": "curl -X POST https://tu-api.com/api/v1/clientes/consultar -H 'Content-Type: application/json' -d '{\"placa\": \"ABC123\"}'",
            "get_cliente": "curl 'https://tu-api.com/api/v1/clientes/consultar?tipoDocumento=CC&numeroDocumento=1234567890'",
            "get_vehiculo": "curl 'https://tu-api.com/api/v1/clientes/consultar?placa=ABC123'"
        },
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/', methods=['GET'])
@log_request
def root():
    """Endpoint raíz - redirige a info"""
    return jsonify({
        "message": "API Unificada de Consultas - Seguros Bolívar",
        "version": "3.0.0",
        "documentation": "/api/v1/info",
        "health_check": "/api/v1/health",
        "main_endpoint": "/api/v1/clientes/consultar",
        "features": [
            "Consulta de clientes por documento",
            "Consulta de vehículos por placa",
            "Detección automática del tipo de consulta"
        ]
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

    print("Iniciando API Unificada de Consultas...")
    print(f"Host: {host}")
    print(f"Puerto: {port}")
    print(f"Debug: {debug}")
    print("Características:")
    print("  ✓ Consulta de clientes por documento")
    print("  ✓ Consulta de vehículos por placa")
    print("  ✓ Detección automática del tipo de consulta")

    # Ejecutar la aplicación
    app.run(
        host=host,
        port=port,
        debug=debug
    )