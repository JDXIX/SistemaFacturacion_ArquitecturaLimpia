"""Objetos de transferencia de datos (DTO) de la capa de Aplicación."""
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class LineaDTO:
    descripcion: str
    cantidad: int
    precio_unitario: Decimal


@dataclass(frozen=True)
class CrearFacturaDTO:
    cliente_id: str
    pais: str
    lineas: list[LineaDTO]


@dataclass(frozen=True)
class FacturaCreadaDTO:
    id: str
    subtotal: Decimal
    impuesto: Decimal
    total: Decimal
