from constants import book_properties, book_allowed_fields, member_properties, member_allowed_properties, \
    ERROR_CONSTANTS
from helper import is_record_available, response_formatter, get_missing_keys, get_error_details, map_keys_to_values
from model import Books, Db, Member, BookMember
from flask import Flask, request, jsonify
from _datetime import datetime
from sqlalchemy import func


def get_books():
    try:
        books = Books.query.all()
        author, title = request.args.get("author"), request.args.get("title")
        if author and title:
            books = Books.query.filter(Books.author.like(author + "%")).filter(Books.title.like(title + "%")).all()
        elif author:
            books = Books.query.filter(Books.author.like(author + "%")).all()
        elif title:
            books = Books.query.filter(Books.title.like(title + "%")).all()
        books_list = [book.to_dict() for book in books]
        return jsonify(books_list)
    except Exception as e:
        return response_formatter(str(e), 500)


def post_book():
    try:
        books = Books.query.all()
        books_list = [book.to_dict() for book in books]
        books = [book['title'] for book in books_list]
        missing_keys = get_missing_keys(book_properties, request.json)

        if missing_keys:
            return response_formatter(missing_keys, 400)

        if is_record_available(books, request.json['title']):
            info, status = get_error_details("ERR_BOOK_NOT_FOUND")
            return response_formatter(info, status)
        else:
            title, author, isbn, publisher, book_count, book_rent = (
                request.json['title'], request.json['author'], request.json['isbn'],
                request.json['publisher'], request.json['book_count'], request.json['book_rent']
            )
            new_book = Books(title=title, author=author, isbn=isbn, publisher=publisher,
                             book_count=book_count, book_rent=book_rent)
            Db.session.add(new_book)
            Db.session.commit()
            info, status = get_error_details("BOOK_ISSUE_SUCCESS")
            return response_formatter(info, status)
    # except KeyError as e:
    #     Db.session.rollback()
    #     return response_formatter(f"Missing field: {str(e)}", 400)
    except Exception as e:
        Db.session.rollback()
        return response_formatter(str(e), 500)


def get_book(book_id):
    try:
        req_book = Books.query.get(book_id)
        if req_book is None:
            info, status = get_error_details("ERR_BOOK_NOT_FOUND")
            return response_formatter(info, status)
        return jsonify(req_book.to_dict())
    except Exception as e:
        return response_formatter(str(e), 500)


def update_book(book_id):
    try:
        req_book = Books.query.get(book_id)
        if req_book is None:
            info, status = get_error_details("ERR_BOOK_NOT_FOUND")
            return response_formatter(info, status)

        for key, value in request.json.items():
            if hasattr(req_book, key) and key in book_allowed_fields:
                setattr(req_book, key, value)

        Db.session.commit()
        info, status = get_error_details("BOOK_UPDATE_SUCCESS")
        return response_formatter(info, status)
    except AttributeError as e:
        Db.session.rollback()
        return response_formatter(f"Attribute error: {str(e)}", 400)
    except Exception as e:
        Db.session.rollback()
        return response_formatter(str(e), 500)


def delete_book(book_id):
    try:
        req_book = Books.query.get(book_id)
        if req_book is None:
            info, status = get_error_details("ERR_BOOK_NOT_FOUND")
            return response_formatter(info, status)
        Db.session.delete(req_book)
        Db.session.commit()
        info, status = get_error_details("BOOK_DELETE_SUCCESS")
        return response_formatter(info, status)
    except Exception as e:
        Db.session.rollback()
        return response_formatter(str(e), 500)


def get_members_details():
    try:
        member_list = Member.query.all()
        return jsonify([member.to_dict() for member in member_list])
    except Exception as e:
        return response_formatter(str(e), 500)


def add_member_details(bcrypt):
    try:
        member_list = Member.query.all()
        user_name = request.json['name']
        email = request.json['email']
        role = request.json['role']
        password = request.json['password']
        missing_keys = get_missing_keys(member_properties, request.json)
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        if missing_keys:
            return response_formatter(missing_keys, 400)

        member_name_list = [member.to_dict()['name'] for member in member_list]
        if is_record_available(member_name_list, user_name):
            info, status = get_error_details("ERR_MEMBER_EXISTS")
            return response_formatter(info, status)
        else:
            new_member = Member(name=user_name, password=hashed_password, email=email, role=role)
            Db.session.add(new_member)
            Db.session.commit()
            info, status = get_error_details("MEMBER_ADDED_SUCCESS")
            return response_formatter(info, status)
    except KeyError as e:
        Db.session.rollback()
        return response_formatter(f"Missing field: {str(e)}", 400)
    except Exception as e:
        Db.session.rollback()
        return response_formatter(str(e), 500)


def get_member_details(member_id, bcrypt):
    try:
        member_details = Member.query.get(member_id)
        if member_details is None:
            info, status = get_error_details("ERR_MEMBER_NOT_FOUND")
            return response_formatter(info, status)
        return jsonify(member_details.to_dict())
    except Exception as e:
        return response_formatter(str(e), 500)


