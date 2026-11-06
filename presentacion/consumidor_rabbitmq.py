"""Adaptador AMQP: traduce mensajes y llama al MISMO puerto ICrearFactura."""
import json
import os

from aplicacion.puertos import ICrearFactura
from presentacion.traductores import convertir_a_crear_factura_dto


class ConsumidorFacturasRabbitMQ:
    def __init__(self, crear_factura_caso_uso: ICrearFactura) -> None:
        self.crear_factura_caso_uso = crear_factura_caso_uso

    def procesar_mensaje(self, mensaje: bytes) -> bool:
        try:
            datos = json.loads(mensaje.decode("utf-8"))
            solicitud = convertir_a_crear_factura_dto(datos)
            resultado = self.crear_factura_caso_uso.ejecutar(solicitud)
            print(f"[RabbitMQ] Factura creada: {resultado.id}; total={resultado.total}", flush=True)
            return True
        except ValueError as error:
            # Mensaje mal formado o rechazado por reglas del dominio: no debe reintentarse.
            print(f"[RabbitMQ] Mensaje rechazado: {error}", flush=True)
            return False

    def escuchar(self) -> None:
        # Pika es un detalle tecnológico exclusivo de Presentación.
        import pika

        host = os.getenv("RABBITMQ_HOST", "localhost")
        usuario = os.getenv("RABBITMQ_USUARIO", "guest")
        clave = os.getenv("RABBITMQ_CLAVE", "guest")
        cola = os.getenv("RABBITMQ_COLA", "facturas_queue")

        conexion = None
        try:
            credenciales = pika.PlainCredentials(usuario, clave)
            parametros = pika.ConnectionParameters(
                host=host,
                port=5672,
                credentials=credenciales,
                heartbeat=60,
            )
            conexion = pika.BlockingConnection(parametros)
            canal = conexion.channel()
            canal.queue_declare(queue=cola, durable=True)
            canal.basic_qos(prefetch_count=1)

            def al_recibir(ch, metodo, propiedades, cuerpo):
                try:
                    if self.procesar_mensaje(cuerpo):
                        ch.basic_ack(delivery_tag=metodo.delivery_tag)
                    else:
                        ch.basic_reject(delivery_tag=metodo.delivery_tag, requeue=False)
                except Exception as error:
                    print(f"[RabbitMQ] Fallo inesperado: {error}", flush=True)
                    ch.basic_nack(delivery_tag=metodo.delivery_tag, requeue=True)

            canal.basic_consume(queue=cola, on_message_callback=al_recibir, auto_ack=False)
            print(f"[RabbitMQ] Escuchando la cola '{cola}' en {host}.", flush=True)
            canal.start_consuming()
        except Exception as error:
            # Permite seguir probando REST si RabbitMQ aún no está levantado.
            print(f"[RabbitMQ] No fue posible iniciar el consumidor: {error}", flush=True)
            print("[RabbitMQ] Inicie el broker y reinicie la aplicación.", flush=True)
        finally:
            if conexion is not None and conexion.is_open:
                conexion.close()
