"""Pruebas sin FastAPI, RabbitMQ, Oracle ni PostgreSQL reales."""
import unittest
from decimal import Decimal

from aplicacion.casos_uso import CasoDeUsoConsultarFactura, CasoDeUsoCrearFactura
from aplicacion.dto import CrearFacturaDTO, LineaDTO
from aplicacion.puertos import ICrearFactura, IConsultarFactura
from dominio.control_fraude import ControlFraude
from dominio.factura import Factura, LineaFactura
from dominio.politica_fiscal import PoliticaFiscal
from infraestructura.repositorios import RepositorioOracleSimulado, RepositorioPostgreSQLSimulado


class PruebasDominio(unittest.TestCase):
    def setUp(self):
        self.repositorio = RepositorioPostgreSQLSimulado()
        self.crear = CasoDeUsoCrearFactura(self.repositorio, ControlFraude(), PoliticaFiscal())
        self.consultar = CasoDeUsoConsultarFactura(self.repositorio)

    def solicitud(self, cliente="CLI-001", cantidad=2, precio="20.00", pais="EC"):
        return CrearFacturaDTO(
            cliente_id=cliente,
            pais=pais,
            lineas=[LineaDTO("Servicio", cantidad, Decimal(precio))],
        )

    def test_01_calculo_correcto_ecuador_simulado(self):
        respuesta = self.crear.ejecutar(self.solicitud())
        self.assertEqual(respuesta.subtotal, Decimal("40.00"))
        self.assertEqual(respuesta.impuesto, Decimal("6.00"))
        self.assertEqual(respuesta.total, Decimal("46.00"))

    def test_02_politica_colombia_simulada(self):
        respuesta = self.crear.ejecutar(self.solicitud(pais="CO"))
        self.assertEqual(respuesta.impuesto, Decimal("7.60"))

    def test_03_cliente_bloqueado(self):
        with self.assertRaisesRegex(ValueError, "cliente bloqueado"):
            self.crear.ejecutar(self.solicitud(cliente="CLI-FRAUDE"))

    def test_04_monto_superior_al_umbral(self):
        with self.assertRaisesRegex(ValueError, "umbral"):
            self.crear.ejecutar(self.solicitud(precio="10001.00", cantidad=1))

    def test_05_cantidad_invalida(self):
        with self.assertRaisesRegex(ValueError, "cantidad"):
            self.crear.ejecutar(self.solicitud(cantidad=0))

    def test_06_factura_sin_lineas(self):
        with self.assertRaisesRegex(ValueError, "al menos una línea"):
            self.crear.ejecutar(CrearFacturaDTO("CLI-001", "EC", []))

    def test_07_consulta_por_identificador(self):
        creada = self.crear.ejecutar(self.solicitud())
        encontrada = self.consultar.ejecutar(creada.id)
        self.assertEqual(creada, encontrada)
        self.assertIsNone(self.consultar.ejecutar("no-existe"))

    def test_08_puertos_de_entrada_implementados(self):
        self.assertIsInstance(self.crear, ICrearFactura)
        self.assertIsInstance(self.consultar, IConsultarFactura)

    def test_09_repositorios_intercambiables(self):
        for tipo in (RepositorioPostgreSQLSimulado, RepositorioOracleSimulado):
            with self.subTest(repositorio=tipo.__name__):
                repositorio = tipo()
                crear = CasoDeUsoCrearFactura(repositorio, ControlFraude(), PoliticaFiscal())
                consultar = CasoDeUsoConsultarFactura(repositorio)
                respuesta = crear.ejecutar(self.solicitud())
                self.assertEqual(consultar.ejecutar(respuesta.id), respuesta)

    def test_10_valores_monetarios_sin_flotantes(self):
        linea = LineaFactura("Servicio", 3, Decimal("0.10"))
        factura = Factura("1", "CLI", "EC", [linea], Decimal("0.05"))
        self.assertEqual(factura.calcular_subtotal(), Decimal("0.30"))
        self.assertEqual(factura.calcular_total(), Decimal("0.35"))


if __name__ == "__main__":
    unittest.main()
