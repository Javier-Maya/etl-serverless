# Best Practices — Estándares de Ingeniería

## Principios generales
- Código escrito para ser leído por humanos primero, por máquinas segundo
- Los comentarios explican el WHY, no el WHAT
- Si necesitas un comentario para explicar QUÉ hace el código, reescribe el código
- Nunca hardcodear credenciales, rutas absolutas ni configuración de entorno
- Toda configuración sensible va en variables de entorno (.env), nunca en código
- Fail fast: validar inputs al inicio, no a mitad del proceso

## Arquitectura
- Single Responsibility: cada función/módulo hace una sola cosa
- Separación de concerns: validación, transformación y carga son capas distintas
- Idempotencia: ejecutar el mismo proceso dos veces debe dar el mismo resultado
- Diseñar para el fallo: asumir que cualquier llamada externa puede fallar

## Python
- PEP 8 para estilo de código
- Type hints en todas las funciones
- Docstrings en funciones públicas (formato Google style — ver conventions.md para ejemplos)
- Manejo explícito de excepciones — nunca `except Exception: pass`
- Logging estructurado en vez de print()

## ETL / Data
- Validar schema antes de procesar
- Registrar siempre: filas recibidas, filas procesadas, filas rechazadas
- Los registros rechazados no se pierden — se loggean con motivo
- Nunca modificar datos en raw/ — es la fuente de verdad, solo lectura
- Deduplicación explícita — nunca asumir que los datos vienen limpios

## Git

### Conventional Commits
Todos los mensajes de commit siguen este estándar. Es una convención adoptada
por la industria que hace el historial de Git legible y permite generar
CHANGELOGs automáticamente.

Formato:
```
type(scope): description
```

**type** — qué tipo de cambio es:

| Tipo | Cuándo usarlo | Ejemplo |
|------|--------------|---------|
| `feat` | Funcionalidad nueva | `feat(lambda): add CSV validation` |
| `fix` | Corrección de bug | `fix(db): handle duplicate transaction ids` |
| `docs` | Solo documentación | `docs(adr): add decision for S3 trigger` |
| `refactor` | Refactorización sin cambio funcional | `refactor(lambda): extract validator to separate module` |
| `test` | Agregar o modificar tests | `test(lambda): add unit tests for transformer` |
| `chore` | Setup, configuración, mantenimiento | `chore(project): initial project structure` |

**scope** — qué parte del proyecto afecta:
- `lambda` — función Lambda y su lógica
- `api` — FastAPI
- `db` — base de datos y migraciones
- `infra` — configuración AWS, IAM
- `docs` — documentación
- `project` — configuración general del proyecto

**description** — qué hiciste, en inglés, imperativo, minúsculas, sin punto final.

### Reglas adicionales
- Commits atómicos: un commit = un cambio lógico
- Nunca commitear archivos .env o credenciales
- main siempre debe estar en estado funcional
- Ramas para features: `feature/nombre-descriptivo`

## Seguridad
- Principio de mínimo privilegio en IAM: solo los permisos estrictamente necesarios
- Nunca usar credenciales de root
- Secrets en AWS Secrets Manager para producción
- Variables de entorno para desarrollo local — nunca hardcodeadas

## Observabilidad
- Todo error debe quedar loggeado con contexto suficiente para debuggear
- Logs estructurados en JSON para facilitar búsqueda en CloudWatch
- Registrar inicio y fin de cada ejecución con métricas básicas:
  filas procesadas, filas rechazadas, duración, estado final

## Testing

### Tipos de tests y cuándo usar cada uno

**Tests unitarios** — prueban una función de forma aislada, sin dependencias externas.
Son rápidos, no necesitan conexión a base de datos ni a AWS.
Cubren la lógica de negocio: validaciones, transformaciones, cálculos.
```
# Ejemplo: testear que la validación detecta una columna faltante
# No necesita S3, no necesita PostgreSQL — solo llama a la función y verifica el resultado
test_validate_csv_missing_column_raises_error
```

**Tests de integración** — prueban que dos o más componentes funcionan juntos.
Son más lentos, pueden requerir conexión a servicios reales o mocks de ellos.
Cubren el flujo completo: Lambda recibe evento → lee S3 → inserta en DB.
```
# Ejemplo: testear que el handler completo procesa un CSV y lo inserta en DB
# Necesita una DB de test o un mock de PostgreSQL
test_handler_valid_csv_inserts_transactions
```

### Regla general
- Prioridad a tests unitarios — son más rápidos y más fáciles de mantener
- Tests de integración para los flujos críticos del negocio
- Todo código nuevo tiene al menos un test unitario antes de hacer commit
- Un test que no puede fallar no sirve de nada

### Nomenclatura
`test_[funcion]_[escenario]_[resultado_esperado]`

## ADRs (Architecture Decision Records)
- Toda decisión técnica importante se documenta en docs/adr/
- Formato: número secuencial + título descriptivo
  Ejemplo: `0002-use-postgresql-over-dynamodb.md`
- Una vez aprobado, un ADR no se modifica — se supersede con uno nuevo
- Registrar siempre: contexto, opciones consideradas, decisión, consecuencias