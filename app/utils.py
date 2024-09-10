from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()


def compare_hashed_password(hashed_password, password):
    return bcrypt.check_password_hash(hashed_password, password)


def generate_hashed_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')
