import base64
from urllib.parse import urlsplit

import keyring


class KeyringTokenAuth:
    scheme = "Bearer"

    def __init__(self, username):
        self.username = username

    def password(self, req):
        return keyring.get_password(
            service_name=urlsplit(req.url).hostname,
            username=self.username,
        )

    def __call__(self, req):
        password = self.password(req)
        req.headers["Authorization"] = f"{self.scheme} {password}"
        return req


class KeyringBasicAuth(KeyringTokenAuth):
    scheme = "Basic"

    def password(self, req):
        pwd = super().password(req)
        return base64.b64encode(f"{self.username}:{pwd}".encode("ascii")).decode("ascii")
