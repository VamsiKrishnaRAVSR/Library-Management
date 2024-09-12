import os
from datetime import timedelta
from flask_migrate import Migrate
from flask import Flask, request, jsonify
from functools import wraps

from book import book_bp
from books import books_bp
from member import member_bp
from members import members_bp
from auth import auth_bp
from helper import response_formatter, calculate_debt, get_error_details, admin_access_routes
from routes import issue_book, submit_book, get_highest_paying_members, get_famous_books_list, get_params_details
from model import Db, Books, BookMember
from flask_jwt_extended import JWTManager, jwt_required
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
Db.init_app(app)
Migrate = Migrate(app, Db)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 1)))


jwt = JWTManager()
jwt.init_app(app)

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(members_bp, url_prefix="/members")
app.register_blueprint(member_bp, url_prefix="/member")
app.register_blueprint(books_bp, url_prefix="/books")
app.register_blueprint(book_bp, url_prefix="/book")


# Custom decorator to handle exceptions
def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            Db.session.rollback()
            return jsonify({"message": f"Missing field: {str(e)}"}), 400
        except AttributeError as e:
            Db.session.rollback()
            return jsonify({"message": f"Attribute error: {str(e)}"}), 400
        except Exception as e:
            Db.session.rollback()
            return jsonify({"message": str(e)}), 500
    return wrapper


@app.route("/issue_book", methods=["POST"])
@jwt_required()
@admin_access_routes()
@handle_exceptions
def issue_book_to_user():
    return issue_book()


# Calculate the debt, show in response
# update the book_id count
# update the transaction debt and add to_date.
@app.route("/submit_book", methods=["POST"])
@jwt_required()
@admin_access_routes()
@handle_exceptions
def update_book_status():
    return submit_book()


@app.route("/get_transactions", methods=["GET"])
@jwt_required()
@admin_access_routes()
@handle_exceptions
def get_transactions():
    transaction_details = BookMember.query.all()
    transactions = [transaction.to_dict() for transaction in transaction_details]
    return transactions


@app.route("/get_transaction_debt", methods=["POST"])
@jwt_required()
@admin_access_routes()
@handle_exceptions
def calculate_transaction_debt():
    book_id, member_id = request.json['book_id'], request.json['member_id']
    transaction_details = Db.session.query(BookMember).filter_by(book_id=book_id, member_id=member_id).first()

    book_rent = Books.query.get(book_id).to_dict()['book_rent']
    if book_rent is None:
        info, status = get_error_details("ERR_BOOK_NOT_FOUND")
        return response_formatter(info, status)
    debt = calculate_debt(transaction_details.issue_date, book_rent, transaction_details.return_date )
    msg = "MAX_TRANSACTION_LIMIT" if (transaction_details.is_book_returned is False) else "TRANSACTION_SUCCESS"
    info, status = get_error_details(msg)
    if debt > 500:
        return response_formatter(info.format(x=500), status)
    book_status = "Returned" if transaction_details.is_book_returned else "Not Returned"
    return response_formatter(info.format(x=debt), book_status)


@app.route("/my_books", methods=["POST"])
@jwt_required()
@handle_exceptions
def get_my_transactions():
    user_id = request.json['member_id']
    # User profile, show all the details of my books [ONLY VIEW]
    user_book_details = BookMember.query.filter_by(member_id=user_id).all()
    user_books = [book.to_dict() for book in user_book_details]
    return user_books


# Calculate the total debt
@app.route("/calculate-debt", methods=["POST"])
@jwt_required()
@handle_exceptions
def calculate_my_debt():
    member_id = request.json["member_id"]
    user_transactions = BookMember.query.filter_by(member_id=member_id).all()
    if user_transactions is None or user_transactions == []:
        info, status = get_error_details("ERR_NO_TRANSACTION")
        return response_formatter(info, status)
    debt = 0
    for k in user_transactions:
        if not k.to_dict()['is_book_returned']:
            book_rent = Books.query.get(k.to_dict()['book_id']).to_dict()['book_rent']
            debt = debt + calculate_debt(k.to_dict()['issue_date'], book_rent, k.to_dict()['return_date'])
    msg = "MAX_TRANSACTION_LIMIT" if (debt != 0) else "TRANSACTION_SUCCESS"
    info, status = get_error_details(msg)
    return response_formatter(info.format(x=debt), status)


@app.route("/highest_paying_customers")
@jwt_required()
@admin_access_routes()
@handle_exceptions
def get_highest_paying_customers():
    return get_highest_paying_members()


@app.route("/famous_books")
@jwt_required()
@handle_exceptions
def get_famous_books():
    return get_famous_books_list()


@jwt.expired_token_loader
def expired_token_loader(jwt_header, jwt_data):
    return response_formatter("Token Expired", 401)


@jwt.invalid_token_loader
def invalid_token_loader(err):
    return response_formatter("Signature Verification failed", 401)


@jwt.unauthorized_loader
def missing_token(err):
    return response_formatter("Request doesn't contain valid token", 401)


if __name__ == '__main__':
    with app.app_context():
        Db.create_all()  # Create tables within the application context
    app.run(debug=True)
