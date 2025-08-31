from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from adapters.orm import start_mappers, metadata
from adapters.repository import SqlAlchemyRepository
from service_layer.services import GroceryListService, GroceryItemService
from domain.models import GroceryList, GroceryItem, ItemStatus

import config


app = Flask(__name__)

# Configure Flask to redirect trailing slashes
app.url_map.strict_slashes = False

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


@app.route("/api/v1/grocery-lists", methods=["GET"])
def get_grocery_lists():
    """Get all grocery lists."""
    try:
        grocery_list_repo = SqlAlchemyRepository(db.session, GroceryList)
        service = GroceryListService(grocery_list_repo)

        grocery_lists = service.get_all_grocery_lists()

        return jsonify(
            [
                {
                    "id": grocery_list.id,
                    "name": grocery_list.name,
                    "created_at": grocery_list.created_at.isoformat(),
                    "updated_at": grocery_list.updated_at.isoformat(),
                }
                for grocery_list in grocery_lists
            ]
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/grocery-lists/<int:list_id>", methods=["GET"])
def get_grocery_list(list_id):
    """Get a grocery list by ID."""
    try:
        grocery_list_repo = SqlAlchemyRepository(db.session, GroceryList)
        service = GroceryListService(grocery_list_repo)

        grocery_list = service.get_grocery_list(list_id)

        if not grocery_list:
            return jsonify({"error": "Grocery list not found"}), 404

        return jsonify(
            {
                "id": grocery_list.id,
                "name": grocery_list.name,
                "created_at": grocery_list.created_at.isoformat(),
                "updated_at": grocery_list.updated_at.isoformat(),
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/grocery-lists/<int:list_id>", methods=["DELETE"])
def delete_grocery_list(list_id):
    """Delete a grocery list by ID."""
    try:
        grocery_list_repo = SqlAlchemyRepository(db.session, GroceryList)
        service = GroceryListService(grocery_list_repo)

        # Check if the grocery list exists first
        grocery_list = service.get_grocery_list(list_id)
        if not grocery_list:
            return jsonify({"error": "Grocery list not found"}), 404

        # Delete the grocery list
        is_deleted = service.delete_grocery_list(list_id)

        if is_deleted:
            db.session.commit()
            return jsonify(
                {"message": "Grocery list deleted successfully"}
            ), 200
        else:
            return jsonify({"error": "Failed to delete grocery list"}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/grocery-lists", methods=["POST"])
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


@app.route("/api/v1/grocery-lists/<int:list_id>/items", methods=["POST"])
def add_item_to_list(list_id):
    """Add a new item to a grocery list."""
    try:
        data = request.get_json()
        if not data or "name" not in data:
            return jsonify({"error": "Item name is required"}), 400

        name = data["name"].strip()
        if not name:
            return jsonify({"error": "Item name cannot be empty"}), 400

        quantity = data.get("quantity", 1)
        if not isinstance(quantity, int) or quantity < 1:
            return jsonify(
                {"error": "Quantity must be a positive integer"}
            ), 400

        # Create repositories
        grocery_list_repo = SqlAlchemyRepository(db.session, GroceryList)
        grocery_item_repo = SqlAlchemyRepository(db.session, GroceryItem)

        # Create service
        service = GroceryItemService(
            grocery_item_repo, grocery_list_repo, db.session
        )

        # Add item to list
        item = service.add_item_to_list(list_id, name, quantity)

        if not item:
            return jsonify({"error": "Grocery list not found"}), 404

        db.session.commit()

        return jsonify(
            {
                "id": item.id,
                "name": item.name,
                "quantity": item.quantity,
                "is_purchased": item.status == ItemStatus.PURCHASED,
                "created_at": item.created_at.isoformat(),
                "updated_at": item.updated_at.isoformat(),
            }
        ), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
