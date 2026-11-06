"""Adaptador HTTP; FastAPI no se filtra a Aplicación ni a Dominio."""
from contextlib import asynccontextmanager
from threading import Thread

from fastapi import FastAPI, HTTPException

from aplicacion.puertos import ICrearFactura, IConsultarFactura
from presentacion.traductores import convertir_a_crear_factura_dto, convertir_a_respuesta


class ControladorFacturasREST:
    def __init__(
        self,
        crear_factura_caso_uso: ICrearFactura,
        consultar_factura_caso_uso: IConsultarFactura,
    ) -> None:
        self.crear_factura_caso_uso = crear_factura_caso_uso
        self.consultar_factura_caso_uso = consultar_factura_caso_uso

    def crear_factura(self, datos: dict) -> dict:
        solicitud = convertir_a_crear_factura_dto(datos)
        resultado = self.crear_factura_caso_uso.ejecutar(solicitud)
        return convertir_a_respuesta(resultado)

    def consultar_factura(self, id: str) -> dict:
        resultado = self.consultar_factura_caso_uso.ejecutar(id)
        if resultado is None:
            raise LookupError("No existe una factura con el identificador indicado.")
        return convertir_a_respuesta(resultado)


def crear_api(controlador: ControladorFacturasREST, consumidor=None) -> FastAPI:
    # Ambos adaptadores comparten los casos de uso y la misma instancia de repositorio.
    @asynccontextmanager
    async def ciclo_de_vida(api: FastAPI):
        if consumidor is not None:
            Thread(target=consumidor.escuchar, daemon=True, name="consumidor-rabbitmq").start()
        yield

    api = FastAPI(
        title="Sistema de Facturación — Arquitectura Limpia",
        description="Ejemplo académico: API REST y RabbitMQ comparten un caso de uso.",
        version="1.0.0",
        lifespan=ciclo_de_vida,
    )

    @api.post("/facturas", status_code=201, summary="Crear factura")
    def crear_factura(datos: dict):
        try:
            return controlador.crear_factura(datos)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @api.get("/facturas/{id}", summary="Consultar factura")
    def consultar_factura(id: str):
        try:
            return controlador.consultar_factura(id)
        except LookupError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    return api
