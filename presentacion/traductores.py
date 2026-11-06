"""Funciones de traducción JSON <-> DTO; no son clases adicionales del UML."""
from decimal import Decimal, InvalidOperation

from aplicacion.dto import CrearFacturaDTO, FacturaCreadaDTO, LineaDTO


def convertir_a_crear_factura_dto(datos: dict) -> CrearFacturaDTO:
    if not isinstance(datos, dict):
        raise ValueError("La factura debe enviarse como un objeto JSON.")

    cliente = datos.get("cliente_id")
    pais = datos.get("pais")
    lineas = datos.get("lineas")
    if not isinstance(cliente, str) or not isinstance(pais, str):
        raise ValueError("'cliente_id' y 'pais' deben ser textos.")
    if not isinstance(lineas, list):
        raise ValueError("'lineas' debe ser una lista.")

    lineas_dto = []
    for posicion, linea in enumerate(lineas, start=1):
        if not isinstance(linea, dict):
            raise ValueError(f"La línea {posicion} debe ser un objeto JSON.")
        descripcion = linea.get("descripcion")
        cantidad = linea.get("cantidad")
        precio = linea.get("precio_unitario")
        if not isinstance(descripcion, str):
            raise ValueError(f"La descripción de la línea {posicion} debe ser texto.")
        if isinstance(cantidad, bool) or not isinstance(cantidad, int):
            raise ValueError(f"La cantidad de la línea {posicion} debe ser un entero.")
        if isinstance(precio, bool) or not isinstance(precio, (str, int, float, Decimal)):
            raise ValueError(f"El precio de la línea {posicion} debe ser numérico.")
        try:
            precio_decimal = Decimal(str(precio))
        except InvalidOperation as error:
            raise ValueError(f"El precio de la línea {posicion} no es válido.") from error
        if not precio_decimal.is_finite():
            raise ValueError(f"El precio de la línea {posicion} debe ser finito.")
        lineas_dto.append(
            LineaDTO(
                descripcion=descripcion,
                cantidad=cantidad,
                precio_unitario=precio_decimal,
            )
        )

    return CrearFacturaDTO(cliente_id=cliente, pais=pais, lineas=lineas_dto)


def convertir_a_respuesta(dto: FacturaCreadaDTO) -> dict:
    # Los valores monetarios viajan como texto para evitar pérdidas por float en JSON.
    return {
        "id": dto.id,
        "subtotal": f"{dto.subtotal:.2f}",
        "impuesto": f"{dto.impuesto:.2f}",
        "total": f"{dto.total:.2f}",
    }
