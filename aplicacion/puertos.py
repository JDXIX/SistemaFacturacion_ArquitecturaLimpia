"""Puertos de entrada: los adaptadores los invocan, los casos de uso los implementan."""
from abc import ABC, abstractmethod
from aplicacion.dto import CrearFacturaDTO, FacturaCreadaDTO


class ICrearFactura(ABC):
    @abstractmethod
    def ejecutar(self, datos: CrearFacturaDTO) -> FacturaCreadaDTO:
        """Crea una factura sin conocer el origen de la solicitud."""


class IConsultarFactura(ABC):
    @abstractmethod
    def ejecutar(self, id: str) -> FacturaCreadaDTO | None:
        """Consulta una factura existente por su identificador."""
