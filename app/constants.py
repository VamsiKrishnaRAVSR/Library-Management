book_properties = ['title', 'author', 'isbn', 'publisher', 'book_count', 'book_rent']
book_allowed_fields = ["book_count", "book_rent"]
member_properties = ["name", "email", "password", "role"]
member_allowed_properties = ["email", "password", "name"]

ERROR_CONSTANTS = {
    "ERR_BOOK_NOT_FOUND": {"message": "Book not found.", "status": 400},
    "ERR_BOOK_STOCKED_OUT": {"message": "Book stocked out.", "status": 400},
    "BOOK_ALLOTMENT_SUCCESS": {"message": "Book submitted successfully", "status": 201},
    "BOOK_UPDATE_SUCCESS": {"message": "Book updated Successfully", "status": 200},
    "BOOK_UPDATE_FAILURE": {"message": "Book update Failed", "status": 400},
    "BOOK_DELETE_SUCCESS": {"message": "Book Deleted Successfully", "status": 200},
    "BOOK_ISSUE_SUCCESS": {"message": "Book issued successfully", "status": 201},
    "ERR_BOOK_ISSUED": {"message": "Book already issued to this member", "status": 400},
    "ERR_MEMBER_EXISTS": {"message": "Member already exists.", "status": 400},
    "MEMBER_ADDED_SUCCESS": {"message": "Member added successfully", "status": 200},
    "MEMBER_DELETED_SUCCESS": {"message": "Member deleted successfully", "status": 200},
    "MEMBER_DETAILS_UPDATE_SUCCESS": {"message": "Member details updated successfully", "status": 201},
    "ERR_MEMBER_NOT_FOUND": {"message": "Member not found", "status": 400},
    "ERR_INTERNAL_ERROR": {"message": "Internal server error.", "status": 500},
    "ERR_NO_TRANSACTION": {"message": "No Transaction record found.", "status": 400},
    "MAX_TRANSACTION_LIMIT": {"message": "Please pay {x} rupees in order to close the transaction.", "status": 200},
    "TRANSACTION_SUCCESS": {"message": "You paid {x} rupees while submitting the books", "status": 200},
    "ERR_TRANSACTION_EXISTS": {"message": "Transaction already exists", "status": 400},
    "ERR_UNAUTHORIZED": {"message": "You don't have access to view other member details", "status": 403 }
}
