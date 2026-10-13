# Mini Core MVC — Sistema de Comisiones

Proyecto académico para registrar ventas y calcular comisiones por vendedor y período. Incluye una interfaz en React y una API en Django REST Framework. El despliegue de demostración sirve ambos desde un único servicio gratuito en Render.

## Funcionalidades

- Registrar, listar y eliminar ventas desde la interfaz.
- Calcular comisiones entre dos fechas y consultar el detalle de cada vendedor.
- Aplicar la regla activa con el mayor monto mínimo que cumpla cada venta.
- Administrar vendedores y reglas mediante la API o el administrador de Django.

## Tecnologías y estructura

- Backend: Python, Django 5.2 LTS, Django REST Framework y SQLite en desarrollo y PostgreSQL en la nube.
- Frontend: React 19, Vite 6 y Axios.
- Despliegue: Docker, Gunicorn y WhiteNoise.

```text
Backend/       API, modelos, migraciones y comando seed_demo
Fronted/       Interfaz React (se conserva el nombre original de la carpeta)
Dockerfile     Compila React y prepara el servidor Django
render.yaml    Configuración del servicio gratuito
```

Django utiliza modelos, vistas y serializadores; React presenta la interfaz. Las consultas del frontend van a `/api/`: Vite las redirige en desarrollo y Django las atiende en el mismo dominio en el despliegue.

## Datos de demostración

El comando `seed_demo` crea **6 vendedores, 144 ventas y 6 reglas**, distribuidos en el mes actual y los cinco meses anteriores. Las fechas se calculan al cargar la demo usando la zona horaria de Ecuador; las ventas no tienen fechas futuras.

| Monto mínimo | Comisión | Estado |
| --- | --- | --- |
| $50 | 15 % | Inactiva; no participa |
| $100 | 2 % | Activa |
| $500 | 5 % | Activa |
| $1.000 | 8 % | Activa |
| $2.000 | 10 % | Activa |
| $5.000 | 12 % | Activa |

Hay ventas de $75 sin comisión y ventas exactamente en los límites. Ejemplos: $500 genera $25; $1.000 genera $80; $5.000 genera $600. La comisión se calcula por venta, no sobre el total mensual de un vendedor.

El comando solo carga datos cuando vendedores, reglas y ventas están vacíos. No sobrescribe datos existentes. En desarrollo se ejecuta manualmente; el contenedor lo ejecuta después de las migraciones cuando SEED_DEMO=true.

## Ejecutar en Windows

Requisitos: Python 3.13 o 3.14 y Node.js 22. Desde la raíz del repositorio, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r Backend/requirements.txt
cd Backend
..\.venv\Scripts\python.exe manage.py migrate
..\.venv\Scripts\python.exe manage.py seed_demo
..\.venv\Scripts\python.exe manage.py runserver
```

En una segunda terminal, desde la raíz:

```powershell
cd Fronted
npm.cmd ci
npm.cmd run dev
```

Abrir **http://localhost:3000**. API: **http://127.0.0.1:8000/api/**. Opcionalmente crear un administrador con `..\.venv\Scripts\python.exe manage.py createsuperuser` desde `Backend`.

Las variables se leen del entorno; no se cargan archivos `.env` automáticamente. El desarrollo usa SQLite local y DEBUG habilitado por defecto.


### Comportamiento de los datos

En la nube, los datos se guardan en PostgreSQL y se conservan al reiniciar el servidor. En desarrollo se usa SQLite local si no se proporciona DATABASE_URL. Todos los visitantes comparten los mismos datos.

La demo permite modificar información públicamente y no crea credenciales de administrador. Para un sistema real habría que añadir autenticación y permisos.

## API

| Ruta | Uso |
| --- | --- |
| `/api/vendedores/` | CRUD de vendedores |
| `/api/reglas/` | CRUD de reglas activas |
| `/api/ventas/` | CRUD de ventas |
| `/api/comisiones/calcular/` | POST con `fecha_inicio` y `fecha_fin` en formato `YYYY-MM-DD` |
| `/api/comisiones/resumen/` | Resumen general; admite filtros por fechas |
| `/api/comisiones-calculadas/` | Consulta de comisiones almacenadas |

El cálculo por período devuelve resultados sin guardarlos en `ComisionCalculada`. Las comisiones mostradas se calculan usando las reglas activas actuales, incluso para ventas de meses anteriores.

## Verificación

Desde `Backend`, ejecutar `..\.venv\Scripts\python.exe manage.py test`. Desde `Fronted`, ejecutar `npm.cmd run build`.




## Base de datos persistente

Esta versión utiliza PostgreSQL mediante `DATABASE_URL`. En desarrollo, sin esa variable y con DEBUG habilitado, utiliza SQLite. En el servidor, la URL es obligatoria: no hay retorno automático a una base temporal. Las migraciones crean el esquema; `SEED_DEMO=true` carga los datos de ejemplo solo si las tablas principales están vacías. Los reinicios no borran los datos de PostgreSQL. Las credenciales se mantienen fuera del repositorio.
