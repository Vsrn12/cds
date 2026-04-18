# Practica 2 - Backend CRUD completo con Flask + MySQL + SQLAlchemy

Este proyecto implementa una API REST de administrador de tareas sin frontend. Usa Flask como framework web, MySQL como motor de base de datos y SQLAlchemy como ORM para mapear objetos Python a tablas SQL.

## Que construye esta practica

La API expone estos endpoints:

- `GET /tasks` para listar tareas.
- `GET /tasks/<id>` para obtener una tarea puntual.
- `POST /tasks` para crear tareas.
- `PUT /tasks/<id>` para actualizar tareas.
- `DELETE /tasks/<id>` para eliminar tareas.
- `GET /tasks/done` para listar tareas completadas.
- `GET /tasks/pending` para listar tareas pendientes.
- `GET /healthz` para verificar que la API responde.

## Estructura del proyecto

```text
Practica2/
|-- .env
|-- .env.example
|-- .gitignore
|-- app.py
|-- config.py
|-- db_setup.py
|-- models.py
|-- README.md
`-- requirements.txt
```

## 1. Crear y correr MySQL con Docker

```bash
docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=my-secret-pw -p 3306:3306 -d mysql:latest
```

Este comando:

- crea un contenedor llamado `mysql-container`.
- define la clave del usuario `root`.
- expone MySQL en el puerto `3306`.
- deja el contenedor ejecutandose en segundo plano.

## 2. Crear la base de datos

Entra al cliente MySQL:

```bash
docker exec -it mysql-container mysql -u root -p
```

Luego ejecuta:

```sql
CREATE DATABASE IF NOT EXISTS task_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

`utf8mb4` permite guardar texto Unicode completo.

## 3. Preparar el entorno con Anaconda

```bash
conda create -n flask_crud python=3.11 -y
conda activate flask_crud
pip install -r requirements.txt
```

Si quieres utilidades extra para desarrollo:

```bash
pip install ipython
```

### Por que se instala cada paquete

- `flask`: framework web para crear la API.
- `flask_sqlalchemy`: integra SQLAlchemy con Flask.
- `pymysql`: driver de MySQL en Python.
- `python-dotenv`: carga variables desde `.env`.

## 4. Configuracion local

El archivo `.env` contiene la configuracion local:

```env
DB_USER=root
DB_PASSWORD=my-secret-pw
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=task_db
FLASK_ENV=development
SECRET_KEY=cambia-esta-clave-en-produccion
```

### Explicacion de cada variable

- `DB_USER`: usuario de MySQL.
- `DB_PASSWORD`: clave del usuario anterior.
- `DB_HOST`: host al que Flask se conectara.
- `DB_PORT`: puerto de MySQL.
- `DB_NAME`: nombre de la base de datos.
- `FLASK_ENV`: modo de trabajo de Flask.
- `SECRET_KEY`: clave usada por Flask para firmar datos internos.

## 5. Explicacion del codigo por archivo

### `config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()
```

- `import os` permite leer variables de entorno.
- `load_dotenv()` carga automaticamente el contenido de `.env` en el proceso actual.

```python
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "task_db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
```

- `os.getenv(...)` intenta leer la variable y, si no existe, usa un valor por defecto.
- Esto evita que la aplicacion falle por una variable faltante en desarrollo.

```python
SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

- `mysql+pymysql://` indica a SQLAlchemy que debe usar MySQL con el driver PyMySQL.
- `SQLALCHEMY_TRACK_MODIFICATIONS = False` desactiva una funcionalidad que no usamos y ahorra memoria.

### `models.py`

```python
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

- `datetime` se usa para sellos de tiempo.
- `db = SQLAlchemy()` crea la instancia global del ORM que luego se enlaza con Flask.

```python
class Task(db.Model):
    __tablename__ = "tasks"
```

- `Task` representa una tabla de la base de datos.
- `__tablename__` fuerza el nombre exacto de la tabla: `tasks`.

```python
id = db.Column(db.Integer, primary_key=True)
content = db.Column(db.String(200), nullable=False)
done = db.Column(db.Boolean, default=False, nullable=False)
```

- `id` es la llave primaria.
- `content` guarda el texto de la tarea y no acepta `NULL`.
- `done` indica si la tarea fue completada.

```python
created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
updated_at = db.Column(
    db.DateTime,
    default=datetime.utcnow,
    onupdate=datetime.utcnow,
    nullable=False,
)
```

- `created_at` toma la fecha actual cuando se inserta el registro.
- `updated_at` se actualiza automaticamente cuando el registro cambia.

```python
def to_dict(self):
    return {
        "id": self.id,
        "content": self.content,
        "done": self.done,
        "created_at": self.created_at.isoformat(),
        "updated_at": self.updated_at.isoformat(),
    }
```

- Este metodo convierte el objeto a un diccionario JSON-friendly.
- `isoformat()` serializa fechas en un formato estandar para APIs.

### `app.py`

```python
from flask import Flask, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
import config
from models import Task, db
```

- `Flask` crea la app.
- `jsonify` produce respuestas JSON correctas.
- `request` lee el body enviado por el cliente.
- `SQLAlchemyError` permite capturar fallos del ORM.

```python
def create_app():
    app = Flask(__name__)
