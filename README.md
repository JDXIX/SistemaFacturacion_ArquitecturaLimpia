# Sistema de Facturación — Arquitectura Limpia (Python)

Proyecto académico de Arquitectura de Software. Implementa un solo núcleo de negocio con dos adaptadores de entrada **REST (FastAPI)** y **AMQP (RabbitMQ)**, y dos adaptadores de salida **PostgreSQL/Oracle simulados en memoria**.

La fuente de verdad es el enunciado del docente. Los nombres y contratos siguen el diagrama UML de clases de 13 elementos (más tres DTO auxiliares).

## 1. Estructura

```text
SistemaFacturacion_ArquitecturaLimpia/
├── dominio/
│   ├── factura.py                    # Factura, LineaFactura
│   ├── control_fraude.py              # ControlFraude
│   ├── politica_fiscal.py             # PoliticaFiscal
│   └── repositorio_facturas.py        # IRepositorioFacturas
├── aplicacion/
│   ├── dto.py                         # 3 DTO
│   ├── puertos.py                     # ICrearFactura, IConsultarFactura
│   └── casos_uso.py                  # Casos de uso de crear y consultar
├── infraestructura/
│   └── repositorios.py               # PostgreSQL y Oracle simulados
├── presentacion/
│   ├── traductores.py                # JSON <-> DTO
│   ├── api_rest.py                   # ControladorFacturasREST
│   └── consumidor_rabbitmq.py        # ConsumidorFacturasRabbitMQ
├── pruebas/                          # unittest, sin SQL real
├── ejemplos/                         # JSON de prueba
├── main.py                           # Composition Root
├── enviar_mensaje.py                 # Publicador de prueba opcional
├── compose.yaml                      # RabbitMQ local opcional
├── requirements.txt
└── ARQUITECTURA_Y_UML.md
```

## 2. Requisitos

- Python 3.10 o superior (recomendado 3.11+).
- VS Code y GitHub Desktop si desea trabajar con esas herramientas.
- RabbitMQ disponible para probar la entrada AMQP. Puede utilizar Docker **solo** para el broker si lo tiene instalado.

## 3. Preparar el proyecto (Windows, PowerShell)

Abra la carpeta del proyecto en VS Code y ejecute desde su raíz:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell no permite activar el entorno, puede usar `cmd` con `.venv\Scripts\activate.bat`, o invocar `.venv\Scripts\python.exe` directamente.

## 4. Iniciar RabbitMQ

Con Docker instalado, desde la misma carpeta:

```powershell
docker compose up -d
```

Esto crea solo RabbitMQ (contenedor para desarrollo) y expone **únicamente en localhost**:

- AMQP: `localhost:5672`
- Panel web: `http://localhost:15672`
- Usuario y clave **solo locales**: `guest` / `guest`

Si ya dispone de RabbitMQ instalado, no necesita Docker. Configure las variables de conexión indicadas abajo.

## 5. Ejecutar la aplicación

En la raíz del proyecto:

```powershell
$env:DB_PROVIDER = "postgres"
$env:RABBITMQ_HABILITADO = "1"
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Abra `http://127.0.0.1:8000/docs` (Swagger UI). Si el broker está disponible, la consola debe mostrar `[RabbitMQ] Escuchando la cola 'facturas_queue'`.

**Importante:** ejecute la API con **un solo proceso**, sin `--workers`, porque REST y RabbitMQ comparten el mismo repositorio **en memoria**. Si arranca la API sin RabbitMQ, REST funciona, pero debe iniciar RabbitMQ y reiniciar el programa para activar el consumidor.

Para probar REST sin RabbitMQ:

