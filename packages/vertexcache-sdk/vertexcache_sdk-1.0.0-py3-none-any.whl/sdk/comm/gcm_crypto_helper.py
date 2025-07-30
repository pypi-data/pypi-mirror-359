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
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

GCM_IV_LENGTH = 12
GCM_TAG_LENGTH = 16  # Implicit in AESGCM output


def encrypt(plaintext: bytes, key: bytes) -> bytes:
    iv = os.urandom(GCM_IV_LENGTH)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, plaintext, associated_data=None)
    return iv + ciphertext


def decrypt(encrypted: bytes, key: bytes) -> bytes:
    if len(encrypted) < GCM_IV_LENGTH + GCM_TAG_LENGTH:
        raise ValueError("Encrypted data is too short")
    iv = encrypted[:GCM_IV_LENGTH]
    ciphertext = encrypted[GCM_IV_LENGTH:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(iv, ciphertext, associated_data=None)


def encode_base64_key(key: bytes) -> str:
    return base64.b64encode(key).decode("utf-8")


def decode_base64_key(encoded: str) -> bytes:
    return base64.b64decode(encoded.strip())


def generate_base64_key() -> str:
    return encode_base64_key(os.urandom(32))
