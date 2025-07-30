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

import threading
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from sdk.comm import socket_helper
from sdk.model.vertex_cache_sdk_exception import VertexCacheSdkException
from sdk.comm import message_codec
from sdk.comm import gcm_crypto_helper
from sdk.model.encryption_mode import EncryptionMode


class ClientConnector:
    def __init__(self, options):
        self.options = options
        self.socket = None
        self.reader = None
        self.writer = None
        self.connected = False
        self._lock = threading.Lock()

    def connect(self):
        try:
            if self.options.enable_tls_encryption:
                self.socket = socket_helper.SocketHelper.create_secure_socket(self.options)
            else:
                self.socket = socket_helper.SocketHelper.create_socket_non_tls(self.options)

            self.reader = self.socket
            self.writer = self.socket

            ident_payload = self.options.build_ident_command().encode("utf-8")
            framed = message_codec.write_framed_message(self._encrypt_if_enabled(ident_payload))
            self.writer.sendall(framed)

            response = self._read_response()
            if not response.startswith("+OK"):
                raise VertexCacheSdkException("Authorization failed: " + response)

            self.connected = True
        except Exception as e:
            raise VertexCacheSdkException("Failed to connect: " + str(e))

    def send(self, message):
        with self._lock:
            try:
                payload = message.encode("utf-8")
                framed = message_codec.write_framed_message(self._encrypt_if_enabled(payload))
                self.writer.sendall(framed)
                response = self._read_response()
                return response
            except Exception as e:
                raise VertexCacheSdkException("Unexpected failure during send: " + str(e))

    def _read_response(self):
        buffer = bytearray()
        while True:
            chunk = self.reader.recv(4096)
            if not chunk:
                break
            buffer.extend(chunk)
            result = message_codec.read_framed_message(bytes(buffer))
            if result:
                payload, _ = result
                return payload.decode("utf-8")
        raise VertexCacheSdkException("Connection closed by server")

    def _encrypt_if_enabled(self, plain_text: bytes) -> bytes:
        mode = self.options.get_encryption_mode()
        try:
            if mode == EncryptionMode.ASYMMETRIC:
                message_codec.switch_to_asymmetric()
                public_key = self.options.get_public_key_as_object()
                return public_key.encrypt(
                    plain_text,
                    padding.PKCS1v15()
                )
            elif mode == EncryptionMode.SYMMETRIC:
                message_codec.switch_to_symmetric()
                return gcm_crypto_helper.encrypt(plain_text, self.options.get_shared_encryption_key_as_bytes())
            else:
                return plain_text
        except Exception:
            raise VertexCacheSdkException("Encryption failed for, text redacted *****")

    def is_connected(self):
        try:
            return self.connected and self.socket is not None
        except Exception:
            return False

    def close(self):
        try:
            if self.socket:
                self.socket.close()
        except Exception:
            pass
        self.connected = False