# Registro de Cambios Realizados

## Response Schemas y Tipado de Endpoints

### 28. Creacion de Response Schemas para todos los endpoints
**Archivo nuevo:** `schemas/base.py`
**Archivos modificados:** `schemas/sedes.py`, `schemas/entrenadores.py`, `schemas/miembros.py`, `schemas/evaluaciones.py`, `schemas/metodos_pago.py`, `schemas/planes.py`, `schemas/rutinas.py`, `schemas/pagos.py`, `routers/sedes.py`, `routers/entrenadores.py`, `routers/miembros.py`, `routers/evaluaciones.py`, `routers/metodos_pago.py`, `routers/planes.py`, `routers/rutinas.py`, `routers/pagos.py`
**Problema:** Los endpoints retornaban el modelo SQLModel completo, exponiendo el campo `estado` (soft-delete interno) y potencialmente relaciones de la BD en las respuestas de la API.
**Solucion:**
- Se creo `MessageResponse[T]`, un wrapper generico Pydantic para el patron `{"message": str, "detail": T}` usado en la mayoria de endpoints.
- Se crearon Response schemas para cada entidad (`SedeResponse`, `EntrenadorResponse`, `MiembroResponse`, `EvaluacionFisicaResponse`, `MetodoPagoResponse`, `PlanResponse`, `RutinaResponse`, `PagoResponse`) que excluyen el campo `estado` y las relaciones.
- Se aplico `response_model` a todos los endpoints de todos los routers para tipar correctamente las respuestas en Swagger/OpenAPI.
- `estado_imc` se conserva en `EvaluacionFisicaResponse` ya que es un dato calculado, no el campo de soft-delete.
- Los endpoints GET por ID que retornaban el objeto directamente ahora usan el patron `MessageResponse` para consistencia.

## Refactorizacion de Tablas Relacionales

### 27. Eliminacion de endpoints y schemas dedicados para link tables
**Archivos eliminados:** `schemas/pagos_planes_link.py`, `schemas/rutinas_planes_link.py`, `schemas/miembros_entrenadores_link.py`, `routers/pagos_planes_link.py`, `routers/rutinas_planes_link.py`, `routers/miembros_entrenadores_link.py`
**Archivos modificados:** `main.py`, `routers/pagos.py`, `routers/planes.py`, `routers/miembros.py`
**Problema:** Las tablas relacionales puras (sin campos propios) tenian schemas y routers dedicados innecesarios. Los modelos ya tenian `Relationship` con `link_model` configurado, lo que permite usar `.append()` directamente.
**Solucion:** Se crearon sub-endpoints RESTful en los routers existentes:
- `POST /pago/{pago_id}/planes/{plan_id}/` - Asociar plan a pago
- `POST /plan/{plan_id}/rutinas/{rutina_id}/` - Asociar rutina a plan
- `POST /miembro/{miembro_ci}/entrenadores/{entrenador_ci}/` - Asociar entrenador a miembro
Se eliminaron 6 archivos (3 schemas + 3 routers) y sus registros en `main.py`.

## Bugs Criticos Corregidos

### 1. Parametros de ruta no coincidian con los parametros de funcion
**Archivos:** `routers/sedes.py`, `routers/planes.py`, `routers/metodos_pago.py`, `routers/evaluaciones.py`
**Problema:** Las rutas usaban `{id}` pero las funciones declaraban parametros como `sede_id`, `plan_id`, etc. En FastAPI, el nombre del parametro de ruta debe coincidir con el nombre del parametro de la funcion. Esto causaba que el parametro de ruta se ignorara y el parametro de funcion se tratara como query parameter, resultando en errores 422.
**Solucion:** Se unificaron los nombres: `{sede_id}`, `{plan_id}`, `{metodo_id}`, `{evaluacion_id}`, `{rutina_id}`, `{pago_id}` en rutas y funciones.

### 2. Logica invertida en `metodos_pago.py` (inactivar/activar)
**Archivo:** `routers/metodos_pago.py`
**Problema (linea 84 original):** `if metodo_pago.estado:` con mensaje "ya se encuentra inactivo" - la condicion estaba invertida. Si `estado` es `True`, el metodo esta **activo**, no inactivo.
**Problema (linea 98 original):** `if not metodo_pago.estado:` con mensaje "ya se encuentra inactivo" en el endpoint de **activar** - misma inversion.
**Solucion:** Corregidas las condiciones: `if not metodo_pago.estado` para inactivar, `if metodo_pago.estado` para activar.

### 3. Logica invertida en `pagos.py` (get_planes_pago)
**Archivo:** `routers/pagos.py` (linea 91 original)
**Problema:** `if planes:` lanzaba excepcion "No existen planes asociados..." - es decir, si **si** habia planes, decia que no habia. Debia ser `if not planes:`.
**Solucion:** Corregido a `if not planes:`.

