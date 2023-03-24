from passlib.context import CryptContext
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    password_context.hash(password)


def validate_password(plain_password: str, hashed_password: str):
    return password_context.verify(plain_password, hashed_password)