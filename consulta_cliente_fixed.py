import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConsultaClienteAPI:
    def __init__(self):
        # URLs de los endpoints (PRODUCCIÓN)
        self.auth_url = "https://api-conecta.segurosbolivar.com/prod/oauth2/token"
        self.graphql_url = "https://api-conecta.segurosbolivar.com/prod/dataops/graphql/cliente"

        # Credenciales para autenticación (PRODUCCIÓN)
        self.client_id = "16hs1d35ec86b9m6q7q13djhmi"
        self.client_secret = "1htj7f9sm197dorel8lhoikl845ph4gpf6tts2gmpr2um6935stj"

        # Headers para GraphQL
        self.user_key = "3673e3bd9d58483dad434d8cc059ed84"
        self.api_key = "SruptfIF0Z7S4kAp5j5kLPXzhwlOdWbt9lImnu30"

    def obtener_token_acceso(self) -> Optional[str]:
        """
        Obtiene el token de acceso usando las credenciales del cliente.

        Returns:
            str: Token de acceso si es exitoso, None si falla
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        try:
            logger.info("Obteniendo token de acceso...")
            response = requests.post(self.auth_url, headers=headers, data=data, timeout=30)
            response.raise_for_status()

            token_data = response.json()
            logger.info("Token de acceso obtenido exitosamente")
            return token_data.get("access_token")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener token de acceso: {e}")
            return None

    def generar_query_graphql(self, tipo_documento: str, numero_documento: str) -> str:
        """
        Genera el query GraphQL con el tipo y número de documento especificados.

        Args:
            tipo_documento (str): Tipo de documento del cliente (ej: "CC", "CE", "NIT", etc.)
            numero_documento (str): Número de documento del cliente

        Returns:
            str: Query GraphQL completo
        """
        return f'''
        query Cliente {{
            cliente(cliente: {{ tipoDocumento: "{tipo_documento}", numeroDocumento: {numero_documento} }}) {{
                tipoDocumento
                numeroDocumento
                tipoPersona
                nombreEmpresa
                estadoCliente
                nombreCompleto
                portafolioVigente {{
                    codigoRamoEmision
                    nombreRamoEmision
                    codigoProducto
                    nombreProducto
                    tipoDocumentoTomador
                    numeroDocumentoTomador
                    tipoDocumentoAsegurado
                    numeroDocumentoAsegurado
                    numeroSecuenciaPoliza
                    numeroPoliza
                    alturaPoliza
                    fechaInicioPoliza
                    fechaFinPoliza
                    maximoNumeroEndoso
                    primaTotal
                    valorAsegurado
                    estadoPoliza
                    claveAgente
                    codigoLocalidad
                    codigoCanal
                    rol
                    pk
                    beneficiarios {{
                        codigoCompania
                        codigoRamoEmision
                        nombreRamoEmision
                        codigoProducto
                        nombreProducto
                        codigoSubproducto
                        nombreSubproducto
                        claveAgente
                        nombreAgente
                        codigoLocalidad
                        nombreLocalidad
                        codigoCanal
                        nombreCanal
                        numeroPoliza
                        fechaInicioPoliza
                        fechaFinPoliza
                        numeroDocumentoTomador
                        tipoDocumentoTomador
                        codigoRiesgo
                        numeroDocumentoAsegurado
                        tipoDocumentoAsegurado
                        numeroDocumentoBeneficiario
                        tipoDocumentoBeneficiario
                        fechaCorte
                        apellidosBeneficiario
                        nombresBeneficiario
                        porcentaje
                        parentesco
                        calidad
                    }}
                    deducible {{
                        codigoProducto
                        deducible
                        plan
                    }}
                    coberturas {{
                        codigoCompania
                        codigoRamoEmision
                        codigoProducto
                        numeroSecuenciaPoliza
                        numeroPoliza
                        codigoRamoContable
                        codigoRiesgo
                        codigoCobertura
                        primaEmitida
                        primaAnual
                        fechaInicioEndoso
                        fechaFinEndoso
                        maximoNumeroEndoso
                        numeroEndosoCreacion
                        numeroEndosoMaxPoliza
                        numeroDocumentoAsegurado
                        tipoDocumentoAsegurado
                        valorAsegurado
                        periodoFacturacion
                        medioPago
                        tipoMedioPago
                        moneda
                        tasaCambio
                        claveAgente
                        nombreAgente
                        codigoLocalidad
                        nombreLocalidad
                        codigoCanal
                        nombreCanal
                        codigoSubproducto
                        nombreSubproducto
                    }}
                    asistencias {{
                        fechaAsistencia
                        numeroAsistencia
                        estadoAsistencia
                        descEstadoAsistencia
                        totalValorAPagar
                        numeroPoliza
                        nombreRamoEmision
                        descRamo
                        descProducto
                        codigoProducto
                        tipoAsistencia
                        tipoDocumentoCliente
                        documentoCliente
                        tipoDocumentoAsegurado
                        numeroDocumentoAsegurado
                        numeroSiniestroAseguradora
                        tipoDocumentoTomador
                        numeroDocumentoTomador
                        cantidadRiesgos
                        envioCorreoAsistencia
                        tipoLlamada
                    }}
                    siniestros {{
                        tipoDocumentoAsegurado
                        numeroDocumentoAsegurado
                        tipoDocumentoTomador
                        numeroDocumentoTomador
                        numeroSecuenciaPoliza
                        numeroPoliza
                        codigoRamoEmision
                        nombreRamoEmision
                        codigoProducto
                        nombreProducto
                        numeroSiniestro
                        estadoSiniestro
                        fechaSiniestro
                        fechaAviso
                        descripcionCausa
                        descripcionSiniestro
                        coberturasAfectadas
                        estadoSiniestroCalculado
                        totalIncurridoBolivar
                        totalLiquidadoBolivar
                    }}
                }}
                demografica {{
                    sexo
                    fechaNacimiento
                    estratoSocial
                    nacionalidad
                    direccion
                    municipio
                    departamento
                    edad
                }}
                siniestros {{
                    tipoDocumentoAsegurado
                    numeroDocumentoAsegurado
                    tipoDocumentoTomador
                    numeroDocumentoTomador
                    numeroSecuenciaPoliza
                    numeroPoliza
                    codigoRamoEmision
                    nombreRamoEmision
                    codigoProducto
                    nombreProducto
                    numeroSiniestro
                    estadoSiniestro
                    fechaSiniestro
                    fechaAviso
                    descripcionCausa
                    descripcionSiniestro
                    coberturasAfectadas
                    estadoSiniestroCalculado
                    totalIncurridoBolivar
                    totalLiquidadoBolivar
                }}
                asistencias {{
                    fechaAsistencia
                    numeroAsistencia
                    estadoAsistencia
                    descEstadoAsistencia
                    totalValorAPagar
                    numeroPoliza
                    nombreRamoEmision
                    descRamo
                    descProducto
                    codigoProducto
                    tipoAsistencia
                    tipoDocumentoCliente
                    documentoCliente
                    tipoDocumentoAsegurado
                    numeroDocumentoAsegurado
                    numeroSiniestroAseguradora
                    tipoDocumentoTomador
                    numeroDocumentoTomador
                    cantidadRiesgos
                    envioCorreoAsistencia
                    tipoLlamada
                }}
            }}
        }}
        '''

    def consultar_cliente_por_documento(self, tipo_documento: str, numero_documento: str) -> Optional[Dict[str, Any]]:
        """
        Consulta los datos de un cliente por su tipo y número de documento.

        Args:
            tipo_documento (str): Tipo de documento del cliente (ej: "CC", "CE", "NIT", etc.)
            numero_documento (str): Número de documento del cliente

        Returns:
            dict: Respuesta estructurada con los datos del cliente
        """
        # Paso 1: Obtener token de acceso
        access_token = self.obtener_token_acceso()
        if not access_token:
            return None

        # Paso 2: Preparar la consulta GraphQL
        query = self.generar_query_graphql(tipo_documento, numero_documento)

        headers = {
            "Authorization": f"Bearer {access_token}",
            "x-user-key": self.user_key,
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "query": query
        }

        try:
            # Paso 3: Realizar consulta GraphQL
            logger.info(f"Consultando cliente: {tipo_documento} {numero_documento}")
            response = requests.post(self.graphql_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            graphql_data = response.json()
            logger.info("Consulta GraphQL exitosa")

            # Paso 4: Estructurar los datos
            return self.estructurar_respuesta(graphql_data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error al consultar GraphQL: {e}")
            if 'response' in locals():
                logger.error(f"Response status: {response.status_code}")
                try:
                    logger.error(f"Response body: {response.text}")
                except:
                    pass
            return None

    def estructurar_respuesta(self, graphql_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estructura la respuesta como lo hace el nodo Code en n8n.

        Args:
            graphql_data (dict): Datos crudos de GraphQL

        Returns:
            dict: Respuesta estructurada
        """
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "data": graphql_data.get("data"),
            "errors": graphql_data.get("errors")
        }


# Función auxiliar para uso en la API
def consultar_cliente(tipo_documento: str, numero_documento: str) -> Optional[Dict[str, Any]]:
    """
    Función auxiliar para consultar un cliente de forma rápida.

    Args:
        tipo_documento (str): Tipo de documento (CC, CE, NIT, etc.)
        numero_documento (str): Número de documento

    Returns:
        dict: Respuesta con los datos del cliente o None si hay error
    """
    api = ConsultaClienteAPI()
    return api.consultar_cliente_por_documento(tipo_documento, numero_documento)


if __name__ == "__main__":
    # Función principal para probar el script
    api = ConsultaClienteAPI()
    tipo_documento_ejemplo = "CC"
    numero_documento_ejemplo = "12345678"  # Documento de ejemplo para testing

    print(f"Consultando datos para el cliente: {tipo_documento_ejemplo} {numero_documento_ejemplo}")
    resultado = api.consultar_cliente_por_documento(tipo_documento_ejemplo, numero_documento_ejemplo)

    if resultado:
        print("Consulta exitosa!")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    else:
        print("Error en la consulta")