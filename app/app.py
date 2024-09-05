from _datetime import datetime

from flask import Flask, request, jsonify
from model import Db, Books, Member, BookMember

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///LibraryManagement.db'  # Replace with your desired database URI

# Bind Db (SQLAlchemy) to the app
Db.init_app(app)


def message(msg):
    return jsonify({"message": msg})


def is_record_available(arr, key, book_name):
    for key in arr:
        if key == book_name:
            return True
    return False


def calculate_debt(issue_date: datetime, cost_per_day: float) -> float:
    return_date = datetime.now()
    return (return_date - issue_date).days * cost_per_day


@app.route("/books", methods=["GET", "POST"])
def get_books():
    books = Books.query.all()
    author, title = request.args.get("author"), request.args.get("title")
    if (request.method == "GET"):
        if author and title:
            books = Books.query.filter(Books.author.like(author + "%")).filter(Books.title.like(title + "%")).all()
        elif author:
            books = Books.query.filter(Books.author.like(author + "%")).all()
        elif title:
            books = Books.query.filter(Books.title.like(title + "%")).all()
        books_list = [book.to_dict() for book in books]
        return jsonify(books_list)
    else:
        # check if title exists, if yes increase the count
        found = False
        books_list = [book.to_dict() for book in books]
        books = [book['title'] for book in books_list]
        if is_record_available(books, "title", request.json['title']):
            return message("Book already exists")
        else:
            # else add it to the library
            title, author, isbn, publisher, book_count, book_rent = request.json['title'], request.json['author'], \
                request.json['isbn'], request.json['publisher'], request.json['book_count'], request.json['book_rent']
            new_book = Books(title=title, author=author, isbn=isbn, publisher=publisher, book_count=book_count,
                             book_rent=book_rent)
            Db.session.add(new_book)
            Db.session.commit()
            return message("Book Added successfully")


@app.route("/books/<int:book_id>", methods=["GET", "PATCH", "DELETE"])
def get_book(book_id):
    req_book = Books.query.get(book_id)
    if req_book is None:
        return message("Book not found!!")
    if request.method == "GET":
        return jsonify(req_book.to_dict())
    elif request.method == "PATCH":
        # --------restrict to change id, title, author, isbn ----------------------------
        restricted_list = ["book_count", "book_rent"]
        for key, value in request.json.items():
            if getattr(req_book, key) and key in restricted_list:
                setattr(req_book, key, value)
        Db.session.commit()
        return message("Book updated Successfully")
    elif request.method == "DELETE":
        Db.session.delete(req_book)
        Db.session.commit()
        return message(F"{req_book.to_dict()['title']} book deleted successfully")


@app.route("/members", methods=["GET", "POST"])
def member_fn():
    member_list = Member.query.all()
    if (request.method == "GET"):
        return jsonify([member.to_dict() for member in member_list])
    else:
        user_name = request.json['name']
        if is_record_available(member_list, 'name', user_name):
            return message("User already exists")
        else:
            new_member = Member(name=user_name)
            Db.session.add(new_member)
            Db.session.commit()
            return message(F"User - {user_name} added Successfully")


@app.route("/member/<int:member_id>", methods=["GET", "PATCH", "DELETE"])
def get_member(member_id):
    member_details = Member.query.get(member_id)
    if member_details == None:
        return message("No user exists")
    if request.method == "GET":
        return jsonify(member_details.to_dict())
    elif request.method == "PATCH":
        updated_name = request.json['name']
        for key, value in request.json.items():
            if getattr(member_details, key) and key == "name":
                setattr(member_details, key, updated_name)
        Db.session.commit()
        return message(F"Member name updated to {updated_name} successfully")
    else:
        Db.session.delete(member_details)
        Db.session.commit()
        return message(F"{member_details['name']} is deleted")


