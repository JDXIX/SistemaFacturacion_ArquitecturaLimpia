"""Política fiscal totalmente simulada; no representa tasas oficiales actuales."""
from decimal import Decimal, ROUND_HALF_UP


class PoliticaFiscal:
    def calcular_impuesto(self, pais: str, subtotal: Decimal) -> Decimal:
        if not isinstance(pais, str) or not pais.strip():
            raise ValueError("El país es obligatorio para aplicar la política fiscal.")
        if not isinstance(subtotal, Decimal) or not subtotal.is_finite() or subtotal < 0:
            raise ValueError("El subtotal debe ser un número decimal no negativo.")

        pais_normalizado = pais.strip().upper()
        tasas_simuladas = {
            "EC": Decimal("0.15"),
            "ECUADOR": Decimal("0.15"),
            "CO": Decimal("0.19"),
            "COLOMBIA": Decimal("0.19"),
        }
        tasa = tasas_simuladas.get(pais_normalizado, Decimal("0.10"))
        return (subtotal * tasa).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
