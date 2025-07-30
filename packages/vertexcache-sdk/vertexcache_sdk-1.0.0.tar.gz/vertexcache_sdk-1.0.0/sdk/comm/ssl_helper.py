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

import ssl
import tempfile
from sdk.model.vertex_cache_sdk_exception import VertexCacheSdkException


class SSLHelper:
    @staticmethod
    def create_verified_socket_context(pem_cert: str) -> ssl.SSLContext:
        try:
            if not pem_cert or "BEGIN CERTIFICATE" not in pem_cert:
                raise VertexCacheSdkException("Invalid certificate format")

            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.load_verify_locations(cadata=pem_cert)
            return context
        except Exception:
            raise VertexCacheSdkException("Failed to create secure socket connection")

    @staticmethod
    def create_insecure_socket_context() -> ssl.SSLContext:
        try:
            context = ssl._create_unverified_context()
            return context
        except Exception:
            raise VertexCacheSdkException("Failed to create non secure socket connection")
