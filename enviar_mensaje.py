"""Publicador opcional de pruebas (periférico, no es parte del núcleo UML)."""
import json
import os
from pathlib import Path

import pika


archivo_ejemplo = Path(__file__).parent / "ejemplos" / "factura_valida.json"
datos = json.loads(archivo_ejemplo.read_text(encoding="utf-8"))

conexion = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "localhost"),
        port=5672,
        credentials=pika.PlainCredentials(
            os.getenv("RABBITMQ_USUARIO", "guest"),
            os.getenv("RABBITMQ_CLAVE", "guest"),
        ),
    )
)
try:
    canal = conexion.channel()
    cola = os.getenv("RABBITMQ_COLA", "facturas_queue")
    canal.queue_declare(queue=cola, durable=True)
    canal.basic_publish(
        exchange="",
        routing_key=cola,
        body=json.dumps(datos, ensure_ascii=False).encode("utf-8"),
        properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
    )
    print(f"Mensaje JSON publicado correctamente en '{cola}'.")
finally:
    conexion.close()
