import base64
from typing import Optional

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError


class AuthError(Exception):
    pass


class Authenticator:
    def __init__(
        self,
        public_key_b64: Optional[str] = None,
        public_key_path: Optional[str] = None,
    ):
        if public_key_b64:
            key_pem = base64.b64decode(public_key_b64).decode("utf-8")
        elif public_key_path:
            with open(public_key_path, "r") as f:
                key_pem = f.read()
        else:
            raise ValueError("Provide either public_key_b64 or public_key_path")
        self.public_key = key_pem

    def validate_token(self, token: str, audience: str = None) -> dict:
        try:
            return jwt.decode(
                token, self.public_key, algorithms=["RS256"], audience=audience
            )
        except ExpiredSignatureError:
            raise AuthError("Token expired")
        except JWTClaimsError:
            raise AuthError("Invalid claims")
        except JWTError as e:
            raise AuthError(f"Invalid token: {e}")
