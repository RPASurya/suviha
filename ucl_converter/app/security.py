import os
from cryptography.fernet import Fernet, InvalidToken


def get_fernet():
    key = os.getenv("UCL_ENCRYPTION_KEY", "").strip()
    if not key or key == "PASTE_GENERATED_FERNET_KEY_HERE":
        raise RuntimeError("Set UCL_ENCRYPTION_KEY in .env before saving provider API keys.")
    try:
        return Fernet(key.encode())
    except Exception as exc:
        raise RuntimeError("UCL_ENCRYPTION_KEY is invalid. Generate a Fernet key and restart.") from exc


def encrypt_secret(value: str) -> str:
    return get_fernet().encrypt(value.encode()).decode() if value else ""


def decrypt_secret(value: str) -> str:
    if not value:
        return ""
    try:
        return get_fernet().decrypt(value.encode()).decode()
    except InvalidToken as exc:
        raise RuntimeError("Cannot decrypt saved API key. Check that UCL_ENCRYPTION_KEY has not changed.") from exc