@app.route("/issue_book", methods=["POST"])
def issue_book():
    book_id, member_id = request.json['book_id'], request.json['member_id']
    issue_date = datetime.now()

    # Check if book count exists, else reject this operation
    # add the new record
    # issued book cannot be issued once again
    existing_issue = Db.session.query(BookMember).filter_by(book_id=book_id, member_id=member_id).first()
    if existing_issue:
        if not existing_issue.is_book_returned:
            return jsonify({'error': 'Book already issued to this member'}), 400
    book_details = Books.query.get(book_id)
    member_details = Member.query.get(member_id)
    if (book_details == None or member_details == None):
        return message("Please check the provided details")
    else:
        count = book_details.to_dict()['book_count']
        if (count <= 0):
            return message("Books stocked out")
        else:
            setattr(book_details, 'book_count', count - 1)
            book_issue = BookMember(book_id=book_id, issue_date=issue_date, member_id=member_id, debt=0,
                                    return_date=None, is_book_returned=False)
            Db.session.add(book_issue)
            Db.session.commit()
            return message("Book issued successfully")


# Calculate the debt, show in response
# update the book_id count
# update the transaction debt and add to_date.
@app.route("/submit_book", methods=["POST"])
def submit_book():
    # return_date = datetime(2024, 6, 11)
    return_date = datetime.now()
    book_id, member_id = request.json['book_id'], request.json['member_id']
    transaction_details = Db.session.query(BookMember).filter_by(book_id=book_id, member_id=member_id).first()
    book_details = Books.query.get(book_id).to_dict()
    book_rent = book_details['book_rent']
    if transaction_details is None:
        return message("Transaction doesn't exist")
    else:
        debt = (return_date - transaction_details.issue_date).days * book_rent
        # updating the book count and updating the transactions
        transaction_details.return_date = return_date
        transaction_details.debt = debt
        transaction_details.is_book_returned = True

        book_details.update({"book_count": book_details["book_count"] + 1})
        print(transaction_details.to_dict(), return_date)
        Db.session.commit()
        return message("Book submitted successfully")


@app.route("/get_transactions", methods=["GET"])
def get_transactions():
    transaction_details = BookMember.query.all()
    transactions = [transaction.to_dict() for transaction in transaction_details]
    return transactions


@app.route("/get_transaction_debt", methods=["POST"])
def calculate_transaction_debt():
    book_id, member_id = request.json['book_id'], request.json['member_id']
    transaction_details = Db.session.query(BookMember).filter_by(book_id=book_id, member_id=member_id).first()

    book_rent = Books.query.get(book_id).to_dict()['book_rent']
    if book_rent is None:
        return message("Book doesn't exist")
    debt = calculate_debt(transaction_details.issue_date, book_rent)
    if debt > 500:
        return message("You need to pay 500 rupees in order to close the transaction")
    return message(F"You need to pay {debt} rupees in order to close the transaction")


@app.route("/my_books", methods=["POST"])
def get_my_transactions():
    user_id = request.json['member_id']
    # User profile, show all the details of my books [ONLY VIEW]
    user_book_details = BookMember.query.filter_by(member_id=user_id).all()
    user_books = [book.to_dict() for book in user_book_details]
    return user_books


# Calculate the total debt
@app.route("/calculate-debt", methods=["POST"])
def calculate_my_debt():
    member_id = request.json["member_id"]
    user_transactions = BookMember.query.filter_by(member_id=member_id).all()
    if user_transactions is None or user_transactions == []:
        return message("No Books taken by user")
    debt = 0
    for k in user_transactions:
        if not k.to_dict()['is_book_returned']:
            book_rent = Books.query.get(k.to_dict()['book_id']).to_dict()['book_rent']
            debt = debt + calculate_debt(k.to_dict()['issue_date'], book_rent)
            print(book_rent, debt)
    member_details = Member.query.get(member_id).to_dict()["name"]
    return message(F"{member_details} has to pay {debt} rupees")


if __name__ == '__main__':
    with app.app_context():
        Db.create_all()  # Create tables within the application context
    app.run(debug=True)
