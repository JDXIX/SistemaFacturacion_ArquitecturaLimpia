# Correspondencia entre UML y código Python

Este proyecto implementa las **13 cajas principales del diagrama UML de clases**, más **3 DTO auxiliares** que ya aparecían en las firmas pero que no se dibujaron como cajas.

| Elemento UML | Archivo Python | Capa |
|---|---|---|
| `Factura` | `dominio/factura.py` | Dominio |
| `LineaFactura` | `dominio/factura.py` | Dominio |
| `ControlFraude` | `dominio/control_fraude.py` | Dominio |
| `PoliticaFiscal` | `dominio/politica_fiscal.py` | Dominio |
| `IRepositorioFacturas` | `dominio/repositorio_facturas.py` | Dominio |
| `ICrearFactura` | `aplicacion/puertos.py` | Aplicación |
| `IConsultarFactura` | `aplicacion/puertos.py` | Aplicación |
| `CasoDeUsoCrearFactura` | `aplicacion/casos_uso.py` | Aplicación |
| `CasoDeUsoConsultarFactura` | `aplicacion/casos_uso.py` | Aplicación |
| `ControladorFacturasREST` | `presentacion/api_rest.py` | Presentación |
| `ConsumidorFacturasRabbitMQ` | `presentacion/consumidor_rabbitmq.py` | Presentación |
| `RepositorioPostgreSQLSimulado` | `infraestructura/repositorios.py` | Infraestructura |
| `RepositorioOracleSimulado` | `infraestructura/repositorios.py` | Infraestructura |

## DTO que figuran como tipos en el UML

`CrearFacturaDTO`, `LineaDTO` y `FacturaCreadaDTO` viven en `aplicacion/dto.py`.

## Contratos y realizaciones UML

- `ControladorFacturasREST ..> ICrearFactura` (usa).
- `ControladorFacturasREST ..> IConsultarFactura` (usa).
- `ConsumidorFacturasRabbitMQ ..> ICrearFactura` (usa).
- `CasoDeUsoCrearFactura ..|> ICrearFactura` (implementa).
- `CasoDeUsoConsultarFactura ..|> IConsultarFactura` (implementa).
- `CasoDeUsoCrearFactura ..> Factura`, `ControlFraude`, `PoliticaFiscal`, `IRepositorioFacturas` (usa).
- `CasoDeUsoConsultarFactura ..> IRepositorioFacturas` (usa).
- `Factura "1" *-- "1..*" LineaFactura` (composición).
- `RepositorioPostgreSQLSimulado ..|> IRepositorioFacturas` (implementa).
- `RepositorioOracleSimulado ..|> IRepositorioFacturas` (implementa).

**Nota sobre la imagen generada anteriormente:** una flecha del consumidor aparecía orientada por error hacia `IConsultarFactura`. **En el código se aplica la relación correcta prevista en el enunciado y la definición UML:** `ConsumidorFacturasRabbitMQ` utiliza `ICrearFactura`. No sería correcto reproducir el error gráfico.

## Regla de Dependencia

- **Dominio** no importa nada de Aplicación, Presentación ni Infraestructura.
- **Aplicación** conoce Dominio, pero no tecnologías externas.
- **Presentación** conoce interfaces de Aplicación y traduce HTTP/AMQP a DTO.
- **Infraestructura** implementa `IRepositorioFacturas`, interfaz del Dominio.
- **`main.py`** es el *Composition Root*: ensambla los objetos y elige el repositorio por `DB_PROVIDER`.

## Decisiones académicas conscientes

- Las tasas de impuestos (EC 15 %, CO 19 %, otros 10 %) son exclusivamente **simuladas**. No representan legislación vigente.
- Se bloquea `CLI-FRAUDE` y subtotales mayores a 10 000 para demostrar el control de fraude. Son **reglas de ejemplo**, no requisitos numéricos del docente.
- Dos implementaciones simulan PostgreSQL/Oracle con diccionarios; no existe conexión SQL real.
- La API REST y el consumidor AMQP se ejecutan dentro de **un único proceso** para compartir una instancia del mismo repositorio volátil. El comando recomendado no usa varios workers.
- Se implementó confirmación manual de mensajes de RabbitMQ. Los mensajes rechazados por política o inválidos no se reencolan; los errores inesperados se reencolan. Para producción sería necesario diseñar idempotencia, reintentos limitados y cola de errores.
- El proyecto es una demostración académica, no un sistema de facturación electrónica ni una plataforma financiera de producción.
