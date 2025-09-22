import base64
import json
import zlib
from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer


class SimpleSecureCookieSessionInterface(SecureCookieSessionInterface):
    def get_signing_serializer(self, secret_key):
        signer_kwargs = dict(
            key_derivation=self.key_derivation,
            digest_method=self.digest_method
        )

        return URLSafeTimedSerializer(
            [secret_key], 
            salt=self.salt,
            serializer=self.serializer,
            signer_kwargs=signer_kwargs
        )

def encodeFlaskCookie(secret_key, cookieDict):
    return SimpleSecureCookieSessionInterface() \
            .get_signing_serializer(secret_key) \
            .dumps(cookieDict)

def decodeFlaskCookie(secret_key, cookie):
    return SimpleSecureCookieSessionInterface() \
            .get_signing_serializer(secret_key) \
            .loads(cookie)

def get_data_from_flask_session(session_cookie: str):
    data = session_cookie.split('.')[1].encode()
    for padding_length in range(3):
        try:
            data = zlib.decompress(base64.urlsafe_b64decode(data + b'=' * padding_length)).decode()
        except:
            continue

        break
    else:
        raise Exception("Failed to get data from flask session")

    data = json.loads(data)
    return data