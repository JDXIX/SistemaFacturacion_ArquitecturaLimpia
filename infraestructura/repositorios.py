"""Dos adaptadores simulados: ambos persisten en memoria, no en motores reales."""
from copy import deepcopy
from threading import Lock

from dominio.factura import Factura
from dominio.repositorio_facturas import IRepositorioFacturas


class RepositorioPostgreSQLSimulado(IRepositorioFacturas):
    def __init__(self) -> None:
        self._facturas: dict[str, Factura] = {}
        self._bloqueo = Lock()

    def guardar(self, factura: Factura) -> None:
        with self._bloqueo:
            self._facturas[factura.id] = deepcopy(factura)

    def buscar_por_id(self, id: str) -> Factura | None:
        with self._bloqueo:
            factura = self._facturas.get(id)
            return deepcopy(factura) if factura is not None else None


class RepositorioOracleSimulado(IRepositorioFacturas):
    def __init__(self) -> None:
        self._facturas: dict[str, Factura] = {}
        self._bloqueo = Lock()

    def guardar(self, factura: Factura) -> None:
        with self._bloqueo:
            self._facturas[factura.id] = deepcopy(factura)

    def buscar_por_id(self, id: str) -> Factura | None:
        with self._bloqueo:
            factura = self._facturas.get(id)
            return deepcopy(factura) if factura is not None else None
