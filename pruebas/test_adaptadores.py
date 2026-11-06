"""Mismo caso de uso desde REST y mensajería, con un repositorio compartido."""
import json
import unittest

from fastapi.testclient import TestClient

from aplicacion.casos_uso import CasoDeUsoConsultarFactura, CasoDeUsoCrearFactura
from dominio.control_fraude import ControlFraude
from dominio.politica_fiscal import PoliticaFiscal
from infraestructura.repositorios import RepositorioPostgreSQLSimulado
from presentacion.api_rest import ControladorFacturasREST, crear_api
from presentacion.consumidor_rabbitmq import ConsumidorFacturasRabbitMQ


DATOS = {
    "cliente_id": "CLI-001",
    "pais": "EC",
    "lineas": [{"descripcion": "Auditoría", "cantidad": 2, "precio_unitario": "25.00"}],
}


class PruebasAdaptadores(unittest.TestCase):
    def setUp(self):
        self.repositorio = RepositorioPostgreSQLSimulado()
        self.crear = CasoDeUsoCrearFactura(self.repositorio, ControlFraude(), PoliticaFiscal())
        self.consultar = CasoDeUsoConsultarFactura(self.repositorio)
        self.controlador = ControladorFacturasREST(self.crear, self.consultar)
        self.consumidor = ConsumidorFacturasRabbitMQ(self.crear)
        self.cliente = TestClient(crear_api(self.controlador, consumidor=None))

    def test_11_api_crea_y_consulta(self):
        respuesta = self.cliente.post("/facturas", json=DATOS)
        self.assertEqual(respuesta.status_code, 201)
        creada = respuesta.json()
        self.assertEqual(creada["total"], "57.50")
        consulta = self.cliente.get(f"/facturas/{creada['id']}")
        self.assertEqual(consulta.status_code, 200)
        self.assertEqual(consulta.json(), creada)

    def test_12_api_rechaza_fraude(self):
        datos = {**DATOS, "cliente_id": "CLI-FRAUDE"}
        respuesta = self.cliente.post("/facturas", json=datos)
        self.assertEqual(respuesta.status_code, 422)

    def test_13_consulta_inexistente(self):
        respuesta = self.cliente.get("/facturas/inexistente")
        self.assertEqual(respuesta.status_code, 404)

    def test_14_rabbitmq_utiliza_el_mismo_caso_de_uso(self):
        self.assertIs(self.controlador.crear_factura_caso_uso, self.consumidor.crear_factura_caso_uso)
        self.assertTrue(self.consumidor.procesar_mensaje(json.dumps(DATOS).encode("utf-8")))
        self.assertEqual(len(self.repositorio._facturas), 1)
        id_creado = next(iter(self.repositorio._facturas))
        self.assertEqual(self.cliente.get(f"/facturas/{id_creado}").status_code, 200)

    def test_15_rabbitmq_descarta_mensaje_invalido(self):
        self.assertFalse(self.consumidor.procesar_mensaje(b"no-es-json"))
        self.assertEqual(len(self.repositorio._facturas), 0)


if __name__ == "__main__":
    unittest.main()
