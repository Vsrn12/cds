# Backend Introduction - API REST con Flask

API REST construida con **Flask** que gestiona **tareas** y **usuarios**, con un frontend HTML integrado como panel de control.

## Tecnologías

- Python 3
- Flask
- Flask-CORS

## Instalación

```bash
pip install flask flask-cors
```

## Ejecución

```bash
python app.py
```

El servidor se inicia en `http://127.0.0.1:5000/`

## Endpoints

### Tareas (`/tasks`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/tasks` | Obtener todas las tareas |
| GET | `/tasks/<id>` | Obtener una tarea por ID |
| POST | `/tasks` | Crear una tarea |
| PUT | `/tasks/<id>` | Actualizar contenido de una tarea |
| PATCH | `/tasks/<id>/done` | Alternar estado completado/pendiente |
| DELETE | `/tasks/<id>` | Eliminar una tarea |

**Body para crear/actualizar tarea:**
```json
{
  "content": "Texto de la tarea"
}
```

### Usuarios (`/users`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/users` | Obtener todos los usuarios |
| GET | `/users/<id>` | Obtener un usuario por ID |
| POST | `/users` | Crear un usuario |
| PUT | `/users/<id>` | Actualizar datos de un usuario |
| DELETE | `/users/<id>` | Eliminar un usuario |

**Body para crear/actualizar usuario:**
```json
{
  "name": "Juan",
  "lastname": "Pérez",
  "address": {
    "city": "Arequipa",
    "country": "Perú",
    "code": "04000"
  }
}
```

## Frontend

Al acceder a `http://127.0.0.1:5000/` se sirve un panel de control HTML (`index.html`) que permite interactuar con la API desde el navegador: crear, editar, eliminar tareas y usuarios.

## Estructura del proyecto

```
├── app.py         # Servidor Flask con todos los endpoints
├── index.html     # Frontend (panel de control)
└── README.md
```

## Notas

- Los datos se almacenan en memoria (listas de Python), por lo que se pierden al reiniciar el servidor.
- CORS está habilitado para permitir peticiones desde cualquier origen.