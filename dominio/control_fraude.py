"""Política de fraude simulada; no depende de protocolos ni bases de datos."""
from decimal import Decimal
from dominio.factura import Factura


class ControlFraude:
    def verificar(self, factura: Factura) -> None:
        # Estas condiciones son académicas, NO reglas reales de una institución.
        if factura.cliente_id.strip().upper() == "CLI-FRAUDE":
            raise ValueError("Factura rechazada: cliente bloqueado por control de fraude.")
        if factura.calcular_subtotal() > Decimal("10000.00"):
            raise ValueError("Factura rechazada: subtotal superior al umbral simulado de fraude.")
