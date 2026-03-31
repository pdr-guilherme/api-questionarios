import secrets
import string

ALPHABET = string.ascii_letters + string.digits


def create_password(length: int = 16) -> str:
    password = "".join(secrets.choice(ALPHABET) for _ in range(length))
    return password
