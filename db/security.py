"""Password hashing and verification using salted PBKDF2-SHA256."""
import hashlib
import hmac
import os

ITERATIONS = 200_000


def hash_password(password: str) -> str:
    """Return a salted PBKDF2 hash safe to store in the database."""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Check a typed password against a stored PBKDF2-SHA256 hash."""
    if not password or not stored:
        return False
    try:
        parts = stored.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        _algo, iterations, salt_hex, digest_hex = parts
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except Exception:
        return False
