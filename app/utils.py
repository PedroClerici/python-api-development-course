from passlib.context import CryptContext
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    password_context.hash(password)