```

- Se usa el patron app factory.
- Esto facilita pruebas y despliegue porque la app se construye con una funcion.

```python
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config["SECRET_KEY"] = config.SECRET_KEY
db.init_app(app)
```

- Aqui Flask recibe la configuracion centralizada.
- `db.init_app(app)` enlaza la instancia de SQLAlchemy con esta aplicacion.

```python
@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Recurso no encontrado"}), 404
```

- Este manejador hace que los errores 404 tambien respondan en JSON.

```python
@app.route("/tasks", methods=["GET"])
def list_tasks():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks]), 200
```

- Consulta todas las tareas.
- `order_by(...desc())` devuelve primero las mas recientes.
- El listado se serializa con `to_dict()`.

```python
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = db.session.get(Task, task_id)
```

- `<int:task_id>` convierte el parametro de la URL en entero.
- `db.session.get(...)` busca por llave primaria usando la sesion actual.

```python
payload = request.get_json(silent=True) or {}
content = str(payload.get("content", "")).strip()
```

- `get_json(silent=True)` evita lanzar una excepcion si el body no es JSON valido.
- `strip()` elimina espacios al inicio y al final.

```python
if not content:
    return jsonify({"error": "El campo 'content' es obligatorio y no puede estar vacio."}), 400
```

- Esta validacion impide crear tareas vacias.
- `400` significa error del cliente por datos invalidos.

```python
try:
    db.session.add(task)
    db.session.commit()
except SQLAlchemyError:
    db.session.rollback()
```

- `add()` registra el objeto para insercion.
- `commit()` confirma la transaccion.
- `rollback()` revierte cambios si ocurre un error.

```python
if "content" in payload:
    ...
if "done" in payload:
    ...
```

- Esto permite actualizacion parcial con `PUT` sobre los campos enviados.

```python
tasks = Task.query.filter_by(done=True).order_by(Task.updated_at.desc()).all()
```

- `filter_by(done=True)` filtra solo tareas completadas.
- El mismo patron se usa para tareas pendientes con `done=False`.

### `db_setup.py`

```python
from app import create_app
from models import db

app = create_app()

with app.app_context():
    db.create_all()
```

- Se construye la app.
- `app.app_context()` activa el contexto que Flask necesita para trabajar con extensiones.
- `db.create_all()` crea las tablas definidas en los modelos si aun no existen.

## 6. Inicializar la base de datos

```bash
python db_setup.py
```

Si todo esta bien, veras un mensaje indicando que las tablas fueron creadas o ya existian.

## 7. Ejecutar la API

```bash
python app.py
```

La API quedara disponible en:

```text
http://127.0.0.1:5000
```

## 8. Pruebas con cURL

### Crear tarea

```bash
curl -X POST http://127.0.0.1:5000/tasks -H "Content-Type: application/json" -d '{"content": "Escribir API con Flask y MySQL"}'
```

### Listar tareas

```bash
curl http://127.0.0.1:5000/tasks
```

### Obtener una tarea por ID

```bash
curl http://127.0.0.1:5000/tasks/1
```

### Actualizar tarea

```bash
curl -X PUT http://127.0.0.1:5000/tasks/1 -H "Content-Type: application/json" -d '{"done": true, "content": "Escribir API con Flask y MySQL actualizada"}'
```

### Eliminar tarea

```bash
curl -X DELETE http://127.0.0.1:5000/tasks/1
```

### Listar completadas y pendientes

```bash
curl http://127.0.0.1:5000/tasks/done
curl http://127.0.0.1:5000/tasks/pending
```

## 9. Como el ORM se traduce a SQL

### Crear

```python
task = Task(content="Ejemplo")
db.session.add(task)
db.session.commit()
```

SQL aproximado:

```sql
INSERT INTO tasks (content, done, created_at, updated_at)
VALUES ('Ejemplo', 0, NOW(), NOW());
```

### Leer

```python
Task.query.filter_by(done=False).all()
```

SQL aproximado:

```sql
SELECT * FROM tasks WHERE done = 0;
```

### Actualizar

```python
task.done = True
db.session.commit()
```

SQL aproximado:

```sql
UPDATE tasks SET done = 1, updated_at = NOW() WHERE id = ?;
```

### Eliminar

```python
db.session.delete(task)
db.session.commit()
```

SQL aproximado:

```sql
DELETE FROM tasks WHERE id = ?;
```

## 10. Problemas comunes

### `ModuleNotFoundError: No module named 'pymysql'`

Instala dependencias:

```bash
pip install -r requirements.txt
```

### Error `Access denied`

Revisa el usuario, la clave y el puerto en `.env`.

### No conecta con MySQL

Confirma que el contenedor este arriba:

```bash
docker ps
```

### `db.create_all()` no crea tablas

Verifica que `DB_NAME` apunte a `task_db` y que esa base exista realmente.

## 11. Siguientes mejoras sugeridas

- paginacion con `GET /tasks?page=1&limit=20`
- busqueda por texto con `GET /tasks?query=algo`
- soft delete con `deleted_at`
- relacion `User -> Task`
- migrar luego a PostgreSQL
