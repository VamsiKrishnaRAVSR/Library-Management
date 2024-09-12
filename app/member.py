from flask import Blueprint
from flask_jwt_extended import jwt_required

from helper import admin_access_routes
from routes import get_member_details, delete_member, update_member

member_bp = Blueprint("member", __name__)


@member_bp.get("/<int:member_id>")
@jwt_required()
def get_members(member_id):
    return get_member_details(member_id)


@member_bp.patch("/<int:member_id>")
@jwt_required()
def update_member_details(member_id):
    return update_member(member_id)


@member_bp.delete("/<int:member_id>")
@jwt_required()
@admin_access_routes()
def delete_member_record(member_id):
    return delete_member(member_id)
