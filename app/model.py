from sqlalchemy import Integer, String, ForeignKey, DateTime, Float, Boolean
from flask_sqlalchemy import SQLAlchemy

Db = SQLAlchemy()


class Books(Db.Model):
    id = Db.Column(Integer, primary_key=True, autoincrement=True)
    title = Db.Column(String)
    author = Db.Column(String)
    isbn = Db.Column(String(255))
    publisher = Db.Column(String(255))
    book_count = Db.Column(Integer)
    book_rent = Db.Column(Integer)

    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'author': self.author,
                'isbn': self.isbn, 'publisher':self.publisher , 'book_count': self.book_count, 'book_rent': self.book_rent }


class Member(Db.Model):
    id = Db.Column(Integer, primary_key=True, autoincrement=True)
    name = Db.Column(String)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name
        }


class BookMember(Db.Model):
    id = Db.Column(Integer, primary_key=True, autoincrement=True)
    book_id = Db.Column(Integer, ForeignKey('books.id'))
    member_id = Db.Column(Integer, ForeignKey('member.id'))
    issue_date = Db.Column(DateTime(timezone=True))
    return_date = Db.Column(DateTime(timezone=True))
    debt = Db.Column(Float)
    is_book_returned = Db.Column(Boolean)

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "member_id": self.member_id,
            "issue_date": self.issue_date,
            "return_date": self.return_date,
            "debt": self.debt,
            "is_book_returned": self.is_book_returned
        }