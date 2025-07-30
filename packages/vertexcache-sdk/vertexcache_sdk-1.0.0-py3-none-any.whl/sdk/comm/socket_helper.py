# ------------------------------------------------------------------------------
# Copyright 2025 to Present, Jason Lam - VertexCache (https://github.com/vertexcache)
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

import socket
import ssl
from sdk.comm.ssl_helper import SSLHelper
from sdk.model.client_option import ClientOption
from sdk.model.vertex_cache_sdk_exception import VertexCacheSdkException


class SocketHelper:
    @staticmethod
    def create_secure_socket(option: ClientOption) -> ssl.SSLSocket:
        try:
            raw_sock = socket.create_connection(
                (option.server_host, option.server_port),
                timeout=option.connect_timeout
            )
            raw_sock.settimeout(option.read_timeout)

            context = (
                SSLHelper.create_verified_socket_context(option.tls_certificate)
                if option.verify_certificate
                else SSLHelper.create_insecure_socket_context()
            )

            wrapped_sock = context.wrap_socket(
                raw_sock,
                server_hostname=option.server_host
            )
            wrapped_sock.settimeout(option.read_timeout)
            return wrapped_sock
        except Exception:
            raise VertexCacheSdkException("Failed to create Secure Socket")

    @staticmethod
    def create_socket_non_tls(option: ClientOption) -> socket.socket:
        try:
            sock = socket.create_connection(
                (option.server_host, option.server_port),
                timeout=option.connect_timeout
            )
            sock.settimeout(option.read_timeout)
            return sock
        except Exception:
            raise VertexCacheSdkException("Failed to create Non Secure Socket")