```powershell
$env:RABBITMQ_HABILITADO = "0"
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

## 6. Crear una factura por REST

En Swagger `POST /facturas`, seleccione «Try it out» y envíe:

```json
{
  "cliente_id": "CLI-001",
  "pais": "EC",
  "lineas": [
    {"descripcion": "Consultoría", "cantidad": 2, "precio_unitario": "25.00"},
    {"descripcion": "Soporte técnico", "cantidad": 1, "precio_unitario": "10.00"}
  ]
}
```

Resultado HTTP **201** (identificador aleatorio diferente en cada ejecución):

```json
{
  "id": "<uuid-generado>",
  "subtotal": "60.00",
  "impuesto": "9.00",
  "total": "69.00"
}
```

Los importes viajan como texto JSON para preservar los valores decimales. La tasa del ejemplo es **simulada**, no oficial.

## 7. Consultar una factura por REST

Copie el `id` de la respuesta y abra `GET /facturas/{id}` en Swagger. Si existe, recibirá el mismo resumen. Si no existe, obtendrá HTTP **404**.

## 8. Crear una factura por RabbitMQ

**Opción A: publicar desde el panel**

1. Abra `http://localhost:15672` con usuario y clave locales.
2. Ingrese a **Queues and Streams** y abra `facturas_queue` (se crea al iniciar el consumidor).
3. En **Publish message**, copie el JSON del paso 6 al campo `Payload` y pulse **Publish message**.
4. Consulte la consola de la API: debe mostrar `[RabbitMQ] Factura creada: <id>; total=69.00`.
5. Utilice el `id` mostrado para consultar esa misma factura por `GET /facturas/{id}`. Esto funciona porque ambos adaptadores comparten la misma instancia de memoria.

**Opción B: publicador de ejemplo**

Deje la API ejecutándose y abra **otra terminal** en la raíz del proyecto:

```powershell
python enviar_mensaje.py
```

El script publica `ejemplos/factura_valida.json`. La consola del servidor mostrará el identificador generado.

## 9. Cambiar PostgreSQL por Oracle (simulados)

Detenga la aplicación con `Ctrl+C` y reiníciela con:

```powershell
$env:DB_PROVIDER = "oracle"
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Cree y consulte otra factura: funcionará igual, sin cambiar una línea de `dominio/` ni de `aplicacion/`.

**Aclaración:** la variable `DB_PROVIDER` cambia el adaptador activo, **no migra datos**. Al reiniciar se pierden todas las facturas porque la persistencia es volátil.

## 10. Pruebas automatizadas

Con las dependencias instaladas, desde la raíz:

```powershell
python -m unittest discover -s pruebas -v
```

Las pruebas cubren dominio, fraudes, impuestos, ambos repositorios, API y el procesamiento de mensajes del consumidor. Las pruebas del consumidor **no requieren un broker real**; el uso del broker debe verificarse manualmente en el paso 8.

## 11. Reglas simuladas usadas en esta demostración

- Cliente `CLI-FRAUDE`: creación rechazada.
- Subtotal mayor a `10000.00`: creación rechazada.
- País `EC` o `Ecuador`: tasa académica del 15 %.
- País `CO` o `Colombia`: tasa académica del 19 %.
- Otros países: tasa académica del 10 %.
- Cantidades y precios unitarios positivos; mínimo una línea.
- Redondeo monetario a dos decimales con `ROUND_HALF_UP`.

Las tasas y el umbral **no provienen del enunciado como valores obligatorios**: son decisiones de ejemplo para poder ejecutar y evaluar las reglas del dominio. **No utilizar para facturación real.**

## 12. Recomendaciones para GitHub Desktop

1. Abra GitHub Desktop → **File → Add local repository** (o **Create repository** si aún no está inicializado).
2. Seleccione esta carpeta; si corresponde, inicialice un repositorio Git.
3. Revise los cambios, cree el primer commit y publique en GitHub.
4. Nunca publique `.env`, secretos ni contraseñas reales; `.gitignore` ya excluye el archivo `.env`.

## 13. Qué demuestra la Arquitectura Limpia

- **Puerto de entrada:** `ICrearFactura`, declarado en Aplicación y realizado por `CasoDeUsoCrearFactura`. REST y RabbitMQ **lo invocan**, no lo implementan.
- **Puerto de salida:** `IRepositorioFacturas`, declarado en Dominio y realizado por ambos repositorios simulados.
- **Regla de Dependencia:** Dominio y Aplicación no importan FastAPI, Pika ni clases concretas de repositorios.
- **Inyección de dependencias:** `main.py` es el *Composition Root*: selecciona el repositorio por configuración y lo suministra a ambos casos de uso.

Para el mapeo de las 13 cajas del UML y sus relaciones, consulte [ARQUITECTURA_Y_UML.md](ARQUITECTURA_Y_UML.md).
