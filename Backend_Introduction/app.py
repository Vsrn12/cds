from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

tasks = []
users = []

# GET http://127.0.0.1:5000/
@app.route("/")
def home():
    return send_from_directory(".", "index.html")

# GET http://127.0.0.1:5000/users
@app.route("/users", methods=["GET"])
def get_users():
    return jsonify({"users": users})

# GET http://127.0.0.1:5000/users/0
# Devuelve UN solo usuario buscándolo por su ID
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user})

# POST http://127.0.0.1:5000/users
# Crea un usuario nuevo. Requiere name y lastname.
@app.route("/users", methods=["POST"])
def add_user():
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    name = data.get("name", "")
    lastname = data.get("lastname", "")

    if not name or not name.strip():
        return jsonify({"error": "User name cannot be empty"}), 400
    if not lastname or not lastname.strip():
        return jsonify({"error": "User lastname cannot be empty"}), 400

    address = data.get("address", {})
    user = {
        "id": len(users),
        "name": name.strip(),
        "lastname": lastname.strip(),
        "address": {
            "city": address.get("city", "Arequipa"),
            "country": address.get("country", "Perú"),
            "code": address.get("code", "04000")
        }
    }
    users.append(user)
    return jsonify({"message": "User added!", "user": user}), 201

# PUT http://127.0.0.1:5000/users/0
# Actualiza los datos de un usuario
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    user["name"] = data.get("name", user["name"])
    user["lastname"] = data.get("lastname", user["lastname"])
    if "address" in data:
        addr = data["address"]
        user["address"]["city"] = addr.get("city", user["address"]["city"])
        user["address"]["country"] = addr.get("country", user["address"]["country"])
        user["address"]["code"] = addr.get("code", user["address"]["code"])

    return jsonify({"message": "User updated!", "user": user})

# DELETE http://127.0.0.1:5000/users/0
# Elimina un usuario de la lista
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    users.remove(user)
    return jsonify({"message": "User deleted!", "user": user})

# GET http://127.0.0.1:5000/tasks
# Devuelve TODAS las tareas guardadas en la lista
@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify({"tasks": tasks})


# GET http://127.0.0.1:5000/tasks/0
# Devuelve UNA sola tarea buscándola por su ID
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)

    if task is None:
        return jsonify({"error": "Task not found"}), 404 

    return jsonify({"task": task})

# POST http://127.0.0.1:5000/tasks
@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json  

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400  

    content = data.get("content", "") 

    if not content or not content.strip():
        return jsonify({"error": "Task content cannot be empty"}), 400

    # Construimos el diccionario de la tarea
    task = {
        "id": len(tasks),        
        "content": content.strip(),  
        "done": False           
    }

    tasks.append(task)
    return jsonify({"message": "Task added!", "task": task}), 201

# PUT http://127.0.0.1:5000/tasks/0
# Actualiza el CONTENIDO de una tarea. El cliente manda: {"content": "Nuevo texto"}
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    data = request.json
    # Si no manda "content", dejamos el que ya tenía
    task["content"] = data.get("content", task["content"])

    return jsonify({"message": "Task updated!", "task": task})

# PATCH http://127.0.0.1:5000/tasks/0/done
@app.route("/tasks/<int:task_id>/done", methods=["PATCH"])
def toggle_done(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    task["done"] = not task["done"]

    status = "completed" if task["done"] else "pending"
    return jsonify({"message": f"Task marked as {status}!", "task": task})

# DELETE http://127.0.0.1:5000/tasks/0
# Elimina una tarea de la lista
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    tasks.remove(task)  # Eliminamos el objeto de la lista
    return jsonify({"message": "Task deleted!", "task": task})

if __name__ == "__main__":
    app.run(debug=True)