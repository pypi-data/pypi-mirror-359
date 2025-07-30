"""URL-safe Base64 encoding without padding.

This format uses only characters that are safe for URLs, filenames etc.
Refer to Python's urlsafe_b64encode and base64.urlsafe_b64decode for more details.

Fixes Python base64 module's faults:
- Padding "==" is optional and not produced by b64url.enc
- Base64 type is str (stdlib is retarded and uses bytes)
- Otherwise identical to urlsafe_b64encode/urlsafe_b64decode
"""

from base64 import urlsafe_b64decode as _decode
from base64 import urlsafe_b64encode as _encode

__all__ = ["enc", "dec"]


def enc(data: bytes) -> str:
    """Base64 encode bytes to a URL-safe string without padding."""
    return _encode(data).decode("ascii").rstrip("=")


def dec(s: str) -> bytes:
    """Decode URL-safe Base64 into bytes. Padding optional."""
    # Testing whether needs padding is slower, this is the fastest way and constant time.
    return _decode(s + "=" * (4 - (len(s) % 4)))
