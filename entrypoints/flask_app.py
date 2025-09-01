from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from adapters.orm import start_mappers, metadata
from adapters.repository import SqlAlchemyRepository
from service_layer.services import GroceryListService, GroceryItemService
from domain.models import GroceryList, GroceryItem

import config


app = Flask(__name__)

# Enable CORS for all routes
# For production use more specific origin
CORS(app)

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
            [grocery_list.to_dict() for grocery_list in grocery_lists]
        ), 200

    except Exception as e:
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

        return jsonify(grocery_list.to_dict()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/grocery-lists/<int:list_id>", methods=["PUT"])
def update_grocery_list(list_id):
    """Update a grocery list's name."""
    try:
        data = request.get_json()
        if not data or "name" not in data:
            return jsonify({"error": "Name is required"}), 400

        name = data["name"].strip()
        if not name:
            return jsonify({"error": "Name cannot be empty"}), 400

        grocery_list_repo = SqlAlchemyRepository(db.session, GroceryList)
        service = GroceryListService(grocery_list_repo)

        updated_list = service.update_grocery_list(list_id, name)

        if not updated_list:
            return jsonify({"error": "Grocery list not found"}), 404

        db.session.commit()

        return jsonify(updated_list.to_dict()), 200

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

        # Delete the grocery list (cascade will automatically delete all items)
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

        return jsonify(grocery_list.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/grocery-lists/<int:list_id>/items", methods=["GET"])
def get_items_by_list(list_id):
    """Get all items for a specific grocery list."""
    try:
        # Create repositories
        grocery_list_repo = SqlAlchemyRepository(db.session, GroceryList)
        grocery_item_repo = SqlAlchemyRepository(db.session, GroceryItem)

        # Create service
        service = GroceryItemService(
            grocery_item_repo, grocery_list_repo, db.session
        )

        # Get items and list name
        result = service.get_items_by_list(list_id)

        if result is None:
            return jsonify({"error": "Grocery list not found"}), 404

        response_data = {
            "grocery_list_name": result["grocery_list_name"],
            "items": [item.to_dict() for item in result["items"]]
        }

        return jsonify(response_data), 200

    except Exception as e:
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

        return jsonify(item.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/grocery-items/<int:item_id>", methods=["PATCH"])
def update_grocery_item(item_id):
    """Update a grocery item's name and/or quantity."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # Extract optional fields
        name = data.get("name")
        quantity = data.get("quantity")

        # Validate name if provided
        if name is not None:
            name = name.strip()
            if not name:
                return jsonify({"error": "Name cannot be empty"}), 400

        # Validate quantity if provided
        if quantity is not None:
            if not isinstance(quantity, int) or quantity < 1:
                return jsonify(
                    {"error": "Quantity must be a positive integer"}
                ), 400

        # At least one field must be provided
        if name is None and quantity is None:
            return jsonify(
                {
                    "error": "At least one field (name or quantity) must be provided"
                }
            ), 400

        # Create repositories
        grocery_list_repo = SqlAlchemyRepository(db.session, GroceryList)
        grocery_item_repo = SqlAlchemyRepository(db.session, GroceryItem)

        # Create service
        service = GroceryItemService(
            grocery_item_repo, grocery_list_repo, db.session
        )

        # Update the item
        updated_item = service.update_item(
            item_id, name=name, quantity=quantity
        )

        if not updated_item:
            return jsonify({"error": "Grocery item not found"}), 404

        db.session.commit()

        return jsonify(updated_item.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/grocery-items/<int:item_id>/purchase", methods=["POST"])
def mark_item_as_purchased(item_id):
    """Mark a grocery item as purchased."""
    try:
        # Create repositories
        grocery_list_repo = SqlAlchemyRepository(db.session, GroceryList)
        grocery_item_repo = SqlAlchemyRepository(db.session, GroceryItem)

        # Create service
        service = GroceryItemService(
            grocery_item_repo, grocery_list_repo, db.session
        )

        # Mark item as purchased
        updated_item = service.mark_item_as_purchased(item_id)

        if not updated_item:
            return jsonify({"error": "Grocery item not found"}), 404

        db.session.commit()

        return jsonify(updated_item.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/grocery-items/<int:item_id>/unpurchase", methods=["POST"])
def mark_item_as_pending(item_id):
    """Mark a grocery item as pending (not purchased)."""
    try:
        # Create repositories
        grocery_list_repo = SqlAlchemyRepository(db.session, GroceryList)
        grocery_item_repo = SqlAlchemyRepository(db.session, GroceryItem)

        # Create service
        service = GroceryItemService(
            grocery_item_repo, grocery_list_repo, db.session
        )

        # Mark item as pending
        updated_item = service.mark_item_as_pending(item_id)

        if not updated_item:
            return jsonify({"error": "Grocery item not found"}), 404

        db.session.commit()

        return jsonify(updated_item.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/grocery-items/<int:item_id>", methods=["DELETE"])
def delete_grocery_item(item_id):
    """Delete a grocery item by ID."""
    try:
        # Create repositories
        grocery_list_repo = SqlAlchemyRepository(db.session, GroceryList)
        grocery_item_repo = SqlAlchemyRepository(db.session, GroceryItem)

        # Create service
        service = GroceryItemService(
            grocery_item_repo, grocery_list_repo, db.session
        )

        # Check if the item exists first
        item = service.get_item(item_id)
        if not item:
            return jsonify({"error": "Grocery item not found"}), 404

        # Delete the item
        is_deleted = service.delete_item(item_id)

        if is_deleted:
            db.session.commit()
            return jsonify(
                {"message": "Grocery item deleted successfully"}
            ), 200
        else:
            return jsonify({"error": "Failed to delete grocery item"}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
