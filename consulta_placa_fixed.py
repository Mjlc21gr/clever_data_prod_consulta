import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional


class ConsultaPlacaAPI:
    def __init__(self):
        # URLs de los endpoints
        self.auth_url = "https://conecta-stg-portal-auth.auth.us-east-1.amazoncognito.com/oauth2/token"
        self.graphql_url = "https://stg-api-conecta.segurosbolivar.com/stage/api/dataops/graphql/cliente"

        # Credenciales para autenticación
        self.client_id = "4otakrqfu0p38n90qr25m0cq4i"
        self.client_secret = "27hqt7jo60le5rnr91ei3ohgjranaq0c7ebm7038mc91nrfqca6"

        # Headers para GraphQL
        self.user_key = "4ece6db2dff1462a99e3164eb53e7049"
        self.api_key = "dNNSjqadzQaozr285maNg2w9q4hkZ5GT4YsiK60v"

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
            response = requests.post(self.auth_url, headers=headers, data=data)
            response.raise_for_status()

            token_data = response.json()
            return token_data.get("access_token")

        except requests.exceptions.RequestException as e:
            print(f"Error al obtener token de acceso: {e}")
            return None

    def generar_query_graphql(self, placa: str) -> str:
        """
        Genera el query GraphQL con la placa especificada.

        Args:
            placa (str): Placa del vehículo

        Returns:
            str: Query GraphQL completo
        """
        return f'''
        query Cliente {{
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
                    coberturas {{
                        codigoCompania
                        codigoRamoEmision
                        codigoProducto
                        numeroSecuenciaPoliza
                        numeroPoliza
                        codigoRamoContable
                        codigoRiesgo
                        codigoCobertura
                        nombreCobertura
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
                    deducible {{
                        codigoProducto
                        deducible
                        plan
                    }}
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
                }}
            }}
        }}
        '''

    def consultar_vehiculo_por_placa(self, placa: str) -> Optional[Dict[str, Any]]:
        """
        Consulta los datos de un vehículo por su placa.

        Args:
            placa (str): Placa del vehículo a consultar

        Returns:
            dict: Respuesta estructurada con los datos del vehículo
        """
        # Paso 1: Obtener token de acceso
        access_token = self.obtener_token_acceso()
        if not access_token:
            return None

        # Paso 2: Preparar la consulta GraphQL
        query = self.generar_query_graphql(placa)

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
            response = requests.post(self.graphql_url, headers=headers, json=payload)
            response.raise_for_status()

            graphql_data = response.json()

            # Paso 4: Estructurar los datos (como hace el nodo Code en n8n)
            return self.estructurar_respuesta(graphql_data)

        except requests.exceptions.RequestException as e:
            print(f"Error al consultar GraphQL: {e}")
            print(f"Response status: {response.status_code if 'response' in locals() else 'No response'}")
            if 'response' in locals():
                try:
                    print(f"Response body: {response.text}")
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


if __name__ == "__main__":
    # Función principal para probar el script
    api = ConsultaPlacaAPI()
    placa_ejemplo = "AAA000"

    print(f"Consultando datos para la placa: {placa_ejemplo}")
    resultado = api.consultar_vehiculo_por_placa(placa_ejemplo)

    if resultado:
        print("Consulta exitosa!")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    else:
        print("Error en la consulta")
