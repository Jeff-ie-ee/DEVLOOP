
from app.core.security import hash_password, verify_password


def test_password_is_hashed():
    password = "DEVLOOP-Test-Password-2026!"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert hashed_password.startswith("$argon2id$")


def test_correct_password_is_verified():
    password = "DEVLOOP-Test-Password-2026!"
    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password) is True


def test_incorrect_password_is_rejected():
    password = "DEVLOOP-Test-Password-2026!"
    hashed_password = hash_password(password)

    assert verify_password("Wrong-Password", hashed_password) is False


def test_password_hashes_use_unique_salts():
    password = "DEVLOOP-Test-Password-2026!"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash
    assert verify_password(password, first_hash)
    assert verify_password(password, second_hash)
