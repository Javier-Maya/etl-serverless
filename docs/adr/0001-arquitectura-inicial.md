# ADR 0001 — Arquitectura Inicial: Serverless ETL Event-Driven

## Estado
Aprobado — 2026-06-06

## Contexto
Se requiere procesar archivos CSV de transacciones de punto de venta
que llegan periódicamente a un bucket S3. El procesamiento debe ocurrir
automáticamente sin intervención humana y sin necesidad de un servidor
corriendo 24/7.

Background del equipo: experiencia en ETL on-premise (IBM DataStage),
migrando hacia arquitecturas cloud modernas.

## Opciones consideradas

### Opción 1 — EC2 con script polling (enfoque tradicional)
Servidor corriendo continuamente, chequeando S3 cada N minutos.
- ✅ Familiar para equipos con background on-premise
- ❌ Costo fijo aunque no haya archivos que procesar
- ❌ Requiere administración de servidor (parches, disponibilidad)
- ❌ Latencia artificial por el intervalo de polling

### Opción 2 — Lambda + S3 Event Trigger (serverless event-driven)
Función Lambda activada automáticamente cuando llega un archivo a S3.
- ✅ Costo por uso real — no hay costo cuando no hay archivos
- ✅ Sin administración de servidores
- ✅ Escalado automático ante múltiples archivos simultáneos
- ✅ Latencia mínima — reacción inmediata al evento
- ❌ Cold start (~1-2 segundos en primera ejecución)
- ❌ Límite de 15 minutos por ejecución (no relevante para este caso)

### Opción 3 — ECS/Fargate con contenedor
Contenedor Docker activado por evento.
- ✅ Sin límite de tiempo de ejecución
- ✅ Mayor control sobre el entorno
- ❌ Mayor complejidad operacional
- ❌ Innecesario para el volumen de datos del caso de uso

## Decisión
**Opción 2 — Lambda + S3 Event Trigger**

El patrón event-driven serverless es el más adecuado para este caso de uso.
Los archivos CSV de transacciones POS son de tamaño acotado y el procesamiento
no supera los límites de Lambda. El costo operacional es mínimo y la
arquitectura demuestra patrones modernos relevantes para el portfolio.

## Consecuencias
- El handler de Lambda debe completar el procesamiento en menos de 15 minutos
- La función debe ser idempotente (mismo archivo procesado dos veces = mismo resultado)
- Se requiere IAM Role con permisos específicos para S3, CloudWatch y RDS
- Cold start es aceptable para este caso de uso (procesamiento batch, no real-time)
- PostgreSQL debe ser accesible desde Lambda (configuración de VPC o RDS Proxy)