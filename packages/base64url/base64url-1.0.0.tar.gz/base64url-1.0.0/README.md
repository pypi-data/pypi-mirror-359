# URL-safe Base64 for Python

A simple module for encoding without padding, fixing Python standard library's flaws.

Replaces the standard library's `base64.urlsafe_b64encode` and `base64.urlsafe_b64decode` with a cleaner implementation that returns strings instead of bytes and avoids unnecessary padding.

## Features

- **URL safe**: Uses only characters that are safe for URLs and filenames
- **No padding**: Removes trailing `=` characters for cleaner output
- **String output**: Returns proper strings instead of bytes (unlike Python's standard library)
- **Fast**: Based on Python stdlib, with constant-time padding restoration

## Installation

```sh
pip install base64url
```

Or for your project using [uv](https://docs.astral.sh/uv/):
```sh
uv add base64url
```

## Usage

```python
import base64url

text = base64url.enc(bytes(4)) # Returns "AAAAAA"
data = base64url.dec(text)     # Recovers the bytes
```

### `enc(data: bytes) -> str`

Base64 encode bytes to a URL-safe string without padding.

### `dec(s: str) -> bytes`

Decode URL-safe Base64 into bytes. Padding optional.