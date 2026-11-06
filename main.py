"""Composition Root: selecciona tecnologías, instancia e inyecta dependencias."""
import os

from aplicacion.casos_uso import CasoDeUsoConsultarFactura, CasoDeUsoCrearFactura
from dominio.control_fraude import ControlFraude
from dominio.politica_fiscal import PoliticaFiscal
from dominio.repositorio_facturas import IRepositorioFacturas
from infraestructura.repositorios import RepositorioOracleSimulado, RepositorioPostgreSQLSimulado
from presentacion.api_rest import ControladorFacturasREST, crear_api
from presentacion.consumidor_rabbitmq import ConsumidorFacturasRabbitMQ


def seleccionar_repositorio() -> IRepositorioFacturas:
    proveedor = os.getenv("DB_PROVIDER", "postgres").strip().lower()
    if proveedor == "postgres":
        return RepositorioPostgreSQLSimulado()
    if proveedor == "oracle":
        return RepositorioOracleSimulado()
    raise ValueError("DB_PROVIDER debe ser 'postgres' u 'oracle'.")


# LA ÚNICA selección del repositorio ocurre en el exterior del núcleo.
repositorio = seleccionar_repositorio()
crear = CasoDeUsoCrearFactura(repositorio, ControlFraude(), PoliticaFiscal())
consultar = CasoDeUsoConsultarFactura(repositorio)
controlador = ControladorFacturasREST(crear, consultar)

habilitar_rabbitmq = os.getenv("RABBITMQ_HABILITADO", "1").strip().lower() in ("1", "true", "si")
consumidor = ConsumidorFacturasRabbitMQ(crear) if habilitar_rabbitmq else None

app = crear_api(controlador, consumidor)
