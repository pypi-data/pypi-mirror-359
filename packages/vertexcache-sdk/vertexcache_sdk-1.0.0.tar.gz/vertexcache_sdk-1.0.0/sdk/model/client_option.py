# ------------------------------------------------------------------------------
# Copyright 2025 to Present, Jason Lam - VertexCache (https://github.com/vertexcache/vertexcache)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

from sdk.model.encryption_mode import EncryptionMode
from sdk.model.vertex_cache_sdk_exception import VertexCacheSdkException
from sdk.comm import key_parser_helper
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

class ClientOption:
    DEFAULT_CLIENT_ID = "sdk-client"
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 50505
    DEFAULT_READ_TIMEOUT = 3000
    DEFAULT_CONNECT_TIMEOUT = 3000

    def __init__(self):
        self.client_id: str = self.DEFAULT_CLIENT_ID
        self.client_token: str = ""

        self.server_host: str = self.DEFAULT_HOST
        self.server_port: int = self.DEFAULT_PORT

        self.enable_tls_encryption: bool = False
        self.tls_certificate: str = ""
        self.verify_certificate: bool = False

        self.encryption_mode: EncryptionMode = EncryptionMode.NONE
        self.encrypt_with_public_key: bool = False
        self.encrypt_with_shared_key: bool = False

        self.public_key: str = ""
        self.shared_encryption_key: str = ""

        self.read_timeout: int = self.DEFAULT_READ_TIMEOUT
        self.connect_timeout: int = self.DEFAULT_CONNECT_TIMEOUT

    def get_client_id(self) -> str:
        return self.client_id if self.client_id is not None else ""

    def get_client_token(self) -> str:
        return self.client_token if self.client_token is not None else ""

    def build_ident_command(self) -> str:
        return f'IDENT {{"client_id":"{self.get_client_id()}", "token":"{self.get_client_token()}"}}'

    def set_public_key(self, public_key: str):
        self.public_key = public_key

    def set_shared_encryption_key(self, shared_key: str):
        self.shared_encryption_key = shared_key

    def get_encryption_mode(self) -> EncryptionMode:
        return self.encryption_mode

    def get_public_key_as_object(self):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.backends import default_backend
        try:
            return serialization.load_pem_public_key(
                self.public_key.encode("utf-8"),
                backend=default_backend()
            )
        except Exception:
            raise VertexCacheSdkException("Invalid public key")

    def get_shared_encryption_key_as_bytes(self) -> bytes:
        return key_parser_helper.config_shared_key_if_enabled(self.shared_encryption_key)
