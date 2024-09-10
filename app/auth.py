from flask import Blueprint, jsonify, request

from utils import generate_hashed_password
from routes import add_member_details

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register_user():
    return add_member_details()
