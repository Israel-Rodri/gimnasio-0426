# Arquitectura del Proyecto - Sistema de Gestion de Gimnasio

## Descripcion General

API REST para la gestion de un gimnasio, desarrollada con **FastAPI** y **SQLModel** como ORM, conectada a una base de datos **PostgreSQL**. El sistema permite administrar sedes, miembros, entrenadores, planes de ejercicio, rutinas, evaluaciones fisicas, pagos y metodos de pago.

## Stack Tecnologico

| Componente | Tecnologia | Version |
|---|---|---|
| Framework Web | FastAPI | 0.135.3 |
| ORM | SQLModel (SQLAlchemy + Pydantic) | 0.0.38 |
| Base de Datos | PostgreSQL | - |
| Driver DB | psycopg2-binary | 2.9.11 |
| Validacion | Pydantic | 2.12.5 |
| Servidor ASGI | Uvicorn | 0.44.0 |

## Estructura de Directorios

```
gimnasio-0426/
├── main.py                        # Punto de entrada de la aplicacion
├── database.py                    # Configuracion de la conexion a BD
├── .env                           # Variables de entorno (DATABASE_URL)
├── requirements.txt               # Dependencias del proyecto
├── models/                        # Modelos ORM (tablas de la BD)
│   ├── __init__.py
│   ├── sedes.py
│   ├── miembros.py
│   ├── entrenadores.py
│   ├── planes.py
│   ├── rutinas.py
│   ├── evaluaciones.py
│   ├── pagos.py
│   ├── metodos_pago.py
│   ├── miembros_entrenadores_link.py
│   ├── pagos_planes_link.py
│   └── rutinas_planes_link.py
├── schemas/                       # Esquemas de validacion (DTOs)
│   ├── sedes.py
│   ├── miembros.py
│   ├── entrenadores.py
│   ├── planes.py
│   ├── rutinas.py
│   ├── evaluaciones.py
│   ├── pagos.py
│   ├── metodos_pago.py
│   ├── miembros_entrenadores_link.py
│   ├── pagos_planes_link.py
│   └── rutinas_planes_link.py
└── routers/                       # Controladores de rutas (endpoints)
    ├── sedes.py
    ├── miembros.py
    ├── entrenadores.py
    ├── planes.py
    ├── rutinas.py
    ├── evaluaciones.py
    ├── pagos.py
    ├── metodos_pago.py
    ├── miembros_entrenadores_link.py
    ├── pagos_planes_link.py
    └── rutinas_planes_link.py
```

## Patron Arquitectonico

El proyecto sigue una **arquitectura de 3 capas**:

### 1. Capa de Rutas (`routers/`)
- Maneja las solicitudes HTTP y las respuestas
- Contiene la logica de negocio y la validacion de entrada
- Gestiona las transacciones de base de datos mediante inyeccion de dependencias (`Depends(get_session)`)

### 2. Capa de Modelos (`models/`)
- Define las tablas de la base de datos y sus relaciones mediante SQLModel
- Mapeo ORM con SQLAlchemy bajo el capot
- Incluye tablas intermedias para relaciones muchos-a-muchos

### 3. Capa de Esquemas (`schemas/`)
- DTOs (Data Transfer Objects) para validacion de entrada
- Tres tipos por entidad:
  - `Create*`: Para la creacion de registros
  - `Update*`: Para actualizacion completa (PUT)
  - `Update*Optional`: Para actualizacion parcial (PATCH)

## Modelo de Base de Datos

### Diagrama de Entidades

```
┌──────────┐      ┌──────────────┐      ┌──────────────────────┐
│  Sedes   │1───N│  Miembros     │N───M│    Entrenadores       │
│          │      │               │      │                      │
│ id (PK)  │      │ id (PK)       │      │ id (PK)              │
│ nombre   │      │ ci (unique)   │      │ ci (unique)          │
│ direccion│      │ nombre        │      │ nombre               │
│ telefono │      │ apellido      │      │ apellido             │
│ horario  │      │ fecha_nac     │      │ especialidad         │
│ estado   │      │ telefono      │      │ certificaciones      │
└──────────┘      │ email         │      │ telefono             │
                  │ fecha_insc.   │      │ email                │
     ┌────────────│ estado        │      │ estado               │
     │            │ entrenador_id │      │ sede_id (FK)         │
     │            │ sede_id (FK)  │      └──────────────────────┘
     │            └───────────────┘               │
     │                   │                         │
     │                   │1                        │1
     │                   │                         │
     │              ┌────┴─────┐            ┌──────┴──────────────┐
     │              │  Planes  │            │ EvaluacionesFisicas │
     │              │          │            │                     │
     │              │ id (PK)  │            │ id (PK)             │
     │              │ nombre   │            │ peso                │
     │              │ duracion │            │ talla               │
     │              │ precio   │            │ imc (calculado)     │
     │              │ benefic. │            │ estado_imc          │
     │              │ estado   │            │ medidas (JSONB)     │
     │              │ miemb_id │            │ observaciones       │
     │              └────┬─────┘            │ fecha_evaluacion    │
     │                   │                  │ miembro_id (FK)     │
     │              N    │    N             │ entrenador_id (FK)  │
     │              │    │    │             │ estado              │
     │         ┌────┘    │    └────┐        └─────────────────────┘
     │         │         │         │
     │    ┌────┴───┐     │    ┌────┴────┐
     │    │ Pagos  │     │    │ Rutinas │
     │    │        │     │    │         │
     │    │ id(PK) │     │    │ id(PK)  │
     │    │ mensual│     │    │ nombre  │
     │    │ fecha  │     │    │ objetivo│
     │    │ monto  │     │    │ nivel   │
     │    │ refer. │     │    │ descrip.│
     │    │ estado │     │    │ duracion│
     │    │ miemb. │     │    │ estado  │
     │    │ metodo │     │    └─────────┘
     │    └────────┘
     │         │
     │    ┌────┴──────────┐
     │    │ MetodosPago   │
     │    │               │
     │    │ id (PK)       │
     │    │ nombre(unique)│
     │    │ estado        │
     │    └───────────────┘
```

