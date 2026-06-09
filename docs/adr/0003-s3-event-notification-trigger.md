# ADR 0003 — S3 Event Notification como trigger de Lambda

## Contexto
Se necesita activar la función Lambda `etl-csv-processor` automáticamente
cuando llega un archivo CSV al prefijo `raw/` del bucket S3.
Existen dos opciones principales en AWS para este caso de uso.

## Opciones consideradas

**S3 Event Notifications**
Integración directa entre S3 y Lambda. S3 envía un evento a Lambda
cuando se crea un objeto. Sin servicios intermedios, sin costo adicional.

**Amazon EventBridge**
Bus de eventos central de AWS. S3 puede enviar eventos a EventBridge,
que los enruta a Lambda u otros destinos. Más flexible y observable,
pero agrega un servicio intermedio con costo y complejidad adicional.

## Decisión
S3 Event Notifications.

## Motivo
El proyecto tiene un único origen de eventos (S3) y un único consumidor
(Lambda). EventBridge aporta valor cuando hay múltiples productores
o múltiples consumidores que necesitan enrutamiento flexible.
Para este caso de uso, sería overhead sin beneficio real.

## Configuración aplicada
- Bucket: `etl-serverless-451580497892-us-east-1-an`
- Nombre: `trigger-etl-lambda-on-raw-upload`
- Prefix filter: `raw/`
- Suffix filter: `.csv`
- Event type: `s3:ObjectCreated:*`
- Destination: `etl-csv-processor`

## Consecuencias
- Activación directa sin latencia adicional
- El filtro por prefix `raw/` evita loops infinitos al mover
  archivos a `processed/` o `failed/`
- Si en el futuro se requiere enrutar el mismo evento a múltiples
  consumidores, migrar a EventBridge
