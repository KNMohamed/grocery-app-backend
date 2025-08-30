from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from adapters.orm import start_mappers, metadata
from adapters.repository import SqlAlchemyRepository
from service_layer.services import GroceryListService
from domain.models import GroceryList

import config


app = Flask(__name__)

# Configure Flask-Migrate
app.config["SQLALCHEMY_DATABASE_URI"] = config.get_postgres_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy with the app and metadata object holding table definitions.
db = SQLAlchemy(app, metadata=metadata)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# start_mappers() needs an active application context to properly configure the mappers
with app.app_context():
    start_mappers()


@app.route("/grocery-lists", methods=["POST"])
def create_grocery_list():
    """Create a new grocery list."""
    try:
        data = request.get_json()
        if not data or "name" not in data:
            return jsonify({"error": "Name is required"}), 400

        name = data["name"].strip()
        if not name:
            return jsonify({"error": "Name cannot be empty"}), 400

        grocery_list_repo = SqlAlchemyRepository(db.session, GroceryList)

        service = GroceryListService(grocery_list_repo)

        grocery_list = service.create_grocery_list(name)
        db.session.commit()

        return jsonify(
            {
                "id": grocery_list.id,
                "name": grocery_list.name,
                "created_at": grocery_list.created_at.isoformat(),
                "updated_at": grocery_list.updated_at.isoformat(),
            }
        ), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
