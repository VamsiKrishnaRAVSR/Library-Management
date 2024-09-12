from functools import wraps

from flask import jsonify
from _datetime import datetime
from constants import ERROR_CONSTANTS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt



def response_formatter(msg, status_code=200):
    return jsonify({"message": msg}), status_code


def is_record_available(arr, book_name):
    for key in arr:
        if key == book_name:
            return True
    return False


def calculate_debt(issue_date: datetime, cost_per_day: float, return_date) -> float:
    print(issue_date, return_date, cost_per_day)
    if return_date is None:
        return_date = datetime.now()
    return (return_date - issue_date).days * cost_per_day


# All it does is to return missing keys from the response
def get_missing_keys(static_keys, json):
    missing_or_empty_fields = []
    for field in static_keys:
        if field not in json:
            missing_or_empty_fields.append(f"{field} is missing")
        elif json[field] == "":
            missing_or_empty_fields.append(f"{field} is empty")

    return missing_or_empty_fields


def get_error_details(error_key):
    error_data = ERROR_CONSTANTS.get(error_key, {})
    info = error_data.get("message", "No info available")  # Default if key not found
    status = error_data.get("status", 500)  # Default to 500 if status not found
    return info, status


def map_keys_to_values(keys_list, values_arr):
    arr=[]
    for i in values_arr:
        dict={}
        for k in range(len(keys_list)):
            dict[keys_list[k]] = i[k]
        arr.append(dict)
    return arr


def admin_access_routes():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            email, role = claims.get("sub") ,claims.get('role')
            if not email or role != "admin":
                return jsonify({"message": "Unauthorized"}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator


def get_email_from_jwt():
    claims = get_jwt()
    email = claims.get("sub")
    return email


def is_admin():
    claims = get_jwt()
    print(claims)
    return claims.get("role") == "admin"
