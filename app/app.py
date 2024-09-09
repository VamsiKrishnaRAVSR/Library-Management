from flask_migrate import Migrate
from flask import Flask, request, jsonify
from functools import wraps
from flask_bcrypt import Bcrypt

from helper import response_formatter, calculate_debt, get_error_details
from routes import get_books, post_book, update_book, delete_book, get_book, get_member_details, add_member_details, \
    get_members_details, delete_member, update_member, issue_book, submit_book, get_highest_paying_members, \
    get_famous_books_list
from model import Db, Books, Member, BookMember

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///LibraryManagement.db'  # Replace with your desired database URI

# Bind Db (SQLAlchemy) to the app
Db.init_app(app)
Migrate = Migrate(app, Db)
bcrypt = Bcrypt(app)

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


@app.route("/books", methods=["GET"])
def get_all_books():
    return get_books()


@app.route("/books", methods=["POST"])
def create_new_book():
    return post_book()


@app.route("/books/<int:book_id>")
def get_single_book(book_id):
    return get_book(book_id)


@app.route("/books/<int:book_id>", methods=["PATCH"])
def update_book_details(book_id):
    return update_book(book_id)


@app.route("/books/<int:book_id>", methods=["DELETE"])
def remove_book(book_id):
    return delete_book(book_id)


@app.route("/members")
def get_members():
    return get_members_details()


@app.route("/members", methods=["POST"])
def create_member():
    return add_member_details(bcrypt)


@app.route("/member/<int:member_id>")
def get_member(member_id):
    return get_member_details(member_id, bcrypt)


@app.route("/member/<int:member_id>", methods=["PATCH"])
def update_profile(member_id):
    return update_member(member_id, bcrypt)


@app.route("/member/<int:member_id>", methods=["DELETE"])
def delete_profile(member_id):
    return delete_member(member_id)


@app.route("/issue_book", methods=["POST"])
@handle_exceptions
def issue_book_to_user():
    return issue_book()


# Calculate the debt, show in response
# update the book_id count
# update the transaction debt and add to_date.
@app.route("/submit_book", methods=["POST"])
@handle_exceptions
def update_book_status():
    return submit_book()


@app.route("/get_transactions", methods=["GET"])
@handle_exceptions
def get_transactions():
    transaction_details = BookMember.query.all()
    transactions = [transaction.to_dict() for transaction in transaction_details]
    return transactions


@app.route("/get_transaction_debt", methods=["POST"])
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
    return response_formatter(info.format(x=debt), status)


@app.route("/my_books", methods=["POST"])
@handle_exceptions
def get_my_transactions():
    user_id = request.json['member_id']
    # User profile, show all the details of my books [ONLY VIEW]
    user_book_details = BookMember.query.filter_by(member_id=user_id).all()
    user_books = [book.to_dict() for book in user_book_details]
    return user_books


# Calculate the total debt
@app.route("/calculate-debt", methods=["POST"])
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
def get_highest_paying_customers():
    return get_highest_paying_members()


@app.route("/famous_books")
def get_famous_books():
    return get_famous_books_list()


if __name__ == '__main__':
    with app.app_context():
        Db.create_all()  # Create tables within the application context
    app.run(debug=True)
