# ADR 0002 — Estructura IAM: permisos via grupos, no directos a usuarios

## Contexto
El usuario IAM `javier` necesita permisos para desarrollar el proyecto
(Lambda, S3, CloudWatch, RDS) y para gestionar sus propias credenciales.
La opción inicial fue adjuntar políticas directamente al usuario.

## Problema
Adjuntar políticas directamente a usuarios viola el principio de mínimo
privilegio organizacional: dificulta el onboarding de nuevos usuarios,
dispersa la gestión de permisos y es difícil de auditar.

## Decisión
Gestionar todos los permisos a través de grupos IAM:

- Grupo `iam-baseline` → política `IAMSelfServicePolicy`
  Para cualquier usuario de la cuenta: gestión de contraseña y MFA propios.

- Grupo `etl-serverless-devs` → política `ETLServerlessDevPolicy`
  Para developers del proyecto: acceso a Lambda, S3, CloudWatch, RDS e IAM
  acotado al proyecto.

## Consecuencias
- Onboarding de un nuevo developer: agregar al grupo, hereda permisos
- Cambio de permisos del proyecto: editar la política del grupo, aplica a todos
- `javier` no tiene ninguna política adjunta directamente