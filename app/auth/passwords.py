"""Password hashing with bcrypt directly (no passlib)."""
import bcrypt


def hash_password(plain: str) -> str:
    """Convert a plain password into a bcrypt hash."""
    # bcrypt requires bytes, and has a 72-byte limit
    password_bytes = plain.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Check if a plain password matches a stored hash."""
    try:
        password_bytes = plain.encode("utf-8")[:72]
        return bcrypt.checkpw(password_bytes, hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False