### Relaciones

| Relacion | Tipo | Tabla Intermedia |
|---|---|---|
| Sede -> Miembros | 1:N | - |
| Sede -> Entrenadores | 1:N | - |
| Miembro -> Planes | 1:N | - |
| Miembro -> Pagos | 1:N | - |
| Miembro -> EvaluacionesFisicas | 1:N | - |
| Entrenador -> EvaluacionesFisicas | 1:N | - |
| MetodoPago -> Pagos | 1:N | - |
| Miembros <-> Entrenadores | N:M | `miembros_entrenadores_link` |
| Pagos <-> Planes | N:M | `pagos_planes_link` |
| Rutinas <-> Planes | N:M | `rutinas_planes_link` |

### Tipos de Datos Especiales

- **JSONB**: Usado en `horario` (Sedes) y `medidas` (EvaluacionesFisicas) para datos flexibles
- **ARRAY(String)**: Usado en `certificaciones` (Entrenadores) y `beneficios` (Planes)
- **Soft Delete**: Todas las entidades usan un campo `estado` (bool) para eliminacion logica

## Endpoints de la API

### Sedes (`/sede`)
| Metodo | Ruta | Descripcion |
|---|---|---|
| POST | `/` | Crear sede |
| GET | `/` | Obtener sedes activas |
| GET | `/all/` | Obtener todas las sedes |
| GET | `/filter/` | Filtrar sedes |
| GET | `/{sede_id}/` | Obtener sede por ID |
| GET | `/{sede_id}/miembros/` | Obtener miembros de la sede |
| GET | `/{sede_id}/entrenadores/` | Obtener entrenadores de la sede |
| PUT | `/update/{sede_id}/` | Actualizar sede (completo) |
| PATCH | `/update/{sede_id}/` | Actualizar sede (parcial) |
| DELETE | `/{sede_id}/` | Inactivar sede |
| PATCH | `/{sede_id}/` | Activar sede |

### Miembros (`/miembro`)
| Metodo | Ruta | Descripcion |
|---|---|---|
| POST | `/` | Crear miembro |
| GET | `/` | Obtener miembros activos |
| GET | `/all/` | Obtener todos los miembros |
| GET | `/filter/` | Filtrar miembros |
| GET | `/{miembro_ci}/` | Obtener miembro por CI |
| GET | `/{miembro_ci}/evaluaciones/` | Evaluaciones del miembro |
| GET | `/{miembro_ci}/planes/` | Planes del miembro |
| GET | `/{miembro_ci}/pagos/` | Pagos del miembro |
| GET | `/{miembro_ci}/entrenadores/` | Entrenadores del miembro |
| PUT | `/update/{miembro_ci}/` | Actualizar miembro (completo) |
| PATCH | `/update/{miembro_ci}/` | Actualizar miembro (parcial) |
| DELETE | `/{miembro_ci}/` | Inactivar miembro |
| PATCH | `/{miembro_ci}/` | Activar miembro |

### Entrenadores (`/entrenador`)
| Metodo | Ruta | Descripcion |
|---|---|---|
| POST | `/` | Crear entrenador |
| GET | `/` | Obtener entrenadores activos |
| GET | `/all/` | Obtener todos los entrenadores |
| GET | `/filter/` | Filtrar entrenadores |
| GET | `/{entrenador_ci}/` | Obtener entrenador por CI |
| GET | `/{entrenador_ci}/miembros/` | Miembros del entrenador |
| PUT | `/update/{entrenador_ci}/` | Actualizar entrenador (completo) |
| PATCH | `/update/{entrenador_ci}/` | Actualizar entrenador (parcial) |
| DELETE | `/{entrenador_ci}/` | Inactivar entrenador |
| PATCH | `/{entrenador_ci}/` | Activar entrenador |

