Requirements:
Flask (Framework)
SQLObject (ORM)

Library Management Restful APIs:
------------------------------------------------------
A local library is in dire need of a web application to ease their work. The library management system must allow a librarian to track books and their quantity, books issued to members, and book fees.

For the sake of simplicity, you don't have to implement sessions and roles, you can assume that the app will be used by the librarian only. We can add a borrower role along with borrower registration later on.

The following functionalities are expected from the application:

Base Library System
Librarians must be able to maintain:
Books with stock maintained
Members
Transactions

The use cases included here are to:
Perform general CRUD operations on Books and Members
Issue a book to a member
Issue a book return from a member
Search for a book by name and author
Charge a rent fee on book returns
Make sure a member’s outstanding debt is not more than Rs.500

Integration for Data Import
The librarian should be able to import books into the system using the API and create book records.

How does the API work?
This API will give you only 20 books at a time.
It accepts title, authors, isbn, publisher, and page as parameters.

How to use the API?
Build an interface in your app to interact with our API.
Add a field to specify the number of books to import, at the very least.
You may additionally give the librarian any set of parameters; for instance, they should be able to import 30 books titled "Harry Potter".
Insert book records.

