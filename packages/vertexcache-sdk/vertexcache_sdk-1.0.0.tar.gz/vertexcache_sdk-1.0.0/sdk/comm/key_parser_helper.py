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

import base64
import re
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from sdk.model.vertex_cache_sdk_exception import VertexCacheSdkException


def config_public_key_if_enabled(public_key_pem: str):
    try:
        cleaned = re.sub(r"\s+", "", public_key_pem.replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", ""))
        decoded = base64.b64decode(cleaned, validate=True)

        serialization.load_der_public_key(decoded, backend=default_backend())
        return decoded
    except Exception:
        raise VertexCacheSdkException("Invalid public key")


def config_shared_key_if_enabled(shared_key: str) -> bytes:
    try:
        decoded = base64.b64decode(shared_key, validate=True)
        if base64.b64encode(decoded).decode().strip() != shared_key.strip().replace("\n", "").replace("\r", ""):
            raise VertexCacheSdkException("Invalid shared key")
        return decoded
    except Exception:
        raise VertexCacheSdkException("Invalid shared key")
