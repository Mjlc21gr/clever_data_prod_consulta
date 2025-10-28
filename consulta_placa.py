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


def main():
    """Función principal para probar el script"""
    # Crear instancia de la API
    api = ConsultaPlacaAPI()

    # Ejemplo de uso - cambiar por una placa real
    placa_ejemplo = "AAA000"  # Usar la placa que mencionaste

    print(f"Consultando datos para la placa: {placa_ejemplo}")
    resultado = api.consultar_vehiculo_por_placa(placa_ejemplo)

    if resultado:
        print("✅ Consulta exitosa!")
        print("=" * 80)

        # Mostrar información básica
        vehiculos = resultado.get("data", {}).get("vehiculos", []) if resultado.get("data") else []

        if vehiculos:
            vehiculo = vehiculos[0]

            # INFORMACIÓN BÁSICA DEL VEHÍCULO
            print("🚗 INFORMACIÓN BÁSICA DEL VEHÍCULO")
            print("-" * 50)
            print(f"   Placa: {vehiculo.get('placa', 'N/A')}")
            print(f"   Marca: {vehiculo.get('marca', 'N/A')}")
            print(f"   Línea: {vehiculo.get('linea', 'N/A')}")
            print(f"   Modelo: {vehiculo.get('modelo', 'N/A')}")
            print(f"   Color: {vehiculo.get('color', 'N/A')}")
            print(f"   Servicio: {vehiculo.get('servicio', 'N/A')}")
            print(f"   Uso: {vehiculo.get('uso', 'N/A')}")
            print(f"   Tipo: {vehiculo.get('tipo', 'N/A')}")
            print(f"   Clase Vehículo: {vehiculo.get('claseVehiculo', 'N/A')}")
            print(f"   Cilindraje: {vehiculo.get('cilindraje', 'N/A')}")
            print(f"   Número Pasajeros: {vehiculo.get('numeroPasajeros', 'N/A')}")
            print(f"   Número Motor: {vehiculo.get('numeroMotor', 'N/A')}")
            print(f"   Número Chasis: {vehiculo.get('numeroChasis', 'N/A')}")
            print(f"   VIN: {vehiculo.get('vin', 'N/A')}")
            print(f"   Código Fasecolda: {vehiculo.get('codigoFasecolda', 'N/A')}")
            print(f"   Origen Registro: {vehiculo.get('origenRegistro', 'N/A')}")
            print(f"   Fecha Registro: {vehiculo.get('fechaRegistro', 'N/A')}")
            print(f"   Organismo Tránsito: {vehiculo.get('organismoTransito', 'N/A')}")
            print(f"   Declaración Importación: {vehiculo.get('declaracionImportacion', 'N/A')}")
            print(f"   Prenda: {vehiculo.get('prenda', 'N/A')}")
            print(f"   Limitación: {vehiculo.get('limitacion', 'N/A')}")
            print(f"   Blindaje: {vehiculo.get('blindaje', 'N/A')}")
            print(f"   Número Fuente: {vehiculo.get('numeroFuente', 'N/A')}")
            print(f"   Nombre Fuente: {vehiculo.get('nombreFuente', 'N/A')}")

            # PÓLIZAS
            polizas = vehiculo.get('polizas', [])
            print(f"\n📋 PÓLIZAS ({len(polizas)} encontradas)")
            print("-" * 50)

            for i, poliza in enumerate(polizas, 1):
                print(f"\n   📄 PÓLIZA {i}:")
                print(f"      Número Póliza: {poliza.get('numeroPoliza', 'N/A')}")
                print(f"      Producto: {poliza.get('nombreProducto', 'N/A')} ({poliza.get('codigoProducto', 'N/A')})")
                print(
                    f"      Ramo: {poliza.get('nombreRamoEmision', 'N/A')} ({poliza.get('codigoRamoEmision', 'N/A')})")
                print(f"      Estado: {poliza.get('estadoPoliza', 'N/A')}")
                print(f"      Fecha Inicio: {poliza.get('fechaInicioPoliza', 'N/A')}")
                print(f"      Fecha Fin: {poliza.get('fechaFinPoliza', 'N/A')}")
                print(f"      Prima Total: {poliza.get('primaTotal', 'N/A')}")
                print(f"      Valor Asegurado: {poliza.get('valorAsegurado', 'N/A')}")
                print(
                    f"      Tomador: {poliza.get('tipoDocumentoTomador', 'N/A')} {poliza.get('numeroDocumentoTomador', 'N/A')}")
                print(
                    f"      Asegurado: {poliza.get('tipoDocumentoAsegurado', 'N/A')} {poliza.get('numeroDocumentoAsegurado', 'N/A')}")
                print(f"      Agente: {poliza.get('claveAgente', 'N/A')}")
                print(f"      Canal: {poliza.get('codigoCanal', 'N/A')}")
                print(f"      Localidad: {poliza.get('codigoLocalidad', 'N/A')}")

                # Siniestros de esta póliza
                siniestros_poliza = poliza.get('siniestros', [])
                if siniestros_poliza:
                    print(f"\n      🚨 SINIESTROS EN ESTA PÓLIZA ({len(siniestros_poliza)}):")
                    for j, siniestro in enumerate(siniestros_poliza, 1):
                        print(f"         Siniestro {j}: {siniestro.get('numeroSiniestro', 'N/A')}")
                        print(f"         Estado: {siniestro.get('estadoSiniestro', 'N/A')}")
                        print(f"         Fecha: {siniestro.get('fechaSiniestro', 'N/A')}")
                        print(f"         Causa: {siniestro.get('descripcionCausa', 'N/A')}")
                        print(f"         Total Incurrido: {siniestro.get('totalIncurridoBolivar', 'N/A')}")
                        print(f"         Total Liquidado: {siniestro.get('totalLiquidadoBolivar', 'N/A')}")

                # Asistencias de esta póliza
                asistencias = poliza.get('asistencias', [])
                if asistencias:
                    print(f"\n      🆘 ASISTENCIAS EN ESTA PÓLIZA ({len(asistencias)}):")
                    for j, asistencia in enumerate(asistencias, 1):
                        print(f"         Asistencia {j}: {asistencia.get('numeroAsistencia', 'N/A')}")
                        print(
                            f"         Estado: {asistencia.get('estadoAsistencia', 'N/A')} - {asistencia.get('descEstadoAsistencia', 'N/A')}")
                        print(f"         Fecha: {asistencia.get('fechaAsistencia', 'N/A')}")
                        print(f"         Tipo: {asistencia.get('tipoAsistencia', 'N/A')}")
                        print(f"         Valor a Pagar: {asistencia.get('totalValorAPagar', 'N/A')}")

                # Coberturas de esta póliza
                coberturas = poliza.get('coberturas', [])
                if coberturas:
                    print(f"\n      🛡️ COBERTURAS EN ESTA PÓLIZA ({len(coberturas)}):")
                    for j, cobertura in enumerate(coberturas, 1):
                        print(
                            f"         Cobertura {j}: {cobertura.get('nombreCobertura', 'N/A')} ({cobertura.get('codigoCobertura', 'N/A')})")
                        print(f"         Prima Emitida: {cobertura.get('primaEmitida', 'N/A')}")
                        print(f"         Prima Anual: {cobertura.get('primaAnual', 'N/A')}")
                        print(f"         Valor Asegurado: {cobertura.get('valorAsegurado', 'N/A')}")

                # Deducibles
                deducibles = poliza.get('deducible', [])
                if deducibles:
                    print(f"\n      💰 DEDUCIBLES:")
                    for deducible in deducibles:
                        print(f"         Plan: {deducible.get('plan', 'N/A')}")
                        print(f"         Deducible: {deducible.get('deducible', 'N/A')}")

                # Beneficiarios
                beneficiarios = poliza.get('beneficiarios', [])
                if beneficiarios:
                    print(f"\n      👥 BENEFICIARIOS ({len(beneficiarios)}):")
                    for j, beneficiario in enumerate(beneficiarios, 1):
                        print(
                            f"         Beneficiario {j}: {beneficiario.get('nombresBeneficiario', 'N/A')} {beneficiario.get('apellidosBeneficiario', 'N/A')}")
                        print(
                            f"         Documento: {beneficiario.get('tipoDocumentoBeneficiario', 'N/A')} {beneficiario.get('numeroDocumentoBeneficiario', 'N/A')}")
                        print(f"         Porcentaje: {beneficiario.get('porcentaje', 'N/A')}%")
                        print(f"         Parentesco: {beneficiario.get('parentesco', 'N/A')}")

            # SINIESTROS GENERALES (fuera de pólizas específicas)
            siniestros_generales = vehiculo.get('siniestros', [])
            if siniestros_generales:
                print(f"\n🚨 SINIESTROS GENERALES ({len(siniestros_generales)})")
                print("-" * 50)
                for i, siniestro in enumerate(siniestros_generales, 1):
                    print(f"\n   Siniestro {i}:")
                    print(f"      Número: {siniestro.get('numeroSiniestro', 'N/A')}")
                    print(f"      Estado: {siniestro.get('estadoSiniestro', 'N/A')}")
                    print(f"      Fecha Siniestro: {siniestro.get('fechaSiniestro', 'N/A')}")
                    print(f"      Fecha Aviso: {siniestro.get('fechaAviso', 'N/A')}")
                    print(f"      Causa: {siniestro.get('descripcionCausa', 'N/A')}")
                    print(f"      Descripción: {siniestro.get('descripcionSiniestro', 'N/A')}")
                    print(f"      Coberturas Afectadas: {siniestro.get('coberturasAfectadas', 'N/A')}")
                    print(f"      Total Incurrido: {siniestro.get('totalIncurridoBolivar', 'N/A')}")
                    print(f"      Total Liquidado: {siniestro.get('totalLiquidadoBolivar', 'N/A')}")
                    print(f"      Póliza: {siniestro.get('numeroPoliza', 'N/A')}")
                    print(f"      Producto: {siniestro.get('nombreProducto', 'N/A')}")

            # RIESGOS EN PÓLIZAS
            riesgos = vehiculo.get('riesgoEnPolizas', [])
            if riesgos:
                print(f"\n⚠️ RIESGOS EN PÓLIZAS ({len(riesgos)})")
                print("-" * 50)
                for i, riesgo in enumerate(riesgos, 1):
                    print(f"\n   Riesgo {i}:")
                    print(f"      Póliza: {riesgo.get('numeroPoliza', 'N/A')}")
                    print(f"      Conductor - Sexo: {riesgo.get('sexoConductor', 'N/A')}")
                    print(f"      Conductor - Fecha Nacimiento: {riesgo.get('fechaNctoConductor', 'N/A')}")
                    print(
                        f"      Conductor - Profesión: {riesgo.get('nombreProfesionConductor', 'N/A')} ({riesgo.get('codigoProfesionConductor', 'N/A')})")
                    print(f"      Conductor - Estado Civil: {riesgo.get('estadoCivilConductor', 'N/A')}")
                    print(f"      Municipio Movilización: {riesgo.get('nombreMunicipioMovilizacion', 'N/A')}")
                    print(f"      Departamento Movilización: {riesgo.get('nombreDepartamenMovilizacion', 'N/A')}")
                    print(f"      Valor Asegurado: {riesgo.get('valorAsegurado', 'N/A')}")
                    print(f"      Valor Asegurado Accesorios: {riesgo.get('valorAseguradoAccesorios', 'N/A')}")
                    print(f"      Límite RC Una: {riesgo.get('limiteRcUna', 'N/A')}")
                    print(f"      Límite RC Dos: {riesgo.get('limiteRcDos', 'N/A')}")
                    print(f"      Límite Daños: {riesgo.get('limiteDanos', 'N/A')}")

            # Guardar resultado completo
            with open(f'resultado_{placa_ejemplo}.json', 'w', encoding='utf-8') as f:
                json.dump(resultado, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resultado completo guardado en: resultado_{placa_ejemplo}.json")
        else:
            print("❌ No se encontraron vehículos con esa placa")

        # Mostrar errores si los hay
        if resultado.get("errors"):
            print(f"\n⚠️ Errores en la consulta: {resultado['errors']}")

        print("=" * 80)
    else:
        print("❌ Error en la consulta")


if __name__ == "__main__":
    main()