from flask import Blueprint
from flask_jwt_extended import jwt_required
from routes import get_members_details
from helper import admin_access_routes
members_bp = Blueprint("members", __name__)


@members_bp.get("/all")
@jwt_required()
@admin_access_routes()
def get_members():
    return get_members_details()