### Planes (`/plan`)
| Metodo | Ruta | Descripcion |
|---|---|---|
| POST | `/` | Crear plan |
| GET | `/` | Obtener planes activos |
| GET | `/all/` | Obtener todos los planes |
| GET | `/filter/` | Filtrar planes |
| GET | `/{plan_id}/` | Obtener plan por ID |
| GET | `/{plan_id}/pagos/` | Pagos del plan |
| GET | `/{plan_id}/rutinas/` | Rutinas del plan |
| PUT | `/update/{plan_id}/` | Actualizar plan (completo) |
| PATCH | `/update/{plan_id}/` | Actualizar plan (parcial) |
| DELETE | `/{plan_id}/` | Inactivar plan |
| PATCH | `/{plan_id}/` | Activar plan |

### Rutinas (`/rutina`)
| Metodo | Ruta | Descripcion |
|---|---|---|
| POST | `/` | Crear rutina |
| GET | `/` | Obtener rutinas activas |
| GET | `/all/` | Obtener todas las rutinas |
| GET | `/filter/` | Filtrar rutinas |
| GET | `/{rutina_id}/` | Obtener rutina por ID |
| GET | `/{rutina_id}/planes/` | Planes de la rutina |
| PUT | `/update/{rutina_id}/` | Actualizar rutina (completo) |
| PATCH | `/update/{rutina_id}/` | Actualizar rutina (parcial) |
| DELETE | `/{rutina_id}/` | Inactivar rutina |
| PATCH | `/{rutina_id}/` | Activar rutina |

### Evaluaciones Fisicas (`/evaluacion-fisica`)
| Metodo | Ruta | Descripcion |
|---|---|---|
| POST | `/` | Crear evaluacion (calcula IMC automaticamente) |
| GET | `/` | Obtener evaluaciones activas |
| GET | `/all/` | Obtener todas las evaluaciones |
| GET | `/filter/` | Filtrar por CI de miembro o fecha |
| PUT | `/update/{evaluacion_id}/` | Actualizar evaluacion (recalcula IMC) |
| PATCH | `/update/{evaluacion_id}/` | Actualizar evaluacion parcial |
| DELETE | `/{evaluacion_id}/` | Inactivar evaluacion |
| PATCH | `/{evaluacion_id}/` | Activar evaluacion |

### Pagos (`/pago`)
| Metodo | Ruta | Descripcion |
|---|---|---|
| POST | `/` | Crear pago |
| GET | `/` | Obtener pagos activos |
| GET | `/all/` | Obtener todos los pagos |
| GET | `/filter/` | Filtrar pagos |
| GET | `/{pago_id}/` | Obtener pago por ID |
| GET | `/{pago_id}/planes/` | Planes del pago |
| GET | `/{pago_id}/metodo/` | Metodo de pago |
| DELETE | `/{pago_id}/` | Inactivar pago |
| PATCH | `/{pago_id}/` | Activar pago |

### Metodos de Pago (`/metodo-pago`)
| Metodo | Ruta | Descripcion |
|---|---|---|
| POST | `/` | Crear metodo de pago |
| GET | `/` | Obtener metodos activos |
| GET | `/all/` | Obtener todos los metodos |
| GET | `/filter/` | Filtrar por nombre |
| GET | `/{metodo_id}/` | Obtener metodo por ID |
| PUT | `/update/{metodo_id}/` | Actualizar metodo |
| DELETE | `/{metodo_id}/` | Inactivar metodo |
| PATCH | `/{metodo_id}/` | Activar metodo |

### Enlaces N:M
| Metodo | Ruta | Descripcion |
|---|---|---|
| POST | `/miembros-entrenadores/` | Vincular miembro con entrenador |
| GET | `/miembros-entrenadores/` | Listar vinculos miembro-entrenador |
| POST | `/pagos-planes/` | Vincular pago con plan |
| GET | `/pagos-planes/` | Listar vinculos pago-plan |
| POST | `/rutinas-planes/` | Vincular rutina con plan |
| GET | `/rutinas-planes/` | Listar vinculos rutina-plan |

## Configuracion

### Variables de Entorno (`.env`)
```
DATABASE_URL = "postgresql+psycopg2://usuario:password@localhost:5432/gimnasio"
```

### Ejecucion
```bash
# Instalar dependencias
pip install -r requirements.txt

# Crear la base de datos PostgreSQL
createdb gimnasio

# Ejecutar el servidor
uvicorn main:app --reload
```

La documentacion interactiva de la API estara disponible en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Convenciones del Proyecto

- **Eliminacion logica**: Todas las entidades usan `estado` (True/False) en lugar de eliminacion fisica
- **Identificacion**: Miembros y Entrenadores se identifican por `ci` (cedula) en las rutas, las demas entidades por `id`
- **Validacion**: Los esquemas de entrada validan los datos antes de llegar a la capa de persistencia
- **IMC automatico**: Las evaluaciones fisicas calculan automaticamente el IMC y su clasificacion
