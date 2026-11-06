"""Orquestación del negocio: no define fraude, impuestos ni persistencia concreta."""
from decimal import Decimal
from uuid import uuid4

from aplicacion.dto import CrearFacturaDTO, FacturaCreadaDTO
from aplicacion.puertos import ICrearFactura, IConsultarFactura
from dominio.control_fraude import ControlFraude
from dominio.factura import Factura, LineaFactura
from dominio.politica_fiscal import PoliticaFiscal
from dominio.repositorio_facturas import IRepositorioFacturas


class CasoDeUsoCrearFactura(ICrearFactura):
    def __init__(
        self,
        repositorio: IRepositorioFacturas,
        control_fraude: ControlFraude,
        politica_fiscal: PoliticaFiscal,
    ) -> None:
        self.repositorio = repositorio
        self.control_fraude = control_fraude
        self.politica_fiscal = politica_fiscal

    def ejecutar(self, datos: CrearFacturaDTO) -> FacturaCreadaDTO:
        factura = Factura(
            id=str(uuid4()),
            cliente_id=datos.cliente_id,
            pais=datos.pais,
            lineas=[
                LineaFactura(
                    descripcion=linea.descripcion,
                    cantidad=linea.cantidad,
                    precio_unitario=linea.precio_unitario,
                )
                for linea in datos.lineas
            ],
            impuesto=Decimal("0.00"),
        )

        # Únicamente invocamos políticas del dominio: NO calculamos aquí sus reglas.
        self.control_fraude.verificar(factura)
        factura.impuesto = self.politica_fiscal.calcular_impuesto(
            factura.pais, factura.calcular_subtotal()
        )
        self.repositorio.guardar(factura)
        return FacturaCreadaDTO(
            id=factura.id,
            subtotal=factura.calcular_subtotal(),
            impuesto=factura.impuesto,
            total=factura.calcular_total(),
        )


class CasoDeUsoConsultarFactura(IConsultarFactura):
    def __init__(self, repositorio: IRepositorioFacturas) -> None:
        self.repositorio = repositorio

    def ejecutar(self, id: str) -> FacturaCreadaDTO | None:
        factura = self.repositorio.buscar_por_id(id)
        if factura is None:
            return None
        # La consulta devuelve los importes ya almacenados; no aplica otra vez las políticas.
        return FacturaCreadaDTO(
            id=factura.id,
            subtotal=factura.calcular_subtotal(),
            impuesto=factura.impuesto,
            total=factura.calcular_total(),
        )
