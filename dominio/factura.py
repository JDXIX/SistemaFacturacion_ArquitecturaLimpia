"""Entidades de dominio: factura y líneas que la componen."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


CENTAVO = Decimal("0.01")


@dataclass
class LineaFactura:
    descripcion: str
    cantidad: int
    precio_unitario: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.descripcion, str) or not self.descripcion.strip():
            raise ValueError("La descripción de cada línea es obligatoria.")
        if isinstance(self.cantidad, bool) or not isinstance(self.cantidad, int) or self.cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero positivo.")
        if not isinstance(self.precio_unitario, Decimal) or not self.precio_unitario.is_finite():
            raise ValueError("El precio unitario debe ser un número decimal válido.")
        if self.precio_unitario <= 0:
            raise ValueError("El precio unitario debe ser positivo.")

    def calcular_subtotal(self) -> Decimal:
        return (self.precio_unitario * self.cantidad).quantize(CENTAVO, rounding=ROUND_HALF_UP)


@dataclass
class Factura:
    id: str
    cliente_id: str
    pais: str
    lineas: list[LineaFactura]
    impuesto: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("La factura necesita un identificador.")
        if not isinstance(self.cliente_id, str) or not self.cliente_id.strip():
            raise ValueError("El identificador del cliente es obligatorio.")
        if not isinstance(self.pais, str) or not self.pais.strip():
            raise ValueError("El país es obligatorio.")
        if not isinstance(self.lineas, list) or not self.lineas:
            raise ValueError("La factura debe contener al menos una línea.")
        if any(not isinstance(linea, LineaFactura) for linea in self.lineas):
            raise ValueError("Todas las líneas deben ser del tipo LineaFactura.")
        if not isinstance(self.impuesto, Decimal) or not self.impuesto.is_finite() or self.impuesto < 0:
            raise ValueError("El impuesto debe ser un importe decimal válido no negativo.")

    def calcular_subtotal(self) -> Decimal:
        return sum((linea.calcular_subtotal() for linea in self.lineas), Decimal("0.00"))

    def calcular_total(self) -> Decimal:
        return (self.calcular_subtotal() + self.impuesto).quantize(CENTAVO, rounding=ROUND_HALF_UP)
