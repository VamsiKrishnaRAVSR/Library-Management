from flask import Blueprint, jsonify, request

from helper import response_formatter
from model import Member
from utils import compare_hashed_password
from model import Db
from flask_jwt_extended import create_access_token, create_refresh_token
from routes import add_member_details

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register_user():
    return add_member_details()


@auth_bp.post("/login")
def login_user():
    data = request.get_json()
    email, password = data.get("email"), data.get("password")
    member_details = Member.get_member_by_email(email = email)
    if member_details is None:
        return response_formatter("No user found")
    member_details = member_details.get_all_details()
    if member_details and compare_hashed_password(member_details["password"], password):
        access_token = create_access_token(identity=email ,additional_claims={"role": member_details['role']})
        refresh_token = create_refresh_token(identity=email)
        return jsonify({
            "message": "Token created successfully",
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        }), 200
    return jsonify({
        "message": "Invalid Email or Password"
    })
