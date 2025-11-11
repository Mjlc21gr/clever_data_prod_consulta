import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConsultaVehiculoAPI:
    def __init__(self):
        # URLs de los endpoints (PRODUCCIÓN)
        self.auth_url = "https://api-conecta.segurosbolivar.com/prod/oauth2/token"
        self.graphql_url = "https://api-conecta.segurosbolivar.com/prod/api/dataops/graphql/cliente"

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
            logger.info("Obteniendo token de acceso para consulta de vehículos...")
            response = requests.post(self.auth_url, headers=headers, data=data, timeout=30)
            response.raise_for_status()

            token_data = response.json()
            logger.info("Token de acceso obtenido exitosamente")
            return token_data.get("access_token")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener token de acceso: {e}")
            return None

    def generar_query_graphql_vehiculo(self, placa: str) -> str:
        """
        Genera el query GraphQL para consultar un vehículo por placa.

        Args:
            placa (str): Placa del vehículo

        Returns:
            str: Query GraphQL completo
        """
        return f'''
        query Vehiculos {{
            vehiculos(placa: "{placa}") {{
                placa
                origenRegistro
                fechaRegistro
                organismoTransito
                declaracionImportacion
                prenda
                limitacion
                modelo
                color
                marca
                linea
                numeroMotor
                numeroChasis
                vin
                cilindraje
                numeroPasajeros
                codigoFasecolda
                claseVehiculo
                servicio
                uso
                tipo
                blindaje
                numeroFuente
                nombreFuente
                polizas {{
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
                    primaTotalSinImpuestos
                    impuestos
                    primaTotalConImpuestos
                    rol
                    pk
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
                riesgoEnPolizas {{
                    placa
                    numeroSecuenciaPoliza
                    numeroPoliza
                    sexoConductor
                    fechaNctoConductor
                    codigoProfesionConductor
                    nombreProfesionConductor
                    estadoCivilConductor
                    tipoDocumentoTomador
                    numeroDocumentoTomador
                    tipoDocumentoAsegurado
                    numeroDocumentoAsegurado
                    claveAgente
                    codigoOpcionAsistencia
                    codigoOpcionTarifa
                    codigoFasecolda
                    codigoMunicipioMovilizacion
                    nombreMunicipioMovilizacion
                    nombreDepartamenMovilizacion
                    codigoRiesgo
                    valorAsegurado
                    valorAseguradoAccesorios
                    valLimAseRceDanosYDos
                    limiteRcUna
                    limiteRcDos
                    limiteDanos
                    limiteRcUnaSuplementario
                    limiteRcDosSuplementario
                    limiteRcDanosSuplementario
                    deducRcExtraSmmlv
                    deducRcExtraPorcentaje
                    deducPtdSmmlv
                    deducPtdPorcentaje
                    deducPpfSmmlv
                    deducPpdPorcentaje
                    deducPthSmmlv
                    deducPthPorcentaje
                    deducPphSmmlv
                    deducPphPorcentaje
                    fechaProceso
                    vehiculo {{
                        placa
                        modelo
                        marca
                        linea
                        color
                        codigoFasecolda
                        claseVehiculo
                    }}
                }}
            }}
        }}
        '''

    def consultar_vehiculo_por_placa(self, placa: str) -> Optional[Dict[str, Any]]:
        """
        Consulta los datos de un vehículo por su placa.

        Args:
            placa (str): Placa del vehículo

        Returns:
            dict: Respuesta estructurada con los datos del vehículo
        """
        # Paso 1: Obtener token de acceso
        access_token = self.obtener_token_acceso()
        if not access_token:
            return None

        # Paso 2: Preparar la consulta GraphQL
        query = self.generar_query_graphql_vehiculo(placa)

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
            logger.info(f"Consultando vehículo con placa: {placa}")
            response = requests.post(self.graphql_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            graphql_data = response.json()
            logger.info("Consulta GraphQL de vehículo exitosa")

            # Paso 4: Estructurar los datos
            return self.estructurar_respuesta(graphql_data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error al consultar GraphQL para vehículo: {e}")
            if 'response' in locals():
                logger.error(f"Response status: {response.status_code}")
                try:
                    logger.error(f"Response body: {response.text}")
                except:
                    pass
            return None

    def estructurar_respuesta(self, graphql_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estructura la respuesta de la consulta de vehículos.

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
def consultar_vehiculo(placa: str) -> Optional[Dict[str, Any]]:
    """
    Función auxiliar para consultar un vehículo de forma rápida.

    Args:
        placa (str): Placa del vehículo

    Returns:
        dict: Respuesta con los datos del vehículo o None si hay error
    """
    api = ConsultaVehiculoAPI()
    return api.consultar_vehiculo_por_placa(placa)


if __name__ == "__main__":
    # Función principal para probar el script
    api = ConsultaVehiculoAPI()
    placa_ejemplo = "AAA000"  # Placa de ejemplo para testing

    print(f"Consultando datos para el vehículo con placa: {placa_ejemplo}")
    resultado = api.consultar_vehiculo_por_placa(placa_ejemplo)

    if resultado:
        print("Consulta exitosa!")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    else:
        print("Error en la consulta")