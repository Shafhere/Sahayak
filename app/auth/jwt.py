"""JWT token creation and verification."""
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import jwt

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))


def create_access_token(user_id: int, email: str, role: str) -> str:
    """Create a signed JWT token for a user."""
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=EXPIRY_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Verify and decode a JWT token. Raises jwt.PyJWTError if invalid."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])