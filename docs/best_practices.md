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

### Principios generales
- Principio de mínimo privilegio en IAM: solo los permisos estrictamente necesarios
- Nunca usar credenciales de root para trabajo diario
- Nunca crear access keys para el usuario root
- Secrets en AWS Secrets Manager para producción
- Variables de entorno para desarrollo local — nunca hardcodeadas
- Nunca dar permisos directamente a usuarios — siempre a través de grupos o roles

### iam:PassRole — acción sensible
`iam:PassRole` permite asignar un rol a un servicio AWS. Es una acción
crítica de seguridad porque puede usarse para escalar privilegios.

**El riesgo:** si un usuario tiene PassRole sin restricciones, puede crear
una función Lambda, asignarle un rol con más permisos de los que él tiene,
y ejecutar esa Lambda para acceder a recursos que normalmente no podría tocar.
Esto se llama escalación de privilegios y es difícil de detectar porque
en los logs aparece el servicio (Lambda) como actor, no el usuario.

**La solución:** siempre limitar PassRole con la condición `iam:PassedToService`:

```json
{
  "Effect": "Allow",
  "Action": "iam:PassRole",
  "Resource": "arn:aws:iam::ACCOUNT_ID:role/*",
  "Condition": {
    "StringEquals": {
      "iam:PassedToService": "lambda.amazonaws.com"
    }
  }
}
```

Esto limita PassRole exclusivamente al servicio Lambda — no puede usarse
para asignar roles a EC2, RDS, ni ningún otro servicio.

### Resource: "*" vs ARN específico
- Usar ARN específico cuando la acción opera sobre un recurso concreto con nombre
  (crear un rol, leer un archivo, modificar una función)
- Usar `"*"` cuando la acción opera sobre toda la cuenta y no tiene recurso específico
  (listar políticas, listar roles, listar buckets)
- Señal de error: si pones ARN específico y AWS da acceso denegado,
  probablemente esa acción requiere `"*"`
- Consultar siempre la documentación de acciones IAM del servicio para confirmar

### Usuarios nuevos en AWS
- Un usuario nuevo no tiene ningún permiso por defecto — ni siquiera puede
  ver sus propias credenciales o configurar su MFA
- Siempre crear una política base de self-service que permita al usuario
  gestionar sus propias credenciales y configurar su MFA
- El MFA debe configurarlo el propio usuario desde su sesión, no el administrador

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

**Tests de integración** — prueban que dos o más componentes funcionan juntos.
Son más lentos, pueden requerir conexión a servicios reales o mocks de ellos.
Cubren el flujo completo: Lambda recibe evento → lee S3 → inserta en DB.

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