from flask import Blueprint
from flask_jwt_extended import jwt_required

from helper import admin_access_routes
from routes import get_book, update_book, delete_book

book_bp = Blueprint("book", __name__)


@book_bp.get("/<int:book_id>")
@jwt_required()
def get_existing_book(book_id):
    return get_book(book_id)


@book_bp.patch("/<int:book_id>")
@jwt_required()
@admin_access_routes()
def update_new_book(book_id):
    return update_book(book_id)


@book_bp.delete("/<int:book_id>")
@admin_access_routes()
@jwt_required()
def delete_existing_book(book_id):
    return delete_book(book_id)
