import base64
import json
import hmac
import hashlib
import random
import string
import time
from typing import Any, Dict
from urllib.parse import urlparse

from .exceptions import ValidationError


def validate_url(url: str) -> None:
    """
    Validate if the provided string is a valid URL.

    Args:
        url (str): The URL string to validate.

    Raises:
        ValidationError: If the URL is invalid or missing scheme/netloc.
    """
    parsed = urlparse(url)
    if not (parsed.scheme and parsed.netloc):
        raise ValidationError(f"Invalid URL: {url}")


def validate_amount(value: float, field_name: str) -> None:
    """
    Validate that the given amount is non-negative.

    Args:
        value (float): The amount value to validate.
        field_name (str): Name of the field for error messages.

    Raises:
        ValidationError: If the amount is negative.
    """
    if value < 0:
        raise ValidationError(f"{field_name} must be non-negative.")


def generate_hmac_sha256_hash(
    data: str,
    secret: str,
    algorithm: str = "sha256",
    encoding: str = "base64"
) -> str:
    """
    Generate an HMAC SHA-256 hash of the given data string using the secret key.

    Args:
        data (str): The data string to hash.
        secret (str): The secret key for HMAC hashing.
        algorithm (str, optional): Hashing algorithm to use (default is "sha256").
        encoding (str, optional): Encoding format of output ("base64" or "hex", default "base64").

    Returns:
        str: The resulting HMAC hash encoded as specified.

    Raises:
        ValidationError: If data or secret is missing.
    """
    if not data or not secret:
        raise ValidationError("Both data and secret are required to generate a hash.")
    hash_bytes = hmac.new(secret.encode(), data.encode(), getattr(hashlib, algorithm)).digest()
    if encoding == "base64":
        return base64.b64encode(hash_bytes).decode()
    return hash_bytes.hex()


def safe_json_dumps(obj: Any) -> str:
    """
    Safely serialize an object to a JSON string, ignoring circular references.

    Args:
        obj (Any): The Python object to serialize.

    Returns:
        str: JSON string representation of the object without circular references.
    """
    seen = set()

    def default(o):
        if id(o) in seen:
            return None
        seen.add(id(o))
        return str(o)

    return json.dumps(obj, default=default)


def base64_decode(encoded: str) -> Dict:
    """
    Decode a Base64 or Base64Url encoded string to a Python dictionary.

    Args:
        encoded (str): The Base64/Base64Url encoded string.

    Returns:
        Dict: The decoded JSON as a Python dictionary.
    """
    padded = encoded + "=" * (-len(encoded) % 4)
    standard_b64 = padded.replace("-", "+").replace("_", "/")
    decoded_bytes = base64.b64decode(standard_b64)
    return json.loads(decoded_bytes)


def generate_unique_id() -> str:
    """
    Generate a unique transaction ID string.

    Returns:
        str: A unique ID in the format "id-{timestamp}-{random_string}".
    """
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
    return f"id-{int(time.time())}-{random_part}"
