from flask import Flask, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

import config
from models import Task, db


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config["SECRET_KEY"] = config.SECRET_KEY

    db.init_app(app)

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify({"error": "Metodo no permitido"}), 405

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify({"error": "Error interno del servidor"}), 500

    @app.route("/")
    def root():
        return jsonify({"message": "API Task Manager con Flask, MySQL y SQLAlchemy"}), 200

    @app.route("/healthz")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.route("/tasks", methods=["GET"])
    def list_tasks():
        tasks = Task.query.order_by(Task.created_at.desc()).all()
        return jsonify([task.to_dict() for task in tasks]), 200

    @app.route("/tasks/<int:task_id>", methods=["GET"])
    def get_task(task_id):
        task = db.session.get(Task, task_id)
        if task is None:
            return jsonify({"error": "Tarea no encontrada"}), 404
        return jsonify(task.to_dict()), 200

    @app.route("/tasks", methods=["POST"])
    def create_task():
        payload = request.get_json(silent=True) or {}
        content = str(payload.get("content", "")).strip()

        if not content:
            return jsonify({"error": "El campo 'content' es obligatorio y no puede estar vacio."}), 400

        task = Task(content=content, done=bool(payload.get("done", False)))

        try:
            db.session.add(task)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            return jsonify({"error": "No se pudo crear la tarea en la base de datos."}), 500

        return jsonify(task.to_dict()), 201

    @app.route("/tasks/<int:task_id>", methods=["PUT"])
    def update_task(task_id):
        task = db.session.get(Task, task_id)
        if task is None:
            return jsonify({"error": "Tarea no encontrada"}), 404

        payload = request.get_json(silent=True) or {}

        if "content" in payload:
            new_content = str(payload["content"]).strip()
            if not new_content:
                return jsonify({"error": "El campo 'content' no puede estar vacio."}), 400
            task.content = new_content

        if "done" in payload:
            task.done = bool(payload["done"])

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            return jsonify({"error": "No se pudo actualizar la tarea en la base de datos."}), 500

        return jsonify(task.to_dict()), 200

    @app.route("/tasks/<int:task_id>", methods=["DELETE"])
    def delete_task(task_id):
        task = db.session.get(Task, task_id)
        if task is None:
            return jsonify({"error": "Tarea no encontrada"}), 404

        try:
            db.session.delete(task)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            return jsonify({"error": "No se pudo eliminar la tarea en la base de datos."}), 500

        return jsonify({"message": "Tarea eliminada"}), 200

    @app.route("/tasks/done", methods=["GET"])
    def list_done():
        tasks = Task.query.filter_by(done=True).order_by(Task.updated_at.desc()).all()
        return jsonify([task.to_dict() for task in tasks]), 200

    @app.route("/tasks/pending", methods=["GET"])
    def list_pending():
        tasks = Task.query.filter_by(done=False).order_by(Task.created_at.desc()).all()
        return jsonify([task.to_dict() for task in tasks]), 200

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True)
