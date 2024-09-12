from flask import Blueprint
from flask_jwt_extended import jwt_required

from helper import admin_access_routes
from routes import get_books, post_book

books_bp = Blueprint("books", __name__)


@books_bp.get("/")
@jwt_required()
def get_all_books():
    return get_books()


@books_bp.post("/")
@jwt_required()
@admin_access_routes()
def create_new_book():
    return post_book()