def update_member(member_id, bcrypt):
    try:
        member_details = Member.query.get(member_id)
        if member_details is None:
            info, status = get_error_details("ERR_MEMBER_NOT_FOUND")
            return response_formatter(info, status)
        else:
            for key, value in request.json.items():
                if getattr(member_details, key) and key in member_allowed_properties:
                    if(key=="password"):
                        hashed_password = bcrypt.generate_password_hash(value).decode('utf-8')
                        setattr(member_details, key, hashed_password)
                    else:
                        setattr(member_details, key, value)
            Db.session.commit()
            info, status = get_error_details("MEMBER_DETAILS_UPDATE_SUCCESS")
            return response_formatter(info, status)
    except AttributeError as e:
        Db.session.rollback()
        return response_formatter(f"Attribute error: {str(e)}", 400)


def delete_member(member_id):
    try:
        member_details = Member.query.get(member_id)
        if member_details is None:
            info, status = get_error_details("ERR_MEMBER_NOT_FOUND")
            return response_formatter(info, status)
        Db.session.delete(member_details)
        Db.session.commit()
        info, status = get_error_details("MEMBER_DELETED_SUCCESS")
        return response_formatter(info, status)
    except Exception as e:
        print(e)
        Db.session.rollback()
        return response_formatter(str(e), 500)


def issue_book():
    book_id, member_id = request.json['book_id'], request.json['member_id']
    issue_date = datetime.now()
    # Check if book count exists, else reject this operation
    # add the new record
    # issued book cannot be issued once again
    existing_issue = Db.session.query(BookMember).filter_by(book_id=book_id, member_id=member_id).first()
    if existing_issue:
        if not existing_issue.is_book_returned:
            info, status = get_error_details("ERR_BOOK_ISSUED")
            return response_formatter(info, status)
    book_details = Books.query.get(book_id)
    member_details = Member.query.get(member_id)
    if book_details is None:
        info, status = get_error_details("ERR_BOOK_NOT_FOUND")
        return response_formatter(info, status)
    if member_details is None:
        info, status = get_error_details("ERR_MEMBER_NOT_FOUND")
        return response_formatter(info, status)
    else:
        count = book_details.to_dict()['book_count']
        if count <= 0:
            info, status = get_error_details("ERR_BOOK_STOCKED_OUT")
            return response_formatter(info, status)
        else:
            setattr(book_details, 'book_count', count - 1)
            book_issue = BookMember(book_id=book_id, issue_date=issue_date, member_id=member_id, debt=0,
                                    return_date=None, is_book_returned=False)
            # raise Exception("Just for fun")
            Db.session.add(book_issue)
            Db.session.commit()
            info, status = get_error_details("BOOK_ISSUE_SUCCESS")
            return response_formatter(info, status)


def submit_book():
    return_date = datetime.now()
    book_id, member_id = request.json['book_id'], request.json['member_id']
    transaction_details = Db.session.query(BookMember).filter_by(book_id=book_id, member_id=member_id).first()
    book_details = Books.query.get(book_id).to_dict()
    book_rent = book_details['book_rent']
    if transaction_details is None:
        info, status = get_error_details("ERR_NO_TRANSACTION")
        return response_formatter(info, status)
    else:
        if not transaction_details.is_book_returned:
            debt = (return_date - transaction_details.issue_date).days * book_rent
            # updating the book count and updating the transactions
            transaction_details.return_date = return_date
            transaction_details.debt = debt
            transaction_details.is_book_returned = True

            book_details.update({"book_count": book_details["book_count"] + 1})
            Db.session.commit()
            info, status = get_error_details("BOOK_ALLOTMENT_SUCCESS")
            return response_formatter(info, status)
        else:
            info, status = get_error_details("ERR_TRANSACTION_EXISTS")
            return response_formatter(info, status)


def get_highest_paying_members():
    results = Db.session.query(Member.id, Member.name, func.sum(BookMember.debt)).join(Member, BookMember.member_id == Member.id).group_by(BookMember.member_id).order_by(BookMember.debt.desc()).all()
    # debt = Db.session.query(BookMember.member_id, func.sum(BookMember.debt)).group_by(BookMember.member_id).all()
    keys_list = ["member_id", "member_name", "debt"]
    members_list = map_keys_to_values(keys_list, results)
    return members_list


def get_famous_books_list():
    #  select book_member.book_id, books.title, count(book_member.member_id) from book_member
    #  left join books on book_member.book_id = books.id group by book_member.book_id;
    results = Db.session.query(Books.id, Books.title, func.count(BookMember.member_id)).join(BookMember, Books.id== BookMember.book_id).group_by(BookMember.book_id).order_by(func.count(BookMember.member_id).desc()).all()
    keys_list = ["id", "title", "count_of_members_taken"]
    serialised_json = map_keys_to_values(keys_list, results)
    return serialised_json