### 4. Uso de `ilike()` en campos no-string
**Archivos:** `routers/miembros.py`, `routers/entrenadores.py`, `routers/pagos.py`, `routers/planes.py`
**Problema:** Se usaba `.ilike()` (busqueda de texto parcial) en campos de tipo `int`, `float` y `date` como `entrenador_id`, `sede_id`, `ci`, `mensualidades`, `fecha`, `monto`, `precio`. `ilike` solo funciona con columnas de texto.
**Solucion:** Reemplazado por `==` (igualdad exacta) para campos numericos y de fecha.

### 5. `query.limit()` sin reasignacion
**Archivos:** `routers/miembros.py`, `routers/entrenadores.py`, `routers/pagos.py`, `routers/rutinas.py`, `routers/evaluaciones.py`
**Problema:** Se escribia `query.limit(limite)` sin `query =`, por lo que el limite nunca se aplicaba realmente (SQLAlchemy devuelve un nuevo query, no modifica el existente).
**Solucion:** Cambiado a `query = query.limit(limite)`.

### 6. Referencia a campos inexistentes en modelos
**Archivo:** `routers/evaluaciones.py`
**Problema:** El filtro usaba `EvaluacionFisica.miembro_ci` pero el modelo solo tiene `miembro_id`. Tambien el update referenciaba `evaluacion.miembro_ci`.
**Solucion:** El filtro ahora busca primero el miembro por CI y luego filtra evaluaciones por `miembro_id`. Se elimino `miembro_ci` de los updates ya que no tiene sentido cambiar el miembro de una evaluacion.

**Archivo:** `routers/rutinas.py`
**Problema:** El filtro usaba `Rutina.plan_id` pero el modelo `Rutina` no tiene ese campo (la relacion es M:N via tabla intermedia).
**Solucion:** Se elimino el filtro por `plan_id` del endpoint de filtro de rutinas.

**Archivo:** `routers/miembros.py`
**Problema:** El update y filtro referenciaban `Miembro.plan_id` que no existe en el modelo.
**Solucion:** Se elimino `plan_id` de los schemas de update y del filtro.

### 7. Crash al crear miembro con entrenador_ci nulo
**Archivo:** `routers/miembros.py` (linea 39 original)
**Problema:** `id_entrenador.id` fallaba si no se encontraba entrenador (None.id). Ademas, si `entrenador_ci` era None, se intentaba buscar igualmente.
**Solucion:** Se agrega verificacion: solo busca entrenador si `entrenador_ci` no es None, y valida que exista antes de acceder a `.id`.

### 8. Calculo incorrecto de estado_imc en evaluaciones
**Archivo:** `routers/evaluaciones.py` (linea 49 original)
**Problema:** `calcular_estado_imc(data.imc)` usaba `data.imc` que es `None` por defecto, en lugar del IMC recien calculado.
**Solucion:** Se calcula primero `imc = calcular_imc(...)` y luego `estado_imc = calcular_estado_imc(imc)`.

### 9. Decorador faltante en rutinas_planes_link
**Archivo:** `routers/rutinas_planes_link.py` (linea 38 original)
**Problema:** `router.get("/")` sin `@` - la funcion `get_all_rutinas_planes_link` nunca se registraba como endpoint.
**Solucion:** Corregido a `@router.get("/")`.

### 10. Falta `precio` al crear plan
**Archivo:** `routers/planes.py`
**Problema:** Al construir `Plan(...)` faltaba la asignacion `precio = data.precio`, por lo que el precio no se guardaba.
**Solucion:** Agregado `precio = data.precio` al constructor.

### 11. Condicion de filtro con OR en lugar de AND en pagos
**Archivo:** `routers/pagos.py` (linea 104 original)
**Problema:** `if not ... or not ... or not ... or not ...` - esta condicion con `or` es verdadera cuando **cualquier** campo falta, lo que significa que **siempre** lanza error a menos que **todos** los campos esten presentes.
**Solucion:** Cambiado a `if not ... and not ... and not ... and not ...` (solo lanza error si **ningun** campo fue proporcionado).

### 12. Mensajes incorrectos en pagos_planes_link
**Archivo:** `routers/pagos_planes_link.py`
**Problema:** Los mensajes de error y exito referenciaban "rutina" en lugar de "pago" (ej: `pago.nombre` no existe, `Pago` no tiene atributo `nombre`).
**Solucion:** Corregidos los mensajes para usar `pago.referencia`.

## Mejoras de Esquemas (schemas/)

### 13. Atributos de BD en esquemas de validacion
**Archivos:** `schemas/sedes.py`, `schemas/entrenadores.py`, `schemas/planes.py`, `schemas/evaluaciones.py`, `schemas/metodos_pago.py`
**Problema:** Los schemas usaban `sa_type=JSONB`, `sa_column=Column(ARRAY(String))`, `unique=True`, `index=True`. Estos son atributos de SQLAlchemy para la BD, no deben estar en esquemas Pydantic de validacion.
**Solucion:** Eliminados los atributos especificos de BD de todos los schemas.

