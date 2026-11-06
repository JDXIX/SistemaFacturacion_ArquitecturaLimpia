"""Contrato de persistencia exigido por el enunciado: pertenece al Dominio."""
from abc import ABC, abstractmethod
from dominio.factura import Factura


class IRepositorioFacturas(ABC):
    @abstractmethod
    def guardar(self, factura: Factura) -> None:
        """Almacena una factura independientemente de la tecnología utilizada."""

    @abstractmethod
    def buscar_por_id(self, id: str) -> Factura | None:
        """Obtiene una factura por identificador, si existe."""