### 14. Campos imc/estado_imc en schema de creacion de evaluacion
**Archivo:** `schemas/evaluaciones.py`
**Problema:** `CreateEvaluacionFisica` incluia `imc` y `estado_imc` como opcionales. Estos campos se calculan automaticamente y no deben ser enviados por el cliente.
**Solucion:** Eliminados `imc` y `estado_imc` del schema de creacion. Agregado `entrenador_id` que era necesario pero faltaba.

### 15. Campo miembro_ci en schemas de update de evaluacion
**Archivo:** `schemas/evaluaciones.py`
**Problema:** Los schemas de update incluian `miembro_ci` e `imc`/`estado_imc`, campos que se calculan automaticamente o no deben modificarse.
**Solucion:** Eliminados los campos que no deben actualizarse manualmente.

### 16. Campo plan_id en rutinas
**Archivo:** `schemas/rutinas.py`
**Problema:** `CreateRutina` y `UpdateRutina` incluian `plan_id`, pero `Rutina` no tiene FK directa a `Plan` (es relacion M:N via tabla intermedia).
**Solucion:** Eliminado `plan_id` de todos los schemas de rutina. La vinculacion se hace via el endpoint `/rutinas-planes/`.

## Mejoras Generales

### 17. main.py - Deprecacion de on_event
**Archivo:** `main.py`
**Problema:** `@app.on_event("startup")` esta deprecado desde FastAPI 0.109+.
**Solucion:** Reemplazado por `lifespan` (asynccontextmanager).

### 18. requirements.txt - Dependencias
**Archivo:** `requirements.txt`
**Problema:** Faltaba `python-dotenv` (usado en `database.py`). Habia dependencias no utilizadas: `bcrypt`, `passlib`, `python-jose`, `cryptography`, `annotated-doc`.
**Solucion:** Agregado `python-dotenv`. Eliminadas las dependencias no utilizadas.

### 19. Validaciones innecesarias de `if not data`
**Archivos:** Todos los routers
**Problema:** `if not data: raise HTTPException(...)` al inicio de los POST. Pydantic ya valida que el body no sea vacio; si falta, FastAPI devuelve 422 automaticamente.
**Solucion:** Eliminadas las validaciones redundantes.

### 20. Validaciones innecesarias de `if not id`
**Archivos:** Todos los routers
**Problema:** `if not sede_id: raise HTTPException(...)` - Los parametros de ruta siempre existen (FastAPI los requiere). Ademas, `not 0` es `True`, lo que rechazaria incorrectamente el ID 0.
**Solucion:** Eliminadas las validaciones redundantes de parametros de ruta.

### 21. Uso de `if data.campo:` en lugar de `if data.campo is not None:`
**Archivos:** Todos los routers con PATCH
**Problema:** `if data.nombre:` evaluaria como `False` para strings vacios, `0`, etc. En un PATCH, el cliente puede querer establecer un valor a `""` o `0`.
**Solucion:** Cambiado a `if data.campo is not None:` para distinguir entre "no enviado" (None) y "enviado con valor falsy".

### 22. Typos corregidos en mensajes de error
- "enceuntra" -> "encuentra"
- "miembrosa" -> "miembros"
- "registrtado" -> "registrado"
- "aosicado" -> "asociado"
- "encutra" -> "encuentra"
- "ecuentran" -> "encuentran"
- "encuetra" -> "encuentra"
- "actiualizar" -> "actualizar"
- "sdio" -> "sido"
- "existosa" -> "exitosa"
- "sida" -> "sido"
- "econtrada" -> "encontrada"
- "nigún" -> "ningun"
- "seministrada" -> "suministrada"
- "exite" -> "existe"

### 23. Mensaje incompleto en creacion de miembro
**Archivo:** `routers/miembros.py` (linea 28 original)
**Problema:** `f"La sede con la ID {data.sede_id}"` - mensaje incompleto, no dice que esta mal.
**Solucion:** `f"La sede con la ID {data.sede_id} no se encuentra registrada"`.

### 24. Falta de endpoints de inactivar/activar en pagos
**Archivo:** `routers/pagos.py`
**Problema:** No habia endpoints para inactivar/activar pagos (DELETE y PATCH).
**Solucion:** Agregados endpoints de inactivacion y activacion.

### 25. UpdateSede.horario era requerido
**Archivo:** `schemas/sedes.py`
**Problema:** `horario: Dict` en `UpdateSede` era obligatorio, pero deberia ser opcional ya que no todas las sedes necesitan horario definido.
**Solucion:** Cambiado a `Optional[Dict]`.

### 26. Filtro de metodos de pago mejorado
**Archivo:** `routers/metodos_pago.py`
**Problema:** El filtro usaba `==` (igualdad exacta) en lugar de `ilike` (busqueda parcial), y no aplicaba limite.
**Solucion:** Cambiado a `ilike` con limite.
